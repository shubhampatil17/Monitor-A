from models import JobHandler, Products
from pushbullet_operations import send_push_notification
from mail_client import send_email
from datetime import datetime
from urllib import parse
from collections import OrderedDict

import requests
import api_endpoints
import hmac
import hashlib
import base64
import json
import time
import random
import xml.etree.ElementTree as et
import database_connection

config = json.loads(open('config.json').read())

amazon_namespaces = {
    'error': 'http://ecs.amazonaws.com/doc/2013-08-01/',
    'response': 'http://webservices.amazon.com/AWSECommerceService/2013-08-01'
}


def get_number_of_calls_for_batch(batch_size):
    number_of_calls = (batch_size // 10) + 1 if batch_size % 10 else (batch_size // 10)
    return number_of_calls


def fetch_interval_validity(interval, asin, username):
    existing_product = Products.objects(asin=asin, username=username).first()
    interval_exception = existing_product.interval if existing_product else None
    total_api_calls_consumed = 0

    for job in JobHandler.objects:
        batch_size = job.batch_size

        if interval_exception and job.interval == interval_exception:
            batch_size -= 1

        if job.interval == interval:
            batch_size += 1

        total_api_calls_consumed += (get_number_of_calls_for_batch(batch_size) / job.interval) * 3600

    if total_api_calls_consumed > 2000:
        api_calls_remaining = 2000 - total_api_calls_consumed
        suggested_interval = (3600 / api_calls_remaining)

        status = False
        err = "Error : Cannot add product. " \
              "API call limits exceeding. " \
              "Suggested interval : Greater than or equal to {} second(s)".format(str(suggested_interval))

    else:
        status, err = True, None

    return status, err


def get_request_signature(params, locale):
    canonical_string = 'GET\n{}\n/onca/xml\n{}'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[locale.lower()],
                                                       parse.urlencode(params))
    digest = hmac.new(config['AWS_SECRET_KEY'].encode(), msg=canonical_string.encode(),
                      digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    return signature


def fetch_product_validity(asin, locale):
    params = OrderedDict(sorted({
                                    'Service': 'AWSECommerceService',
                                    'AWSAccessKeyId': config['AWS_ACCESS_KEY_ID'],
                                    'AssociateTag': config['AWS_LOCALE_CREDENTRIALS'][locale.lower()]['associate_tag'],
                                    'Operation': 'ItemLookup',
                                    'ItemId': asin.upper(),
                                    'IdType': 'ASIN',
                                    'ResponseGroup': 'ItemAttributes,Offers,Images',
                                    'Version': '2013-08-01',
                                    'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                                }.items()))

    params['Signature'] = get_request_signature(params, locale)
    response = et.fromstring(
        requests.get('https://{}/onca/xml'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[locale.lower()]),
                     params=params).text)

    if response.find('error:Error', amazon_namespaces):
        valid_asin = False
        message = "Something went wrong ! Please try again later."
        product_url = None
        image_url = None
        price = None
    elif response.find('.//response:Request/response:Errors', amazon_namespaces):
        error = response.find('.//response:Request/response:Errors', amazon_namespaces).find('response:Error',
                                                                                             amazon_namespaces)
        valid_asin = False
        message = error.find('response:Message', amazon_namespaces).text
        product_url = None
        image_url = None
        price = None
    else:
        valid_asin = True
        message = None
        product_url = response.find('.//response:DetailPageURL', amazon_namespaces).text
        image_url = response.find('.//response:Item/response:LargeImage', amazon_namespaces).find('response:URL',
                                                                                                  amazon_namespaces).text
        price = float(response.find('.//response:OfferSummary/response:LowestNewPrice/response:Amount',
                                    amazon_namespaces).text) / 100

    return valid_asin, message, product_url, image_url, price


def fetch_product_data_by_item_lookup(products):
    try:
        while True:
            params = OrderedDict(sorted({
                                            'Service': 'AWSECommerceService',
                                            'AWSAccessKeyId': config['AWS_ACCESS_KEY_ID'],
                                            'AssociateTag':
                                                config['AWS_LOCALE_CREDENTRIALS'][products[0].locale.lower()][
                                                    'associate_tag'],
                                            'Operation': 'ItemLookup',
                                            'ItemId': ','.join([product.asin.upper() for product in products]),
                                            'IdType': 'ASIN',
                                            'ResponseGroup': 'ItemAttributes,Offers,Images',
                                            'Version': '2013-08-01',
                                            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        }.items()))

            params['Signature'] = get_request_signature(params, products[0].locale)
            response = et.fromstring(requests.get(
                'https://{}/onca/xml'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[products[0].locale.lower()]),
                params=params).text)

            if response.find('error:Error', amazon_namespaces):
                time.sleep(random.randint(1, 10))
            else:
                data = [{'price': float(item.find('.//response:OfferSummary/response:LowestNewPrice/response:Amount', amazon_namespaces).text)/100} for item in response.findall('.//response:Item', amazon_namespaces)]
                break;
    except:
        data = [{'price': product.last_notified_price} for product in products ]

    return data


def check_product_price_on_regular_interval(interval, locale):
    products = Products.objects(interval=interval, locale=locale)
    number_of_batches = (len(products) // 10) + 1

    for x in range(number_of_batches):
        start_index = x * 10
        end_index = x * 10 + 10 if x < number_of_batches - 1 else len(products)
        batch = products[start_index:end_index]
        data = fetch_product_data_by_item_lookup(batch)

        for index in range(len(batch)):
            product, current_price = batch[index], data[index]['price']

            if current_price < product.threshold_price and current_price != product.last_notified_price:
                send_push_notification(product, current_price)
                send_email(product, current_price)

            product.last_notified_price = current_price
            product.save()

        time.sleep(1)

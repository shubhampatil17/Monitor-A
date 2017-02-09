from models import JobHandler, Products
import requests
import api_endpoints
import database_connection
from pushbullet_operations import send_push_notification
from mail_client import send_email
from datetime import datetime
from urllib import parse
from collections import OrderedDict
from copy import deepcopy

import hmac
import hashlib
import base64
import json

config = json.loads(open('config.json').read())


def get_number_of_calls_for_batch(batch_size):
    number_of_calls = (batch_size // 10) + 1 if batch_size % 10 else (batch_size // 10)
    return number_of_calls


def is_interval_valid(interval, asin, username):
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


def get_request_signature(params, endpoint, aws_secret_key):
    canonical_string = 'GET\n{}\n/onca/xml\n{}'.format(endpoint, parse.urlencode(params))
    print(canonical_string)
    digest = hmac.new(aws_secret_key.encode(), msg=canonical_string.encode(), digestmod=hashlib.sha256).digest()
    encrypted_hmac = parse.quote(base64.b64encode(digest))
    return encrypted_hmac


def is_asin_valid(asin, locale):
    params = {
        'Service': 'AWSECommerceService',
        'AWSAccessKeyId': config['AWS_ACCESS_KEY_ID'],
        'AssociateTag': config['AWS_LOCALE_CREDENTRIALS'][locale.lower()]['associate_tag'],
        'Operation': 'ItemLookup',
        'ItemId': asin.upper(),
        'IdType': 'ASIN',
        # 'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews',
        'Version': '2013-08-01',
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    print(parse.urlencode(params))
    params = OrderedDict(sorted(params.items()))
    print(parse.urlencode(params))

    string_to_sign = 'GET\n{}\n/onca/xml\n{}'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[locale], parse.urlencode(params))
    print(string_to_sign)

    digest = hmac.new(config['AWS_SECRET_KEY'].encode(), msg=string_to_sign.encode(), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    print(signature)

    params['Signature'] = signature
    print(parse.urlencode(params))

    # params = OrderedDict(sorted({
    #     'Service': 'AWSECommerceService',
    #     'AWSAccessKeyId': config['AWS_ACCESS_KEY_ID'],
    #     'AssociateTag': config['AWS_LOCALE_CREDENTRIALS'][locale.lower()]['associate_tag'],
    #     'Operation': 'ItemLookup',
    #     'ItemId': asin.upper(),
    #     'IdType': 'ASIN',
    #     # 'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews',
    #     'Version': '2013-08-01',
    #     'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    # }.items()))
    #
    # print(params)
    # aws_secret_key = config['AWS_SECRET_KEY']
    # signature = get_request_signature(params, api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[locale], aws_secret_key)
    # params['Signature'] = signature
    #
    # response = requests.get('http://{}/onca/xml'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[locale.lower()]), params=params)
    # print(response.url)
    # print(response.text)
    return True, None


def fetch_product_data_by_item_lookup(products):
    params = {
        'Service': 'AWSECommerceService',
        'AWSAccessKeyId': config['AWS_ACCESS_KEY_ID'],
        'AssociateTag': config['AWS_LOCALE_CREDENTRIALS'][products[0].locale.lower()]['associate_tag'],
        'Operation': 'ItemLookup',
        'ItemId': ','.join([product.asin.upper() for product in products]),
        # 'ItemId': 'B00008OE6I,B35987036I,B0002546I,B25468OE6I,B09788OE6I,B00453OE6I',
        'IdType': 'ASIN',
        # 'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews',
        'Version': '2013-08-01',
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    aws_secret_key = bytearray(config['AWS_SECRET_KEY'], encoding='utf-8')
    signature = get_request_signature(params, api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[products[0].locale], aws_secret_key)
    params['Signature'] = signature

    response = requests.get('https://{}/onca/xml'.format(api_endpoints.AMAZON_PRODUCT_API_ENDPOINTS[products[0].locale.lower()]), params=params)
    #parse response


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
                send_push_notification(product)
                # send_email(product)

is_asin_valid("B00J9A9TKY", "co.uk")
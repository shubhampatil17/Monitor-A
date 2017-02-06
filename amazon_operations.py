# from models import JobHandler, Products
# import requests
# import api_endpoints
# import database_connection
# from pushbullet_operations import send_push_notification
# from mail_client import send_email
#
# def get_number_of_calls_for_batch(batch_size):
#     number_of_calls = (batch_size // 10) + 1 if batch_size % 10 else (batch_size // 10)
#     return number_of_calls
#
#
# def is_interval_valid(interval, asin, username):
#     existing_product = Products.objects(asin=asin, username=username).first()
#     interval_exception = existing_product.interval if existing_product else None
#     total_api_calls_consumed = 0
#
#     for job in JobHandler.objects:
#         batch_size = job.batch_size
#
#         if interval_exception and job.interval == interval_exception:
#             batch_size -= 1
#
#         if job.interval == interval:
#             batch_size += 1
#
#         total_api_calls_consumed += (get_number_of_calls_for_batch(batch_size) / job.interval) * 3600
#
#     if total_api_calls_consumed > 2000:
#         api_calls_remaining = 2000 - total_api_calls_consumed
#         suggested_interval = (3600 / api_calls_remaining)
#
#         status = False
#         err = "Error : Cannot add product. " \
#               "API call limits exceeding. " \
#               "Suggested interval : Greater than or equal to {} second(s)".format(str(suggested_interval))
#
#     else:
#         status, err = True, None
#
#     return status, err
#
# def amazon_item_lookup(asins):
#     params = {
#         'Service': 'AWSECommerceService',
#         'AWSAccessKeyId': 'access_key_id',
#         'AssociateTag': 'associate_tag',
#         'Operation': 'ItemLookup',
#         'ItemId': ','.join(asins),
#         'IdType': 'ASIN',
#         'Timestamp': 'some_time_stamp',
#         'Signature': 'some_signature'
#     }
#
#     response = requests.get(api_endpoints.AMAZON_UK_PRODUCT_API_ENDPOINT, params=params)
#     return response
#
# def is_asin_valid(asin):
#     # call amazon api here and
#     # check response if asin is valid
#     return True, None
#
#
# def fetch_product_data_by_item_lookup(products):
#     # call amazon api here to fetch data for products
#     pass
#
#
# def check_product_price_on_regular_interval(interval, locale):
#     pass
#     # products = Products.objects(interval=interval, locale=locale)
#     # number_of_batches = (len(products) // 10) + 1
#     #
#     # for x in range(number_of_batches):
#     #     start_index = x * 10
#     #     end_index = x * 10 + 10 if x < number_of_batches - 1 else len(products)
#     #     batch = products[start_index:end_index]
#     #     data = fetch_product_data_by_item_lookup(batch)
#     #
#     #     for index in range(len(batch)):
#     #         product, current_price = batch[index], data[index]['price']
#     #         if current_price < product.threshold_price and current_price != product.last_notified_price:
#     #             send_push_notification(product)
#                 # send_email(product)

from datetime import datetime
from urllib import parse

awsAccessKeyId = 'AKIAIOSFODNN7EXAMPLE'
awsSecretKey = '1234567890'

params = {
    'Service': 'AWSECommerceService',
    'AWSAccessKeyId': awsAccessKeyId,
    'AssociateTag': 'mytag-20',
    'Operation': 'ItemLookup',
    'ItemId': 'B00008OE6I,B35987036I,B0002546I,B25468OE6I,B09788OE6I,B00453OE6I',
    'ResponseGroup': 'ItemAttributes,Offers,Images,Reviews',
    'Version': '2013-08-01',
    'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
}

for key in params:
    params[key]=parse.quote(params[])

print(params)
# print(parse.urlencode(params))
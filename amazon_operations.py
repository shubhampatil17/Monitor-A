from models import JobHandler, Products
from database_connection import *

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

        total_api_calls_consumed += (get_number_of_calls_for_batch(batch_size)/job.interval)*3600

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


def is_asin_valid(asin):
    #call amazon api here and
    #check response if asin is valid
    return True, None

def check_product_price_on_regular_interval(interval):
    print("Ok")

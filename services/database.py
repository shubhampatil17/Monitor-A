from mongoengine import connect
from models.Product import Product
from services.utils import get_time_in_seconds

class DatabaseService:

    def __init__(self, db, host=None, port=None, username=None, password=None):
        connect(db, host=host, port=port, username=username, password=password)

    def save_product(self, asin, interval, interval_unit, threshold_price, last_notified_price, job_id):
        Product(
            asin=asin,
            interval=interval,
            interval_unit=interval_unit,
            threshold_price=threshold_price,
            last_notified_price=last_notified_price,
            job_id=job_id
        ).save()

    def find_products(self, asin=None, interval=None, interval_unit=None, threshold_price=None, last_notified_price=None, job_id=None):

        products = Product.objects(
            asin=asin,
            interval=interval,
            interval_unit=interval_unit,
            threshold_price=threshold_price,
            last_notified_price=last_notified_price,
            job_id=job_id
        )

        return products

    def is_valid_interval(self, interval, interval_unit):
        total_api_calls_consumed = 0

        for product in Product.objects:
            current_interval, current_interval_unit = product.interval, product.interval_unit
            time_per_api_call = get_time_in_seconds(current_interval, current_interval_unit)
            total_api_calls_consumed += (3600/time_per_api_call)

        time_per_api_call = get_time_in_seconds(interval, interval_unit)
        api_calls_consumed_by_current_product = (3600/time_per_api_call)

        if (total_api_calls_consumed + api_calls_consumed_by_current_product) > 2000:
            api_calls_remaining = 2000 - total_api_calls_consumed
            suggested_interval = (3600/api_calls_remaining)

            err = "Error : Cannot add product. " \
                  "API call limits exceeding. " \
                  "Suggested interval : Greater than or equal to " + str(suggested_interval) + " second(s)"

            return False, err

        else:
            return True, None





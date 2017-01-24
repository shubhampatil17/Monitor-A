from models import JobHandler
from database_connection import *

def get_number_of_calls_for_batch(length_of_batch):
    number_of_calls = (length_of_batch//10) + 1 if length_of_batch%10 else (length_of_batch//10)
    return number_of_calls

def is_interval_valid(interval):
    total_api_calls_consumed = 0
    job_for_current_interval = JobHandler.objects(interval = interval).first()

    total_api_calls_consumed += (get_number_of_calls_for_batch(len(job_for_current_interval.asins)+1)/interval)*3600 if job_for_current_interval else (3600/interval)
    api_calls_per_job_per_hour = [(get_number_of_calls_for_batch(len(job.asins))/job.interval)*3600 for job in JobHandler.objects if job.interval != interval]
    total_api_calls_consumed += sum(api_calls_per_job_per_hour)

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

def check_product_price_on_regular_interval(asin, threshold_price):
    print("Ok")

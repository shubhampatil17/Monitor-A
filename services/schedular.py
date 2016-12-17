from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from services.amazon import check_product

jobstores = {
    'mongo' : MongoDBJobStore()
}

executors = {
    'default' : ThreadPoolExecutor(),
    'processpool' : ProcessPoolExecutor()
}

class SchedularService():
    def __init__(self):
        self.schedular = BackgroundScheduler(jobstores = jobstores, executors = executors, timezone = utc)

    def start_schedular(self):
        self.schedular.start()

    def add_job_to_schedular_store(self, id, asin, threshold_price, weeks=None, days=None, hours=None, minutes=None, seconds=None):
        self.schedular.add_job(
            check_product(asin, threshold_price),
            'interval',
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            id=id
        )
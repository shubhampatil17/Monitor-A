from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

jobstores = {
    'mongo' : MongoDBJobStore()
}

executors = {
    'default' : ThreadPoolExecutor(),
    'processpool' : ProcessPoolExecutor()
}

schedular = BackgroundScheduler(jobstores = jobstores, executors = executors, timezone = utc)
schedular.start()

def add_job_to_schedular(job, interval, job_id, args):
    schedular.add_job(
        job,
        'interval',
        seconds=interval,
        id=job_id,
        args=args,
        replace_existing=True
    )
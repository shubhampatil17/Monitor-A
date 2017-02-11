from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

jobstores = {
    'default' : MongoDBJobStore(database="test", collection="jobs")
}

executors = {
    'default' : ThreadPoolExecutor(),
    'processpool' : ProcessPoolExecutor()
}

job_defaults = {
    'max_instances': 3
}

schedular = BackgroundScheduler(jobstores = jobstores, executors = executors, job_defaults=job_defaults, timezone = utc)
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
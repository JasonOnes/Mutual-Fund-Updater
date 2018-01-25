from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


jobstores = {
    # 'mongo': MongoDBJobStore(),
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True, # if app interrupted not inundated with all the missing job executions (eg 100 texts about vtsmx)
    'max_instances': 10
}

# TODO add user input of timezone, localize()
pst = timezone('US/Pacific')
skedge = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=pst, id=id)


def skedge_start_with_check():
    try:
        skedge.start() 
    except SchedulerAlreadyRunningError:
        pass 

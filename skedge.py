from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
# JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from zappa.async import task

jobstores = {
    #'mongo': MongoDBJobStore(),
   
    # rds_url = 'mysql+pymysql://jasonones:rK4RKUm308JL@mysqlforfundr.cxsze9sotcbm.us-west-2.rds.amazonaws.com:3306/FunUp'
    'default': SQLAlchemyJobStore(url='mysql+pymysql://jasonones:rK4RKUm308JL@mysqlforfundr.cxsze9sotcbm.us-west-2.rds.amazonaws.com:3306/FunUp')
    #'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': ThreadPoolExecutor(20),
    #'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True, # if app interrupted not inundated with all the missing job executions (eg 100 texts about vtsmx)
    'max_instances': 10
}
skedge = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc, id=id)



@task # zappa task decorator to make a separate Lambda (AWS) instance when called
def skedge_check():
    try:
        skedge.start() 
    except SchedulerAlreadyRunningError:
        pass 

#skedge = BackgroundScheduler(daemon=True)
# skedge= BackgroundScheduler({
#         'apscheduler.jobstores.default':{
#         'type': 'sqlalchemy',
#         'url': 'sqlite:///jobs.sqlite'}
#     })

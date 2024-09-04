from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.database.base import database


# Define a function to create the appropriate scheduler
def create_scheduler(schedule_type):
    jobstores = {
        'default': SQLAlchemyJobStore(engine=database.engine)
    }
    
    if schedule_type == "background":
        return BackgroundScheduler(jobstores=jobstores)
    elif schedule_type == "asyncio":
        return AsyncIOScheduler(jobstores=jobstores)
    else:
        raise ValueError(f"Invalid schedule type: {schedule_type}")
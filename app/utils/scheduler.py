from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Define a function to create the appropriate scheduler
def create_scheduler(schedule_type):
    if schedule_type == "background":
        return BackgroundScheduler()
    elif schedule_type == "asyncio":
        return AsyncIOScheduler()
    else:
        raise ValueError(f"Invalid schedule type: {schedule_type}")
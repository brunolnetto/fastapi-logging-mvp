# This code snippet is setting up a scheduler in Python using the `asyncio` library for scheduling a
# task to clean up logs at regular intervals. Here's a breakdown of what the code is doing:
from datetime import timedelta

from .base import setup_scheduler
from .tasks import cleanup_logs
from .base import create_scheduled_job, setup_scheduler
from .schedulers import asyncio_scheduler

# Create a job function for scheduling
# Define cron parameters for scheduling
CLEANUP_CRON_KWARGS = {
    'minute': '0',
    'hour': '0',        # Runs at midnight
    'day': '*',         # Every day
    'month': '*',       # Every month
    'day_of_week': '*'  # Every day of the week
}
CLEANUP_AGE=timedelta(days=7)


cleanup_job_function = create_scheduled_job(
    task_name=f"Cleanup Logs with period {CLEANUP_CRON_KWARGS}", 
    task_type="cleanup",
    task_callable=cleanup_logs,
    age=CLEANUP_AGE
)

# Set up the scheduler
setup_scheduler(
    asyncio_scheduler, job_function=cleanup_job_function, 
    schedule_type="cron", **CLEANUP_CRON_KWARGS
)

schedulers = [
    asyncio_scheduler
]
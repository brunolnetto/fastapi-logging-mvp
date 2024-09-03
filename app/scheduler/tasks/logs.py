from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import timedelta
import asyncio

from app.database.base import get_session
from app.repositories.logs import RequestLogRepository, TaskLogRepository
from app.schemas import TaskConfig

async def cleanup_request_logs(time_delta: timedelta):
    """
    Cleans up requests logs older than the specified timedelta.

    Args:
        time_delta (timedelta): The time difference from now. Logs older than this will be deleted.
    """
    with get_session() as db_session:
        request_log_repository = RequestLogRepository(db_session)
        await request_log_repository.delete_old_logs(time_delta)

async def cleanup_task_logs(time_delta: timedelta):
    """
    Cleans up tasks logs older than the specified timedelta.

    Args:
        time_delta (timedelta): The time difference from now. Logs older than this will be deleted.
    """
    with get_session() as db_session:
        task_log_repository = TaskLogRepository(db_session)
        await task_log_repository.delete_old_logs(time_delta)

# Create a job function for scheduling
# Define cron parameters for scheduling
CLEANUP_REQUEST_CRON_KWARGS = {
    'minute': '0',
    'hour': '0',        # Runs at midnight
    'day': '*',         # Every day
    'month': '*',       # Every month
    'day_of_week': '*'  # Every day of the week
}

# Schedule the task to run at regular intervals
cleanup_request_config=TaskConfig(
    schedule_type='asyncio',
    schedule_params=CLEANUP_REQUEST_CRON_KWARGS,
    task_name=f"Cleanup request logs with schedule period {CLEANUP_REQUEST_CRON_KWARGS}",
    task_type="cron",
    task_callable=cleanup_request_logs,
    task_args=(timedelta(days=7), ),
)

# Define cron parameters for scheduling
CLEANUP_TASK_CRON_KWARGS = {
    'minute': '0',
    'hour': '0',        # Runs at midnight
    'day': '1',         # Every first day of the month
    'month': '*',       # Every month
    'day_of_week': '*'  # Every day of the week
}

# Schedule the task to run at regular intervals
cleanup_task_config=TaskConfig(
    schedule_type='asyncio',
    schedule_params=CLEANUP_TASK_CRON_KWARGS,
    task_name=f"Cleanup task logs with schedule period {CLEANUP_TASK_CRON_KWARGS}",
    task_type="cron",
    task_callable=cleanup_request_logs,
    task_args=(timedelta(days=30),),
)

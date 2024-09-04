from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import timedelta
import asyncio

from app.database.base import get_session
from app.repositories.logs import RequestLogRepository, TaskLogRepository
from app.schemas import TaskConfig
from app.config import settings

async def cleanup_request_logs(time_delta: timedelta, max_rows: int = None):
    """
    Cleans up requests logs based on either time or table row count.

    Args:
        time_delta (timedelta): The time difference from now. Logs older than this will be deleted.
        max_rows (int, optional): The maximum number of rows to retain. If specified, logs will be deleted based on their creation time and this count.
    """
    with get_session() as db_session:
        request_log_repository = RequestLogRepository(db_session)
        if max_rows is not None:
            await request_log_repository.delete_excess_logs(max_rows)
        else:
            await request_log_repository.delete_old_logs(time_delta)

async def cleanup_task_logs(time_delta: timedelta, max_rows: int = None):
    """
    Cleans up tasks logs based on either time or table row count.

    Args:
        time_delta (timedelta): The time difference from now. Logs older than this will be deleted.
        max_rows (int, optional): The maximum number of rows to retain. If specified, logs will be deleted based on their creation time and this count.
    """
    with get_session() as db_session:
        task_log_repository = TaskLogRepository(db_session)
        if max_rows is not None:
            await task_log_repository.delete_excess_logs(max_rows)
        else:
            await task_log_repository.delete_old_logs(time_delta)

# Schedule the task to run at regular intervals
cleanup_request_config=TaskConfig(
    schedule_type='asyncio',
    schedule_params=settings.REQUEST_CLEANUP_CRON_KWARGS,
    task_name=f"Cleanup request logs with schedule period {settings.REQUEST_CLEANUP_CRON_KWARGS}",
    task_type="cron",
    task_callable=cleanup_request_logs,
    task_args=(
        settings.REQUEST_CLEANUP_AGE, 
        settings.REQUEST_CLEANUP_MAX_ROWS
    ),
)

# Schedule the task to run at regular intervals
cleanup_task_config=TaskConfig(
    schedule_type='asyncio',
    schedule_params=settings.TASK_CLEANUP_CRON_KWARGS,
    task_name=f"Cleanup task logs with schedule period {settings.TASK_CLEANUP_CRON_KWARGS}",
    task_type="cron",
    task_callable=cleanup_task_logs,
    task_args=(
        settings.TASK_CLEANUP_AGE,
        settings.TASK_CLEANUP_MAX_ROWS
    ),
)

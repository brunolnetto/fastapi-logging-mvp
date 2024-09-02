from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import timedelta
import asyncio

from app.database import get_session
from app.repositories.logs import RequestLogRepository


async def setup_cleanup_logs(time_delta: timedelta):
    """
    Cleans up logs older than the specified timedelta.

    Args:
        time_delta (timedelta): The time difference from now. Logs older than this will be deleted.
    """
    with get_session() as db_session:
        log_repository = RequestLogRepository(db_session)
        await log_repository.delete_old_logs(time_delta)

async def cleanup_logs(age: timedelta):
    """
    Cleans up logs older than a specified time delta.
    """
    await setup_cleanup_logs(age)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from typing import Dict, Any, Callable
from datetime import datetime
import traceback
import inspect

from app.database import get_session
from app.models import TaskLog

# Custom exception for invalid scheduling parameters
class InvalidScheduleParameter(Exception):
    pass

def validate_interval_kwargs(kwargs: Dict[str, Any]):
    allowed_keys = {'weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'end_date', 'timezone'}
    invalid_keys = set(kwargs) - allowed_keys
    if invalid_keys:
        raise InvalidScheduleParameter(f"Invalid interval scheduling parameters: {invalid_keys}")

def validate_cron_kwargs(kwargs: Dict[str, Any]):
    allowed_keys = {
        'year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second',
        'start_date', 'end_date', 'timezone', 'jitter'
    }
    invalid_keys = set(kwargs) - allowed_keys
    if invalid_keys:
        raise InvalidScheduleParameter(f"Invalid cron scheduling parameters: {invalid_keys}")

# Generic function to set up scheduler
def setup_scheduler(scheduler, job_function, schedule_type="interval", **kwargs):
    """
    Set up the scheduler to run a specified job function based on the given schedule type.

    Args:
        job_function (callable): The function to schedule.
        schedule_type (str): The type of schedule to use ('interval' or 'cron').
        **kwargs: Additional keyword arguments for the trigger, such as 'days', 'hours', 'cron' parameters, etc.
    """
    if schedule_type == "interval":
        validate_interval_kwargs(kwargs)
        trigger = IntervalTrigger(**kwargs)
    elif schedule_type == "cron":
        validate_cron_kwargs(kwargs)
        trigger = CronTrigger(**kwargs)
    else:
        raise ValueError("Unsupported schedule_type. Use 'interval' or 'cron'.")

    scheduler.add_job(job_function, trigger)

async def run_task(
    task_name: str, task_type: str, task_details: Dict[str, Any], task_callable: Callable, *args, **kwargs
):
    """
    Run a task and log its execution details in the TaskLog table.

    Args:
        task_name (str): The name of the task being executed.
        task_type (str): The type of task (e.g., 'cleanup', 'data_processing').
        task_details (Dict[str, Any]): Additional details about the task (e.g., parameters used).
        task_callable (Callable): The function or method that executes the task logic.
        *args: Positional arguments to pass to the task_callable.
        **kwargs: Keyword arguments to pass to the task_callable.
    """
    with get_session() as session:
        task_log = TaskLog(
            talo_name=task_name,
            talo_type=task_type,
            talo_details=task_details,
            talo_start_time=datetime.now(),
            talo_status='running'
        )
        session.add(task_log)
        session.commit()

        try:
            # Determine if task_callable is asynchronous
            if inspect.iscoroutinefunction(task_callable):
                result = await task_callable(*args, **kwargs)
            else:
                result = task_callable(*args, **kwargs)

            task_log.talo_success = True
            task_log.talo_status = 'completed'
            task_log.talo_details['result'] = result

        except Exception as e:
            task_log.talo_success = False
            task_log.talo_status = 'failed'
            task_log.talo_error_message = str(e)
            task_log.talo_error_trace = traceback.format_exc()

        finally:
            task_log.talo_end_time = datetime.now()
            session.commit()

def create_scheduled_job(
    task_name: str, task_type: str, task_callable: Callable, task_details: Dict[str, Any] = dict(), *args, **kwargs
):
    """
    Create a job function for scheduling.

    Args:
        task_name (str): The name of the task being executed.
        task_type (str): The type of task (e.g., 'cleanup', 'data_processing').
        task_details (Dict[str, Any]): Additional details about the task (e.g., parameters used).
        task_callable (Callable): The function or method that executes the task logic.
        *args: Positional arguments to pass to the task_callable.
        **kwargs: Keyword arguments to pass to the task_callable.
    """
    async def job_function():
        await run_task(task_name, task_type, task_details, task_callable, *args, **kwargs)

    return job_function
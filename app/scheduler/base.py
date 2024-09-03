from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError

from typing import Dict, List, Tuple, Any, Callable
from datetime import datetime, timedelta
import traceback
import asyncio
import inspect

from app.database.base import get_session
from app.database.models.logs import TaskLog
from app.schemas import TaskConfig
from app.utils.scheduler import create_scheduler
from app.repositories.tasks import TaskRepository
from app.schemas import TaskCreate

# Custom exception for invalid scheduling parameters
class InvalidScheduleParameter(Exception):
    pass

def validate_date_format(date_str: str, date_format: str = "%Y-%m-%d"):
    try:
        datetime.strptime(date_str, date_format)
    except ValueError:
        raise InvalidScheduleParameter(f"Date '{date_str}' does not match format '{date_format}'")


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
def setup_scheduler(scheduler, job_function, schedule_params, task_type="interval"):
    """
    Set up the scheduler to run a specified job function based on the given schedule type.

    Args:
        job_function (callable): The function to schedule.
        schedule_type (str): The type of schedule to use ('interval' or 'cron').
        **kwargs: Additional keyword arguments for the trigger, such as 'days', 'hours', 'cron' parameters, etc.
    """
    if task_type == "interval":
        validate_interval_kwargs(schedule_params)
        trigger = IntervalTrigger(**schedule_params)
    elif task_type == "cron":
        validate_cron_kwargs(schedule_params)
        trigger = CronTrigger(**schedule_params)
    elif task_type == "date":
        if 'run_date' not in schedule_params:
            raise ValueError("For task_type 'date', 'run_date' must be specified in schedule_params.")
        trigger = DateTrigger(
            run_date=schedule_params['run_date'], 
            timezone=schedule_params.get('timezone')
        )
    
    else:
        raise ValueError("Unsupported schedule_type. Use 'interval' or 'cron'.")

    scheduler.add_job(job_function, trigger)

async def run_task(
    task_name: str, 
    task_type: str,  
    task_callable: Callable, 
    *task_args,
    **task_details
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
                result = await task_callable(*task_args, **task_details)
            else:
                result = task_callable(*task_args, **task_details)

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
    task_name: str, 
    task_type: str, 
    task_callable: Callable, 
    *task_args: Tuple[Any],
    **task_details: Dict[str, Any]
) -> Callable:
    """
    Create a job function for scheduling.
    """
    async def job_function():
        await run_task(task_name, task_type, task_callable, *task_args, **task_details)

    def run_job():
        # Create a new event loop if none exists for the current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(job_function())
        finally:
            loop.close()

    return run_job

class TaskOrchestrator:
    def __init__(self):
        self.schedulers = {
            "background": create_scheduler("background"),
            "asyncio": create_scheduler("asyncio")
        }

    def start(self):
        for scheduler in self.schedulers.values():
            scheduler.start()

    def shutdown(self):
        for scheduler in self.schedulers.values():
            scheduler.shutdown()

    async def add_task(self, task_config: TaskConfig):
        scheduler=self.schedulers.get(task_config.schedule_type, None)
        
        if scheduler:
            job_function = create_scheduled_job(
                task_name=task_config.task_name,
                task_type=task_config.task_type,
                task_callable=task_config.task_callable,
                task_details=task_config.task_details
            )

            setup_scheduler(
                scheduler, job_function, task_config.schedule_params, task_config.task_type
            )

        else:
            invalid_message=f"Invalid scheduler type: {task_config.schedule_type}."
            available_message=f"Available schedulers: {self.schedulers.keys()}"
            raise ValueError(f"{invalid_message} {available_message}")

    def remove_task(self, schedule_type: str, task_name: str):
        scheduler = self._get_scheduler(schedule_type)
        try:
            scheduler.remove_job(task_name)
        except JobLookupError:
            raise ValueError(f"Task '{task_name}' not found in scheduler '{schedule_type}'.")

    def list_tasks(self, schedule_type: str):
        scheduler = self._get_scheduler(schedule_type)
        return scheduler.get_jobs()

    def _get_scheduler(self, schedule_type: str):
        scheduler = self.schedulers.get(schedule_type)
        if not scheduler:
            invalid_message = f"Invalid scheduler type: {schedule_type}."
            available_message = f"Available schedulers: {list(self.schedulers.keys())}"
            raise ValueError(f"{invalid_message} {available_message}")

        return scheduler
    
class TaskRegister:
    def __init__(self, session):
        self.task_repository = TaskRepository(session)

    def register(self, task_configs: List[TaskConfig]):
        for config in task_configs:
            # Prepare task data using TaskCreate Pydantic model
            task_data = TaskCreate(
                task_name=config.task_name,
                task_type=config.task_type,
                task_details=config.task_details,
                task_is_active=True
            )
            # Register the task using the repository's create method
            self.task_repository.create(task_data)
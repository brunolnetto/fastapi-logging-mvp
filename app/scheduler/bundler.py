# This code snippet is setting up a scheduler in Python using the `asyncio` library for scheduling a
# task to clean up logs at regular intervals. Here's a breakdown of what the code is doing:
from datetime import timedelta
from asyncio import create_task

from app.scheduler.tasks.logs import cleanup_request_logs
from app.scheduler.base import TaskOrchestrator, TaskRegister
from app.repositories.tasks import TaskRepository

from app.database.base import get_session

from app.scheduler.tasks.bundler import task_configs

task_orchestrator = TaskOrchestrator()

async def add_tasks():
    """
    This function creates a task orchestrator and adds tasks to it.
    
    The tasks are defined in the `task_configs` list, which contains 
    dictionaries with the following keys
    """

    for task_config in task_configs: 
        await task_orchestrator.add_task(task_config)

# Add to task orchestrator
create_task(add_tasks())

# Insert on database
with get_session() as session:
    task_register = TaskRegister(session)
    task_register.register(task_configs)

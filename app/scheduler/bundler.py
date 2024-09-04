# This code snippet is setting up a scheduler in Python using the `asyncio` library for scheduling a
# task to clean up logs at regular intervals. Here's a breakdown of what the code is doing:
from datetime import timedelta
import asyncio

from app.scheduler.tasks.logs import cleanup_request_logs
from app.scheduler.base import TaskOrchestrator, TaskRegister
from app.repositories.tasks import TaskRepository, get_task_repository
from app.schemas import TaskConfig

from app.database.base import get_session

from app.scheduler.tasks.bundler import task_configs

task_orchestrator = TaskOrchestrator()

async def add_tasks():
    """
    This function creates a task orchestrator and adds tasks to it.
    
    The tasks are defined in the `task_configs` list, which contains 
    instances of TaskConfig.
    """
    
    task_repository = get_task_repository()
    
    for index, task_config in enumerate(task_configs):
        # Check if a task with the same name already exists in the database
        existing_tasks = task_repository.get_all()  # Adjust if needed to filter by name
        
        # Compare existing tasks with the new one to avoid duplication
        duplicate_task = None
        for existing_task in existing_tasks:
            if existing_task.task_name == task_config.task_name:
                duplicate_task = existing_task
                break
        
        if duplicate_task:
            print(f"Task '{task_config.task_name}' already exists, skipping database addition...")
            
            print('antes')
            print(task_configs[index].task_id)

            task_configs[index].task_id = duplicate_task.task_id

            print('depois')
            print(task_configs[index].task_id)

            # Add the task to the orchestrator
            await task_orchestrator.add_task(task_config)
            continue

        # Save the new task to the database using the repository
        task_repository.create(task_config)

# Add to task orchestrator
asyncio.create_task(add_tasks())

# Insert on database
with get_session() as session:
    task_register = TaskRegister(session)
    task_register.register(task_configs)

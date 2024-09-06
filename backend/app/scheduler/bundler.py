# This code snippet is setting up a scheduler in Python using the `asyncio` library for scheduling a
# task to clean up logs at regular intervals. Here's a breakdown of what the code is doing:
import asyncio

from backend.app.scheduler.base import TaskOrchestrator, TaskRegister
from backend.app.repositories.tasks import get_task_repository
from backend.app.scheduler.tasks.bundler import task_configs

task_orchestrator = TaskOrchestrator()


async def add_tasks():
    """
    This function creates a task orchestrator and adds tasks to it.

    The tasks are defined in the `task_configs` list, which contains
    instances of TaskConfig.
    """

    task_repository = get_task_repository()

    # Check if a task with the same name already exists in the database
    existing_tasks = task_repository.get_all()  # Adjust if needed to filter by name

    for index, task_config in enumerate(task_configs):
        # Compare existing tasks with the new one to avoid duplication
        duplicate_task = None
        for existing_task in existing_tasks:
            if existing_task.task_name == task_config.task_name:
                duplicate_task = existing_task
                break

        if duplicate_task:
            task_configs[index].task_id = duplicate_task.task_id

            # Add the task to the orchestrator
            await task_orchestrator.add_task(task_configs[index])
            continue

        # Save the new task to the database using the repository
        task_register = TaskRegister(task_repository)
        task_register.register(task_configs)

    await asyncio.sleep(1)


# Add to task orchestrator
asyncio.create_task(add_tasks())

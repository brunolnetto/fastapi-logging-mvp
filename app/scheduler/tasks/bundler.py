from app.scheduler.tasks.logs import cleanup_request_config, cleanup_task_config
from app.scheduler.tasks.misc import print_empty_task_config, print_full_task_config
from app.schemas import TaskCreate, TaskConfig
from typing import List

task_configs=[
    cleanup_request_config, 
    cleanup_task_config,
    print_empty_task_config, 
    print_full_task_config
]

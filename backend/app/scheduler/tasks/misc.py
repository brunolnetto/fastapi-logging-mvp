from datetime import datetime
from uuid import uuid4

from backend.app.schemas import TaskConfig


def print_test(*args, **kwargs):
    print(datetime.now())
    print("Task details:", kwargs)
    print("Other args:", args)


# Create a job function for scheduling
# Define cron parameters for scheduling
SCHEDULE_PRINT_BACKGROUND_KWARGS = {"minutes": 1}

# Schedule the task to run at regular intervals
print_empty_task_config = TaskConfig(
    task_id=uuid4(),
    schedule_type="background",
    schedule_params=SCHEDULE_PRINT_BACKGROUND_KWARGS,
    task_name=f"Print 'Test task!' with schedule period {SCHEDULE_PRINT_BACKGROUND_KWARGS}",
    task_type="interval",
    task_callable=print_test,
)

PRINT_BACKGROUND_KWARGS = {"param1": "value1", "param2": "value2"}

print_full_task_config = TaskConfig(
    task_id=uuid4(),
    schedule_type="background",
    schedule_params=SCHEDULE_PRINT_BACKGROUND_KWARGS,
    task_name=f"Print 'Test task!' with schedule period {SCHEDULE_PRINT_BACKGROUND_KWARGS} and params {PRINT_BACKGROUND_KWARGS}",
    task_type="interval",
    task_callable=print_test,
    task_args=("test_arg",),
    task_details=PRINT_BACKGROUND_KWARGS,
)

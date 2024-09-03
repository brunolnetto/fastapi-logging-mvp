from datetime import timedelta
from app.database.base import get_session
from app.repositories.logs import TaskLogRepository
from app.schemas import TaskConfig

async def print_test():
    print('Test task!')

# Create a job function for scheduling
# Define cron parameters for scheduling
PRINT_BACKGROUND_KWARGS = {'minutes': 1}

# Schedule the task to run at regular intervals
print_task_config=TaskConfig(
    schedule_type='background',
    schedule_params=PRINT_BACKGROUND_KWARGS,
    task_name=f"Print 'Test task!' with schedule period {PRINT_BACKGROUND_KWARGS}",
    task_type="interval",
    task_callable=print_test
)
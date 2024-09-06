from backend.app.routers.misc import router as misc_router
from backend.app.routers.tasks import router as task_router
from backend.app.routers.logs import router as logs_router

routers = [misc_router, task_router, logs_router]

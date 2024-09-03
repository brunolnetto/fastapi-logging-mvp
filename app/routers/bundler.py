from app.routers.misc import router as misc_router
from app.routers.tasks import router as task_router
from app.routers.logs import router as logs_router

routers = [
    misc_router,
    task_router,
    logs_router
]
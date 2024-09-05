from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import UUID4
from jinja2 import Template

from backend.app.repositories.logs import (
    TaskLogsRepositoryDependency,
)

from backend.app.repositories.tasks import (
    TaskRepositoryDependency,
)
from backend.app.schemas import TaskLogCreate
from backend.app.rate_limiter import limiter
from backend.app.config import settings

router = APIRouter(prefix='/tasks', tags=["Tasks"])

@router.get("/")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def list_tasks(
        request: Request, task_repository: TaskRepositoryDependency,
        limit: int = 100, offset: int = 0
    ):
    tasks = task_repository.get_all(limit=limit, offset=offset)
    return {"tasks": tasks}

@router.post("/")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def create_task(
        request: Request,
        task_repository: TaskRepositoryDependency,
        task_data: TaskLogCreate
    ):
    task = task_repository.create(task_data.model_dump())
    return {"task_id": task.task_id, "message": "Task created successfully"}

@router.get("/logs")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def read_logs(
        request: Request,
        task_log_repository: TaskLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    logs=task_log_repository.get_all(offset=offset, limit=limit)
    
    return { "logs": logs }


@router.get("/admin", response_class=HTMLResponse)
async def admin_interface(
    request: Request, task_repository: TaskRepositoryDependency
):
    try:
        schedulers = ["background", "asyncio"]
        tasks_by_scheduler = {}
        for scheduler_type in schedulers:
            tasks_by_scheduler[scheduler_type] = await task_repository.get_tasks_by_scheduler(scheduler_type)
        
        
        
        template = Template(get_admin_template())
        return template.render(schedulers=schedulers, tasks=tasks_by_scheduler)
    except Exception as e:
        # Handle specific exceptions and provide more informative error messages
        raise HTTPException(status_code=500, detail=str(e))


def get_admin_template() -> str:
    with open("static/admin_template.html", "r") as f:
        return f.read()


@router.get("/{task_id}")
@limiter.limit("10/minute")
async def read_task(
        request: Request, task_repository: TaskRepositoryDependency,
        task_id: UUID4
    ):
    task = task_repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

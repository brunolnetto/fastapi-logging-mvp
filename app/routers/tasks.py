from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import UUID4

from app.repositories.tasks import TaskRepository
from app.database.base import get_session
from app.repositories.tasks import get_task_repository
from app.schemas import TaskLogCreate
from app.rate_limiter import limiter
from app.repositories.logs import (
    TaskLogsRepositoryDependency, 
    RequestLogsRepositoryDependency,
)

router = APIRouter(prefix='/tasks', tags=["Tasks"])

@router.get("/")
@limiter.limit("10/minute")
async def list_tasks(
        request: Request,
        task_repository: TaskLogsRepositoryDependency,
        limit: int = 100, offset: int = 0
    ):
    tasks = task_repository.get_all(limit=limit, offset=offset)
    return {"tasks": tasks}

@router.post("/")
@limiter.limit("10/minute")
async def create_task(
        request: Request,
        task_repository: TaskLogsRepositoryDependency,
        task_data: TaskLogCreate
    ):
    task = task_repository.create_task(task_data.dict())
    return {"task_id": task.task_id, "message": "Task created successfully"}

@router.get("/logs")
@limiter.limit("10/minute")
async def read_logs(
        request: Request,
        request_log_repository: RequestLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    logs=request_log_repository.get_all(offset=offset, limit=limit)
    
    return { "logs": logs }


@router.get("/{task_id}")
@limiter.limit("10/minute")
async def read_task(
        request: Request,
        task_repository: TaskLogsRepositoryDependency,
        task_id: UUID4
    ):
    task = task_repository.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

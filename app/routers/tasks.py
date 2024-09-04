from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import UUID4

from app.repositories.tasks import TaskRepository
from app.database.base import get_session
from app.database.models.tasks import Task
from app.repositories.logs import (
    TaskLogsRepositoryDependency, 
    RequestLogsRepositoryDependency,
)
from app.repositories.tasks import get_task_repository
from app.schemas import TaskLogCreate
from app.rate_limiter import limiter
from app.scheduler.bundler import task_orchestrator
from app.schemas import TaskResponse

router = APIRouter(prefix='/tasks', tags=["Tasks"])

@router.get("/")
@limiter.limit("10/minute")
async def list_tasks(
        request: Request, task_repository: TaskLogsRepositoryDependency,
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
    task = task_repository.create(task_data.model_dump())
    return {"task_id": task.task_id, "message": "Task created successfully"}

@router.get("/logs")
@limiter.limit("10/minute")
async def read_logs(
        request: Request,
        task_log_repository: TaskLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    logs=task_log_repository.get_all(offset=offset, limit=limit)
    
    return { "logs": logs }


@router.get("/{task_id}")
@limiter.limit("10/minute")
async def read_task(
        request: Request, task_repository: TaskLogsRepositoryDependency,
        task_id: UUID4
    ):
    task = task_repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.get("/admin", response_class=HTMLResponse)
async def admin_interface(request: Request):
    try:
        schedulers = ["background", "asyncio"]
        tasks = {}
        for scheduler_type in schedulers:
            jobs = task_orchestrator.list_tasks(scheduler_type)
            tasks[scheduler_type] = [
                f"<li>{job.name} - {job.type} - {job.schedule}</li>"
                for job in jobs
            ]
        return f"""
        <html>
            <body>
                <h1>Task Management Interface</h1>
                {"".join([f"<h2>{scheduler}</h2><ul>{''.join(task_list)}</ul>" for scheduler, task_list in tasks.items()])}
                <form action="/tasks/add" method="post">
                    <label for="task_name">Task Name:</label>
                    <input type="text" id="task_name" name="task_name">
                    <label for="task_type">Task Type:</label>
                    <input type="text" id="task_type" name="task_type">
                    <label for="schedule_type">Schedule Type:</label>
                    <input type="text" id="schedule_type" name="schedule_type">
                    <label for="schedule_params">Schedule Params (JSON):</label>
                    <input type="text" id="schedule_params" name="schedule_params">
                    <label for="task_callable">Task Callable:</label>
                    <input type="text" id="task_callable" name="task_callable">
                    <label for="task_args">Task Args (JSON):</label>
                    <input type="text" id="task_args" name="task_args">
                    <label for="task_details">Task Details (JSON):</label>
                    <input type="text" id="task_details" name="task_details">
                    <input type="submit" value="Add Task">
                </form>
                <form action="/tasks/remove" method="post">
                    <label for="remove_task_name">Task Name to Remove:</label>
                    <input type="text" id="remove_task_name" name="task_name">
                    <label for="remove_schedule_type">Scheduler Type:</label>
                    <input type="text" id="remove_schedule_type" name="schedule_type">
                    <input type="submit" value="Remove Task">
                </form>
            </body>
        </html>
        """
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
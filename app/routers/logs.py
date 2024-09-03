from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any

from app.repositories.logs import TaskLogRepository, RequestLogRepository
from app.database.base import get_session
from app.schemas import TaskLogCreate
from app.repositories.logs import RequestLogsRepositoryDependency
from app.rate_limiter import limiter

router = APIRouter(prefix='/logs', tags=["Logs"])

@router.post("/test_log_request")
@limiter.limit("10/minute")
def create_log(
        request: Request,
        data: Dict[str, Any],
        request_log_repository: RequestLogsRepositoryDependency
    ):
    return data

@router.get("/requests")
@limiter.limit("10/minute")
async def read_logs(
        request: Request,
        request_log_repository: RequestLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    return request_log_repository.get_all(offset=offset, limit=limit)

@router.get("/tasks")
@limiter.limit("10/minute")
async def read_logs(
        request: Request,
        request_log_repository: RequestLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    return request_log_repository.get_all(offset=offset, limit=limit)


from fastapi import APIRouter, Request
from typing import Dict, Any

from backend.app.repositories.logs import RequestLogsRepositoryDependency
from backend.app.rate_limiter import limiter
from backend.app.config import settings

router = APIRouter(prefix='/logs', tags=["Logs"])

@router.post("/test_log_request")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
def create_log(
        request: Request,
        data: Dict[str, Any],
        request_log_repository: RequestLogsRepositoryDependency
    ):
    return data

@router.get("/requests")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def read_logs(
        request: Request,
        request_log_repository: RequestLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    return request_log_repository.get_all(offset=offset, limit=limit)

@router.get("/tasks")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def read_logs(
        request: Request,
        request_log_repository: RequestLogsRepositoryDependency, 
        offset: int = 0, limit: int = 100
    ):
    return request_log_repository.get_all(offset=offset, limit=limit)


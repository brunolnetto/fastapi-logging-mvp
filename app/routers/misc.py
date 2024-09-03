from fastapi import APIRouter, Request, Depends
from typing import Any, Dict
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler

from app.repositories.logs import RequestLogRepository, get_request_logs_repository
from app.rate_limiter import limiter

router=APIRouter(prefix="/misc", tags=["Miscelaneous"])

@router.get("/hello")
@limiter.limit("10/minute")
def hello(request: Request):
    return {"hello": "world"}

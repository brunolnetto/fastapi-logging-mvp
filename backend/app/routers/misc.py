from fastapi import APIRouter, Request

from backend.app.rate_limiter import limiter
from backend.app.config import settings

router = APIRouter(prefix="/misc", tags=["Miscelaneous"])


@router.get("/hello")
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
def hello(request: Request):
    return {"hello": "world"}

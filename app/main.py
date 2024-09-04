from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Any

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database.base import database, init_database, get_session
from app.repositories.logs import RequestLogRepository
from app.repositories.logs import get_request_logs_repository

from app.schemas import RequestLogCreate
from app.middlewares.logs import AsyncRequestLoggingMiddleware
from app.utils.migrations import generate_migrations, run_migrations

from app.scheduler.bundler import task_orchestrator

from app.rate_limiter import limiter

from app.config import settings

# Dependency to get DB session
async def get_db():
    async for session in get_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    database=init_database()
    
    task_orchestrator.start()
    print("Scheduler started!")

    yield
    database.disconnect()
    
    task_orchestrator.shutdown()
    print("Scheduler shutdown!")

# Dependency to get the async session
app = FastAPI(
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

from app.routers.bundler import routers
for router in routers:
    app.include_router(router, prefix=settings.API_V1_STR)

# Register the rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handling example for rate limiting
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    detail_dict={"detail": "Too many requests, please slow down!"}
    return JSONResponse(status_code=429, content=detail_dict)

app.add_middleware(AsyncRequestLoggingMiddleware)

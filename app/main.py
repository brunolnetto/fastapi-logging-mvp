from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Any

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import database, init_database, get_session
from .repositories.logs import RequestLogRepository
from .schemas import RequestLogCreate
from .middleware import AsyncRequestLoggingMiddleware
from .repositories.logs import get_request_logs_repository
from .utils.migrations import generate_migrations, run_migrations
from .scheduler.bundler import schedulers

# Dependency to get DB session
async def get_db():
    async for session in get_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    
    for scheduler in schedulers:
        scheduler.start()
    print("Scheduler started!")

    yield
    database.disconnect()

# Dependency to get the async session
app = FastAPI(lifespan=lifespan)

# Initialize the Limiter with a global rate limit (e.g., 5 requests per minute)
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

# Register the rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handling example for rate limiting
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, please slow down!"},
    )


app.add_middleware(AsyncRequestLoggingMiddleware)

@app.get("/hello")
@limiter.limit("10/minute")
def hello(request: Request):
    return {"hello": "world"}

@app.post("/request_logs")
@limiter.limit("10/minute")
def create_log(
        request: Request,
        data: Dict[str, Any],
        request_log_repository: RequestLogRepository = Depends(get_request_logs_repository)
    ):
    return data

@app.get("/request_logs")
@limiter.limit("10/minute")
async def read_logs(
        request: Request,
        request_log_repository: RequestLogRepository = Depends(get_request_logs_repository), 
        skip: int = 0, limit: int = 100
    ):
    return request_log_repository.get_request_logs(skip=skip, limit=limit)
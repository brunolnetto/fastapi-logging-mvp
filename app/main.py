from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Any

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
app.add_middleware(AsyncRequestLoggingMiddleware)

@app.get("/hello")
def read_logs():
    return {"hello": "world"}

@app.post("/request_logs")
def create_log(
        data: Dict[str, Any],
        request_log_repository: RequestLogRepository = Depends(get_request_logs_repository)
    ):
    return data

@app.get("/request_logs")
async def read_logs(
        request_log_repository: RequestLogRepository = Depends(get_request_logs_repository), 
        skip: int = 0, limit: int = 100
    ):
    return request_log_repository.get_request_logs(skip=skip, limit=limit)
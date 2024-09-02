from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from .database import database, init_database, get_session
from .repositories.request_logs import RequestLogRepository
from .schemas import RequestLogCreate
from .middleware import AsyncRequestLoggingMiddleware

# Dependency to get DB session
async def get_db():
    async for session in get_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    database = init_database()
    
    yield

# Dependency to get the async session
app = FastAPI(lifespan=lifespan)

app.add_middleware(AsyncRequestLoggingMiddleware)

@app.get("/hello")
def read_logs():
    return {"hello": "world"}

@app.post("/request_logs")
async def create_log(log: RequestLogCreate, session: AsyncSession = Depends(get_session)):
    repository = RequestLogRepository(session)
    return await repository.create_request_log(log)

@app.get("/request_logs")
async def read_logs(skip: int = 0, limit: int = 100,session: AsyncSession = Depends(get_session)):
    repository = RequestLogRepository(session)
    return await repository.get_request_logs(skip=skip, limit=limit)
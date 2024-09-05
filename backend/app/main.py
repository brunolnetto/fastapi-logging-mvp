from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.database.base import init_database
from backend.app.middlewares.logs import AsyncRequestLoggingMiddleware
from backend.app.scheduler.bundler import task_orchestrator
from backend.app.routers.bundler import routers
from backend.app.config import settings

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

for router in routers:
    app.include_router(router, prefix=settings.API_V1_STR)

# Register the rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handling example for rate limiting
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    detail_dict={"detail": "Too many requests, please slow down!"}
    return JSONResponse(status_code=429, content=detail_dict)

app.add_middleware(AsyncRequestLoggingMiddleware)

# Add CORS middleware
origins = [
    "http://frontend:5000",
    "https://frontend:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from slowapi.errors import RateLimitExceeded
from time import time, strftime, localtime
from io import BytesIO
import logging

from app.utils.logs import request_to_log
from app.schemas import RequestLogCreate
from app.repositories.logs import RequestLogRepository
from app.database.base import get_session

class AsyncRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()

        # Call the next middleware or endpoint
        response: Response = await call_next(request)

        process_time = time() - start_time

        # Capture response body from StreamingResponse
        response_body = b''
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Create a new StreamingResponse with the body content
        response = StreamingResponse(
            BytesIO(response_body),
            headers=dict(response.headers),
            status_code=response.status_code,
            media_type=response.media_type
        )
        response_size = len(response_body)

        log_data={
            "relo_method": request.method,
            "relo_url": str(request.url),
            "relo_body": (await request.body()).decode() if await request.body() else '',
            "relo_headers": dict(request.headers),
            "relo_status_code": response.status_code,
            "relo_ip_address": request.client.host,
            "relo_device_info": request.headers.get('user-agent', 'Unknown'),
            "relo_absolute_path": str(request.url),
            "relo_request_duration_seconds": f"{process_time:.6f}",
            "relo_response_size": response_size,
            "relo_inserted_at": strftime('%Y-%m-%d %H:%M:%S', localtime(start_time))
        }
        
        log=RequestLogCreate(**log_data)

        with get_session() as db_session:
            log_repository = RequestLogRepository(db_session)
            log_repository.create(log)

        return response

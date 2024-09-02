from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from time import time, strftime, localtime
import logging
from io import BytesIO

from .utils.logs import request_to_log
from .schemas import RequestLogCreate
from .repositories.logs import RequestLogRepository
from .database import get_session

class AsyncRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()

        # Call the next middleware or endpoint
        response: Response = await call_next(request)

        process_time = time() - start_time
        
        # Ensure the response body is captured correctly
        if isinstance(response, StreamingResponse):
            body: bytes | None = request.scope.get('cached_body')
            
            # Temporarily consume the response body and replace it
            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk
            response_size = len(response_body)
            
            # Create a new StreamingResponse with the consumed body
            response = StreamingResponse(
                BytesIO(response_body),
                headers=dict(response.headers),
                status_code=response.status_code,
                media_type=response.media_type
            )
        else:
            response_size = len(response.body) if response.body else 0
        
        log_data={
            "method": request.method,
            "url": str(request.url),
            "body": body.decode() if body else '',
            "headers": dict(request.headers),
            "status_code": response.status_code,
            "ip_address": request.client.host,
            "device_info": request.headers.get('user-agent', 'Unknown'),
            "absolute_path": str(request.url),
            "request_duration_seconds": f"{process_time:.6f}",
            "response_size": response_size,
            "inserted_at": strftime('%Y-%m-%d %H:%M:%S', localtime(start_time))
        }
        
        log=RequestLogCreate(**log_data)

        with get_session() as db_session:
            log_repository = RequestLogRepository(db_session)
            log_repository.create_request_log(log)

        return response

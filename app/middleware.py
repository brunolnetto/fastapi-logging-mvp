from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

import time
import logging
from io import BytesIO

from .schemas import RequestLogCreate
from .repositories.request_logs import RequestLogRepository
from .database import get_session

class AsyncRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        absolute_path = str(request.url)

        # Call the next middleware or endpoint
        response: Response = await call_next(request)

        # Capture response size and body if it's not a StreamingResponse
        if isinstance(response, StreamingResponse):
            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk
            response_size = len(response_body)
            response_body_iterator = BytesIO(response_body)
            response = StreamingResponse(
                response_body_iterator,
                headers=dict(response.headers),
                status_code=response.status_code,
                media_type=response.media_type
            )
        else:
            response_size = len(response.body) if response.body else 0

        process_time = time.time() - start_time

        log_data = {
            "method": request.method,
            "url": request.url.path,
            "body": await request.body(),
            "headers": dict(request.headers),
            "status_code": response.status_code,
            "ip_address": client_ip,
            "device_info": user_agent,
            "absolute_path": absolute_path,
            "request_duration_seconds": f"{process_time:.6f}",
            "response_size": response_size,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        }

        log=RequestLogCreate(**log_data)
        
        with get_session() as db_session:
            log_repository = RequestLogRepository(db_session)
            log_repository.create_request_log(log)

        return response

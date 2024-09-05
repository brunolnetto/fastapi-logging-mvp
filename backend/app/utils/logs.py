from fastapi import Request
from starlette.responses import Response, StreamingResponse
from typing import Dict, Any
from io import BytesIO

from time import time

async def request_to_log(request_start_time: float, request: Request, response: Response) -> Dict[str, Any]:
    process_time = time() - request_start_time
    
    # Capture request body
    body = await request.body()
    
    # Ensure the response body is captured correctly
    if isinstance(response, StreamingResponse):
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
    
    return {
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
        "inserted_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request_start_time))
    }
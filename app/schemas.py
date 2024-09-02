# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RequestLogBase(BaseModel):
    method: str
    url: str
    body: Optional[str] = None
    headers: dict
    status_code: int
    ip_address: Optional[str] = Field(None, description="Client's IP address")
    device_info: Optional[str] = Field(None, description="Device information")
    absolute_path: Optional[str] = Field(None, description="Absolute path of the request")
    request_duration_seconds: Optional[float] = Field(None, description="Duration of the request in seconds")
    response_size: Optional[int] = Field(None, description="Size of the response in bytes")

class RequestLogCreate(RequestLogBase):
    pass

class RequestLog(RequestLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

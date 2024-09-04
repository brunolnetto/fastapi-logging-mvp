# app/schemas.py
from pydantic import BaseModel, Field, UUID4
from typing import Tuple, Dict, Callable, Optional, Any
from datetime import datetime

from uuid import uuid4
class RequestLogBase(BaseModel):
    relo_method: str
    relo_url: str
    relo_body: Optional[str] = None
    relo_headers: dict
    relo_status_code: int
    relo_ip_address: Optional[str] = Field(None, description="Client's IP address")
    relo_device_info: Optional[str] = Field(None, description="Device information")
    relo_absolute_path: Optional[str] = Field(None, description="Absolute path of the request")
    relo_request_duration_seconds: Optional[float] = Field(None, description="Duration of the request in seconds")
    relo_response_size: Optional[int] = Field(None, description="Size of the response in bytes")

class RequestLogCreate(RequestLogBase):
    pass

class TaskCreate(BaseModel):
    task_name: str
    task_type: str
    task_is_active: bool
    task_details: dict

class TaskLogCreate(BaseModel):
    talo_name: str
    talo_status: str
    talo_type: str
    talo_details: Dict[str, Optional[str]] = Field(default_factory=dict)
    talo_start_time: datetime
    talo_end_time: Optional[datetime] = None
    talo_success: bool = False
    talo_error_message: Optional[str] = None
    talo_error_trace: Optional[str] = None

class TaskCreate(BaseModel):
    task_name: str = Field(..., title="Task Name", description="The name of the task")
    task_type: str = Field(..., title="Task Type", description="The type of the task")
    task_is_active: Optional[bool] = Field(True, title="Task Active", description="Indicates if the task is active")
    task_details: Optional[Dict[str, Any]] = Field({}, title="Task Details", description="Additional details about the task")

class TaskRead(BaseModel):
    task_id: UUID4 = Field(default_factory=uuid4, title="Task ID", description="The unique identifier of the task")
    task_created_at: datetime = Field(default_factory=datetime.utcnow, title="Task Created At", description="The timestamp when the task was created")
    task_name: str = Field(..., title="Task Name", description="The name of the task")
    task_type: str = Field(..., title="Task Type", description="The type of the task")
    task_is_active: Optional[bool] = Field(True, title="Task Active", description="Indicates if the task is active")
    task_details: Optional[Dict[str, Any]] = Field({}, title="Task Details", description="Additional details about the task")

    class Config:
        from_atributes = True

class TaskResponse(BaseModel):
    task_id: UUID4
    task_created_at: str
    task_name: str
    task_type: str
    task_is_active: bool
    task_details: dict

    class Config:
        from_atributes = True

class TaskConfig(BaseModel):
    schedule_type: str
    schedule_params: Dict[str, Any] = Field(default_factory=dict)
    task_name: str
    task_type: str
    task_callable: Callable
    task_args: Tuple[Any] = ()
    task_details: Dict[str, Any] = Field(default_factory=dict)
    
    def __eq__(self, other):
        if not isinstance(other, TaskConfig):
            return NotImplemented

        return (
            self.schedule_type == other.schedule_type and
            self.schedule_params == other.schedule_params and
            self.task_name == other.task_name and
            self.task_type == other.task_type and
            self.task_callable == other.task_callable and
            self.task_args == other.task_args and
            self.task_details == other.task_details
        )

    def __hash__(self):
        # Implementing __hash__ allows TaskConfig to be used in sets or as dict keys
        return hash((
            self.schedule_type, 
            tuple(sorted(self.schedule_params.items())), 
            self.task_name, 
            self.task_type, 
            self.task_callable, 
            self.task_args, 
            tuple(sorted(self.task_details.items()))
        ))
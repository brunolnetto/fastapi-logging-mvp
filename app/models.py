# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from .database import Base, database

import uuid

class RequestLog(Base):
    __tablename__ = 'request_log'

    relo_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    relo_method = Column(String, index=True)
    relo_url = Column(String, index=True)
    relo_headers = Column(JSONB)
    relo_body = Column(String)
    relo_status_code = Column(Integer)
    relo_ip_address = Column(String)
    relo_device_info = Column(String)
    relo_absolute_path = Column(String)
    relo_request_duration = Column(Integer)
    relo_response_size = Column(Integer)
    relo_inserted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        params=f"id={self.relo_id}, method={self.relo_method}, url={self.relo_url}, status_code={self.relo_status_code}"
        return f"<RequestLog({params})>"


class TaskLog(Base):
    __tablename__ = 'task_log'

    talo_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    talo_name = Column(String, index=True)
    talo_status = Column(String, index=True)
    talo_type = Column(String)
    talo_details = Column(JSONB)
    talo_start_time = Column(DateTime(timezone=True))
    talo_end_time = Column(DateTime(timezone=True))
    talo_success = Column(Boolean, default=False)
    talo_error_message = Column(Text, nullable=True)
    talo_error_trace = Column(Text, nullable=True)
    talo_inserted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        params = f"id={self.talo_id}, name={self.talo_name}, status={self.talo_status}, success={self.talo_success}"
        return f"<TaskLog({params})>"
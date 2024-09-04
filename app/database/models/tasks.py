from __future__ import annotations
from typing import List
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    task_created_at = Column(DateTime(timezone=True), server_default=func.now())
    task_schedule_type = Column(String, index=True)
    task_schedule_params = Column(JSONB)
    task_name = Column(String, index=True)
    task_callable = Column(String, index=True)
    task_type = Column(String)
    task_is_active = Column(Boolean, default=True)

    # Define a relationship with TaskLog model (one-to-many)
    logs = relationship("TaskLog", backref="task")

    def __repr__(self):
        params = f"id={self.task_id}, name={self.task_name}, type={self.task_type}, active={self.task_is_active}"
        return f"<Task({params})>"

# app/repositories/request_log_repository.py
from datetime import datetime, timedelta
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Annotated,  Optional
from contextlib import contextmanager
from fastapi import Depends


from uuid import UUID

from app.database.models.logs import TaskLog, RequestLog
from app.schemas import TaskLogCreate

from app.schemas import RequestLogCreate
from app.database.base import get_session
from app.repositories.base import BaseRepository

class RequestLogRepository(BaseRepository):
    def create(self, log: RequestLogCreate) -> RequestLog:
        db_log = RequestLog(**log.model_dump())
        self.session.add(db_log)
        self.session.commit()
        self.session.refresh(db_log)
        return db_log

    def update(self, id: UUID, data: Dict[str, Any]) -> Optional[RequestLog]:
        # Not typically used for RequestLog, but implemented for completeness
        return None

    def get_by_id(self, id: UUID) -> Optional[RequestLog]:
        return self.session.get(RequestLog, id)

    def delete_by_id(self, id: UUID) -> bool:
        log = self.get_by_id(id)
        if not log:
            return False
        self.session.delete(log)
        self.session.commit()
        return True

    def get_all(self, limit: int = 100, offset: int = 0) -> List[RequestLog]:
        result = self.session.execute(select(RequestLog).offset(offset).limit(limit))
        return result.scalars().all()

    def delete_old_logs(self, time_delta: timedelta):
        cutoff_date = datetime.now() - time_delta
        delete_query = delete(RequestLog).where(RequestLog.relo_inserted_at < cutoff_date)
        self.session.execute(delete_query)
        self.session.commit()


async def get_request_logs_repository() -> RequestLogRepository:
    """
    Provides a RequestLogRepository instance.
    
    Args:
        session (AsyncSession): The async session dependency.
    
    Returns:
        RequestLogRepository: The repository instance.
    """
    with get_session() as session:
        return RequestLogRepository(session)


class TaskLogRepository(BaseRepository):
    def create(self, task_log_data: TaskLogCreate) -> TaskLog:
        task_log = TaskLog(**task_log_data)
        self.session.add(task_log)
        self.session.commit()
        self.session.refresh(task_log)
        return task_log

    def update(self, id: UUID, data: TaskLogCreate) -> Optional[TaskLog]:
        task_log = self.get_by_id(id)
        if not task_log:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(task_log, key, value)

        self.session.commit()
        self.session.refresh(task_log)
        return task_log

    def get_by_id(self, id: UUID) -> Optional[TaskLog]:
        return self.session.get(TaskLog, id)

    def delete_by_id(self, id: UUID) -> bool:
        task_log = self.get_by_id(id)
        if not task_log:
            return False

        self.session.delete(task_log)
        self.session.commit()
        return True

    def get_all(self, limit: int = 100, offset: int = 0) -> List[TaskLog]:
        return self.session.execute(
            select(TaskLog).offset(offset).limit(limit)
        ).scalars().all()

    def delete_old_logs(self, time_delta: timedelta):
        cutoff_date = datetime.now() - time_delta
        self.session.query(TaskLog).filter(TaskLog.talo_start_time < cutoff_date).delete()
        self.session.commit()


def get_request_logs_repository():
    with get_session() as session:
        return RequestLogRepository(session)
    
def get_task_logs_repository():
    with get_session() as session:
        return TaskLogRepository(session)

RequestLogsRepositoryDependency=Annotated[
    RequestLogRepository, Depends(get_request_logs_repository)
]

TaskLogsRepositoryDependency=Annotated[
    TaskLogRepository, Depends(get_task_logs_repository)
]
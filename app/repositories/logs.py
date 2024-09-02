# app/repositories/request_log_repository.py
from datetime import datetime, timedelta
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from contextlib import contextmanager
from fastapi import Depends

from ..models import RequestLog
from ..schemas import RequestLogCreate
from ..database import get_session


class RequestLogRepository:

    def __init__(self, session):
        self.session = session

    def create_request_log(self, log: RequestLogCreate) -> RequestLog:
        db_log = RequestLog(
            relo_method=log.method,
            relo_url=log.url,
            relo_body=log.body,
            relo_headers=log.headers,
            relo_absolute_path=log.absolute_path,
            relo_status_code=log.status_code,
            relo_ip_address=log.ip_address,
            relo_device_info=log.device_info,
            relo_request_duration=log.request_duration_seconds,
            relo_response_size=log.response_size
        )
        self.session.add(db_log)
        self.session.commit()
        self.session.refresh(db_log)
        return db_log

    def get_request_logs(self, skip: int = 0, limit: int = 100) -> List[RequestLog]:
        """
        Get a list of request logs.

        Args:
            skip (int, optional): Value to skip results. Defaults to 0.
            limit (int, optional): Value to limit the results. Defaults to 100.

        Returns:
            List[RequestLog]: _description_
        """
        
        result = self.session.execute(select(RequestLog).offset(skip).limit(limit))
        return result.scalars().all()

    async def delete_old_logs(self, time_delta: timedelta):
        """Delete logs older than a certain number of days."""
        cutoff_date = datetime.now() - time_delta
        
        # Build the delete query
        delete_query = delete(RequestLog).where(RequestLog.relo_inserted_at < cutoff_date)
        self.session.execute(delete_query)


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

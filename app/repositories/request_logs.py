# app/repositories/request_log_repository.py

from sqlalchemy.future import select
from ..models import RequestLog
from ..schemas import RequestLogCreate
from typing import List

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
        result = self.session.execute(select(RequestLog).offset(skip).limit(limit))
        return result.scalars().all()

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID

from typing import Dict, List, Any, Optional

from app.database.base import get_session
from app.database.models.tasks import Task
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, task_data: Dict[str, Any]) -> Task:
        task = Task(**task_data.model_dump())
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
    
    def update(self, task_id: UUID, task_data: Dict[str, Any]) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        
        for key, value in task_data.items():
            setattr(task, key, value)
        
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, task_id: UUID) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Task]:
        return self.session.execute(
            select(Task).offset(offset).limit(limit)
        ).scalars().all()
        
    def delete_by_id(self, id: UUID) -> bool:
        log = self.get_by_id(id)
        if not log:
            return False
        self.session.delete(log)
        self.session.commit()
        return True
        
def get_task_repository():
    with get_session() as session:
        return TaskRepository(session)
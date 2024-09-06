from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseRepository(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[Any]:
        pass

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[Any]:
        pass

    @abstractmethod
    def delete_by_id(self, id: Any) -> bool:
        pass

    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        pass

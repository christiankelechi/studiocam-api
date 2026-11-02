"""Generic Abstract Base Repository implementing the Repository Pattern."""

from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, TypeVar
import threading

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository providing standard CRUD contract."""

    @abstractmethod
    def get(self, entity_id: str) -> Optional[T]:
        """Retrieve an entity by primary ID."""
        pass

    @abstractmethod
    def list(self) -> List[T]:
        """List all entities."""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Persist a new entity."""
        pass

    @abstractmethod
    def update(self, entity_id: str, updates: Dict) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Remove an entity by ID."""
        pass


class ThreadSafeInMemoryRepository(BaseRepository[T]):
    """Thread-safe generic in-memory repository implementation."""

    def __init__(self):
        self._storage: Dict[str, T] = {}
        self._lock = threading.RLock()

    def get(self, entity_id: str) -> Optional[T]:
        with self._lock:
            return self._storage.get(entity_id)

    def list(self) -> List[T]:
        with self._lock:
            return list(self._storage.values())

    def create(self, entity: T) -> T:
        with self._lock:
            # Assumes entity has an 'id' attribute
            entity_id = getattr(entity, "id")
            self._storage[entity_id] = entity
            return entity

    def update(self, entity_id: str, updates: Dict) -> Optional[T]:
        with self._lock:
            item = self._storage.get(entity_id)
            if not item:
                return None
            for key, val in updates.items():
                if hasattr(item, key) and val is not None:
                    setattr(item, key, val)
            return item

    def delete(self, entity_id: str) -> bool:
        with self._lock:
            if entity_id in self._storage:
                del self._storage[entity_id]
                return True
            return False


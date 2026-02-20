"""Base interfaces for persistence layer.

These protocols define the contract that any storage implementation must fulfill.
Implementations can be JSON files, SQLite, PostgreSQL, or any other storage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
ID = TypeVar("ID")


@runtime_checkable
class Repository(Protocol[T, ID]):
    """Generic repository interface for CRUD operations.

    Repositories abstract away the storage mechanism.
    Business logic should depend on this interface, not implementations.
    """

    def get(self, id: ID) -> Optional[T]:
        """Get entity by ID."""
        ...

    def get_all(self) -> List[T]:
        """Get all entities."""
        ...

    def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        ...

    def delete(self, id: ID) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        ...

    def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        ...


class UnitOfWork(ABC):
    """Unit of Work pattern for transaction management.

    Ensures all changes within a business operation are committed
    or rolled back as a single unit.
    """

    @abstractmethod
    def __enter__(self) -> UnitOfWork:
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        """Commit all changes."""
        ...

    @abstractmethod
    def rollback(self) -> None:
        """Rollback all changes."""
        ...


class BaseRepository(Generic[T, ID], ABC):
    """Abstract base class for repositories with common functionality."""

    @abstractmethod
    def get(self, id: ID) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        pass

    @abstractmethod
    def delete(self, id: ID) -> bool:
        """Delete entity by ID."""
        pass

    def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        return self.get(id) is not None

    def count(self) -> int:
        """Count all entities."""
        return len(self.get_all())

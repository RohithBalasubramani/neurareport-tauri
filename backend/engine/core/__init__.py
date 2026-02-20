"""Core module - cross-cutting concerns for the entire backend."""

from .errors import (
    NeuraError,
    ValidationError,
    NotFoundError,
    ConflictError,
    ExternalServiceError,
    ConfigurationError,
)
from .result import Result, Ok, Err
from .events import Event, EventBus, EventHandler
from .types import EntityId, Timestamp, JSON

__all__ = [
    "NeuraError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "ExternalServiceError",
    "ConfigurationError",
    "Result",
    "Ok",
    "Err",
    "Event",
    "EventBus",
    "EventHandler",
    "EntityId",
    "Timestamp",
    "JSON",
]

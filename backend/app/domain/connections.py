"""Domain entities for connections.

Pure business logic: no SQL drivers / network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConnectionStatus(str, Enum):
    UNKNOWN = "unknown"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Connection:
    id: str
    name: str
    db_type: str
    status: ConnectionStatus = ConnectionStatus.UNKNOWN
    created_at: datetime | None = None
    updated_at: datetime | None = None
    latency_ms: float | None = None


"""Connection repository port."""

from __future__ import annotations

from typing import Protocol

from backend.app.domain.connections import Connection


class ConnectionRepository(Protocol):
    async def get(self, connection_id: str) -> Connection | None: ...
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[Connection]: ...
    async def upsert(self, connection: Connection) -> Connection: ...
    async def delete(self, connection_id: str) -> bool: ...


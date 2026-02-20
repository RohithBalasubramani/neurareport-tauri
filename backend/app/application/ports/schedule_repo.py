"""Schedule repository port."""

from __future__ import annotations

from typing import Protocol

from backend.app.domain.schedules import Schedule


class ScheduleRepository(Protocol):
    async def get(self, schedule_id: str) -> Schedule | None: ...
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[Schedule]: ...
    async def upsert(self, schedule: Schedule) -> Schedule: ...
    async def delete(self, schedule_id: str) -> bool: ...


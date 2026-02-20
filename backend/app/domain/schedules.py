"""Domain entities for report schedules.

Pure business logic: no APScheduler/FastAPI imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Schedule:
    id: str
    name: str
    template_id: str
    connection_id: str | None
    interval_minutes: int
    active: bool = True
    start_date: datetime | None = None
    end_date: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


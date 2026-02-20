"""Domain entities for durable jobs and step-level progress.

Pure business logic: no FastAPI/SQLAlchemy/Redis imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class JobStepStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class JobStep:
    id: str
    job_id: str
    name: str
    label: str
    status: JobStepStatus = JobStepStatus.QUEUED
    progress: float = 0.0
    error: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    type: str
    status: JobStatus = JobStatus.QUEUED
    template_id: str | None = None
    connection_id: str | None = None
    schedule_id: str | None = None
    idempotency_key: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancellation_requested_at: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None

    def is_terminal(self) -> bool:
        return self.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELED}


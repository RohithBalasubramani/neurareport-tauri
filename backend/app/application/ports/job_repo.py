"""Job repository port (application-facing interface)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from backend.app.domain.jobs import Job, JobStatus, JobStep, JobStepStatus


class JobRepository(Protocol):
    async def create(self, job: Job) -> Job: ...
    async def get(self, job_id: str) -> Job | None: ...
    async def list(self, *, limit: int = 50, offset: int = 0) -> list[Job]: ...

    async def request_cancel(self, job_id: str, *, when: datetime) -> bool: ...
    async def set_status(self, job_id: str, *, status: JobStatus, finished_at: datetime | None = None) -> bool: ...
    async def set_result(self, job_id: str, *, result: dict[str, Any] | None, error: str | None) -> bool: ...

    async def add_step(self, step: JobStep) -> JobStep: ...
    async def update_step(
        self,
        job_id: str,
        name: str,
        *,
        status: JobStepStatus | None = None,
        progress: float | None = None,
        label: str | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> JobStep | None: ...


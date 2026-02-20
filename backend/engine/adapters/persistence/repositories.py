"""Repository interfaces for each domain entity."""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import List, Optional, Protocol

from backend.engine.domain.templates import Template
from backend.engine.domain.connections import Connection
from backend.engine.domain.jobs import Job, JobStatus, Schedule
from backend.engine.domain.reports import Report


class TemplateRepository(Protocol):
    """Repository for Template entities."""

    def get(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        ...

    def get_all(self) -> List[Template]:
        """Get all templates."""
        ...

    def save(self, template: Template) -> Template:
        """Save template."""
        ...

    def delete(self, template_id: str) -> bool:
        """Delete template."""
        ...

    def exists(self, template_id: str) -> bool:
        """Check if template exists."""
        ...

    def find_by_kind(self, kind: str) -> List[Template]:
        """Find templates by kind (pdf/excel)."""
        ...

    def find_by_name(self, name: str) -> Optional[Template]:
        """Find template by name."""
        ...


class ConnectionRepository(Protocol):
    """Repository for Connection entities."""

    def get(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID."""
        ...

    def get_all(self) -> List[Connection]:
        """Get all connections."""
        ...

    def save(self, connection: Connection) -> Connection:
        """Save connection."""
        ...

    def delete(self, connection_id: str) -> bool:
        """Delete connection."""
        ...

    def exists(self, connection_id: str) -> bool:
        """Check if connection exists."""
        ...

    def find_by_name(self, name: str) -> Optional[Connection]:
        """Find connection by name."""
        ...

    def get_default(self) -> Optional[Connection]:
        """Get the default connection."""
        ...


class JobRepository(Protocol):
    """Repository for Job entities."""

    def get(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        ...

    def get_all(self) -> List[Job]:
        """Get all jobs."""
        ...

    def save(self, job: Job) -> Job:
        """Save job."""
        ...

    def delete(self, job_id: str) -> bool:
        """Delete job."""
        ...

    def find_by_status(self, status: JobStatus) -> List[Job]:
        """Find jobs by status."""
        ...

    def find_by_template(self, template_id: str) -> List[Job]:
        """Find jobs for a template."""
        ...

    def find_active(self) -> List[Job]:
        """Find all active (non-terminal) jobs."""
        ...

    def find_recent(self, limit: int = 50) -> List[Job]:
        """Find recent jobs."""
        ...


class ScheduleRepository(Protocol):
    """Repository for Schedule entities."""

    def get(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID."""
        ...

    def get_all(self) -> List[Schedule]:
        """Get all schedules."""
        ...

    def save(self, schedule: Schedule) -> Schedule:
        """Save schedule."""
        ...

    def delete(self, schedule_id: str) -> bool:
        """Delete schedule."""
        ...

    def find_active(self) -> List[Schedule]:
        """Find all active schedules."""
        ...

    def find_due(self, now: Optional[datetime] = None) -> List[Schedule]:
        """Find schedules that are due for execution."""
        ...

    def find_by_template(self, template_id: str) -> List[Schedule]:
        """Find schedules for a template."""
        ...


class ReportRepository(Protocol):
    """Repository for Report entities (run history)."""

    def get(self, report_id: str) -> Optional[Report]:
        """Get report by ID."""
        ...

    def get_all(self) -> List[Report]:
        """Get all reports."""
        ...

    def save(self, report: Report) -> Report:
        """Save report."""
        ...

    def delete(self, report_id: str) -> bool:
        """Delete report."""
        ...

    def find_by_template(
        self, template_id: str, limit: int = 50
    ) -> List[Report]:
        """Find reports for a template."""
        ...

    def find_by_connection(
        self, connection_id: str, limit: int = 50
    ) -> List[Report]:
        """Find reports for a connection."""
        ...

    def find_by_schedule(
        self, schedule_id: str, limit: int = 50
    ) -> List[Report]:
        """Find reports for a schedule."""
        ...

    def find_recent(self, limit: int = 50) -> List[Report]:
        """Find recent reports."""
        ...

"""Persistence adapters - storage for domain entities."""

from .base import Repository, UnitOfWork
from .repositories import (
    TemplateRepository,
    ConnectionRepository,
    JobRepository,
    ScheduleRepository,
    ReportRepository,
)

__all__ = [
    "Repository",
    "UnitOfWork",
    "TemplateRepository",
    "ConnectionRepository",
    "JobRepository",
    "ScheduleRepository",
    "ReportRepository",
]

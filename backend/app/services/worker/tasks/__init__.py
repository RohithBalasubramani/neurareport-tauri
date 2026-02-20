"""Dramatiq task actors (facade).

The canonical task implementations live in per-domain modules (report/agent/etc).
This package re-exports stable actor names used by tests and integrations.
"""

from .agent_tasks import run_agent as run_agent_task
from .export_tasks import export_document as export_document_task
from .ingestion_tasks import ingest_document as ingest_document_task
from .report_tasks import generate_report as generate_report_task
from .webhook_tasks import send_webhook as send_webhook_task

__all__ = [
    "generate_report_task",
    "run_agent_task",
    "export_document_task",
    "ingest_document_task",
    "send_webhook_task",
]

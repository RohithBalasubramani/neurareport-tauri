from __future__ import annotations

import importlib
import logging
from typing import Any, Optional

from fastapi import HTTPException

from backend.app.services import state_access as state_store_module

logger = logging.getLogger(__name__)
from backend.legacy.services import report_service as report_service_module
from backend.legacy.schemas.report_schema import ScheduleCreatePayload, ScheduleUpdatePayload
from backend.legacy.utils.email_utils import normalize_email_targets
from backend.legacy.utils.schedule_utils import clean_key_values, resolve_schedule_interval, utcnow_iso


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"status": "error", "code": code, "message": message})


def _state_store():
    try:
        api_mod = importlib.import_module("backend.api")
        return getattr(api_mod, "state_store", state_store_module.state_store)
    except Exception:
        return state_store_module.state_store


def _report_service():
    try:
        api_mod = importlib.import_module("backend.api")
        return getattr(api_mod, "report_service", report_service_module)
    except Exception:
        return report_service_module


def list_jobs(status: Optional[list[str]], job_type: Optional[list[str]], limit: int, active_only: bool):
    return _state_store().list_jobs(statuses=status, types=job_type, limit=limit, active_only=active_only)


def list_active_jobs(limit: int):
    return _state_store().list_jobs(limit=limit, active_only=True)


def get_job(job_id: str) -> dict[str, Any] | None:
    return _state_store().get_job(job_id)


def list_schedules():
    return _state_store().list_schedules()


def get_schedule(schedule_id: str) -> dict[str, Any] | None:
    """Get a specific schedule by ID."""
    return _state_store().get_schedule(schedule_id)


def cancel_job(job_id: str, *, force: bool = False) -> dict[str, Any]:
    existing = _state_store().get_job(job_id)
    if not existing:
        raise _http_error(404, "job_not_found", "Job not found.")
    previous_status = str(existing.get("status") or "").strip().lower()
    job = _state_store().cancel_job(job_id)
    if not job:
        raise _http_error(404, "job_not_found", "Job not found.")
    try:
        should_force = force or previous_status in {"running", "in_progress", "started"}
        _report_service().force_cancel_job(job_id, force=should_force)
    except Exception:
        # Best-effort force cancel; do not block the API response.
        logger.warning("force_cancel_failed", exc_info=True)
    return job


def create_schedule(payload: ScheduleCreatePayload) -> dict[str, Any]:
    store = _state_store()
    template = store.get_template_record(payload.template_id) or {}
    if not template:
        raise _http_error(404, "template_not_found", "Template not found.")
    template_status = str(template.get("status") or "").strip().lower()
    # Backward compatibility: older template workflows used "active" for
    # templates that are effectively approved/schedulable.
    if template_status not in {"approved", "active"}:
        raise _http_error(
            400,
            "template_not_ready",
            f"Template must be approved before scheduling runs (current status: {template_status or 'none'}). "
            "Complete the template mapping and approval workflow first.",
        )
    connection = store.get_connection_record(payload.connection_id)
    if not connection:
        raise _http_error(404, "connection_not_found", "Connection not found.")
    if not payload.start_date or not payload.end_date:
        raise _http_error(400, "invalid_schedule_range", "Provide both start_date and end_date.")
    interval_minutes = resolve_schedule_interval(payload.frequency, payload.interval_minutes)
    now_iso = utcnow_iso()
    schedule = store.create_schedule(
        name=(payload.name or template.get("name") or f"Schedule {payload.template_id}")[:120],
        template_id=payload.template_id,
        template_name=template.get("name") or payload.template_id,
        template_kind=template.get("kind") or "pdf",
        connection_id=payload.connection_id,
        connection_name=connection.get("name") or connection.get("connection_name") or payload.connection_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        key_values=clean_key_values(payload.key_values),
        batch_ids=payload.batch_ids,
        docx=payload.docx,
        xlsx=payload.xlsx,
        email_recipients=normalize_email_targets(payload.email_recipients or []),
        email_subject=payload.email_subject,
        email_message=payload.email_message,
        frequency=payload.frequency,
        interval_minutes=interval_minutes,
        next_run_at=now_iso,
        first_run_at=now_iso,
        active=payload.active,
    )
    return schedule


def delete_schedule(schedule_id: str) -> bool:
    return _state_store().delete_schedule(schedule_id)


def update_schedule(schedule_id: str, payload: ScheduleUpdatePayload) -> dict[str, Any]:
    """Update an existing schedule with partial data."""
    store = _state_store()
    existing = store.get_schedule(schedule_id)
    if not existing:
        raise _http_error(404, "schedule_not_found", "Schedule not found.")

    # Build changes dict from non-None fields
    changes: dict[str, Any] = {}
    if payload.name is not None:
        changes["name"] = payload.name[:120]
    if payload.start_date is not None:
        changes["start_date"] = payload.start_date
    if payload.end_date is not None:
        changes["end_date"] = payload.end_date
    if payload.key_values is not None:
        changes["key_values"] = clean_key_values(payload.key_values)
    if payload.batch_ids is not None:
        changes["batch_ids"] = payload.batch_ids
    if payload.docx is not None:
        changes["docx"] = payload.docx
    if payload.xlsx is not None:
        changes["xlsx"] = payload.xlsx
    if payload.email_recipients is not None:
        changes["email_recipients"] = normalize_email_targets(payload.email_recipients)
    if payload.email_subject is not None:
        changes["email_subject"] = payload.email_subject
    if payload.email_message is not None:
        changes["email_message"] = payload.email_message
    if payload.frequency is not None:
        interval_minutes = resolve_schedule_interval(payload.frequency, payload.interval_minutes)
        changes["frequency"] = payload.frequency
        changes["interval_minutes"] = interval_minutes
    elif payload.interval_minutes is not None:
        # Only interval_minutes provided without frequency
        changes["interval_minutes"] = payload.interval_minutes
    if payload.active is not None:
        changes["active"] = payload.active

    if not changes:
        # No updates - return existing
        return existing

    updated = store.update_schedule(schedule_id, **changes)
    if not updated:
        raise _http_error(404, "schedule_not_found", "Schedule not found after update.")
    return updated

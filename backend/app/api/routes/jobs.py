"""Jobs API Routes.

This module contains endpoints for job management:
- List jobs with filtering
- Get job details
- Cancel jobs
- Retry failed jobs
- Dead Letter Queue management
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.services.security import require_api_key
from backend.app.schemas.generate.reports import RunPayload
from backend.app.services.job_status import normalize_job_status, normalize_job
import backend.app.services.state_access as state_access
from backend.legacy.services.scheduler_service import get_job, list_active_jobs, list_jobs, cancel_job

router = APIRouter(dependencies=[Depends(require_api_key)])


# Use shared normalize_job_status and normalize_job from backend.app.services.job_status
_normalize_job_status = normalize_job_status
_normalize_job = normalize_job


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


@router.post("/run-report")
async def run_report_job(payload: RunPayload | list[RunPayload], request: Request):
    """Queue a report generation job (compatibility alias for `/reports/jobs/run-report`)."""
    from backend.legacy.services.report_service import queue_report_job

    payloads = payload if isinstance(payload, list) else [payload]
    kinds = set()
    for item in payloads:
        rec = state_access.get_template_record(item.template_id) or {}
        kinds.add(str(rec.get("kind") or "pdf").strip().lower() or "pdf")
    if len(kinds) > 1:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "mixed_template_kinds",
                "message": "All runs in a batch submission must share the same template kind.",
            },
        )
    kind = next(iter(kinds)) if kinds else "pdf"
    return await queue_report_job(payload, request, kind=kind)


@router.get("")
def list_jobs_route(
    request: Request,
    status: Optional[List[str]] = Query(None),
    job_type: Optional[List[str]] = Query(None, alias="type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(False),
):
    """List jobs with optional filtering by status and type."""
    # Normalize "completed" → "succeeded" for user convenience
    if status:
        status = [("succeeded" if s.lower() == "completed" else s) for s in status]
    # Fetch more than needed to support offset
    fetch_limit = limit + offset
    jobs = list_jobs(status, job_type, fetch_limit, active_only)
    # Apply offset
    jobs = (jobs or [])[offset:]
    normalized_jobs = [_normalize_job(job) for job in jobs]
    return {"jobs": normalized_jobs, "correlation_id": _correlation(request)}


@router.get("/active")
def list_active_jobs_route(request: Request, limit: int = Query(20, ge=1, le=200)):
    """List only active (non-completed) jobs."""
    jobs = list_active_jobs(limit)
    normalized_jobs = [_normalize_job(job) for job in jobs] if jobs else []
    return {"jobs": normalized_jobs, "correlation_id": _correlation(request)}


# =============================================================================
# Dead Letter Queue Endpoints
# IMPORTANT: These must be defined BEFORE /{job_id} routes to avoid path conflicts
# =============================================================================

@router.get("/dead-letter")
def list_dead_letter_jobs_route(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
):
    """List jobs in the Dead Letter Queue."""
    dlq_jobs = state_access.list_dead_letter_jobs(limit=limit)
    stats = state_access.get_dlq_stats()
    return {
        "jobs": dlq_jobs,
        "stats": stats,
        "correlation_id": _correlation(request),
    }


@router.get("/dead-letter/{job_id}")
def get_dead_letter_job_route(job_id: str, request: Request):
    """Get a specific job from the Dead Letter Queue."""
    dlq_job = state_access.get_dead_letter_job(job_id)
    if not dlq_job:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": "dlq_job_not_found",
                "message": "Job not found in Dead Letter Queue",
            }
        )
    return {"job": dlq_job, "correlation_id": _correlation(request)}


@router.post("/dead-letter/{job_id}/requeue")
async def requeue_from_dlq_route(job_id: str, request: Request):
    """
    Requeue a job from the Dead Letter Queue.

    Creates a new job with reset retry count and state.
    """
    dlq_job = state_access.get_dead_letter_job(job_id)
    if not dlq_job:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": "dlq_job_not_found",
                "message": "Job not found in Dead Letter Queue",
            }
        )

    # Create new job from DLQ record
    new_job = state_access.requeue_from_dlq(job_id)
    if not new_job:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "code": "requeue_failed",
                "message": "Failed to requeue job",
            }
        )

    return {
        "status": "ok",
        "message": "Job requeued from Dead Letter Queue",
        "original_job_id": job_id,
        "new_job": new_job,
        "correlation_id": _correlation(request),
    }


@router.delete("/dead-letter/{job_id}")
def delete_from_dlq_route(job_id: str, request: Request):
    """Permanently delete a job from the Dead Letter Queue."""
    deleted = state_access.delete_from_dlq(job_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": "dlq_job_not_found",
                "message": "Job not found in Dead Letter Queue",
            }
        )
    return {
        "status": "ok",
        "message": "Job deleted from Dead Letter Queue",
        "job_id": job_id,
        "correlation_id": _correlation(request),
    }


# =============================================================================
# Job Instance Endpoints (must come AFTER static routes like /dead-letter)
# =============================================================================

@router.get("/{job_id}")
def get_job_route(job_id: str, request: Request):
    """Get details for a specific job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "job_not_found", "message": "Job not found"},
        )
    return {"job": _normalize_job(job), "correlation_id": _correlation(request)}


@router.delete("/{job_id}")
def delete_job_route(job_id: str, request: Request):
    """Delete a job record."""
    deleted = state_access.delete_job(job_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "job_not_found", "message": "Job not found"},
        )
    return {"status": "ok", "job_id": job_id, "correlation_id": _correlation(request)}


@router.post("/{job_id}/cancel")
def cancel_job_route(job_id: str, request: Request, force: bool = Query(False)):
    """Cancel a running job. Cannot cancel already-completed jobs."""
    existing = get_job(job_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "job_not_found", "message": "Job not found"},
        )
    status = _normalize_job_status(existing.get("status"))
    if status in ("succeeded", "completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=409,
            detail={
                "status": "error",
                "code": "job_already_terminal",
                "message": f"Cannot cancel job with status '{status}'. Only active jobs can be cancelled.",
            },
        )
    job = cancel_job(job_id, force=force)
    return {"job": _normalize_job(job), "correlation_id": _correlation(request)}


@router.post("/{job_id}/retry")
async def retry_job_route(job_id: str, request: Request):
    """Retry a failed job by re-queuing it with the same parameters.

    Only jobs with status 'failed' can be retried.
    """
    from backend.legacy.services.report_service import queue_report_job
    from backend.app.schemas.generate.reports import RunPayload

    original_job = get_job(job_id)
    if not original_job:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "job_not_found", "message": "Job not found"}
        )

    normalized_status = _normalize_job_status(original_job.get("status"))
    if normalized_status != "failed":
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "invalid_job_status",
                "message": f"Only failed jobs can be retried. Current status: {normalized_status}"
            }
        )

    job_type = str(original_job.get("type") or original_job.get("job_type") or "").strip() or "run_report"
    if job_type != "run_report":
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "retry_not_supported",
                "message": f"Retry is not supported for job type '{job_type}'. Re-run the original request.",
            },
        )

    # Extract job parameters from meta or direct fields
    meta = original_job.get("meta") or original_job.get("metadata") or {}
    template_id = original_job.get("template_id") or meta.get("template_id")
    connection_id = original_job.get("connection_id") or meta.get("connection_id")
    start_date = meta.get("start_date") or original_job.get("start_date")
    end_date = meta.get("end_date") or original_job.get("end_date")
    key_values = meta.get("key_values") or original_job.get("key_values")
    batch_ids = meta.get("batch_ids") or original_job.get("batch_ids")
    docx = meta.get("docx", False)
    xlsx = meta.get("xlsx", False)
    template_name = original_job.get("template_name") or meta.get("template_name")
    kind = original_job.get("template_kind") or meta.get("kind") or "pdf"

    if not template_id:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "missing_template_id",
                "message": "Cannot retry job: missing template_id"
            }
        )

    # Create payload for new job
    payload = RunPayload(
        template_id=template_id,
        connection_id=connection_id,
        start_date=start_date,
        end_date=end_date,
        key_values=key_values,
        batch_ids=batch_ids,
        docx=docx,
        xlsx=xlsx,
        template_name=template_name,
    )

    # Queue the new job
    result = await queue_report_job(payload, request, kind=kind)

    return {
        "status": "ok",
        "message": "Job retry queued successfully",
        "original_job_id": job_id,
        "new_job": result,
        "correlation_id": _correlation(request),
    }

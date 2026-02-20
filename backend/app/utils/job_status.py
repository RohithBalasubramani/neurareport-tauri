"""
Job Status Normalization Utilities

Provides a single source of truth for job status normalization across
the entire application. All endpoints and services should use these
functions to ensure consistent status values.

Canonical status values:
- queued: Job is waiting to be processed
- running: Job is currently being executed
- succeeded: Job completed successfully
- failed: Job encountered an error
- cancelled: Job was cancelled by user
- cancelling: Job cancellation is in progress
"""
from __future__ import annotations

from typing import Any, Dict, Optional


# Canonical status values - use these constants for comparisons
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
STATUS_CANCELLING = "cancelling"
STATUS_PENDING_RETRY = "pending_retry"  # Job failed but will be retried

# All valid terminal statuses (job is done, no more updates expected)
TERMINAL_STATUSES = frozenset({STATUS_SUCCEEDED, STATUS_FAILED, STATUS_CANCELLED})

# All valid active statuses (job may still update)
ACTIVE_STATUSES = frozenset({STATUS_QUEUED, STATUS_RUNNING, STATUS_CANCELLING, STATUS_PENDING_RETRY})

# Statuses that indicate the job will be retried
RETRY_STATUSES = frozenset({STATUS_PENDING_RETRY})


def normalize_job_status(status: Optional[str]) -> str:
    """Normalize job status to consistent canonical values.

    This is the single source of truth for status normalization.
    All endpoints and services should use this function.

    Args:
        status: Raw status string from any source

    Returns:
        Canonical status string (queued, running, succeeded, failed, cancelled, cancelling)

    Examples:
        >>> normalize_job_status("succeeded")
        'succeeded'
        >>> normalize_job_status("completed")
        'succeeded'
        >>> normalize_job_status("in_progress")
        'running'
        >>> normalize_job_status(None)
        'queued'
    """
    value = (status or "").strip().lower()

    # Map to canonical 'succeeded'
    if value in {"succeeded", "success", "done", "completed"}:
        return STATUS_SUCCEEDED

    # Map to canonical 'queued'
    if value in {"queued", "pending", "waiting"}:
        return STATUS_QUEUED

    # Map to canonical 'running'
    if value in {"running", "in_progress", "started", "processing"}:
        return STATUS_RUNNING

    # Map to canonical 'failed'
    if value in {"failed", "error", "errored"}:
        return STATUS_FAILED

    # Map to canonical 'cancelled'
    if value in {"cancelled", "canceled"}:
        return STATUS_CANCELLED

    # Preserve 'cancelling' as-is
    if value == "cancelling":
        return STATUS_CANCELLING

    # Map to canonical 'pending_retry'
    if value in {"pending_retry", "retry_pending", "retry_scheduled", "awaiting_retry"}:
        return STATUS_PENDING_RETRY

    # Default to queued for unknown/empty statuses
    return STATUS_QUEUED


def normalize_job(job: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Normalize a job record for consistent API responses.

    Args:
        job: Raw job dictionary from storage

    Returns:
        Job dictionary with normalized status field
    """
    if not job:
        return job

    normalized = dict(job)

    # Normalize status field
    if "status" in normalized:
        normalized["status"] = normalize_job_status(normalized["status"])
    elif "state" in normalized:
        # Some older records use 'state' instead of 'status'
        normalized["status"] = normalize_job_status(normalized["state"])

    return normalized


def is_terminal_status(status: Optional[str]) -> bool:
    """Check if a status indicates the job is complete (no more updates).

    Args:
        status: Status string (will be normalized)

    Returns:
        True if the job is in a terminal state
    """
    return normalize_job_status(status) in TERMINAL_STATUSES


def is_active_status(status: Optional[str]) -> bool:
    """Check if a status indicates the job may still be updated.

    Args:
        status: Status string (will be normalized)

    Returns:
        True if the job is still active
    """
    return normalize_job_status(status) in ACTIVE_STATUSES


def is_pending_retry(status: Optional[str]) -> bool:
    """Check if a status indicates the job is waiting for retry.

    Args:
        status: Status string (will be normalized)

    Returns:
        True if the job is pending retry
    """
    return normalize_job_status(status) in RETRY_STATUSES


def can_retry(job: Optional[Dict[str, Any]]) -> bool:
    """Check if a job can be retried.

    A job can be retried if:
    - It exists
    - Its status is 'failed' (not pending_retry, which auto-retries)
    - It has not exceeded max retries

    Args:
        job: Job dictionary from storage

    Returns:
        True if the job can be manually retried
    """
    if not job:
        return False

    status = normalize_job_status(job.get("status"))
    if status != STATUS_FAILED:
        return False

    # Check retry count vs max retries
    retry_count = job.get("retryCount") or job.get("retry_count") or 0
    max_retries = job.get("maxRetries") or job.get("max_retries") or 3

    return retry_count < max_retries

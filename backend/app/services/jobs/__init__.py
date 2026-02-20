"""
Job services for report generation.

Provides:
- Job tracking and step progress
- Error classification for retry decisions
- Webhook notifications for job completion
- Recovery daemon for orphaned jobs
"""
from backend.app.services.jobs.job_tracking import JobRunTracker, DEFAULT_JOB_STEP_PROGRESS
from backend.app.services.jobs.error_classifier import (
    ErrorClassifier,
    ErrorCategory,
    ClassifiedError,
    is_retriable_error,
    classify_error,
)
from backend.app.services.jobs.webhook_service import (
    WebhookService,
    WebhookPayload,
    WebhookResult,
    send_job_webhook,
    send_job_webhook_sync,
    get_webhook_service,
)
from backend.app.services.jobs.recovery_daemon import (
    JobRecoveryDaemon,
    get_recovery_daemon,
    start_recovery_daemon,
    stop_recovery_daemon,
    is_recovery_daemon_running,
    get_recovery_daemon_stats,
)

__all__ = [
    # Job tracking
    "JobRunTracker",
    "DEFAULT_JOB_STEP_PROGRESS",
    # Error classification
    "ErrorClassifier",
    "ErrorCategory",
    "ClassifiedError",
    "is_retriable_error",
    "classify_error",
    # Webhook service
    "WebhookService",
    "WebhookPayload",
    "WebhookResult",
    "send_job_webhook",
    "send_job_webhook_sync",
    "get_webhook_service",
    # Recovery daemon
    "JobRecoveryDaemon",
    "get_recovery_daemon",
    "start_recovery_daemon",
    "stop_recovery_daemon",
    "is_recovery_daemon_running",
    "get_recovery_daemon_stats",
]

"""
Job Recovery Daemon

Background service that:
1. Finds and recovers orphaned jobs (running jobs with stale heartbeats)
2. Re-queues jobs that are ready for retry
3. Delivers pending webhook notifications

This daemon ensures job durability across server restarts and worker failures.
"""
from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Optional

logger = logging.getLogger("neura.jobs.recovery")


class JobRecoveryDaemon:
    """
    Background daemon for job recovery and maintenance.

    Runs periodically to:
    - Detect and recover stale running jobs
    - Re-queue jobs that have waited long enough for retry
    - Deliver pending webhook notifications

    The daemon is designed to be fault-tolerant and will continue
    operating even if individual recovery operations fail.
    """

    DEFAULT_POLL_INTERVAL_SECONDS = 30
    DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 120

    def __init__(
        self,
        poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS,
        heartbeat_timeout_seconds: int = DEFAULT_HEARTBEAT_TIMEOUT_SECONDS,
        reschedule_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the recovery daemon.

        Args:
            poll_interval_seconds: How often to check for recoverable jobs
            heartbeat_timeout_seconds: How long before a running job is considered stale
            reschedule_callback: Function to call to reschedule a job for execution
        """
        self.poll_interval_seconds = poll_interval_seconds
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.reschedule_callback = reschedule_callback

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Statistics
        self._stats = {
            "stale_jobs_recovered": 0,
            "jobs_requeued": 0,
            "jobs_moved_to_dlq": 0,
            "webhooks_sent": 0,
            "idempotency_keys_cleaned": 0,
            "errors": 0,
            "last_run_at": None,
            "runs": 0,
        }

    @property
    def is_running(self) -> bool:
        """Check if the daemon is currently running."""
        return self._running and self._thread is not None and self._thread.is_alive()

    @property
    def stats(self) -> dict:
        """Get daemon statistics."""
        return dict(self._stats)

    def start(self) -> bool:
        """
        Start the recovery daemon in a background thread.

        Returns:
            True if started successfully, False if already running
        """
        if self.is_running:
            logger.warning("recovery_daemon_already_running")
            return False

        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="JobRecoveryDaemon",
            daemon=True,
        )
        self._thread.start()
        logger.info("recovery_daemon_started", extra={"poll_interval": self.poll_interval_seconds})
        return True

    def stop(self, timeout_seconds: float = 10) -> bool:
        """
        Stop the recovery daemon.

        Args:
            timeout_seconds: How long to wait for the daemon to stop

        Returns:
            True if stopped successfully, False if timeout
        """
        if not self._running:
            return True

        logger.info("recovery_daemon_stopping")
        self._running = False
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=timeout_seconds)
            if self._thread.is_alive():
                logger.warning("recovery_daemon_stop_timeout")
                return False

        logger.info("recovery_daemon_stopped", extra={"stats": self._stats})
        return True

    def _run_loop(self) -> None:
        """Main daemon loop - runs in background thread."""
        logger.info("recovery_daemon_loop_started")

        while self._running and not self._stop_event.is_set():
            try:
                self._run_recovery_cycle()
            except Exception:
                self._stats["errors"] += 1
                logger.exception("recovery_daemon_cycle_error")

            # Wait for next cycle or stop signal
            self._stop_event.wait(timeout=self.poll_interval_seconds)

        logger.info("recovery_daemon_loop_exited")

    def _run_recovery_cycle(self) -> None:
        """Run a single recovery cycle."""
        from backend.app.repositories.state.store import state_store

        self._stats["runs"] += 1
        self._stats["last_run_at"] = datetime.now(timezone.utc).isoformat()

        # Step 1: Recover stale running jobs
        self._recover_stale_jobs(state_store)

        # Step 2: Re-queue jobs ready for retry
        self._requeue_retry_jobs(state_store)

        # Step 3: Send pending webhooks
        self._send_pending_webhooks(state_store)

        # Step 4: Clean expired idempotency keys
        self._clean_idempotency_keys(state_store)

        # Step 5: Move permanently failed jobs to DLQ
        self._move_failed_to_dlq(state_store)

    def _recover_stale_jobs(self, state_store) -> None:
        """Find and recover jobs that have stale heartbeats."""
        try:
            stale_jobs = state_store.find_stale_running_jobs(
                heartbeat_timeout_seconds=self.heartbeat_timeout_seconds
            )

            for job in stale_jobs:
                job_id = job.get("id")
                retry_count = job.get("retry_count") or 0
                max_retries = job.get("max_retries") or 3

                logger.info(
                    "recovering_stale_job",
                    extra={
                        "job_id": job_id,
                        "retry_count": retry_count,
                        "max_retries": max_retries,
                        "last_heartbeat": job.get("last_heartbeat_at"),
                    }
                )

                if retry_count < max_retries:
                    # Mark for retry
                    state_store.mark_job_for_retry(
                        job_id,
                        reason="Worker heartbeat timeout - job may have crashed",
                        is_retriable=True,
                    )
                    self._stats["stale_jobs_recovered"] += 1
                else:
                    # Max retries exceeded, mark as permanently failed
                    state_store.record_job_completion(
                        job_id,
                        status="failed",
                        error="Worker died and max retries exceeded",
                    )
                    logger.warning(
                        "stale_job_permanently_failed",
                        extra={"job_id": job_id, "retry_count": retry_count}
                    )

        except Exception:
            self._stats["errors"] += 1
            logger.exception("recover_stale_jobs_error")

    def _requeue_retry_jobs(self, state_store) -> None:
        """Re-queue jobs that are ready for retry."""
        try:
            retry_jobs = state_store.find_jobs_ready_for_retry()

            for job in retry_jobs:
                job_id = job.get("id")

                logger.info(
                    "requeuing_job_for_retry",
                    extra={
                        "job_id": job_id,
                        "retry_count": job.get("retry_count"),
                        "retry_at": job.get("retry_at"),
                    }
                )

                # Move job back to queued state
                state_store.requeue_job_for_retry(job_id)
                self._stats["jobs_requeued"] += 1

                # Trigger re-execution if callback is provided
                if self.reschedule_callback:
                    try:
                        self.reschedule_callback(job_id)
                    except Exception:
                        logger.exception(
                            "reschedule_callback_error",
                            extra={"job_id": job_id}
                        )

        except Exception:
            self._stats["errors"] += 1
            logger.exception("requeue_retry_jobs_error")

    def _send_pending_webhooks(self, state_store) -> None:
        """Send webhook notifications for completed jobs."""
        try:
            from backend.app.services.jobs.webhook_service import send_job_webhook_sync

            pending_jobs = state_store.get_jobs_pending_webhook()

            for job in pending_jobs:
                job_id = job.get("id")
                webhook_url = job.get("webhook_url")

                if not webhook_url:
                    continue

                logger.info(
                    "sending_pending_webhook",
                    extra={
                        "job_id": job_id,
                        "status": job.get("status"),
                    }
                )

                try:
                    result = send_job_webhook_sync(job)

                    if result.success:
                        state_store.mark_webhook_sent(job_id)
                        self._stats["webhooks_sent"] += 1
                    else:
                        logger.warning(
                            "webhook_delivery_failed_in_daemon",
                            extra={
                                "job_id": job_id,
                                "error": result.error,
                                "attempts": result.attempts,
                            }
                        )
                except Exception:
                    logger.exception(
                        "webhook_send_error",
                        extra={"job_id": job_id}
                    )

        except Exception:
            self._stats["errors"] += 1
            logger.exception("send_pending_webhooks_error")

    def _clean_idempotency_keys(self, state_store) -> None:
        """Clean up expired idempotency keys."""
        try:
            cleaned = state_store.clean_expired_idempotency_keys()
            self._stats["idempotency_keys_cleaned"] += cleaned

            if cleaned > 0:
                logger.info(
                    "cleaned_expired_idempotency_keys",
                    extra={"count": cleaned}
                )

        except Exception:
            self._stats["errors"] += 1
            logger.exception("clean_idempotency_keys_error")

    def _move_failed_to_dlq(self, state_store) -> None:
        """
        Move permanently failed jobs to the Dead Letter Queue.

        Jobs are moved to DLQ when:
        - Status is 'failed'
        - Max retries exceeded (retry_count >= max_retries)
        - Not already in DLQ (no dead_letter_at timestamp)
        """
        try:
            # Get all jobs
            all_jobs = state_store.list_jobs(
                statuses=["failed"],
                limit=0,  # No limit - get all
            )

            for job in all_jobs:
                job_id = job.get("id")

                # Skip if already in DLQ
                dead_letter_at = job.get("dead_letter_at") or job.get("deadLetterAt")
                if dead_letter_at:
                    continue

                retry_count = job.get("retry_count", job.get("retryCount", 0)) or 0
                max_retries = job.get("max_retries", job.get("maxRetries", 3)) or 3

                # Only move to DLQ if retries exhausted
                if retry_count >= max_retries:
                    logger.info(
                        "moving_job_to_dlq",
                        extra={
                            "job_id": job_id,
                            "retry_count": retry_count,
                            "max_retries": max_retries,
                            "error": job.get("error"),
                        }
                    )

                    # Build failure history from job error
                    failure_history = [{
                        "attempt": retry_count,
                        "error": job.get("error") or "Unknown error",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "category": "exhausted",
                    }]

                    state_store.move_job_to_dlq(job_id, failure_history)
                    self._stats["jobs_moved_to_dlq"] += 1

        except Exception:
            self._stats["errors"] += 1
            logger.exception("move_failed_to_dlq_error")


# Module-level singleton
_daemon: Optional[JobRecoveryDaemon] = None
_daemon_lock = threading.Lock()


def get_recovery_daemon() -> JobRecoveryDaemon:
    """Get the singleton recovery daemon instance."""
    global _daemon
    if _daemon is None:
        with _daemon_lock:
            if _daemon is None:
                _daemon = JobRecoveryDaemon()
    return _daemon


def start_recovery_daemon(
    reschedule_callback: Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Start the recovery daemon (if not already running).

    Args:
        reschedule_callback: Function to call when a job needs to be re-scheduled

    Returns:
        True if started, False if already running
    """
    daemon = get_recovery_daemon()
    if reschedule_callback:
        daemon.reschedule_callback = reschedule_callback
    return daemon.start()


def stop_recovery_daemon(timeout_seconds: float = 10) -> bool:
    """
    Stop the recovery daemon.

    Args:
        timeout_seconds: How long to wait for stop

    Returns:
        True if stopped successfully
    """
    daemon = get_recovery_daemon()
    return daemon.stop(timeout_seconds)


def is_recovery_daemon_running() -> bool:
    """Check if the recovery daemon is running."""
    return get_recovery_daemon().is_running


def get_recovery_daemon_stats() -> dict:
    """Get recovery daemon statistics."""
    return get_recovery_daemon().stats

"""
Periodic task scheduler using APScheduler + Dramatiq.

Run as a separate process: python -m backend.app.services.worker.scheduler

Based on: Dramatiq cookbook periodic task patterns.
"""
from __future__ import annotations

import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Ensure broker is configured
import backend.app.services.worker  # noqa: F401

logger = logging.getLogger("neura.worker.scheduler")


def start_scheduler():
    """Start the periodic task scheduler."""
    scheduler = BlockingScheduler()

    # Health check heartbeat every 5 minutes
    scheduler.add_job(
        lambda: logger.info("scheduler_heartbeat", extra={"event": "scheduler_heartbeat"}),
        IntervalTrigger(minutes=5),
        id="heartbeat",
        name="Scheduler heartbeat",
    )

    # Example: scheduled report generation (disabled by default)
    if os.getenv("NEURA_ENABLE_SCHEDULED_REPORTS", "").lower() in ("1", "true"):
        from backend.app.services.worker.tasks.report_tasks import generate_report
        scheduler.add_job(
            lambda: generate_report.send(
                job_id="scheduled-daily",
                template_id="daily-summary",
                connection_id="default",
            ),
            CronTrigger.from_crontab(os.getenv("NEURA_REPORT_SCHEDULE", "0 6 * * *")),
            id="daily_report",
            name="Daily report generation",
        )

    logger.info("scheduler_started", extra={"event": "scheduler_started"})
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()

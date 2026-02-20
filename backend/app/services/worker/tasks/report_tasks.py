"""Report generation tasks - durable via Dramatiq + Redis."""
import os

import dramatiq
import logging
from dramatiq.results import Results

logger = logging.getLogger("neura.worker.reports")

try:
    from dramatiq.rate_limits import ConcurrentRateLimiter
    from dramatiq.rate_limits.backends import RedisBackend
    _rate_backend = RedisBackend(url=os.getenv("NEURA_REDIS_URL", "redis://localhost:6379/0"))
    REPORT_MUTEX = ConcurrentRateLimiter(_rate_backend, key="report-generation", limit=3)
except Exception:
    REPORT_MUTEX = None

@dramatiq.actor(
    queue_name="reports",
    max_retries=3,
    min_backoff=5000,
    max_backoff=300000,
    time_limit=600_000,  # 10 min hard limit
    store_results=True,
)
def generate_report(job_id: str, template_id: str, connection_id: str, output_format: str = "pdf", **kwargs):
    """Generate a report. Survives worker crashes via Redis persistence."""
    from backend.app.repositories.state import state_store

    # Idempotency: skip if already completed
    existing = state_store.get_job(job_id)
    if existing and existing.get("status") in ("succeeded", "failed"):
        logger.info("report_skipped_idempotent", extra={"event": "report_skipped_idempotent", "job_id": job_id})
        return existing.get("result", {})

    # Acquire concurrent rate limiter (max 3 simultaneous report generations).
    # If the limiter is unavailable (Redis down, import failure), proceed without it.
    if REPORT_MUTEX is not None:
        with REPORT_MUTEX.acquire():
            return _run_report(job_id, template_id, connection_id, output_format, state_store)
    return _run_report(job_id, template_id, connection_id, output_format, state_store)


def _run_report(job_id: str, template_id: str, connection_id: str, output_format: str, state_store):
    """Core report generation logic, extracted for rate-limiter wrapping."""
    try:
        state_store.record_job_start(job_id)
        # record_job_step enforces keyword-only args after `name`
        state_store.record_job_step(
            job_id,
            "generate",
            status="running",
            label="Starting report generation",
        )

        from backend.engine.pipelines.report_pipeline import ReportPipeline
        pipeline = ReportPipeline()
        result = pipeline.run(
            template_id=template_id,
            connection_id=connection_id,
            output_format=output_format,
        )

        state_store.record_job_completion(job_id, status="succeeded", result=result)
        logger.info("report_generated", extra={"event": "report_generated", "job_id": job_id})
        return result
    except Exception as exc:
        state_store.record_job_completion(job_id, status="failed", error=str(exc))
        logger.exception("report_generation_failed", extra={"event": "report_generation_failed", "job_id": job_id})
        raise

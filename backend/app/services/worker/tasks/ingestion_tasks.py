"""Document ingestion tasks - durable via Dramatiq + Redis."""
import os
import dramatiq
import logging

logger = logging.getLogger("neura.worker.ingestion")

try:
    from dramatiq.rate_limits import ConcurrentRateLimiter
    from dramatiq.rate_limits.backends import RedisBackend
    _rate_backend = RedisBackend(url=os.getenv("NEURA_REDIS_URL", "redis://localhost:6379/0"))
    INGESTION_MUTEX = ConcurrentRateLimiter(_rate_backend, key="ingestion-pipeline", limit=5)
except Exception:
    INGESTION_MUTEX = None


@dramatiq.actor(
    queue_name="ingestion",
    max_retries=2,
    min_backoff=3000,
    max_backoff=60000,
    time_limit=120_000,
    store_results=True,
)
def ingest_document(doc_id: str, source_type: str, source_url: str, **kwargs):
    """Ingest a document from an external source. Survives worker crashes via Redis persistence."""
    logger.info("ingestion_started", extra={"event": "ingestion_started", "doc_id": doc_id, "source_type": source_type})

    # Acquire concurrent rate limiter (max 5 simultaneous ingestions).
    if INGESTION_MUTEX is not None:
        with INGESTION_MUTEX.acquire():
            return _run_ingestion(doc_id, source_type, source_url, **kwargs)
    return _run_ingestion(doc_id, source_type, source_url, **kwargs)


def _run_ingestion(doc_id: str, source_type: str, source_url: str, **kwargs):
    """Core ingestion logic, extracted for rate-limiter wrapping."""
    from backend.app.services.ingestion.service import IngestService
    service = IngestService()
    result = service.ingest(doc_id=doc_id, source_type=source_type, source_url=source_url, **kwargs)
    logger.info("ingestion_completed", extra={"event": "ingestion_completed", "doc_id": doc_id})
    return result

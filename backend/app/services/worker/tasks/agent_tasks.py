"""Agent execution tasks - durable via Dramatiq + Redis."""
import os
import dramatiq
import logging

from backend.app.repositories.agent_tasks import agent_task_repository

logger = logging.getLogger("neura.worker.agents")

try:
    from dramatiq.rate_limits import ConcurrentRateLimiter
    from dramatiq.rate_limits.backends import RedisBackend
    _rate_backend = RedisBackend(url=os.getenv("NEURA_REDIS_URL", "redis://localhost:6379/0"))
    AGENT_MUTEX = ConcurrentRateLimiter(_rate_backend, key="agent-execution", limit=4)
except (ImportError, ConnectionError, OSError):
    logger.warning("Rate limiter unavailable; agent concurrency will not be limited")
    AGENT_MUTEX = None


@dramatiq.actor(
    queue_name="agents",
    max_retries=3,
    min_backoff=5000,
    max_backoff=120000,
    time_limit=300_000,  # 5 min
    store_results=True,
)
def run_agent(task_id: str, agent_type: str, params: dict):
    """Execute an agent task. Survives worker crashes via Redis persistence."""
    from backend.app.services.agents import agent_service_v2

    # Idempotency: skip if already completed
    existing = agent_task_repository.get_task(task_id)
    if existing and existing.status in ("completed", "failed", "cancelled"):
        logger.info("agent_skipped_idempotent", extra={
            "event": "agent_skipped_idempotent", "task_id": task_id, "status": existing.status,
        })
        return

    if AGENT_MUTEX is not None:
        with AGENT_MUTEX.acquire():
            _run_agent(task_id, agent_type, params, agent_service_v2)
    else:
        _run_agent(task_id, agent_type, params, agent_service_v2)


def _run_agent(task_id: str, agent_type: str, params: dict, service):
    """Core agent execution logic, extracted for rate-limiter wrapping."""
    try:
        service.execute_task_sync(task_id, agent_type, params)
        logger.info("agent_task_completed", extra={"event": "agent_task_completed", "task_id": task_id})
    except Exception:
        logger.exception("agent_task_failed", extra={"event": "agent_task_failed", "task_id": task_id})
        raise

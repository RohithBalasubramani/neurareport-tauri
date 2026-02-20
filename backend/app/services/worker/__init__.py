"""
Dramatiq worker configuration.

Configures Redis broker with:
- Results backend (store task results for polling)
- Retries with exponential backoff
- Age limit (discard messages older than TTL)
- Prometheus monitoring middleware

Based on: github.com/Bogdanp/dramatiq patterns
"""
import os
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, Retries, TimeLimit, ShutdownNotifications
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend

from .monitoring import WorkerMetricsMiddleware, start_metrics_server

REDIS_URL = os.getenv("NEURA_REDIS_URL", "redis://localhost:6379/0")
RESULT_TTL_MS = int(os.getenv("NEURA_TASK_RESULT_TTL_MS", "1800000"))
WORKER_METRICS_PORT = int(os.getenv("NEURA_WORKER_METRICS_PORT", "9191"))

result_backend = RedisBackend(url=REDIS_URL)

broker = RedisBroker(url=REDIS_URL)
broker.add_middleware(Results(backend=result_backend))
broker.add_middleware(AgeLimit())
broker.add_middleware(TimeLimit())
broker.add_middleware(ShutdownNotifications())
broker.add_middleware(Retries(max_retries=3, min_backoff=1000, max_backoff=300000))
broker.add_middleware(WorkerMetricsMiddleware())

dramatiq.set_broker(broker)

# Start Prometheus metrics server ONLY when running as a Dramatiq worker process.
# The `dramatiq` CLI sets "dramatiq" in sys.argv[0] or the NEURA_WORKER_MODE env var
# is explicitly set. This prevents port conflicts in tests and app imports.
_is_worker = os.getenv("NEURA_WORKER_MODE", "").lower() in {"1", "true"}
if not _is_worker:
    import sys
    _is_worker = any("dramatiq" in arg for arg in sys.argv[:2])

if _is_worker:
    start_metrics_server(WORKER_METRICS_PORT)

"""Prometheus metrics for Dramatiq worker monitoring."""
import time
import dramatiq
from dramatiq.middleware import Middleware

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

if HAS_PROMETHEUS:
    TASK_COMPLETED = Counter("dramatiq_task_completed_total", "Tasks completed", ["actor", "queue", "status"])
    TASK_DURATION = Histogram("dramatiq_task_duration_seconds", "Task duration", ["actor", "queue"], buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 120, 300, 600])
    TASK_ACTIVE = Gauge("dramatiq_tasks_active", "Active tasks", ["actor", "queue"])
    TASK_ENQUEUED = Counter("dramatiq_task_enqueued_total", "Tasks enqueued", ["actor", "queue"])
    DLQ_SIZE = Gauge("dramatiq_dlq_size", "Dead-lettered tasks", ["queue"])


class WorkerMetricsMiddleware(Middleware):
    """Export Dramatiq metrics to Prometheus."""

    def before_process_message(self, broker, message):
        if not HAS_PROMETHEUS:
            return
        message.options["_prom_start"] = time.monotonic()
        TASK_ACTIVE.labels(actor=message.actor_name, queue=message.queue_name).inc()

    def after_enqueue(self, broker, message, delay):
        if not HAS_PROMETHEUS:
            return
        TASK_ENQUEUED.labels(actor=message.actor_name, queue=message.queue_name).inc()

    def after_process_message(self, broker, message, *, result=None, exception=None):
        if not HAS_PROMETHEUS:
            return
        status = "error" if exception else "success"
        elapsed = time.monotonic() - message.options.get("_prom_start", time.monotonic())
        TASK_COMPLETED.labels(actor=message.actor_name, queue=message.queue_name, status=status).inc()
        TASK_DURATION.labels(actor=message.actor_name, queue=message.queue_name).observe(elapsed)
        TASK_ACTIVE.labels(actor=message.actor_name, queue=message.queue_name).dec()

    def after_skip_message(self, broker, message):
        if not HAS_PROMETHEUS:
            return
        DLQ_SIZE.labels(queue=message.queue_name).inc()


def start_metrics_server(port: int = 9191) -> None:
    """Start a standalone Prometheus HTTP metrics server for the worker process."""
    if not HAS_PROMETHEUS:
        return
    start_http_server(port)

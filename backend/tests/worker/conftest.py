"""Test fixtures for Dramatiq actors using StubBroker.

Provides an in-memory broker with the same middleware stack as production
(Results, Retries, TimeLimit) so tests exercise realistic retry and
timeout behavior without requiring Redis.
"""
from __future__ import annotations

import dramatiq
import pytest
from dramatiq import Worker
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import Retries, TimeLimit
from dramatiq.results import Results
from dramatiq.results.backends import StubBackend


@pytest.fixture(autouse=True)
def stub_broker():
    """Replace the real Redis broker with an in-memory stub.

    Mirrors the production middleware stack:
    - Results (StubBackend instead of Redis)
    - Retries (same backoff settings as production)
    - TimeLimit (for timeout testing)
    """
    result_backend = StubBackend()
    broker = StubBroker()
    broker.add_middleware(Results(backend=result_backend))
    broker.add_middleware(Retries(max_retries=3, min_backoff=100, max_backoff=500))
    broker.add_middleware(TimeLimit())
    dramatiq.set_broker(broker)

    # Re-import actors so they register with the stub broker
    from backend.app.services.worker.tasks import report_tasks  # noqa: F401
    from backend.app.services.worker.tasks import agent_tasks  # noqa: F401
    from backend.app.services.worker.tasks import ingestion_tasks  # noqa: F401

    broker.flush_all()
    yield broker
    broker.close()


@pytest.fixture
def stub_worker(stub_broker):
    """Start a worker that processes messages synchronously in tests."""
    worker = Worker(stub_broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture
def result_backend(stub_broker):
    """Access the stub result backend for assertions on task results."""
    for middleware in stub_broker.middleware:
        if isinstance(middleware, Results):
            return middleware.backend
    return None

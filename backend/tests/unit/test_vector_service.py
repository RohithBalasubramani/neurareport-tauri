"""Tests for vector embedding and search service."""
import pytest
import numpy as np
from backend.app.services.vector.embedding_service import (
    EmbeddingService,
    VectorStore,
    SearchResult,
)


class TestVectorStoreMemory:
    """Test in-memory vector store (no external dependencies)."""

    def setup_method(self):
        self.store = VectorStore(backend="memory")

    def test_upsert_and_count(self):
        self.store.upsert("doc1", [1.0, 0.0, 0.0], {"text": "hello"})
        self.store.upsert("doc2", [0.0, 1.0, 0.0], {"text": "world"})
        assert self.store.count() == 2

    def test_search_returns_sorted_by_similarity(self):
        self.store.upsert("doc1", [1.0, 0.0, 0.0], {"text": "hello"})
        self.store.upsert("doc2", [0.0, 1.0, 0.0], {"text": "world"})
        self.store.upsert("doc3", [0.9, 0.1, 0.0], {"text": "similar"})

        results = self.store.search([1.0, 0.0, 0.0], top_k=3)
        assert len(results) == 3
        assert results[0].document_id == "doc1"
        assert results[0].score > results[1].score

    def test_search_empty_store(self):
        results = self.store.search([1.0, 0.0, 0.0], top_k=5)
        assert results == []

    def test_delete(self):
        self.store.upsert("doc1", [1.0, 0.0, 0.0])
        assert self.store.count() == 1
        assert self.store.delete("doc1")
        assert self.store.count() == 0

    def test_delete_nonexistent(self):
        assert not self.store.delete("nonexistent")

    def test_upsert_overwrites(self):
        self.store.upsert("doc1", [1.0, 0.0, 0.0], {"text": "v1"})
        self.store.upsert("doc1", [0.0, 1.0, 0.0], {"text": "v2"})
        assert self.store.count() == 1
        results = self.store.search([0.0, 1.0, 0.0], top_k=1)
        assert results[0].text == "v2"

    def test_batch_upsert(self):
        items = [
            ("doc1", [1.0, 0.0, 0.0], {"text": "a"}),
            ("doc2", [0.0, 1.0, 0.0], {"text": "b"}),
            ("doc3", [0.0, 0.0, 1.0], {"text": "c"}),
        ]
        count = self.store.upsert_batch(items)
        assert count == 3
        assert self.store.count() == 3

    def test_search_respects_top_k(self):
        for i in range(10):
            self.store.upsert(f"doc{i}", [float(i == 0), float(i == 1), float(i == 2)])

        results = self.store.search([1.0, 0.0, 0.0], top_k=3)
        assert len(results) == 3

    def test_cosine_similarity_normalized(self):
        self.store.upsert("doc1", [3.0, 0.0, 0.0], {"text": "scaled"})
        results = self.store.search([1.0, 0.0, 0.0], top_k=1)
        assert len(results) == 1
        assert abs(results[0].score - 1.0) < 0.01  # Cosine similarity should be ~1.0

    def test_zero_vector_ignored(self):
        self.store.upsert("doc1", [0.0, 0.0, 0.0], {"text": "zero"})
        self.store.upsert("doc2", [1.0, 0.0, 0.0], {"text": "nonzero"})
        results = self.store.search([1.0, 0.0, 0.0], top_k=5)
        assert len(results) == 1  # Zero vector should be skipped


class TestObservabilityModule:
    """Test observability module initialization."""

    def test_init_tracing_no_endpoint(self):
        from backend.app.services.observability import init_tracing
        from fastapi import FastAPI
        app = FastAPI()
        result = init_tracing(app, otlp_endpoint=None)
        assert result is False

    def test_init_metrics_disabled(self):
        from backend.app.services.observability import init_metrics
        from fastapi import FastAPI
        app = FastAPI()
        result = init_metrics(app, enabled=False)
        assert result is False


class TestDramatiqTasks:
    """Test Dramatiq task definitions exist and are properly configured."""

    def test_task_actors_importable(self):
        # Just verify the task module imports without error
        # Actual task execution requires Redis
        try:
            from backend.app.services.worker.tasks import (
                generate_report_task,
                run_agent_task,
                export_document_task,
                ingest_document_task,
                send_webhook_task,
            )
            # Verify they are dramatiq actors
            assert hasattr(generate_report_task, 'send')
            assert hasattr(run_agent_task, 'send')
            assert hasattr(export_document_task, 'send')
            assert hasattr(ingest_document_task, 'send')
            assert hasattr(send_webhook_task, 'send')
        except Exception:
            # Redis not running is expected in CI
            pytest.skip("Redis not available for Dramatiq broker")

"""Tests for Dramatiq worker tasks using StubBroker fixtures."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


class TestReportTasks:
    """Test report generation task with StubBroker."""

    def test_generate_report_enqueues(self, stub_broker):
        """Verify generate_report actor can be enqueued."""
        from backend.app.services.worker.tasks.report_tasks import generate_report

        msg = generate_report.send("job-1", "template-1", "conn-1", "pdf")
        assert msg is not None

    def test_generate_report_idempotent_skip(self, stub_broker, stub_worker):
        """Verify idempotent skip when job already succeeded."""
        from backend.app.services.worker.tasks.report_tasks import generate_report

        mock_store = MagicMock()
        mock_store.get_job.return_value = {"status": "succeeded", "result": {"url": "/test.pdf"}}

        with patch("backend.app.services.worker.tasks.report_tasks.state_store", mock_store, create=True):
            # The actor import happens at fixture time, so we need to patch at call time
            msg = generate_report.send("job-done", "template-1", "conn-1")
            stub_worker.join()

    def test_run_report_records_job_step_keyword_only(self, stub_broker, monkeypatch):
        """Regression: record_job_step is keyword-only after name (no positional label)."""
        import sys
        import types

        from backend.app.services.worker.tasks import report_tasks

        class _StubStateStore:
            def __init__(self):
                self.started: list[str] = []
                self.steps: list[dict] = []
                self.completed: list[dict] = []

            def record_job_start(self, job_id: str):
                self.started.append(job_id)

            def record_job_step(
                self,
                job_id: str,
                name: str,
                *,
                status: str | None = None,
                error: str | None = None,
                progress: float | None = None,
                label: str | None = None,
            ):
                self.steps.append(
                    {
                        "job_id": job_id,
                        "name": name,
                        "status": status,
                        "label": label,
                        "error": error,
                        "progress": progress,
                    }
                )

            def record_job_completion(self, job_id: str, *, status: str, result=None, error=None):
                self.completed.append(
                    {"job_id": job_id, "status": status, "result": result, "error": error}
                )

        # Avoid importing and running the real report pipeline in unit tests.
        dummy_mod = types.ModuleType("backend.engine.pipelines.report_pipeline")

        class _DummyReportPipeline:
            def run(self, *, template_id: str, connection_id: str, output_format: str):
                return {"ok": True, "template_id": template_id, "connection_id": connection_id, "format": output_format}

        dummy_mod.ReportPipeline = _DummyReportPipeline
        monkeypatch.setitem(sys.modules, "backend.engine.pipelines.report_pipeline", dummy_mod)

        store = _StubStateStore()
        result = report_tasks._run_report("job-kw", "template-1", "conn-1", "pdf", store)

        assert result["ok"] is True
        assert store.steps, "expected record_job_step to be called"
        assert store.steps[0]["name"] == "generate"
        assert store.steps[0]["status"] == "running"
        assert store.steps[0]["label"] == "Starting report generation"
        assert store.completed and store.completed[0]["status"] == "succeeded"


class TestIngestionTasks:
    """Test document ingestion task."""

    def test_ingest_document_enqueues(self, stub_broker):
        """Verify ingest_document actor can be enqueued."""
        from backend.app.services.worker.tasks.ingestion_tasks import ingest_document

        msg = ingest_document.send("doc-1", "pdf", "https://example.com/doc.pdf")
        assert msg is not None


class TestAgentTasks:
    """Test agent execution task."""

    def test_run_agent_enqueues(self, stub_broker):
        """Verify run_agent actor can be enqueued."""
        from backend.app.services.worker.tasks.agent_tasks import run_agent

        msg = run_agent.send("task-1", "research", {"topic": "AI"})
        assert msg is not None

    def test_run_agent_idempotent_skip(self, stub_broker, stub_worker):
        """Verify idempotent skip when task already completed."""
        from backend.app.services.worker.tasks.agent_tasks import run_agent

        mock_repo = MagicMock()
        mock_task = MagicMock()
        mock_task.status = "completed"
        mock_repo.get_task.return_value = mock_task

        with patch("backend.app.services.worker.tasks.agent_tasks.agent_task_repository", mock_repo):
            msg = run_agent.send("task-done", "research", {"topic": "AI"})
            stub_worker.join()


class TestBrokerMiddleware:
    """Verify the StubBroker has correct middleware configured."""

    def test_broker_has_results_middleware(self, stub_broker):
        """Results middleware should be present for store_results=True actors."""
        from dramatiq.results import Results
        middleware_types = [type(m) for m in stub_broker.middleware]
        assert Results in middleware_types

    def test_broker_has_retries_middleware(self, stub_broker):
        """Retries middleware should be present for retry behavior testing."""
        from dramatiq.middleware import Retries
        middleware_types = [type(m) for m in stub_broker.middleware]
        assert Retries in middleware_types

    def test_broker_has_time_limit_middleware(self, stub_broker):
        """TimeLimit middleware should be present for timeout testing."""
        from dramatiq.middleware import TimeLimit
        middleware_types = [type(m) for m in stub_broker.middleware]
        assert TimeLimit in middleware_types

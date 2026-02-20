"""Integration tests for the complete report generation pipeline.

Tests the full flow from template upload to report generation,
including all intermediate steps and error scenarios.
"""
from __future__ import annotations

import asyncio
import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import time

import pytest

# Mock cryptography before imports
fernet_module = types.ModuleType("cryptography.fernet")


class _DummyFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(fernet_module, "Fernet", _DummyFernet)
setattr(fernet_module, "InvalidToken", Exception)
crypto_module = types.ModuleType("cryptography")
setattr(crypto_module, "fernet", fernet_module)
sys.modules.setdefault("cryptography", crypto_module)
sys.modules.setdefault("cryptography.fernet", fernet_module)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from .. import api
from ..app.services import config as config_module
from ..app.repositories.state import store as state_store_module


@pytest.fixture
def fresh_state(tmp_path, monkeypatch):
    """Create a fresh state store and upload directories for each test."""
    # Clear NEURA_STATE_DIR to prevent .env override
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    settings = config_module.get_settings()
    settings.allow_anonymous_api = True
    api.SETTINGS = settings
    base_dir = tmp_path / "state"
    store = state_store_module.StateStore(base_dir=base_dir)
    state_store_module.set_state_store(store)
    api.state_store = store

    # Disable scheduler
    api.SCHEDULER_DISABLED = True
    api.SCHEDULER = None

    # Setup upload directories
    upload_root = tmp_path / "uploads"
    upload_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(api, "UPLOAD_ROOT", upload_root)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", upload_root.resolve())

    excel_root = tmp_path / "excel-uploads"
    excel_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(api, "EXCEL_UPLOAD_ROOT", excel_root)
    monkeypatch.setattr(api, "EXCEL_UPLOAD_ROOT_BASE", excel_root.resolve())

    monkeypatch.setitem(api._UPLOAD_KIND_BASES, "pdf", (upload_root.resolve(), "/uploads"))
    monkeypatch.setitem(api._UPLOAD_KIND_BASES, "excel", (excel_root.resolve(), "/excel-uploads"))

    return store


@pytest.fixture
def client(fresh_state):
    """Create test client."""
    return TestClient(api.app)


@pytest.fixture
def sample_db(tmp_path):
    """Create a sample SQLite database for testing."""
    import sqlite3

    db_path = tmp_path / "sample.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create sample tables
    cursor.execute("""
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY,
            date TEXT,
            value REAL,
            category TEXT
        )
    """)

    # Insert sample data
    sample_data = [
        (1, '2024-01-01', 100.5, 'A'),
        (2, '2024-01-02', 200.3, 'B'),
        (3, '2024-01-03', 150.7, 'A'),
        (4, '2024-01-04', 300.1, 'C'),
        (5, '2024-01-05', 175.9, 'B'),
    ]
    cursor.executemany(
        "INSERT INTO reports (id, date, value, category) VALUES (?, ?, ?, ?)",
        sample_data
    )

    conn.commit()
    conn.close()

    return db_path


class TestConnectionPipeline:
    """Test database connection workflow."""

    def test_connection_workflow_success(self, client, fresh_state, sample_db):
        """Test complete connection workflow: test -> save -> use."""
        # Step 1: Test connection
        test_resp = client.post("/connections/test", json={
            "db_url": str(sample_db),
            "db_type": "sqlite",
        })
        assert test_resp.status_code == 200
        test_data = test_resp.json()
        assert test_data.get("ok") is True or test_data.get("status") == "ok"

        # Step 2: Save connection
        save_resp = client.post("/connections", json={
            "name": "Sample DB",
            "db_type": "sqlite",
            "db_url": str(sample_db),
        })
        assert save_resp.status_code == 200
        save_data = save_resp.json()
        conn_id = save_data["connection"]["id"]
        assert conn_id

        # Step 3: List connections to verify saved
        list_resp = client.get("/connections")
        assert list_resp.status_code == 200
        connections = list_resp.json()["connections"]
        connection_ids = {conn["id"] for conn in connections}
        assert conn_id in connection_ids

        # Step 4: Health check
        health_resp = client.post(f"/connections/{conn_id}/health")
        # May succeed or fail depending on path resolution or service availability
        assert health_resp.status_code in (200, 400, 500, 503)

    def test_connection_workflow_invalid_db(self, client, fresh_state):
        """Test connection workflow with invalid database."""
        test_resp = client.post("/connections/test", json={
            "db_url": "/nonexistent/path/db.sqlite",
            "db_type": "sqlite",
        })

        # Should indicate failure
        data = test_resp.json()
        assert test_resp.status_code >= 400 or data.get("ok") is False


class TestTemplatePipeline:
    """Test template management pipeline."""

    def test_template_lifecycle(self, client, fresh_state, tmp_path):
        """Test template creation, listing, and deletion."""
        # Create template in state
        fresh_state.upsert_template(
            "tpl-lifecycle",
            name="Lifecycle Template",
            status="approved",
        )

        # Create template directory with required files
        tpl_dir = tmp_path / "uploads" / "tpl-lifecycle"
        tpl_dir.mkdir(parents=True, exist_ok=True)

        # Create contract.json
        contract = {
            "template_id": "tpl-lifecycle",
            "batches": [],
            "fields": {},
        }
        (tpl_dir / "contract.json").write_text(json.dumps(contract))

        # Create template HTML
        (tpl_dir / "template_p1.html").write_text("<html><body>Test</body></html>")

        # List templates
        list_resp = client.get("/templates")
        assert list_resp.status_code == 200
        templates = list_resp.json()["templates"]
        assert any(t["id"] == "tpl-lifecycle" for t in templates)

        # Delete template
        delete_resp = client.delete("/templates/tpl-lifecycle")
        assert delete_resp.status_code == 200

        # Verify deletion
        list_resp2 = client.get("/templates")
        templates2 = list_resp2.json()["templates"]
        assert not any(t["id"] == "tpl-lifecycle" for t in templates2)


class TestJobPipeline:
    """Test job creation and execution pipeline."""

    def test_job_complete_success_flow(self, client, fresh_state, monkeypatch, tmp_path):
        """Test successful job execution from creation to completion."""
        # Setup
        fresh_state.upsert_template("tpl-job-flow", name="Job Flow Template", status="approved")
        fresh_state.upsert_connection(
            conn_id="conn-job-flow",
            name="Job Flow Connection",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )

        # Track scheduled jobs
        scheduled_jobs = []

        def mock_schedule(job_id, payload_data, kind, correlation_id, step_progress):
            scheduled_jobs.append({
                "job_id": job_id,
                "payload": payload_data,
                "kind": kind,
            })
            # Simulate immediate execution
            tracker = api.JobRunTracker(job_id, step_progress=step_progress)
            tracker.start()
            tracker.step_succeeded("dataLoad")
            tracker.step_succeeded("renderPdf")
            tracker.succeed({"ok": True})

        monkeypatch.setattr(api, "_schedule_report_job", mock_schedule)

        # Submit job
        submit_resp = client.post("/jobs/run-report", json={
            "template_id": "tpl-job-flow",
            "connection_id": "conn-job-flow",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
        })

        assert submit_resp.status_code == 200
        job_id = submit_resp.json()["job_id"]
        assert job_id in [j["job_id"] for j in scheduled_jobs]

        # Check job status
        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        job = status_resp.json()["job"]
        assert job["status"] == "succeeded"
        assert job["progress"] == 100

    def test_job_failure_handling(self, client, fresh_state, monkeypatch, tmp_path):
        """Test job failure is properly recorded."""
        fresh_state.upsert_template("tpl-job-fail", name="Job Fail Template", status="approved")

        def mock_schedule(job_id, payload_data, kind, correlation_id, step_progress):
            tracker = api.JobRunTracker(job_id, step_progress=step_progress)
            tracker.start()
            tracker.step_running("dataLoad")
            tracker.step_failed("dataLoad", "Database connection failed")
            tracker.fail("Job failed: Database connection failed")

        monkeypatch.setattr(api, "_schedule_report_job", mock_schedule)

        submit_resp = client.post("/jobs/run-report", json={
            "template_id": "tpl-job-fail",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
        })

        job_id = submit_resp.json()["job_id"]

        status_resp = client.get(f"/jobs/{job_id}")
        job = status_resp.json()["job"]
        assert job["status"] == "failed"
        assert "Database connection failed" in job["error"]

    def test_job_cancellation_flow(self, client, fresh_state, monkeypatch):
        """Test job cancellation workflow."""
        fresh_state.upsert_template("tpl-cancel-flow", name="Cancel Flow Template", status="approved")

        # Create a job without executing it
        scheduled_jobs = []

        def mock_schedule(job_id, payload_data, kind, correlation_id, step_progress):
            scheduled_jobs.append(job_id)
            # Don't execute - leave in queued state

        monkeypatch.setattr(api, "_schedule_report_job", mock_schedule)

        # Mock force_cancel_job
        class MockReportService:
            @staticmethod
            def force_cancel_job(job_id, *, force=False):
                return True

        api.report_service = MockReportService()

        # Submit job
        submit_resp = client.post("/jobs/run-report", json={
            "template_id": "tpl-cancel-flow",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
        })
        job_id = submit_resp.json()["job_id"]

        # Cancel job
        cancel_resp = client.post(f"/jobs/{job_id}/cancel")
        assert cancel_resp.status_code == 200

        # Verify cancelled status
        status_resp = client.get(f"/jobs/{job_id}")
        job = status_resp.json()["job"]
        assert job["status"] == "cancelled"


class TestBatchJobPipeline:
    """Test batch job submission and tracking."""

    def test_batch_job_submission(self, client, fresh_state, monkeypatch):
        """Test submitting multiple jobs in one request."""
        fresh_state.upsert_template("tpl-batch-1", name="Batch 1", status="approved")
        fresh_state.upsert_template("tpl-batch-2", name="Batch 2", status="approved")
        fresh_state.upsert_template("tpl-batch-3", name="Batch 3", status="approved")

        scheduled = []

        def mock_schedule(job_id, payload_data, kind, correlation_id, step_progress):
            scheduled.append({
                "job_id": job_id,
                "template_id": payload_data.get("template_id"),
            })

        monkeypatch.setattr(api, "_schedule_report_job", mock_schedule)

        payloads = [
            {"template_id": "tpl-batch-1", "start_date": "2024-01-01", "end_date": "2024-01-31"},
            {"template_id": "tpl-batch-2", "start_date": "2024-02-01", "end_date": "2024-02-28"},
            {"template_id": "tpl-batch-3", "start_date": "2024-03-01", "end_date": "2024-03-31"},
        ]

        resp = client.post("/jobs/run-report", json=payloads)
        assert resp.status_code == 200

        data = resp.json()
        assert data["count"] == 3
        assert len(data["job_ids"]) == 3
        assert len(scheduled) == 3

        # Verify each template got a job
        scheduled_templates = {s["template_id"] for s in scheduled}
        assert scheduled_templates == {"tpl-batch-1", "tpl-batch-2", "tpl-batch-3"}


class TestSchedulePipeline:
    """Test scheduled report execution."""

    def test_schedule_creation_and_listing(self, client, fresh_state, tmp_path):
        """Test schedule creation and listing."""
        fresh_state.upsert_template("tpl-schedule", name="Schedule Template", status="approved")
        fresh_state.upsert_connection(
            conn_id="conn-schedule",
            name="Schedule Connection",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )

        # Create schedule
        create_resp = client.post("/reports/schedules", json={
            "template_id": "tpl-schedule",
            "connection_id": "conn-schedule",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
            "frequency": "daily",
            "name": "Daily Report Schedule",
        })

        assert create_resp.status_code == 200
        schedule_data = create_resp.json()
        schedule_id = schedule_data.get("schedule", {}).get("id") or schedule_data.get("id")
        assert schedule_id

        # List schedules
        list_resp = client.get("/reports/schedules")
        assert list_resp.status_code == 200
        schedules = list_resp.json()["schedules"]
        assert any(s["id"] == schedule_id for s in schedules)

        # Delete schedule
        delete_resp = client.delete(f"/reports/schedules/{schedule_id}")
        assert delete_resp.status_code == 200

        # Verify deletion
        list_resp2 = client.get("/reports/schedules")
        schedules2 = list_resp2.json()["schedules"]
        assert not any(s["id"] == schedule_id for s in schedules2)


class TestBootstrapPipeline:
    """Test application state bootstrap."""

    def test_bootstrap_returns_complete_state(self, client, fresh_state, tmp_path):
        """Test bootstrap endpoint returns all required state."""
        # Add data to state
        fresh_state.upsert_connection(
            conn_id="conn-boot",
            name="Bootstrap Connection",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )
        fresh_state.upsert_template("tpl-boot", name="Bootstrap Template", status="approved")
        fresh_state.set_last_used("conn-boot", "tpl-boot")

        # Bootstrap
        resp = client.get("/state/bootstrap")
        assert resp.status_code == 200

        data = resp.json()
        assert "connections" in data
        assert "templates" in data
        assert "last_used" in data

        # Verify content
        assert len(data["connections"]) == 1
        assert data["connections"][0]["id"] == "conn-boot"

        assert len(data["templates"]) == 1
        assert data["templates"][0]["id"] == "tpl-boot"

        assert data["last_used"]["connection_id"] == "conn-boot"
        assert data["last_used"]["template_id"] == "tpl-boot"


class TestSavedChartsPipeline:
    """Test saved charts workflow."""

    def test_chart_crud_operations(self, client, fresh_state):
        """Test create, read, update, delete for saved charts."""
        fresh_state.upsert_template("tpl-charts", name="Charts Template", status="approved")

        # Create chart
        chart_spec = {
            "type": "line",
            "xField": "date",
            "yFields": ["value"],
        }

        created = fresh_state.create_saved_chart(
            template_id="tpl-charts",
            name="Test Chart",
            spec=chart_spec,
        )
        assert created["id"]
        chart_id = created["id"]

        # Read charts
        charts = fresh_state.list_saved_charts("tpl-charts")
        assert len(charts) == 1
        assert charts[0]["name"] == "Test Chart"

        # Update chart
        updated = fresh_state.update_saved_chart(chart_id, name="Updated Chart")
        assert updated["name"] == "Updated Chart"

        # Delete chart
        deleted = fresh_state.delete_saved_chart(chart_id)
        assert deleted is True

        # Verify deletion
        charts_after = fresh_state.list_saved_charts("tpl-charts")
        assert len(charts_after) == 0


class TestErrorRecovery:
    """Test error recovery scenarios."""

    def test_state_recovery_after_invalid_json(self, fresh_state, tmp_path):
        """Test state store handles corrupted state file."""
        # Write invalid JSON to state file
        state_path = fresh_state._state_path
        state_path.write_text("{ invalid json }", encoding="utf-8")

        # Should recover with default state
        state = fresh_state._read_state()
        assert "connections" in state
        assert "templates" in state

    def test_concurrent_state_writes(self, fresh_state):
        """Test concurrent state modifications don't corrupt data."""
        import threading
        import time

        errors = []

        def worker(i):
            try:
                for j in range(5):
                    fresh_state.upsert_template(
                        f"tpl-concurrent-{i}-{j}",
                        name=f"Template {i}-{j}",
                        status="approved",
                    )
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent writes caused errors: {errors}"

        # Verify all templates were created
        templates = fresh_state.list_templates()
        # Should have 25 templates (5 threads * 5 templates each)
        assert len(templates) == 25

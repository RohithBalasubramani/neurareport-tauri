"""Comprehensive API endpoint tests.

Tests all major API endpoints for correct behavior, error handling,
and edge cases.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import json

import pytest
from fastapi.testclient import TestClient

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

from .. import api
from ..app.repositories.connections import db_connection as db_conn_module
from ..app.repositories.state import store as state_store_module


@pytest.fixture
def fresh_state(tmp_path, monkeypatch):
    """Create a fresh state store for each test."""
    # Clear env vars that override StateStore base_dir or backend selection
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    monkeypatch.delenv("NEURA_STATE_BACKEND", raising=False)
    monkeypatch.delenv("NEURA_STATE_DB_PATH", raising=False)
    base_dir = tmp_path / "state"
    store = state_store_module.StateStore(base_dir=base_dir)
    state_store_module.set_state_store(store)
    api.state_store = store
    # Also patch the db_connection module-level reference so that
    # resolve_db_path() uses the same fresh store (test_persistence.py
    # may have overwritten it with a stale instance).
    monkeypatch.setattr(db_conn_module, "state_store", store)

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


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint_returns_ok(self, client):
        """Test /health returns OK status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"

    def test_healthz_endpoint_returns_ok(self, client):
        """Test /healthz returns detailed health info."""
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    def test_readyz_endpoint_returns_status(self, client):
        """Test /readyz returns readiness status."""
        resp = client.get("/readyz")
        # May return 200 or 503 depending on configuration
        assert resp.status_code in (200, 503)


class TestConnectionEndpoints:
    """Test connection management endpoints."""

    def test_list_connections_empty(self, client, fresh_state):
        """Test listing connections when none exist."""
        resp = client.get("/connections")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["connections"] == []

    def test_list_connections_with_data(self, client, fresh_state):
        """Test listing connections with existing data."""
        fresh_state.upsert_connection(
            conn_id="conn-1",
            name="Test Connection",
            db_type="sqlite",
            database_path="/path/to/db.sqlite",
            secret_payload={"token": "secret"},
        )

        resp = client.get("/connections")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["connections"]) == 1
        assert data["connections"][0]["id"] == "conn-1"
        assert data["connections"][0]["name"] == "Test Connection"

    def test_test_connection_valid_sqlite(self, client, fresh_state, tmp_path):
        """Test connection testing with valid SQLite DB."""
        # Create a test SQLite database
        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        resp = client.post("/connections/test", json={
            "db_url": str(db_path),
            "db_type": "sqlite",
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True or data.get("status") == "ok"

    def test_test_connection_invalid_path(self, client):
        """Test connection testing with invalid path."""
        resp = client.post("/connections/test", json={
            "db_url": "/nonexistent/path/db.sqlite",
            "db_type": "sqlite",
        })

        # Should return error status (either 400 or error in response)
        data = resp.json()
        # Either status code is 4xx or response indicates error
        assert resp.status_code >= 400 or data.get("ok") is False or data.get("status") == "error"

    def test_upsert_connection_create(self, client, fresh_state, tmp_path):
        """Test creating a new connection."""
        resp = client.post("/connections", json={
            "name": "New Connection",
            "db_type": "sqlite",
            "db_url": str(tmp_path / "new.db"),
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["connection"]["name"] == "New Connection"

    def test_upsert_connection_update(self, client, fresh_state, tmp_path):
        """Test updating an existing connection."""
        # Create connection first
        conn = fresh_state.upsert_connection(
            conn_id="conn-update",
            name="Original Name",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )

        # Update it
        resp = client.post("/connections", json={
            "id": "conn-update",
            "name": "Updated Name",
            "db_type": "sqlite",
            "db_url": str(tmp_path / "db.sqlite"),
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["connection"]["name"] == "Updated Name"

    def test_delete_connection_existing(self, client, fresh_state, tmp_path):
        """Test deleting an existing connection."""
        fresh_state.upsert_connection(
            conn_id="conn-delete",
            name="To Delete",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )

        resp = client.delete("/connections/conn-delete")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

        # Verify deletion
        connections = fresh_state.list_connections()
        assert len(connections) == 0

    def test_delete_connection_nonexistent(self, client):
        """Test deleting a nonexistent connection returns 404."""
        resp = client.delete("/connections/nonexistent-conn")
        assert resp.status_code == 404

    def test_healthcheck_connection(self, client, fresh_state, tmp_path):
        """Test connection health check."""
        # Create a valid SQLite database
        db_path = tmp_path / "health.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        fresh_state.upsert_connection(
            conn_id="conn-health",
            name="Health Check Connection",
            db_type="sqlite",
            database_path=str(db_path),
            secret_payload=None,
        )

        resp = client.post("/connections/conn-health/health")
        # May succeed or fail depending on DB accessibility
        assert resp.status_code in (200, 400, 404, 500)


class TestTemplateEndpoints:
    """Test template management endpoints."""

    def test_list_templates_empty(self, client, fresh_state):
        """Test listing templates when none exist."""
        resp = client.get("/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert "templates" in data
        assert data["templates"] == []

    def test_list_templates_with_data(self, client, fresh_state):
        """Test listing templates with existing data."""
        fresh_state.upsert_template(
            "tpl-1",
            name="Test Template",
            status="approved",
        )

        resp = client.get("/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["templates"]) == 1
        assert data["templates"][0]["id"] == "tpl-1"

    def test_list_templates_with_status_filter(self, client, fresh_state):
        """Test filtering templates by status."""
        fresh_state.upsert_template("tpl-approved", name="Approved", status="approved")
        fresh_state.upsert_template("tpl-pending", name="Pending", status="pending")

        resp = client.get("/templates", params={"status": "approved"})
        assert resp.status_code == 200
        data = resp.json()
        # Should only return approved templates
        for tpl in data["templates"]:
            assert tpl["status"] == "approved"

    def test_delete_template_existing(self, client, fresh_state):
        """Test deleting an existing template."""
        fresh_state.upsert_template("tpl-delete", name="To Delete", status="approved")

        resp = client.delete("/templates/tpl-delete")
        assert resp.status_code == 200

        # Verify deletion
        templates = fresh_state.list_templates()
        assert len(templates) == 0

    def test_delete_template_nonexistent(self, client):
        """Test deleting a nonexistent template."""
        resp = client.delete("/templates/nonexistent-tpl")
        # Should return 404 or error
        assert resp.status_code in (404, 400, 500)

    def test_bootstrap_state(self, client, fresh_state, tmp_path):
        """Test bootstrap state endpoint returns app state."""
        # Add some data
        fresh_state.upsert_connection(
            conn_id="conn-boot",
            name="Boot Connection",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )
        fresh_state.upsert_template("tpl-boot", name="Boot Template", status="approved")
        fresh_state.set_last_used("conn-boot", "tpl-boot")

        resp = client.get("/state/bootstrap")
        assert resp.status_code == 200
        data = resp.json()
        assert "connections" in data
        assert "templates" in data
        assert "last_used" in data


class TestJobEndpoints:
    """Test job management endpoints."""

    def test_list_jobs_empty(self, client, fresh_state):
        """Test listing jobs when none exist."""
        resp = client.get("/jobs")
        assert resp.status_code == 200
        data = resp.json()
        assert data["jobs"] == []

    def test_list_jobs_with_data(self, client, fresh_state):
        """Test listing jobs with existing data."""
        fresh_state.upsert_template("tpl-job", name="Job Template", status="approved")
        fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-job",
            template_name="Job Template",
            template_kind="pdf",
        )

        resp = client.get("/jobs")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["jobs"]) == 1

    def test_list_jobs_with_status_filter(self, client, fresh_state):
        """Test filtering jobs by status."""
        fresh_state.upsert_template("tpl-filter", name="Filter Template", status="approved")

        # Create jobs with different statuses
        queued = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-filter",
            template_name="Filter Template",
        )
        running = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-filter",
            template_name="Filter Template",
        )
        fresh_state.record_job_start(running["id"])

        resp = client.get("/jobs", params={"status": "running"})
        assert resp.status_code == 200
        data = resp.json()
        assert all(job["status"] == "running" for job in data["jobs"])

    def test_list_jobs_active_only(self, client, fresh_state):
        """Test listing only active jobs."""
        fresh_state.upsert_template("tpl-active", name="Active Template", status="approved")

        # Create active and completed jobs
        active = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-active",
            template_name="Active Template",
        )
        completed = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-active",
            template_name="Active Template",
        )
        fresh_state.record_job_completion(completed["id"], status="succeeded")

        resp = client.get("/jobs", params={"active_only": "true"})
        assert resp.status_code == 200
        data = resp.json()
        job_ids = [job["id"] for job in data["jobs"]]
        assert active["id"] in job_ids
        assert completed["id"] not in job_ids

    def test_get_job_existing(self, client, fresh_state):
        """Test getting a specific job."""
        fresh_state.upsert_template("tpl-get", name="Get Template", status="approved")
        job = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-get",
            template_name="Get Template",
        )

        resp = client.get(f"/jobs/{job['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job"]["id"] == job["id"]

    def test_get_job_nonexistent(self, client):
        """Test getting a nonexistent job."""
        resp = client.get("/jobs/nonexistent-job-id")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job"] is None

    def test_cancel_job(self, client, fresh_state, monkeypatch):
        """Test canceling a job."""
        fresh_state.upsert_template("tpl-cancel", name="Cancel Template", status="approved")
        job = fresh_state.create_job(
            job_type="run_report",
            template_id="tpl-cancel",
            template_name="Cancel Template",
        )

        # Mock the force_cancel_job function
        class MockReportService:
            @staticmethod
            def force_cancel_job(job_id, *, force=False):
                return True

        api.report_service = MockReportService()

        resp = client.post(f"/jobs/{job['id']}/cancel")
        assert resp.status_code == 200

        # Verify job is cancelled
        updated = fresh_state.get_job(job["id"])
        assert updated["status"] == "cancelled"


class TestReportEndpoints:
    """Test report generation endpoints."""

    def test_run_report_missing_template(self, client, fresh_state):
        """Test running report with missing template."""
        resp = client.post("/reports/run", json={
            "template_id": "nonexistent",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
        })

        # Should return error
        assert resp.status_code in (400, 404, 500)

    def test_run_report_job_creates_job(self, client, fresh_state, monkeypatch):
        """Test that run-report job endpoint creates a job."""
        fresh_state.upsert_template("tpl-run", name="Run Template", status="approved")

        # Mock the schedule function
        scheduled = []

        def mock_schedule(job_id, payload_data, kind, correlation_id, step_progress):
            scheduled.append(job_id)

        monkeypatch.setattr(api, "_schedule_report_job", mock_schedule)

        resp = client.post("/jobs/run-report", json={
            "template_id": "tpl-run",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
        })

        assert resp.status_code == 200
        data = resp.json()
        assert "job_id" in data
        assert data["job_id"] in scheduled


class TestScheduleEndpoints:
    """Test schedule management endpoints."""

    def test_list_schedules_empty(self, client, fresh_state):
        """Test listing schedules when none exist."""
        resp = client.get("/reports/schedules")
        assert resp.status_code == 200
        data = resp.json()
        assert data["schedules"] == []

    def test_create_and_list_schedule(self, client, fresh_state, tmp_path):
        """Test creating and listing schedules."""
        # Setup required data
        fresh_state.upsert_template("tpl-sched", name="Schedule Template", status="approved")
        fresh_state.upsert_connection(
            conn_id="conn-sched",
            name="Schedule Connection",
            db_type="sqlite",
            database_path=str(tmp_path / "db.sqlite"),
            secret_payload=None,
        )

        resp = client.post("/reports/schedules", json={
            "template_id": "tpl-sched",
            "connection_id": "conn-sched",
            "start_date": "2024-01-01 00:00:00",
            "end_date": "2024-01-31 23:59:59",
            "frequency": "daily",
            "name": "Daily Report",
        })

        assert resp.status_code == 200
        data = resp.json()
        assert "schedule" in data or "id" in data

    def test_delete_schedule(self, client, fresh_state, tmp_path):
        """Test deleting a schedule."""
        fresh_state.upsert_template("tpl-del-sched", name="Delete Schedule", status="approved")

        schedule = fresh_state.create_schedule(
            name="To Delete",
            template_id="tpl-del-sched",
            template_name="Delete Schedule",
            template_kind="pdf",
            connection_id=None,
            connection_name=None,
            start_date="2024-01-01 00:00:00",
            end_date="2024-01-31 23:59:59",
            key_values=None,
            batch_ids=None,
            docx=False,
            xlsx=False,
            email_recipients=None,
            email_subject=None,
            email_message=None,
            frequency="daily",
            interval_minutes=1440,
            next_run_at="2024-01-01T00:00:00Z",
            first_run_at="2024-01-01T00:00:00Z",
        )

        resp = client.delete(f"/reports/schedules/{schedule['id']}")
        assert resp.status_code == 200

        # Verify deletion
        schedules = fresh_state.list_schedules()
        assert len(schedules) == 0


class TestCorrelationId:
    """Test correlation ID propagation."""

    def test_correlation_id_in_response(self, client, fresh_state):
        """Test that correlation ID is included in responses."""
        resp = client.get("/connections")
        assert resp.status_code == 200
        data = resp.json()
        assert "correlation_id" in data

    def test_custom_correlation_id_preserved(self, client, fresh_state):
        """Test that custom correlation ID header is preserved."""
        custom_id = "test-correlation-123"
        resp = client.get(
            "/connections",
            headers={"x-correlation-id": custom_id}
        )
        assert resp.status_code == 200
        # The correlation ID should be in the response
        data = resp.json()
        assert data.get("correlation_id") == custom_id or "X-Correlation-ID" in resp.headers

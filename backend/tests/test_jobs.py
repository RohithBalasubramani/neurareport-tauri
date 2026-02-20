from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

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

from .. import api  # noqa: E402
from ..app.repositories.connections import db_connection as db_conn_module  # noqa: E402
from ..app.repositories.state import store as state_store_module  # noqa: E402


@pytest.fixture
def fresh_state(tmp_path, monkeypatch):
    # Clear NEURA_STATE_DIR to prevent .env override
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    base_dir = tmp_path / "state"
    store = state_store_module.StateStore(base_dir=base_dir)
    state_store_module.set_state_store(store)
    api.state_store = store
    db_conn_module.state_store = store
    api.SCHEDULER_DISABLED = True
    api.SCHEDULER = None

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
    return TestClient(api.app)


def _seed_template(store, template_id="tpl-job", name="Job Template", kind="pdf"):
    store.upsert_template(template_id, name=name, status="approved", template_type=kind)


def test_job_creation_and_retrieval(client: TestClient, fresh_state, monkeypatch):
    _seed_template(fresh_state, template_id="tpl-create")

    scheduled_ids: list[str] = []

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        scheduled_ids.append(job_id)

    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payload = {
        "template_id": "tpl-create",
        "start_date": "2024-01-01 00:00:00",
        "end_date": "2024-01-31 23:59:59",
    }
    resp = client.post("/jobs/run-report", json=payload)
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]
    assert job_id
    assert job_id in scheduled_ids

    detail = client.get(f"/jobs/{job_id}")
    assert detail.status_code == 200
    job = detail.json()["job"]
    assert job["status"] in {"queued", "running"}
    assert job["createdAt"] is not None
    assert isinstance(job["steps"], list)

    active_resp = client.get("/jobs", params={"active_only": "true"})
    assert active_resp.status_code == 200
    active_ids = [item["id"] for item in active_resp.json()["jobs"]]
    assert job_id in active_ids


def test_job_run_success_records_steps(client: TestClient, fresh_state, monkeypatch):
    _seed_template(fresh_state, template_id="tpl-success")

    def fake_run_report_with_email(payload, *, kind, correlation_id=None, job_tracker=None):
        if job_tracker:
            job_tracker.step_running("dataLoad", label="Load DB")
            job_tracker.step_succeeded("dataLoad", progress=25)
            job_tracker.step_running("renderPdf", label="Render PDF artifacts")
            job_tracker.step_succeeded("renderPdf", progress=80)
        return {"ok": True, "template_id": payload.template_id}

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        api._run_report_job_sync(job_id, payload_data, kind, correlation_id, step_progress)

    monkeypatch.setattr(api, "_run_report_with_email", fake_run_report_with_email)
    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payload = {
        "template_id": "tpl-success",
        "start_date": "2024-02-01 00:00:00",
        "end_date": "2024-02-15 23:59:59",
    }
    resp = client.post("/jobs/run-report", json=payload)
    job_id = resp.json()["job_id"]

    job = client.get(f"/jobs/{job_id}").json()["job"]
    assert job["status"] == "succeeded"
    assert job["progress"] == 100
    step_names = {step["name"]: step["status"] for step in job["steps"]}
    assert step_names.get("dataLoad") == "succeeded"
    assert step_names.get("renderPdf") == "succeeded"


def test_job_run_failure_captures_error(client: TestClient, fresh_state, monkeypatch):
    _seed_template(fresh_state, template_id="tpl-fail")

    def fake_run_report_with_email(payload, *, kind, correlation_id=None, job_tracker=None):
        if job_tracker:
            job_tracker.step_running("dataLoad", label="Load DB")
            job_tracker.step_failed("dataLoad", "Database unreachable")
        raise HTTPException(status_code=400, detail={"message": "Simulated failure"})

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        api._run_report_job_sync(job_id, payload_data, kind, correlation_id, step_progress)

    monkeypatch.setattr(api, "_run_report_with_email", fake_run_report_with_email)
    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payload = {
        "template_id": "tpl-fail",
        "start_date": "2024-03-01 00:00:00",
        "end_date": "2024-03-05 23:59:59",
    }
    resp = client.post("/jobs/run-report", json=payload)
    job_id = resp.json()["job_id"]

    job = client.get(f"/jobs/{job_id}").json()["job"]
    # With retry logic, first failure results in pending_retry (if retriable)
    # or failed (if permanent error or max_retries=0)
    assert job["status"] in ("failed", "pending_retry")
    # Error should be captured regardless of final status
    assert "Simulated failure" in (job["error"] or "") or "Simulated failure" in (job.get("failureReason") or "")
    step_names = {step["name"]: step["status"] for step in job["steps"]}
    assert step_names.get("dataLoad") == "failed"


def test_job_listing_filters_respect_status_and_type(client: TestClient, fresh_state):
    queued = fresh_state.create_job(
        job_type="run_report",
        template_id="tpl-queued",
        template_name="Queued Template",
        template_kind="pdf",
    )
    running = fresh_state.create_job(
        job_type="run_report",
        template_id="tpl-running",
        template_name="Running Template",
        template_kind="pdf",
    )
    fresh_state.record_job_start(running["id"])
    succeeded = fresh_state.create_job(
        job_type="run_report",
        template_id="tpl-done",
        template_name="Done Template",
        template_kind="pdf",
    )
    fresh_state.record_job_start(succeeded["id"])
    fresh_state.record_job_completion(succeeded["id"], status="succeeded", result={"ok": True})
    verify_job = fresh_state.create_job(
        job_type="verify",
        template_id="tpl-verify",
        template_name="Verify Template",
        template_kind="pdf",
    )
    fresh_state.record_job_completion(verify_job["id"], status="failed", error="verify failed")

    running_only = client.get("/jobs", params={"status": "running"}).json()["jobs"]
    assert {job["id"] for job in running_only} == {running["id"]}

    type_filtered = client.get("/jobs", params={"type": "verify"}).json()["jobs"]
    assert {job["id"] for job in type_filtered} == {verify_job["id"]}

    limited = client.get("/jobs", params={"limit": 1}).json()["jobs"]
    assert len(limited) == 1

    active_only = client.get("/jobs", params={"active_only": "true"}).json()["jobs"]
    assert {job["id"] for job in active_only} == {queued["id"], running["id"]}


def test_batch_job_creation_and_active_listing(client: TestClient, fresh_state, monkeypatch):
    _seed_template(fresh_state, template_id="tpl-batch-1", name="Batch 1")
    _seed_template(fresh_state, template_id="tpl-batch-2", name="Batch 2")

    scheduled: list[dict] = []

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        scheduled.append(
            {
                "job_id": job_id,
                "payload": payload_data,
                "correlation_id": correlation_id,
                "kind": kind,
                "step_progress": step_progress,
            }
        )

    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payloads = [
        {"template_id": "tpl-batch-1", "start_date": "2024-04-01 00:00:00", "end_date": "2024-04-02 00:00:00"},
        {"template_id": "tpl-batch-2", "start_date": "2024-04-03 00:00:00", "end_date": "2024-04-04 00:00:00"},
    ]
    resp = client.post("/jobs/run-report", json=payloads)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["job_ids"]) == {entry["job_id"] for entry in scheduled}
    assert data["job_id"] == data["job_ids"][0]
    assert data["count"] == 2

    active_jobs = client.get("/jobs", params={"active_only": "true"}).json()["jobs"]
    active_ids = {job["id"] for job in active_jobs}
    for entry in scheduled:
        assert entry["job_id"] in active_ids
        job = fresh_state.get_job(entry["job_id"])
        assert job["templateId"] in {"tpl-batch-1", "tpl-batch-2"}
        assert len(job["steps"]) > 0
        assert job["status"] in {"queued", "running"}


def test_batch_jobs_record_steps_per_template(client: TestClient, fresh_state, monkeypatch):
    _seed_template(fresh_state, template_id="tpl-batch-a", name="Batch A")
    _seed_template(fresh_state, template_id="tpl-batch-b", name="Batch B")

    def fake_run_report_with_email(payload, *, kind, correlation_id=None, job_tracker=None):
        if job_tracker:
            job_tracker.step_running("dataLoad", label=f"Load DB for {payload.template_id}")
        if payload.template_id.endswith("a"):
            if job_tracker:
                job_tracker.step_succeeded("dataLoad", progress=20)
                job_tracker.step_running("renderPdf", label="Render PDF artifacts")
                job_tracker.step_succeeded("renderPdf", progress=90)
            return {"ok": True, "template_id": payload.template_id}
        if job_tracker:
            job_tracker.step_failed("dataLoad", f"DB missing for {payload.template_id}")
        raise HTTPException(status_code=400, detail={"message": f"DB missing {payload.template_id}"})

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        api._run_report_job_sync(job_id, payload_data, kind, correlation_id, step_progress)

    monkeypatch.setattr(api, "_run_report_with_email", fake_run_report_with_email)
    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payloads = [
        {"template_id": "tpl-batch-a", "start_date": "2024-05-01 00:00:00", "end_date": "2024-05-02 00:00:00"},
        {"template_id": "tpl-batch-b", "start_date": "2024-05-03 00:00:00", "end_date": "2024-05-04 00:00:00"},
    ]
    resp = client.post("/jobs/run-report", json=payloads)
    assert resp.status_code == 200
    job_ids = resp.json()["job_ids"]
    assert len(job_ids) == 2

    jobs = {fresh_state.get_job(job_id)["templateId"]: fresh_state.get_job(job_id) for job_id in job_ids}
    success_job = jobs["tpl-batch-a"]
    failure_job = jobs["tpl-batch-b"]

    assert success_job["status"] == "succeeded"
    success_steps = {step["name"]: step for step in success_job["steps"]}
    assert success_steps["dataLoad"]["status"] == "succeeded"
    assert success_steps["renderPdf"]["status"] == "succeeded"
    assert success_job["progress"] == 100

    # With retry logic, first failure results in pending_retry (if retriable)
    assert failure_job["status"] in ("failed", "pending_retry")
    failure_steps = {step["name"]: step for step in failure_job["steps"]}
    assert failure_steps["dataLoad"]["status"] == "failed"
    assert "DB missing" in (failure_job["error"] or "") or "DB missing" in (failure_job.get("failureReason") or "")


def test_cancel_job_force_invokes_force_cancel(monkeypatch, client: TestClient, fresh_state):
    _seed_template(fresh_state, template_id="tpl-cancel")
    job = fresh_state.create_job(job_type="run_report", template_id="tpl-cancel", template_name="Cancelable")
    called = {}

    class _FakeReportService:
        @staticmethod
        def force_cancel_job(job_id, *, force=False):
            called["job_id"] = job_id
            called["force"] = force
            return True

    api.report_service = _FakeReportService()

    resp = client.post(f"/jobs/{job['id']}/cancel", params={"force": "true"})
    assert resp.status_code == 200
    assert called == {"job_id": job["id"], "force": True}
    assert fresh_state.get_job(job["id"])["status"] == "cancelled"


def test_cancel_job_route_marks_cancelled_without_force(monkeypatch, client: TestClient, fresh_state):
    _seed_template(fresh_state, template_id="tpl-cancel-soft")
    job = fresh_state.create_job(job_type="run_report", template_id="tpl-cancel-soft", template_name="Cancelable")
    called = {}

    class _FakeReportService:
        @staticmethod
        def force_cancel_job(job_id, *, force=False):
            called["job_id"] = job_id
            called["force"] = force
            return True

    api.report_service = _FakeReportService()

    resp = client.post(f"/jobs/{job['id']}/cancel")
    assert resp.status_code == 200
    assert called == {"job_id": job["id"], "force": False}
    job_record = fresh_state.get_job(job["id"])
    assert job_record["status"] == "cancelled"
    assert (job_record.get("error") or "").lower().startswith("cancelled")


def test_report_scheduler_creates_job_for_schedule(monkeypatch, fresh_state, tmp_path):
    from backend.app.services.jobs import report_scheduler as scheduler_module

    scheduler_module.state_store = fresh_state
    _seed_template(fresh_state, template_id="tpl-schedule", name="Scheduled Template")
    fresh_state.upsert_connection(
        conn_id="conn-1",
        name="Connection 1",
        db_type="sqlite",
        database_path=str(tmp_path / "db.sqlite"),
        secret_payload={"token": "secret"},
    )
    schedule = fresh_state.create_schedule(
        name="Nightly run",
        template_id="tpl-schedule",
        template_name="Scheduled Template",
        template_kind="pdf",
        connection_id="conn-1",
        connection_name="Connection 1",
        start_date="2024-01-01 00:00:00",
        end_date="2024-01-02 00:00:00",
        key_values=None,
        batch_ids=None,
        docx=True,
        xlsx=False,
        email_recipients=[],
        email_subject=None,
        email_message=None,
        frequency="daily",
        interval_minutes=60,
        next_run_at="2024-01-01T00:00:00Z",
        first_run_at="2024-01-01T00:00:00Z",
        active=True,
    )

    recorded: list[dict] = []

    def runner(payload, kind, job_tracker=None):
        recorded.append({"payload": payload, "kind": kind, "job_id": getattr(job_tracker, "job_id", None)})
        return {"html_url": "/reports/r.html"}

    scheduler = scheduler_module.ReportScheduler(runner, poll_seconds=1)
    asyncio.run(scheduler._run_schedule(schedule))

    jobs = fresh_state.list_jobs(limit=5)
    assert len(jobs) == 1
    job = jobs[0]
    assert job["scheduleId"] == schedule["id"]
    assert job["status"] == "succeeded"
    assert recorded and recorded[0]["job_id"] == job["id"]


def test_job_retry_flow_allows_second_success(monkeypatch, client: TestClient, fresh_state):
    _seed_template(fresh_state, template_id="tpl-retry", name="Retry Template")

    attempts: list[str] = []

    def fake_run_report_with_email(payload, *, kind, correlation_id=None, job_tracker=None):
        attempts.append(payload.template_id)
        if len(attempts) == 1:
            if job_tracker:
                job_tracker.step_failed("renderPdf", "boom")
            raise HTTPException(status_code=500, detail={"message": "boom"})
        if job_tracker:
            job_tracker.step_succeeded("dataLoad")
            job_tracker.step_succeeded("renderPdf")
        return {"ok": True}

    def immediate_schedule(job_id, payload_data, kind, correlation_id, step_progress):
        api._run_report_job_sync(job_id, payload_data, kind, correlation_id, step_progress)

    monkeypatch.setattr(api, "_run_report_with_email", fake_run_report_with_email)
    monkeypatch.setattr(api, "_schedule_report_job", immediate_schedule)

    payload = {
        "template_id": "tpl-retry",
        "start_date": "2024-06-01 00:00:00",
        "end_date": "2024-06-02 00:00:00",
    }

    first_resp = client.post("/jobs/run-report", json=payload)
    first_job_id = first_resp.json()["job_id"]
    first_job = fresh_state.get_job(first_job_id)
    # With retry logic, first failure results in pending_retry (for retriable errors)
    assert first_job["status"] in ("failed", "pending_retry")
    assert attempts == ["tpl-retry"]

    second_resp = client.post("/jobs/run-report", json=payload)
    second_job_id = second_resp.json()["job_id"]
    second_job = fresh_state.get_job(second_job_id)
    assert second_job["status"] == "succeeded"
    assert attempts == ["tpl-retry", "tpl-retry"]

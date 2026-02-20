from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import api
from backend.app.repositories.state import StateStore


def _write_final_html(root: Path, template_id: str, html: str) -> Path:
    tdir = root / template_id
    tdir.mkdir(parents=True, exist_ok=True)
    (tdir / "report_final.html").write_text(html, encoding="utf-8")
    return tdir


def _register_template(store: StateStore, template_id: str) -> None:
    store.upsert_template(template_id, name=f"Template {template_id}", status="approved")


def _intent_headers(intent_type: str = "update") -> dict[str, str]:
    return {
        "X-Intent-Id": uuid.uuid4().hex,
        "X-Intent-Type": intent_type,
        "Idempotency-Key": uuid.uuid4().hex,
    }

@pytest.fixture
def edit_env(tmp_path, monkeypatch):
    uploads_root = tmp_path / "uploads"
    uploads_root.mkdir(parents=True, exist_ok=True)
    excel_root = tmp_path / "excel-uploads"
    excel_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(api, "UPLOAD_ROOT", uploads_root)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", uploads_root.resolve())
    monkeypatch.setattr(api, "EXCEL_UPLOAD_ROOT", excel_root)
    monkeypatch.setattr(api, "EXCEL_UPLOAD_ROOT_BASE", excel_root.resolve())
    monkeypatch.setitem(api._UPLOAD_KIND_BASES, "pdf", (uploads_root.resolve(), "/uploads"))
    monkeypatch.setitem(api._UPLOAD_KIND_BASES, "excel", (excel_root.resolve(), "/excel-uploads"))
    monkeypatch.setattr("backend.legacy.core.config.UPLOAD_ROOT", uploads_root)
    monkeypatch.setattr("backend.legacy.core.config.EXCEL_UPLOAD_ROOT", excel_root)

    store = StateStore(tmp_path / "state")
    monkeypatch.setattr(api, "state_store", store, raising=False)
    monkeypatch.setattr("backend.app.repositories.state.state_store", store)
    monkeypatch.setattr("backend.app.repositories.state.store.state_store", store)
    monkeypatch.setattr("backend.legacy.services.file_service.helpers.state_store", store)

    client = TestClient(api.app)
    return {"client": client, "uploads_root": uploads_root, "state_store": store}


def test_manual_edit_snapshots_and_diff(edit_env):
    client: TestClient = edit_env["client"]
    uploads_root: Path = edit_env["uploads_root"]
    state_store: StateStore = edit_env["state_store"]
    template_id = "tpl-manual"
    _register_template(state_store, template_id)
    tdir = _write_final_html(uploads_root, template_id, "<html>old</html>")

    response = client.post(
        f"/templates/{template_id}/edit-manual",
        json={"html": "<html>new</html>"},
        headers=_intent_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["diff_summary"] == "+1 line, -1 line"
    assert data["metadata"]["historyCount"] == 1
    assert (tdir / "report_final_prev.html").read_text(encoding="utf-8") == "<html>old</html>"
    assert (tdir / "report_final.html").read_text(encoding="utf-8") == "<html>new</html>"


def test_ai_edit_records_diff_and_prev_copy(edit_env, monkeypatch):
    client: TestClient = edit_env["client"]
    uploads_root: Path = edit_env["uploads_root"]
    state_store: StateStore = edit_env["state_store"]
    template_id = "tpl-ai"
    _register_template(state_store, template_id)
    tdir = _write_final_html(uploads_root, template_id, "<html>start</html>")

    def fake_llm(html: str, instructions: str):
        return "<html>ai</html>", [f"applied:{instructions}"]

    monkeypatch.setattr("backend.legacy.services.file_service.edit._run_template_edit_llm", fake_llm)

    response = client.post(
        f"/templates/{template_id}/edit-ai",
        json={"instructions": "make it better"},
        headers=_intent_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["diff_summary"] == "+1 line, -1 line"
    assert data["summary"] == ["applied:make it better"]
    assert (tdir / "report_final_prev.html").read_text(encoding="utf-8") == "<html>start</html>"
    assert (tdir / "report_final.html").read_text(encoding="utf-8") == "<html>ai</html>"


def test_undo_swaps_versions_and_reports_diff(edit_env):
    client: TestClient = edit_env["client"]
    uploads_root: Path = edit_env["uploads_root"]
    state_store: StateStore = edit_env["state_store"]
    template_id = "tpl-undo"
    _register_template(state_store, template_id)
    tdir = _write_final_html(uploads_root, template_id, "<html>current</html>")
    (tdir / "report_final_prev.html").write_text("<html>previous</html>", encoding="utf-8")

    response = client.post(
        f"/templates/{template_id}/undo-last-edit",
        headers=_intent_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["metadata"]["lastEditType"] == "undo"
    assert data["diff_summary"] == "+1 line, -1 line"
    assert (tdir / "report_final.html").read_text(encoding="utf-8") == "<html>previous</html>"
    assert (tdir / "report_final_prev.html").read_text(encoding="utf-8") == "<html>current</html>"


def test_template_history_is_capped_at_two_entries(edit_env):
    client: TestClient = edit_env["client"]
    uploads_root: Path = edit_env["uploads_root"]
    state_store: StateStore = edit_env["state_store"]
    template_id = "tpl-history"
    _register_template(state_store, template_id)
    tdir = _write_final_html(uploads_root, template_id, "<html>v0</html>")

    timestamps: list[str | None] = []
    for idx in range(3):
        html = f"<html>v{idx + 1}</html>"
        response = client.post(
            f"/templates/{template_id}/edit-manual",
            json={"html": html},
            headers=_intent_headers(),
        )
        assert response.status_code == 200, response.text
        timestamps.append(response.json()["metadata"]["lastEditAt"])

    history_path = tdir / "template_history.json"
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert len(history) == 2
    assert history[0].get("timestamp") == timestamps[1]
    assert history[1].get("timestamp") == timestamps[2]

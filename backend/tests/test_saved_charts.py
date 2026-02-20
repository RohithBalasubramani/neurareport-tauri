from __future__ import annotations

import sys
import types
import uuid
from pathlib import Path

import pytest
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


def _create_template(store, template_id: str) -> dict:
    return store.upsert_template(
        template_id,
        name="Saved Chart Template",
        status="approved",
        artifacts={},
        connection_id=None,
    )


def _sample_spec():
    return {
        "type": "bar",
        "xField": "batch_index",
        "yFields": ["rows"],
        "chartTemplateId": "time_series_basic",
        "title": "Rows Trend",
        "description": "Rows over time",
    }


def test_saved_charts_crud_flow(client: TestClient, fresh_state):
    template_id = str(uuid.uuid4())
    _create_template(fresh_state, template_id)

    list_resp = client.get(f"/templates/{template_id}/charts/saved")
    assert list_resp.status_code == 200
    assert list_resp.json()["charts"] == []

    create_resp = client.post(
        f"/templates/{template_id}/charts/saved",
        json={
            "template_id": template_id,
            "name": "My chart",
            "spec": _sample_spec(),
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    chart_id = created["id"]
    assert created["name"] == "My chart"
    assert created["spec"]["type"] == "bar"

    list_resp = client.get(f"/templates/{template_id}/charts/saved")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["charts"]) == 1

    update_resp = client.put(
        f"/templates/{template_id}/charts/saved/{chart_id}",
        json={"name": "Updated name"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated name"

    delete_resp = client.delete(f"/templates/{template_id}/charts/saved/{chart_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "ok"

    list_resp = client.get(f"/templates/{template_id}/charts/saved")
    assert list_resp.status_code == 200
    assert list_resp.json()["charts"] == []


def test_saved_chart_validation_errors(client: TestClient, fresh_state):
    template_id = str(uuid.uuid4())
    other_id = str(uuid.uuid4())
    _create_template(fresh_state, template_id)

    resp = client.post(
        f"/templates/{template_id}/charts/saved",
        json={"template_id": other_id, "name": "Mismatch", "spec": _sample_spec()},
    )
    assert resp.status_code == 400

    resp = client.post(
        f"/templates/{other_id}/charts/saved",
        json={"template_id": other_id, "name": "Missing template", "spec": _sample_spec()},
    )
    assert resp.status_code == 404

    resp = client.put(
        f"/templates/{template_id}/charts/saved/not-found",
        json={"name": "New name"},
    )
    assert resp.status_code == 404

    resp = client.delete(f"/templates/{template_id}/charts/saved/not-found")
    assert resp.status_code == 404

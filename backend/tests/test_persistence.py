from __future__ import annotations

import sqlite3
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
from backend.legacy.services.report_service import _extract_excel_print_scale_from_html


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


def test_bootstrap_returns_persistent_state(client: TestClient, fresh_state, tmp_path):
    db_path = tmp_path / "dummy.db"
    sqlite3.connect(db_path).close()
    conn = fresh_state.upsert_connection(
        conn_id=None,
        name="sqlite@test.db",
        db_type="sqlite",
        database_path=str(db_path),
        secret_payload={"db_url": f"sqlite:///{db_path}"},
        status="connected",
        latency_ms=12.5,
    )
    fresh_state.record_connection_ping(conn["id"], status="connected", detail="OK", latency_ms=12.5)

    tpl = fresh_state.upsert_template(
        "tpl-1",
        name="Sample Template",
        status="approved",
        artifacts={"template_html_url": "/uploads/tpl-1/template.html"},
        connection_id=conn["id"],
    )
    fresh_state.set_last_used(conn["id"], tpl["id"])

    resp = client.get("/state/bootstrap")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert payload["connections"][0]["id"] == conn["id"]
    assert payload["connections"][0]["summary"] == db_path.name
    assert payload["connections"][0]["hasCredentials"] is True
    assert payload["templates"][0]["id"] == tpl["id"]
    assert payload["last_used"]["connection_id"] == conn["id"]
    assert payload["last_used"]["template_id"] == tpl["id"]


def test_last_used_endpoint_updates_store(client: TestClient, fresh_state):
    resp = client.post("/state/last-used", json={"connection_id": "conn-1", "template_id": "tpl-9"})
    assert resp.status_code == 200
    data = resp.json()["last_used"]
    assert data["connection_id"] == "conn-1"
    assert data["template_id"] == "tpl-9"
    store_state = fresh_state.get_last_used()
    assert store_state["connection_id"] == "conn-1"
    assert store_state["template_id"] == "tpl-9"


def test_delete_template_removes_state_and_files(client: TestClient, fresh_state):
    template_id = str(uuid.uuid4())
    fresh_state.upsert_template(
        template_id,
        name="To remove",
        status="approved",
        artifacts={"template_html_url": f"/uploads/{template_id}/template.html"},
    )
    fresh_state.set_last_used(None, template_id)

    template_dir = api.UPLOAD_ROOT / template_id
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "template.html").write_text("<html/>", encoding="utf-8")

    resp = client.delete(f"/templates/{template_id}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert payload["template_id"] == template_id
    assert not template_dir.exists()
    assert fresh_state.get_template_record(template_id) is None
    assert fresh_state.get_last_used()["template_id"] is None


def test_delete_template_missing_returns_404(client: TestClient):
    template_id = str(uuid.uuid4())
    resp = client.delete(f"/templates/{template_id}")
    assert resp.status_code == 404
    payload = resp.json()
    assert payload["status"] == "error"
    assert payload["code"] == "template_not_found"


def test_reports_run_uses_persisted_connection(client: TestClient, fresh_state, tmp_path, monkeypatch):
    # Prepare sqlite database
    db_path = tmp_path / "data.db"
    sqlite3.connect(db_path).close()

    conn = fresh_state.upsert_connection(
        conn_id=None,
        name="sqlite@data.db",
        db_type="sqlite",
        database_path=str(db_path),
        secret_payload={"db_url": f"sqlite:///{db_path}"},
        status="connected",
        latency_ms=4.2,
    )
    fresh_state.record_connection_ping(conn["id"], status="connected", detail="OK", latency_ms=4.2)

    template_id = "11111111-1111-1111-1111-111111111111"
    template_dir = api.UPLOAD_ROOT / template_id
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "report_final.html").write_text("<html></html>", encoding="utf-8")
    (template_dir / "contract.json").write_text("{}", encoding="utf-8")

    fresh_state.upsert_template(template_id, name="Run Template", status="approved")

    monkeypatch.setattr(api, "validate_contract_schema", lambda _: None)

    from backend.app.services.reports import ReportGenerate as report_generate

    def fake_fill_and_print(**kwargs):
        kwargs["OUT_HTML"].write_text(
            '<html><head><style id="excel-print-sizing">:root { --excel-print-scale: 0.67; }</style></head>'
            "<body>filled</body></html>",
            encoding="utf-8",
        )
        kwargs["OUT_PDF"].write_bytes(b"%PDF-1.4\n%fake\n")

    monkeypatch.setattr(report_generate, "fill_and_print", fake_fill_and_print)

    def fake_html_to_docx(html_path, output_path, **kwargs):
        output_path.write_bytes(b"DOCX")
        return output_path

    def fake_html_to_xlsx(html_path, output_path, **kwargs):
        output_path.write_bytes(b"XLSX")
        return output_path

    monkeypatch.setattr(api, "html_file_to_docx", fake_html_to_docx)
    monkeypatch.setattr(api, "html_file_to_xlsx", fake_html_to_xlsx)

    payload = {
        "template_id": template_id,
        "connection_id": conn["id"],
        "start_date": "2024-01-01 00:00:00",
        "end_date": "2024-01-31 23:59:59",
        "docx": True,
        "xlsx": True,
    }
    resp = client.post("/reports/run", json=payload)
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    assert data["ok"] is True
    assert Path(api.UPLOAD_ROOT / template_id / Path(data["html_url"]).name).exists()
    assert Path(api.UPLOAD_ROOT / template_id / Path(data["pdf_url"]).name).exists()
    assert data["docx_url"] is not None
    assert Path(api.UPLOAD_ROOT / template_id / Path(data["docx_url"]).name).exists()
    assert data["xlsx_url"] is not None
    assert Path(api.UPLOAD_ROOT / template_id / Path(data["xlsx_url"]).name).exists()


def test_extract_excel_print_scale_from_html(tmp_path):
    html_path = tmp_path / "excel.html"
    html_path.write_text(
        '<html><head><style id="excel-print-sizing">:root { --excel-print-scale: 0.63; }</style></head><body></body></html>',
        encoding="utf-8",
    )
    value = _extract_excel_print_scale_from_html(html_path)
    assert value == pytest.approx(0.63, rel=1e-2)


def test_verify_sqlite_materializes_dataframe(tmp_path):
    db_path = tmp_path / "verify.db"
    with sqlite3.connect(db_path) as con:
        con.execute("CREATE TABLE sample (value TEXT)")
        con.execute("INSERT INTO sample (value) VALUES (?)", ("ok",))

    # Should not raise once the SQLite file can be loaded into pandas frames.
    db_conn_module.verify_sqlite(db_path)


def test_verify_sqlite_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        db_conn_module.verify_sqlite(tmp_path / "missing.db")

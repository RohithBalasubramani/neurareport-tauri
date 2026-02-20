from __future__ import annotations

import pytest

from backend.app.utils.errors import AppError
from backend.app.schemas.connections import ConnectionTestRequest, ConnectionUpsertRequest
from backend.app.services.connections.service import ConnectionService


class _FakeRepo:
    def __init__(self):
        self.saved = {}
        self.deleted = set()
        self.pings = []

    def resolve_path(self, *, connection_id, db_url, db_path):
        if db_url == "bad":
            raise RuntimeError("boom")
        return "db.sqlite"

    def verify(self, path):
        return None

    def save(self, payload):
        self.saved["save"] = payload
        return "conn-1"

    def upsert(self, **kwargs):
        self.saved["upsert"] = kwargs
        return {
            "id": kwargs.get("conn_id") or "conn-upsert",
            "name": kwargs.get("name") or "n",
            "db_type": kwargs.get("db_type") or "sqlite",
            "database_path": kwargs.get("database_path") or "",
            "status": kwargs.get("status") or "connected",
            "latency_ms": kwargs.get("latency_ms"),
        }

    def list(self):
        return []

    def delete(self, connection_id: str):
        if connection_id == "missing":
            return False
        self.deleted.add(connection_id)
        return True

    def record_ping(self, connection_id, status, detail, latency_ms):
        self.pings.append((connection_id, status, detail, latency_ms))


def test_connection_test_records_ping():
    repo = _FakeRepo()
    svc = ConnectionService(repo)
    payload = ConnectionTestRequest(db_url="sqlite:///tmp.db")
    result = svc.test(payload, correlation_id="cid-1")
    assert result["ok"] is True
    assert result["connection_id"] == "conn-1"
    assert repo.pings[-1][0] == "conn-1"


def test_connection_upsert_success():
    repo = _FakeRepo()
    svc = ConnectionService(repo)
    payload = ConnectionUpsertRequest(id="abc", database="file.db", name="Friendly")
    out = svc.upsert(payload)
    assert out.id == "abc"
    assert out.name == "Friendly"
    assert repo.saved["upsert"]["database_path"]


def test_connection_delete_missing_raises():
    repo = _FakeRepo()
    svc = ConnectionService(repo)
    with pytest.raises(AppError) as exc:
        svc.delete("missing")
    assert exc.value.code == "connection_not_found"


def test_connection_invalid_db_raises():
    repo = _FakeRepo()
    svc = ConnectionService(repo)
    payload = ConnectionTestRequest(db_url="bad")
    with pytest.raises(AppError) as exc:
        svc.test(payload)
    assert exc.value.code == "invalid_database"


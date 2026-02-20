"""
Connector API Route Tests.

Comprehensive tests for connector CRUD endpoints, StateStore persistence helpers,
connection health, query execution, OAuth, and edge cases.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.connectors import (
    _store_delete,
    _store_get,
    _store_get_all,
    _store_get_config,
    _store_put,
    router,
)
from backend.app.services.security import require_api_key


# =============================================================================
# FIXTURES
# =============================================================================


def _make_connection(
    *,
    connection_id: str | None = None,
    name: str = "test-conn",
    connector_type: str = "postgresql",
    config: dict[str, Any] | None = None,
    status: str = "connected",
    created_at: str = "2025-06-01T00:00:00",
    last_used: str | None = None,
    latency_ms: float | None = 5.0,
) -> dict[str, Any]:
    """Helper to build a connection dict."""
    return {
        "id": connection_id or str(uuid.uuid4()),
        "name": name,
        "connector_type": connector_type,
        "config": config or {"host": "localhost", "port": 5432, "database": "testdb"},
        "status": status,
        "created_at": created_at,
        "last_used": last_used,
        "latency_ms": latency_ms,
    }


def _make_connector_info(
    *,
    cid: str = "postgresql",
    name: str = "PostgreSQL",
    ctype: str = "database",
) -> dict[str, Any]:
    """Helper to build a connector info dict."""
    return {
        "id": cid,
        "name": name,
        "type": ctype,
        "auth_types": ["basic"],
        "capabilities": ["read", "query"],
        "free_tier": True,
        "config_schema": {"type": "object", "properties": {}},
    }


@pytest.fixture
def app():
    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/connectors")
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_connection():
    return _make_connection(connection_id="00000000-aaaa-bbbb-cccc-123456789abc")


@pytest.fixture
def sample_connection_b():
    return _make_connection(
        connection_id="11111111-aaaa-bbbb-cccc-456789abcdef",
        name="second-conn",
        connector_type="mysql",
        created_at="2025-07-01T00:00:00",
    )


@pytest.fixture
def patch_store_get(sample_connection):
    """Patch _store_get to return sample_connection."""
    with patch(
        "backend.app.api.routes.connectors._store_get",
        return_value=sample_connection,
    ) as mock:
        yield mock


@pytest.fixture
def patch_store_get_none():
    """Patch _store_get to return None (missing connection)."""
    with patch(
        "backend.app.api.routes.connectors._store_get",
        return_value=None,
    ) as mock:
        yield mock


@pytest.fixture
def patch_store_put():
    with patch("backend.app.api.routes.connectors._store_put") as mock:
        yield mock


@pytest.fixture
def patch_store_delete_true():
    with patch(
        "backend.app.api.routes.connectors._store_delete",
        return_value=True,
    ) as mock:
        yield mock


@pytest.fixture
def patch_store_delete_false():
    with patch(
        "backend.app.api.routes.connectors._store_delete",
        return_value=False,
    ) as mock:
        yield mock


def _mock_state_store(state: dict):
    """Build a MagicMock that behaves like the state_store singleton.

    Supports both 'connectors' and 'connector_credentials' namespaces.
    """
    store = MagicMock()
    store.read_state.return_value = state

    @contextmanager
    def _transaction():
        yield state

    store.transaction = _transaction
    return store


# =============================================================================
# STATE-STORE HELPER UNIT TESTS
# =============================================================================


class TestStoreGetAll:
    """Unit tests for _store_get_all()."""

    def test_returns_empty_dict_when_no_connectors(self):
        mock_store = _mock_state_store({})
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_all()
        assert result == {}

    def test_returns_all_connectors(self):
        conn_a = _make_connection(connection_id="a")
        conn_b = _make_connection(connection_id="b")
        # Simulate storage: connections stored without config
        safe_a = {k: v for k, v in conn_a.items() if k != "config"}
        safe_a["has_credentials"] = True
        safe_b = {k: v for k, v in conn_b.items() if k != "config"}
        safe_b["has_credentials"] = True
        state = {"connectors": {"a": safe_a, "b": safe_b}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_all()
        assert len(result) == 2
        assert "a" in result
        assert "b" in result

    def test_returns_copy_not_reference(self):
        conn = _make_connection(connection_id="x")
        safe = {k: v for k, v in conn.items() if k != "config"}
        safe["has_credentials"] = True
        state = {"connectors": {"x": safe}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_all()
        # dict() produces a shallow copy, so the dict object should differ
        assert result is not state["connectors"]

    def test_ignores_other_namespaces(self):
        conn = _make_connection(connection_id="a")
        safe = {k: v for k, v in conn.items() if k != "config"}
        safe["has_credentials"] = True
        state = {
            "connectors": {"a": safe},
            "connector_credentials": {"a": {"password": "secret"}},
            "templates": {"tpl-1": {}},
        }
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_all()
        assert list(result.keys()) == ["a"]


class TestStoreGet:
    """Unit tests for _store_get()."""

    def test_returns_connection_by_id(self):
        conn = _make_connection(connection_id="c1")
        state = {"connectors": {"c1": conn}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get("c1")
        assert result is conn

    def test_returns_none_for_missing_id(self):
        state = {"connectors": {}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get("nonexistent")
        assert result is None

    def test_returns_none_when_connectors_namespace_missing(self):
        mock_store = _mock_state_store({})
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get("44444444-aaaa-bbbb-cccc-000000000000")
        assert result is None

    def test_returns_correct_connection_among_many(self):
        conn_a = _make_connection(connection_id="a", name="Alpha")
        conn_b = _make_connection(connection_id="b", name="Beta")
        state = {"connectors": {"a": conn_a, "b": conn_b}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get("b")
        assert result["name"] == "Beta"


class TestStorePut:
    """Unit tests for _store_put()."""

    def test_stores_connection_without_config_in_connectors_namespace(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        conn = _make_connection(connection_id="new-1")
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(conn)
        assert "new-1" in state["connectors"]
        # Verify config is stripped from the connection record
        assert "config" not in state["connectors"]["new-1"]
        # Verify has_credentials flag is set
        assert state["connectors"]["new-1"]["has_credentials"] is True

    def test_stores_config_in_credentials_namespace(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        conn = _make_connection(
            connection_id="new-2",
            config={"host": "db.example.com", "password": "s3cret"},
        )
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(conn)
        assert "new-2" in state["connector_credentials"]
        assert state["connector_credentials"]["new-2"] == conn["config"]

    def test_overwrites_existing_connection(self):
        old = _make_connection(connection_id="upd-1", name="Old Name")
        old_safe = {k: v for k, v in old.items() if k != "config"}
        old_safe["has_credentials"] = True
        state: dict[str, Any] = {
            "connectors": {"upd-1": old_safe},
            "connector_credentials": {"upd-1": old["config"]},
        }
        mock_store = _mock_state_store(state)
        updated = _make_connection(connection_id="upd-1", name="New Name")
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(updated)
        assert state["connectors"]["upd-1"]["name"] == "New Name"
        assert "config" not in state["connectors"]["upd-1"]
        assert state["connectors"]["upd-1"]["has_credentials"] is True

    def test_preserves_other_connections(self):
        existing = _make_connection(connection_id="keep")
        existing_safe = {k: v for k, v in existing.items() if k != "config"}
        existing_safe["has_credentials"] = True
        state: dict[str, Any] = {
            "connectors": {"keep": existing_safe},
            "connector_credentials": {"keep": existing["config"]},
        }
        mock_store = _mock_state_store(state)
        new_conn = _make_connection(connection_id="new")
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(new_conn)
        assert "keep" in state["connectors"]
        assert "new" in state["connectors"]

    def test_sets_has_credentials_false_when_no_config_key(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        conn = {"id": "no-cfg", "name": "test"}
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(conn)
        assert "no-cfg" in state["connectors"]
        assert state["connectors"]["no-cfg"]["has_credentials"] is False
        assert "connector_credentials" not in state

    def test_updates_credentials_on_overwrite(self):
        old_cfg = {"host": "old.host"}
        old_conn = _make_connection(connection_id="c1", config=old_cfg)
        old_safe = {k: v for k, v in old_conn.items() if k != "config"}
        old_safe["has_credentials"] = True
        state: dict[str, Any] = {
            "connectors": {"c1": old_safe},
            "connector_credentials": {"c1": old_cfg},
        }
        mock_store = _mock_state_store(state)
        new_cfg = {"host": "new.host"}
        updated = _make_connection(connection_id="c1", config=new_cfg)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(updated)
        assert state["connector_credentials"]["c1"] == new_cfg
        assert state["connectors"]["c1"]["has_credentials"] is True

    def test_stores_multiple_connections_sequentially(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(_make_connection(connection_id="s1"))
            _store_put(_make_connection(connection_id="s2"))
            _store_put(_make_connection(connection_id="s3"))
        assert len(state["connectors"]) == 3
        assert len(state["connector_credentials"]) == 3
        # Verify all connections have config stripped and has_credentials set
        for conn_id in ["s1", "s2", "s3"]:
            assert "config" not in state["connectors"][conn_id]
            assert state["connectors"][conn_id]["has_credentials"] is True


class TestStoreGetConfig:
    """Unit tests for _store_get_config()."""

    def test_returns_config_for_existing_connection(self):
        config = {"host": "db.example.com", "password": "s3cret"}
        state = {"connector_credentials": {"c1": config}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_config("c1")
        assert result == config

    def test_returns_empty_dict_for_missing_connection(self):
        state = {"connector_credentials": {}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_config("nonexistent")
        assert result == {}

    def test_returns_empty_dict_when_namespace_missing(self):
        mock_store = _mock_state_store({})
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_config("44444444-aaaa-bbbb-cccc-000000000000")
        assert result == {}

    def test_returns_correct_config_among_many(self):
        config_a = {"host": "a.example.com"}
        config_b = {"host": "b.example.com", "port": 3306}
        state = {"connector_credentials": {"a": config_a, "b": config_b}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_get_config("b")
        assert result == config_b


class TestStoreDelete:
    """Unit tests for _store_delete()."""

    def test_deletes_existing_connection(self):
        conn = _make_connection(connection_id="del-1")
        state: dict[str, Any] = {
            "connectors": {"del-1": conn},
            "connector_credentials": {"del-1": conn["config"]},
        }
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_delete("del-1")
        assert result is True
        assert "del-1" not in state["connectors"]

    def test_deletes_credentials_alongside_connection(self):
        conn = _make_connection(connection_id="del-2")
        state: dict[str, Any] = {
            "connectors": {"del-2": conn},
            "connector_credentials": {"del-2": conn["config"]},
        }
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_delete("del-2")
        assert "del-2" not in state.get("connector_credentials", {})

    def test_returns_false_for_missing_id(self):
        state: dict[str, Any] = {"connectors": {}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_delete("missing")
        assert result is False

    def test_returns_false_when_namespace_missing(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_delete("missing")
        assert result is False

    def test_preserves_other_connections_on_delete(self):
        keep = _make_connection(connection_id="keep")
        remove = _make_connection(connection_id="remove")
        state: dict[str, Any] = {
            "connectors": {"keep": keep, "remove": remove},
            "connector_credentials": {"keep": keep["config"], "remove": remove["config"]},
        }
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_delete("remove")
        assert "keep" in state["connectors"]
        assert "keep" in state["connector_credentials"]
        assert "remove" not in state["connectors"]

    def test_handles_missing_credentials_namespace_gracefully(self):
        conn = _make_connection(connection_id="no-cred")
        state: dict[str, Any] = {"connectors": {"no-cred": conn}}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            result = _store_delete("no-cred")
        assert result is True
        assert "no-cred" not in state["connectors"]


# =============================================================================
# CONNECTOR DISCOVERY ENDPOINTS
# =============================================================================


class TestListConnectorTypes:
    """Tests for GET /connectors/types."""

    def test_returns_list_of_connectors(self, client):
        infos = [
            _make_connector_info(cid="postgresql", name="PostgreSQL"),
            _make_connector_info(cid="mysql", name="MySQL"),
        ]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["id"] == "postgresql"
        assert data[1]["id"] == "mysql"

    def test_returns_empty_list_when_none_registered(self, client):
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=[],
        ):
            resp = client.get("/connectors/types")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_response_contains_all_fields(self, client):
        info = _make_connector_info()
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=[info],
        ):
            resp = client.get("/connectors/types")
        item = resp.json()[0]
        for key in ("id", "name", "type", "auth_types", "capabilities", "free_tier", "config_schema"):
            assert key in item


class TestGetConnectorType:
    """Tests for GET /connectors/types/{connector_type}."""

    def test_returns_matching_connector(self, client):
        infos = [
            _make_connector_info(cid="postgresql", name="PostgreSQL"),
            _make_connector_info(cid="mysql", name="MySQL"),
        ]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/postgresql")
        assert resp.status_code == 200
        assert resp.json()["id"] == "postgresql"
        assert resp.json()["name"] == "PostgreSQL"

    def test_returns_404_for_unknown_type(self, client):
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=[],
        ):
            resp = client.get("/connectors/types/nonexistent")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_returns_correct_item_among_many(self, client):
        infos = [
            _make_connector_info(cid="a"),
            _make_connector_info(cid="b", name="B Connector"),
            _make_connector_info(cid="c"),
        ]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/b")
        assert resp.status_code == 200
        assert resp.json()["name"] == "B Connector"


class TestListConnectorsByCategory:
    """Tests for GET /connectors/types/by-category/{category}."""

    def test_filters_by_database_category(self, client):
        infos = [
            _make_connector_info(cid="pg", ctype="database"),
            _make_connector_info(cid="s3", ctype="cloud_storage"),
        ]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/by-category/database")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == "pg"

    def test_filters_by_cloud_storage_category(self, client):
        infos = [
            _make_connector_info(cid="pg", ctype="database"),
            _make_connector_info(cid="s3", ctype="cloud_storage"),
            _make_connector_info(cid="gcs", ctype="cloud_storage"),
        ]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/by-category/cloud_storage")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_returns_empty_for_category_with_no_match(self, client):
        infos = [_make_connector_info(cid="pg", ctype="database")]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/by-category/api")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_rejects_invalid_category(self, client):
        resp = client.get("/connectors/types/by-category/invalid_category")
        assert resp.status_code == 422

    def test_accepts_productivity_category(self, client):
        infos = [_make_connector_info(cid="sheets", ctype="productivity")]
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=infos,
        ):
            resp = client.get("/connectors/types/by-category/productivity")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_accepts_api_category(self, client):
        with patch(
            "backend.app.api.routes.connectors.list_available_connectors",
            return_value=[],
        ):
            resp = client.get("/connectors/types/by-category/api")
        assert resp.status_code == 200


# =============================================================================
# TEST CONNECTION ENDPOINT
# =============================================================================


class TestTestConnection:
    """Tests for POST /connectors/{connector_type}/test."""

    def test_successful_test(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True,
            latency_ms=12.5,
            error=None,
            details={"version": "15.1"},
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.post(
                "/connectors/postgresql/test",
                json={
                    "connector_type": "postgresql",
                    "config": {"host": "localhost"},
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["latency_ms"] == 12.5
        assert data["details"]["version"] == "15.1"

    def test_failed_test(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=False,
            latency_ms=None,
            error="Connection refused",
            details=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.post(
                "/connectors/postgresql/test",
                json={
                    "connector_type": "postgresql",
                    "config": {"host": "unreachable"},
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "Connection refused"

    def test_unknown_connector_type_returns_400(self, client):
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            side_effect=ValueError("Unknown connector: foobar"),
        ):
            resp = client.post(
                "/connectors/foobar/test",
                json={
                    "connector_type": "foobar",
                    "config": {},
                },
            )
        assert resp.status_code == 400
        assert "Unknown connector" in resp.json()["detail"]

    def test_generic_exception_returns_failed_response(self, client):
        """When test_connection raises a non-ValueError, the exception handler
        catches it and returns a TestConnectionResponse with success=False
        and a sanitized error message (no internal details leaked)."""
        mock_connector = AsyncMock()
        mock_connector.test_connection.side_effect = RuntimeError("Unexpected error")
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.post(
                "/connectors/postgresql/test",
                json={
                    "connector_type": "postgresql",
                    "config": {"host": "localhost"},
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is False
            assert "RuntimeError" in data["error"]
            # Ensure internal error message is NOT leaked
            assert "Unexpected error" not in data["error"]

    def test_test_with_empty_config(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=1.0, error=None, details=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.post(
                "/connectors/postgresql/test",
                json={"connector_type": "postgresql", "config": {}},
            )
        assert resp.status_code == 200
        assert resp.json()["success"] is True


# =============================================================================
# CREATE CONNECTION ENDPOINT
# =============================================================================


class TestCreateConnection:
    """Tests for POST /connectors/{connector_type}/connect."""

    def test_successful_creation(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=10.0, error=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(
                "/connectors/postgresql/connect",
                json={
                    "name": "Production DB",
                    "connector_type": "postgresql",
                    "config": {"host": "db.example.com", "port": 5432},
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Production DB"
        assert data["connector_type"] == "postgresql"
        assert data["status"] == "connected"
        assert data["latency_ms"] == 10.0
        assert data["id"]  # UUID assigned
        mock_put.assert_called_once()

    def test_create_stores_connection_via_store_put(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=8.0, error=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(
                "/connectors/mysql/connect",
                json={
                    "name": "Analytics DB",
                    "connector_type": "mysql",
                    "config": {"host": "analytics.local"},
                },
            )
        assert resp.status_code == 200
        stored = mock_put.call_args[0][0]
        assert stored["name"] == "Analytics DB"
        assert stored["connector_type"] == "mysql"
        assert stored["config"] == {"host": "analytics.local"}
        assert stored["status"] == "connected"

    def test_create_fails_when_test_connection_fails(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=False, error="Auth failed", latency_ms=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(
                "/connectors/postgresql/connect",
                json={
                    "name": "Broken DB",
                    "connector_type": "postgresql",
                    "config": {"host": "bad-host"},
                },
            )
        assert resp.status_code == 400
        assert "Connection failed" in resp.json()["detail"]
        mock_put.assert_not_called()

    def test_create_unknown_connector_returns_400(self, client):
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            side_effect=ValueError("Unknown connector: badtype"),
        ):
            resp = client.post(
                "/connectors/badtype/connect",
                json={
                    "name": "Test",
                    "connector_type": "badtype",
                    "config": {},
                },
            )
        assert resp.status_code == 400

    def test_create_assigns_unique_uuid(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=5.0, error=None,
        )
        ids = []
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch("backend.app.api.routes.connectors._store_put"):
            for _ in range(3):
                resp = client.post(
                    "/connectors/postgresql/connect",
                    json={
                        "name": "test",
                        "connector_type": "postgresql",
                        "config": {},
                    },
                )
                ids.append(resp.json()["id"])
        assert len(set(ids)) == 3  # All unique

    def test_create_sets_timestamps(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=5.0, error=None,
        )
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch("backend.app.api.routes.connectors._store_put"):
            resp = client.post(
                "/connectors/postgresql/connect",
                json={
                    "name": "Timestamped",
                    "connector_type": "postgresql",
                    "config": {},
                },
            )
        data = resp.json()
        assert data["created_at"] is not None
        assert data["last_used"] is not None

    def test_create_requires_name(self, client):
        resp = client.post(
            "/connectors/postgresql/connect",
            json={
                "connector_type": "postgresql",
                "config": {},
            },
        )
        assert resp.status_code == 422


# =============================================================================
# LIST CONNECTIONS ENDPOINT
# =============================================================================


class TestListConnections:
    """Tests for GET /connectors."""

    def test_returns_empty_when_no_connections(self, client):
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value={},
        ):
            resp = client.get("/connectors")
        assert resp.status_code == 200
        data = resp.json()
        assert data["connections"] == []
        assert data["total"] == 0

    def test_returns_all_connections(self, client, sample_connection, sample_connection_b):
        store = {
            sample_connection["id"]: sample_connection,
            sample_connection_b["id"]: sample_connection_b,
        }
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=store,
        ):
            resp = client.get("/connectors")
        data = resp.json()
        assert data["total"] == 2
        assert len(data["connections"]) == 2

    def test_sorted_by_created_at_descending(self, client):
        old = _make_connection(connection_id="old", created_at="2025-01-01T00:00:00")
        mid = _make_connection(connection_id="mid", created_at="2025-06-01T00:00:00")
        new = _make_connection(connection_id="new", created_at="2025-12-01T00:00:00")
        store = {"old": old, "mid": mid, "new": new}
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=store,
        ):
            resp = client.get("/connectors")
        ids = [c["id"] for c in resp.json()["connections"]]
        assert ids == ["new", "mid", "old"]

    def test_filter_by_connector_type(self, client, sample_connection, sample_connection_b):
        store = {
            sample_connection["id"]: sample_connection,
            sample_connection_b["id"]: sample_connection_b,
        }
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=store,
        ):
            resp = client.get("/connectors?connector_type=mysql")
        data = resp.json()
        assert data["total"] == 1
        assert data["connections"][0]["connector_type"] == "mysql"

    def test_filter_by_connector_type_no_match(self, client, sample_connection):
        store = {sample_connection["id"]: sample_connection}
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=store,
        ):
            resp = client.get("/connectors?connector_type=bigquery")
        data = resp.json()
        assert data["total"] == 0
        assert data["connections"] == []

    def test_pagination_with_limit(self, client):
        conns = {}
        for i in range(5):
            c = _make_connection(
                connection_id=f"c{i}",
                created_at=f"2025-0{i + 1}-01T00:00:00",
            )
            conns[c["id"]] = c
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=conns,
        ):
            resp = client.get("/connectors?limit=2")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["connections"]) == 2
        assert data["limit"] == 2

    def test_pagination_with_offset(self, client):
        conns = {}
        for i in range(5):
            c = _make_connection(
                connection_id=f"c{i}",
                created_at=f"2025-0{i + 1}-01T00:00:00",
            )
            conns[c["id"]] = c
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=conns,
        ):
            resp = client.get("/connectors?offset=3")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["connections"]) == 2  # 5 - 3 = 2 remaining
        assert data["offset"] == 3

    def test_pagination_with_limit_and_offset(self, client):
        conns = {}
        for i in range(10):
            c = _make_connection(
                connection_id=f"c{i}",
                created_at=f"2025-{(i + 1):02d}-01T00:00:00",
            )
            conns[c["id"]] = c
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value=conns,
        ):
            resp = client.get("/connectors?offset=2&limit=3")
        data = resp.json()
        assert data["total"] == 10
        assert len(data["connections"]) == 3
        assert data["offset"] == 2
        assert data["limit"] == 3

    def test_pagination_offset_beyond_total(self, client):
        c = _make_connection(connection_id="only")
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value={"only": c},
        ):
            resp = client.get("/connectors?offset=100")
        data = resp.json()
        assert data["total"] == 1
        assert data["connections"] == []

    def test_response_includes_pagination_metadata(self, client):
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value={},
        ):
            resp = client.get("/connectors?limit=50&offset=10")
        data = resp.json()
        assert data["limit"] == 50
        assert data["offset"] == 10
        assert "total" in data


# =============================================================================
# GET CONNECTION ENDPOINT
# =============================================================================


class TestGetConnection:
    """Tests for GET /connectors/{connection_id}."""

    def test_returns_existing_connection(self, client, sample_connection, patch_store_get):
        resp = client.get(f"/connectors/{sample_connection['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == sample_connection["id"]
        assert data["name"] == sample_connection["name"]
        assert data["connector_type"] == sample_connection["connector_type"]
        assert data["status"] == sample_connection["status"]

    def test_returns_404_for_missing_connection(self, client, patch_store_get_none):
        resp = client.get("/connectors/99999999-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_response_fields_match_schema(self, client, sample_connection, patch_store_get):
        resp = client.get(f"/connectors/{sample_connection['id']}")
        data = resp.json()
        expected_keys = {"id", "name", "connector_type", "status", "created_at", "last_used", "latency_ms"}
        assert set(data.keys()) == expected_keys

    def test_returns_null_for_optional_fields(self, client):
        conn = _make_connection(last_used=None, latency_ms=None)
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ):
            resp = client.get(f"/connectors/{conn['id']}")
        data = resp.json()
        assert data["last_used"] is None
        assert data["latency_ms"] is None


# =============================================================================
# DELETE CONNECTION ENDPOINT
# =============================================================================


class TestDeleteConnection:
    """Tests for DELETE /connectors/{connection_id}."""

    def test_deletes_existing_connection(self, client, patch_store_delete_true):
        resp = client.delete("/connectors/22222222-aaaa-bbbb-cccc-000000000000")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["message"] == "Connection deleted"

    def test_returns_404_for_missing_connection(self, client, patch_store_delete_false):
        resp = client.delete("/connectors/99999999-0000-0000-0000-999999999999")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_calls_store_delete_with_correct_id(self, client):
        with patch(
            "backend.app.api.routes.connectors._store_delete",
            return_value=True,
        ) as mock_del:
            client.delete("/connectors/33333333-aaaa-bbbb-cccc-000000000000")
        mock_del.assert_called_once_with("33333333-aaaa-bbbb-cccc-000000000000")


# =============================================================================
# CONNECTION HEALTH ENDPOINT
# =============================================================================


class TestCheckConnectionHealth:
    """Tests for POST /connectors/{connection_id}/health."""

    def test_healthy_connection(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=3.2, error=None, details=None,
        )
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(f"/connectors/{sample_connection['id']}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["latency_ms"] == 3.2

    def test_health_updates_status_to_connected(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=5.0, error=None, details=None,
        )
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            client.post(f"/connectors/{sample_connection['id']}/health")
        stored = mock_put.call_args[0][0]
        assert stored["status"] == "connected"

    def test_health_updates_status_to_error_on_failure(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=False, latency_ms=None, error="Timeout", details=None,
        )
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(f"/connectors/{sample_connection['id']}/health")
        stored = mock_put.call_args[0][0]
        assert stored["status"] == "error"
        assert resp.json()["success"] is False

    def test_health_updates_latency_in_store(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=42.0, error=None, details=None,
        )
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            client.post(f"/connectors/{sample_connection['id']}/health")
        stored = mock_put.call_args[0][0]
        assert stored["latency_ms"] == 42.0

    def test_health_returns_404_for_missing_connection(self, client, patch_store_get_none):
        resp = client.post("/connectors/99999999-0000-0000-0000-999999999999/health")
        assert resp.status_code == 404

    def test_health_handles_exception_sets_error_status(self, client, sample_connection):
        """When health check raises a non-ValueError, the exception handler
        catches it, persists error status, and returns a failed response
        with sanitized error message."""
        mock_connector = AsyncMock()
        mock_connector.test_connection.side_effect = RuntimeError("Driver crash")
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(f"/connectors/{sample_connection['id']}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "RuntimeError" in data["error"]
        # Ensure internal error message is NOT leaked
        assert "Driver crash" not in data["error"]
        # Verify error status was persisted
        stored = mock_put.call_args[0][0]
        assert stored["status"] == "error"

    def test_health_persists_on_success(self, client, sample_connection):
        """Verify _store_put is called for a healthy connection."""
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=7.0, error=None, details=None,
        )
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            client.post(f"/connectors/{sample_connection['id']}/health")
        mock_put.assert_called_once()

    def test_health_persists_on_exception(self, client, sample_connection):
        """Verify _store_put is called even when connector throws,
        and a sanitized error response is returned."""
        mock_connector = AsyncMock()
        mock_connector.test_connection.side_effect = Exception("Network")
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            resp = client.post(f"/connectors/{sample_connection['id']}/health")
        assert resp.status_code == 200
        assert resp.json()["success"] is False
        mock_put.assert_called_once()


# =============================================================================
# CONNECTION SCHEMA ENDPOINT
# =============================================================================


class TestGetConnectionSchema:
    """Tests for GET /connectors/{connection_id}/schema."""

    def test_returns_schema(self, client, sample_connection):
        mock_table = MagicMock()
        mock_table.model_dump.return_value = {"name": "users", "columns": []}
        mock_view = MagicMock()
        mock_view.model_dump.return_value = {"name": "active_users", "columns": []}
        mock_schema = MagicMock(
            tables=[mock_table],
            views=[mock_view],
            schemas=["public"],
        )
        mock_connector = AsyncMock()
        mock_connector.connect = AsyncMock()
        mock_connector.discover_schema = AsyncMock(return_value=mock_schema)
        mock_connector.disconnect = AsyncMock()
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.get(f"/connectors/{sample_connection['id']}/schema")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tables"] == [{"name": "users", "columns": []}]
        assert data["views"] == [{"name": "active_users", "columns": []}]
        assert data["schemas"] == ["public"]

    def test_schema_calls_connect_and_disconnect(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_schema = MagicMock(tables=[], views=[], schemas=[])
        mock_connector.connect = AsyncMock()
        mock_connector.discover_schema = AsyncMock(return_value=mock_schema)
        mock_connector.disconnect = AsyncMock()
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            client.get(f"/connectors/{sample_connection['id']}/schema")
        mock_connector.connect.assert_awaited_once()
        mock_connector.disconnect.assert_awaited_once()

    def test_schema_returns_404_for_missing_connection(self, client, patch_store_get_none):
        resp = client.get("/connectors/99999999-0000-0000-0000-999999999999/schema")
        assert resp.status_code == 404

    def test_schema_returns_500_on_connector_error(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.connect = AsyncMock(side_effect=RuntimeError("Cannot connect"))
        mock_connector.disconnect = AsyncMock()
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.get(f"/connectors/{sample_connection['id']}/schema")
        assert resp.status_code == 500
        assert "Failed to retrieve schema" in resp.json()["detail"]

    def test_schema_empty_tables_and_views(self, client, sample_connection):
        mock_schema = MagicMock(tables=[], views=[], schemas=[])
        mock_connector = AsyncMock()
        mock_connector.connect = AsyncMock()
        mock_connector.discover_schema = AsyncMock(return_value=mock_schema)
        mock_connector.disconnect = AsyncMock()
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            resp = client.get(f"/connectors/{sample_connection['id']}/schema")
        data = resp.json()
        assert data["tables"] == []
        assert data["views"] == []
        assert data["schemas"] == []


# =============================================================================
# QUERY EXECUTION ENDPOINT
# =============================================================================


class TestExecuteQuery:
    """Tests for POST /connectors/{connection_id}/query."""

    def _mock_query_connector(self, result_mock):
        """Build a mock connector with query support."""
        mock_connector = AsyncMock()
        mock_connector.connect = AsyncMock()
        mock_connector.execute_query = AsyncMock(return_value=result_mock)
        mock_connector.disconnect = AsyncMock()
        return mock_connector

    def test_successful_select_query(self, client, sample_connection):
        result = MagicMock(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time_ms=15.5,
            truncated=False,
            error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT id, name FROM users", "limit": 100},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["columns"] == ["id", "name"]
        assert data["row_count"] == 2
        assert data["truncated"] is False

    def test_query_with_parameters(self, client, sample_connection):
        result = MagicMock(
            columns=["id"], rows=[[42]], row_count=1,
            execution_time_ms=5.0, truncated=False, error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={
                    "query": "SELECT id FROM users WHERE id = :id",
                    "parameters": {"id": 42},
                    "limit": 10,
                },
            )
        assert resp.status_code == 200
        connector.execute_query.assert_awaited_once_with(
            "SELECT id FROM users WHERE id = :id",
            {"id": 42},
            10,
        )

    def test_query_updates_last_used_timestamp(self, client, sample_connection):
        result = MagicMock(
            columns=[], rows=[], row_count=0,
            execution_time_ms=1.0, truncated=False, error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        conn["last_used"] = None
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ) as mock_put:
            client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT 1", "limit": 10},
            )
        stored = mock_put.call_args[0][0]
        assert stored["last_used"] is not None
        # Verify it looks like an ISO timestamp
        datetime.fromisoformat(stored["last_used"])

    def test_query_calls_connect_and_disconnect(self, client, sample_connection):
        result = MagicMock(
            columns=[], rows=[], row_count=0,
            execution_time_ms=0, truncated=False, error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT 1", "limit": 10},
            )
        connector.connect.assert_awaited_once()
        connector.disconnect.assert_awaited_once()

    def test_query_rejects_drop_table(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "DROP TABLE users", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_delete(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "DELETE FROM users WHERE 1=1", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_insert(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "INSERT INTO users (name) VALUES ('evil')", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_update(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "UPDATE users SET admin=true", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_alter(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "ALTER TABLE users ADD COLUMN age INT", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_truncate(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "TRUNCATE TABLE users", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_empty_query(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_rejects_create_table(self, client, sample_connection, patch_store_get):
        resp = client.post(
            f"/connectors/{sample_connection['id']}/query",
            json={"query": "CREATE TABLE evil (id INT)", "limit": 100},
        )
        assert resp.status_code == 400

    def test_query_allows_with_clause(self, client, sample_connection):
        result = MagicMock(
            columns=["cnt"], rows=[[5]], row_count=1,
            execution_time_ms=10.0, truncated=False, error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={
                    "query": "WITH cte AS (SELECT 1) SELECT * FROM cte",
                    "limit": 100,
                },
            )
        assert resp.status_code == 200
        assert resp.json()["row_count"] == 1

    def test_query_returns_404_for_missing_connection(self, client, patch_store_get_none):
        resp = client.post(
            "/connectors/99999999-0000-0000-0000-999999999999/query",
            json={"query": "SELECT 1", "limit": 10},
        )
        assert resp.status_code == 404

    def test_query_handles_connector_exception(self, client, sample_connection):
        mock_connector = AsyncMock()
        mock_connector.connect = AsyncMock(side_effect=RuntimeError("Connection lost"))
        mock_connector.disconnect = AsyncMock()
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT 1", "limit": 10},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is not None
        assert "RuntimeError" in data["error"]
        assert data["row_count"] == 0

    def test_query_default_limit(self, client, sample_connection):
        result = MagicMock(
            columns=[], rows=[], row_count=0,
            execution_time_ms=0, truncated=False, error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT 1"},
            )
        assert resp.status_code == 200
        # Default limit is 1000
        connector.execute_query.assert_awaited_once()
        call_args = connector.execute_query.call_args
        assert call_args[0][2] == 1000

    def test_query_truncated_result(self, client, sample_connection):
        result = MagicMock(
            columns=["id"],
            rows=[[i] for i in range(100)],
            row_count=100,
            execution_time_ms=50.0,
            truncated=True,
            error=None,
        )
        connector = self._mock_query_connector(result)
        conn = deepcopy(sample_connection)
        config = conn.pop("config", {})
        conn["has_credentials"] = True
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ), patch(
            "backend.app.api.routes.connectors._store_get_config",
            return_value=config,
        ), patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
        ):
            resp = client.post(
                f"/connectors/{sample_connection['id']}/query",
                json={"query": "SELECT id FROM big_table", "limit": 100},
            )
        assert resp.status_code == 200
        assert resp.json()["truncated"] is True

    def test_read_only_validation_before_store_lookup(self, client):
        """Read-only validation should happen before looking up the connection."""
        with patch(
            "backend.app.api.routes.connectors._store_get",
        ) as mock_get:
            resp = client.post(
                "/connectors/44444444-aaaa-bbbb-cccc-000000000000/query",
                json={"query": "DROP TABLE users", "limit": 10},
            )
        assert resp.status_code == 400
        # _store_get should never be called if query is invalid
        mock_get.assert_not_called()


# =============================================================================
# OAUTH ENDPOINTS
# =============================================================================


class TestGetOAuthURL:
    """Tests for GET /connectors/{connector_type}/oauth/authorize."""

    def test_returns_authorization_url(self, client):
        mock_connector = MagicMock()
        mock_connector.get_oauth_url.return_value = "https://oauth.example.com/auth?client_id=abc"
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.get(
                "/connectors/gdrive/oauth/authorize",
                params={"redirect_uri": "https://app.example.com/callback"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["authorization_url"] == "https://oauth.example.com/auth?client_id=abc"
        assert "state" in data

    def test_uses_provided_state(self, client):
        mock_connector = MagicMock()
        mock_connector.get_oauth_url.return_value = "https://oauth.example.com/auth"
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.get(
                "/connectors/gdrive/oauth/authorize",
                params={
                    "redirect_uri": "https://app.example.com/callback",
                    "state": "my-custom-state",
                },
            )
        assert resp.status_code == 200
        assert resp.json()["state"] == "my-custom-state"

    def test_generates_state_when_not_provided(self, client):
        mock_connector = MagicMock()
        mock_connector.get_oauth_url.return_value = "https://oauth.example.com/auth"
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.get(
                "/connectors/gdrive/oauth/authorize",
                params={"redirect_uri": "https://app.example.com/callback"},
            )
        state = resp.json()["state"]
        # Should be a valid UUID
        uuid.UUID(state)

    def test_returns_400_when_oauth_not_supported(self, client):
        mock_connector = MagicMock()
        mock_connector.get_oauth_url.return_value = None
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.get(
                "/connectors/postgresql/oauth/authorize",
                params={"redirect_uri": "https://app.example.com/callback"},
            )
        assert resp.status_code == 400
        assert "OAuth" in resp.json()["detail"]

    def test_returns_400_for_unknown_connector(self, client):
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            side_effect=ValueError("Unknown connector"),
        ):
            resp = client.get(
                "/connectors/unknown/oauth/authorize",
                params={"redirect_uri": "https://app.example.com/callback"},
            )
        assert resp.status_code == 400

    def test_requires_redirect_uri(self, client):
        resp = client.get("/connectors/gdrive/oauth/authorize")
        assert resp.status_code == 422

    def test_passes_redirect_uri_and_state_to_connector(self, client):
        mock_connector = MagicMock()
        mock_connector.get_oauth_url.return_value = "https://oauth.example.com/auth"
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ):
            client.get(
                "/connectors/gdrive/oauth/authorize",
                params={
                    "redirect_uri": "https://my-app.com/cb",
                    "state": "xyz",
                },
            )
        mock_connector.get_oauth_url.assert_called_once_with("https://my-app.com/cb", "xyz")


class TestHandleOAuthCallback:
    """Tests for POST /connectors/{connector_type}/oauth/callback."""

    def test_successful_callback(self, client):
        mock_connector = MagicMock()
        mock_connector.handle_oauth_callback.return_value = {
            "access_token": "abc123",
            "refresh_token": "xyz789",
            "expires_in": 3600,
        }
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.post(
                "/connectors/gdrive/oauth/callback",
                params={
                    "code": "auth-code-123",
                    "redirect_uri": "https://app.example.com/callback",
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        # Tokens are redacted in the response for security
        assert data["tokens"]["access_token"] == "***"
        assert data["tokens"]["refresh_token"] == "***"
        assert data["tokens"]["expires_in"] == 3600
        assert data["tokens"]["_redacted"] is True

    def test_callback_passes_code_and_redirect(self, client):
        mock_connector = MagicMock()
        mock_connector.handle_oauth_callback.return_value = {"access_token": "t"}
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            client.post(
                "/connectors/gdrive/oauth/callback",
                params={
                    "code": "my-code",
                    "redirect_uri": "https://callback.test",
                },
            )
        mock_connector.handle_oauth_callback.assert_called_once_with("my-code", "https://callback.test")

    def test_callback_error_returns_400(self, client):
        mock_connector = MagicMock()
        mock_connector.handle_oauth_callback.side_effect = RuntimeError("Invalid code")
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.post(
                "/connectors/gdrive/oauth/callback",
                params={
                    "code": "bad-code",
                    "redirect_uri": "https://app.example.com/callback",
                },
            )
        assert resp.status_code == 400
        assert "OAuth callback failed" in resp.json()["detail"]

    def test_callback_requires_code(self, client):
        resp = client.post(
            "/connectors/gdrive/oauth/callback",
            params={"redirect_uri": "https://app.example.com/callback"},
        )
        assert resp.status_code == 422

    def test_callback_requires_redirect_uri(self, client):
        resp = client.post(
            "/connectors/gdrive/oauth/callback",
            params={"code": "auth-code"},
        )
        assert resp.status_code == 422

    def test_callback_with_state_parameter(self, client):
        mock_connector = MagicMock()
        mock_connector.handle_oauth_callback.return_value = {"access_token": "t"}
        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._validate_redirect_uri",
        ):
            resp = client.post(
                "/connectors/gdrive/oauth/callback",
                params={
                    "code": "c",
                    "redirect_uri": "https://app.example.com/cb",
                    "state": "my-state",
                },
            )
        assert resp.status_code == 200


# =============================================================================
# CROSS-CUTTING / INTEGRATION-STYLE TESTS
# =============================================================================


class TestStorePutAndDeleteIntegration:
    """Verify _store_put and _store_delete work together across both namespaces."""

    def test_put_then_delete_clears_both_namespaces(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        conn = _make_connection(connection_id="full-cycle")
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(conn)
            assert "full-cycle" in state["connectors"]
            assert "full-cycle" in state["connector_credentials"]

            result = _store_delete("full-cycle")
            assert result is True
            assert "full-cycle" not in state["connectors"]
            assert "full-cycle" not in state["connector_credentials"]

    def test_put_multiple_delete_one(self):
        state: dict[str, Any] = {}
        mock_store = _mock_state_store(state)
        with patch("backend.app.api.routes.connectors.state_store", mock_store):
            _store_put(_make_connection(connection_id="keep"))
            _store_put(_make_connection(connection_id="remove"))
            _store_delete("remove")

        assert "keep" in state["connectors"]
        assert "keep" in state["connector_credentials"]
        assert "remove" not in state["connectors"]
        assert "remove" not in state["connector_credentials"]


class TestCreateAndGetWorkflow:
    """End-to-end workflow: create connection, then get it."""

    def test_create_then_get(self, client):
        mock_connector = AsyncMock()
        mock_connector.test_connection.return_value = MagicMock(
            success=True, latency_ms=5.0, error=None,
        )
        created_id = None

        def capture_put(conn):
            nonlocal created_id
            created_id = conn["id"]

        with patch(
            "backend.app.api.routes.connectors.get_connector",
            return_value=mock_connector,
        ), patch(
            "backend.app.api.routes.connectors._store_put",
            side_effect=capture_put,
        ):
            resp = client.post(
                "/connectors/postgresql/connect",
                json={
                    "name": "My DB",
                    "connector_type": "postgresql",
                    "config": {"host": "localhost"},
                },
            )
        assert resp.status_code == 200
        assert created_id is not None

        # Now fetch the connection
        stored = _make_connection(
            connection_id=created_id,
            name="My DB",
            connector_type="postgresql",
        )
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=stored,
        ):
            resp = client.get(f"/connectors/{created_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "My DB"


class TestQuerySQLValidationEdgeCases:
    """Additional SQL validation edge cases for the query endpoint."""

    def _post_query(self, client, query):
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=_make_connection(),
        ):
            return client.post(
                "/connectors/44444444-aaaa-bbbb-cccc-000000000000/query",
                json={"query": query, "limit": 10},
            )

    def test_rejects_grant_statement(self, client):
        resp = self._post_query(client, "GRANT ALL ON users TO evil")
        assert resp.status_code == 400

    def test_rejects_revoke_statement(self, client):
        resp = self._post_query(client, "REVOKE ALL ON users FROM evil")
        assert resp.status_code == 400

    def test_rejects_exec_statement(self, client):
        resp = self._post_query(client, "EXEC sp_executesql 'DROP TABLE users'")
        assert resp.status_code == 400

    def test_rejects_whitespace_only(self, client):
        resp = self._post_query(client, "   ")
        assert resp.status_code == 400

    def test_rejects_comment_only_query(self, client):
        resp = self._post_query(client, "-- just a comment")
        assert resp.status_code == 400


class TestConnectionResponseModel:
    """Verify ConnectionResponse serialization."""

    def test_get_connection_returns_all_expected_fields(self, client):
        conn = _make_connection(
            connection_id="55555555-aaaa-bbbb-cccc-000000000001",
            name="Test",
            connector_type="mysql",
            status="connected",
            created_at="2025-01-01T00:00:00",
            last_used="2025-06-01T12:00:00",
            latency_ms=7.7,
        )
        with patch(
            "backend.app.api.routes.connectors._store_get",
            return_value=conn,
        ):
            resp = client.get("/connectors/55555555-aaaa-bbbb-cccc-000000000001")
        data = resp.json()
        assert data["id"] == "55555555-aaaa-bbbb-cccc-000000000001"
        assert data["name"] == "Test"
        assert data["connector_type"] == "mysql"
        assert data["status"] == "connected"
        assert data["created_at"] == "2025-01-01T00:00:00"
        assert data["last_used"] == "2025-06-01T12:00:00"
        assert data["latency_ms"] == 7.7

    def test_list_connection_items_match_schema(self, client):
        conn = _make_connection(connection_id="schema-check")
        with patch(
            "backend.app.api.routes.connectors._store_get_all",
            return_value={"schema-check": conn},
        ):
            resp = client.get("/connectors")
        item = resp.json()["connections"][0]
        expected_keys = {"id", "name", "connector_type", "status", "created_at", "last_used", "latency_ms"}
        assert set(item.keys()) == expected_keys


class TestSecurityDependencyOverride:
    """Verify the require_api_key dependency is wired into the router."""

    def test_router_has_security_dependency(self):
        """The router should have require_api_key in its dependencies."""
        dep_callables = [d.dependency for d in router.dependencies]
        assert require_api_key in dep_callables

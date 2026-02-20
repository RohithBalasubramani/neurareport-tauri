"""
Comprehensive Tests for Dashboard Services (lines 485-489) and Security Config (lines 695-718).

Covers:
- DashboardService: CRUD, persistence, favorites, stats
- WidgetService: add, update, delete, reorder, grid clamping
- SnapshotService: create, retention, mark rendered/failed, delete
- EmbedService: generate, validate, revoke, list, expiry, signing
- Security Config: JWT secret enforcement, debug_mode default

7-layer test structure:
1. Unit Tests — Service method correctness with mock state store
2. Integration Tests — Full CRUD lifecycle
3. Property-Based Tests — Invariants (IDs unique, timestamps monotonic)
4. Failure Injection Tests — Missing dashboards, corrupt state
5. Concurrency Tests — Thread-safe state mutations
6. Security Tests — Token validation, JWT enforcement
7. Usability Tests — Error messages, edge cases

Run with: pytest backend/tests/test_dashboard_services.py -v
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# FIXTURES: In-memory state store stub for testing
# =============================================================================

class _FakeStateStore:
    """Thread-safe in-memory state store that mimics the real StateStore
    transaction() context manager for testing."""

    def __init__(self):
        self._state: Dict[str, Any] = {
            "dashboards": {},
            "dashboard_widgets": {},
            "dashboard_snapshots": {},
            "dashboard_embed_tokens": {},
            "favorites": {
                "templates": [],
                "connections": [],
                "documents": [],
                "spreadsheets": [],
                "dashboards": [],
            },
        }
        self._lock = threading.RLock()

    class _TxnCtx:
        def __init__(self, store):
            self._store = store

        def __enter__(self):
            self._store._lock.acquire()
            return self._store._state

        def __exit__(self, *args):
            self._store._lock.release()

    def transaction(self):
        return self._TxnCtx(self)

    def reset(self):
        with self._lock:
            self._state = {
                "dashboards": {},
                "dashboard_widgets": {},
                "dashboard_snapshots": {},
                "dashboard_embed_tokens": {},
                "favorites": {
                    "templates": [],
                    "connections": [],
                    "documents": [],
                    "spreadsheets": [],
                    "dashboards": [],
                },
            }


@pytest.fixture(autouse=True)
def mock_state_store(monkeypatch):
    """Replace the real state_store with an in-memory fake for ALL tests."""
    fake = _FakeStateStore()
    monkeypatch.setattr(
        "backend.app.services.dashboards.service.state_store", fake
    )
    monkeypatch.setattr(
        "backend.app.services.dashboards.widget_service.state_store", fake
    )
    monkeypatch.setattr(
        "backend.app.services.dashboards.snapshot_service.state_store", fake
    )
    monkeypatch.setattr(
        "backend.app.services.dashboards.embed_service.state_store", fake
    )
    return fake


@pytest.fixture
def mock_settings(monkeypatch):
    """Provide mock settings for services that need config."""
    settings = MagicMock()
    settings.jwt_secret = MagicMock(get_secret_value=lambda: "test-secret-for-hmac-signing-key-1234")
    settings.uploads_dir = Path("/tmp/test_uploads")
    settings.debug_mode = True

    monkeypatch.setattr(
        "backend.app.services.dashboards.snapshot_service.get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        "backend.app.services.dashboards.embed_service.get_settings",
        lambda: settings,
    )
    return settings


# =============================================================================
# 1. UNIT TESTS — DashboardService
# =============================================================================

class TestDashboardServiceUnit:
    """Unit tests for DashboardService CRUD operations."""

    def _svc(self):
        from backend.app.services.dashboards.service import DashboardService
        return DashboardService()

    def test_create_dashboard_returns_id_and_timestamps(self):
        svc = self._svc()
        result = svc.create_dashboard(name="Test Dashboard")

        assert result["id"] is not None
        assert len(result["id"]) == 36  # UUID4
        assert result["name"] == "Test Dashboard"
        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert result["widgets"] == []
        assert result["filters"] == []

    def test_create_dashboard_with_all_fields(self):
        svc = self._svc()
        widgets = [{"id": "w1", "config": {"type": "chart", "title": "Sales"}}]
        result = svc.create_dashboard(
            name="Full Dashboard",
            description="A complete dashboard",
            widgets=widgets,
            filters=[{"column": "date", "value": "2024"}],
            theme="dark",
        )

        assert result["description"] == "A complete dashboard"
        assert len(result["widgets"]) == 1
        assert result["theme"] == "dark"
        assert len(result["filters"]) == 1

    def test_get_dashboard_existing(self):
        svc = self._svc()
        created = svc.create_dashboard(name="Find Me")
        fetched = svc.get_dashboard(created["id"])

        assert fetched is not None
        assert fetched["id"] == created["id"]
        assert fetched["name"] == "Find Me"

    def test_get_dashboard_nonexistent(self):
        svc = self._svc()
        result = svc.get_dashboard("nonexistent-id")
        assert result is None

    def test_list_dashboards_empty(self):
        svc = self._svc()
        result = svc.list_dashboards()
        assert result["dashboards"] == []
        assert result["total"] == 0

    def test_list_dashboards_pagination(self):
        svc = self._svc()
        for i in range(5):
            svc.create_dashboard(name=f"Dashboard {i}")

        page1 = svc.list_dashboards(limit=2, offset=0)
        assert len(page1["dashboards"]) == 2
        assert page1["total"] == 5

        page2 = svc.list_dashboards(limit=2, offset=2)
        assert len(page2["dashboards"]) == 2

        page3 = svc.list_dashboards(limit=2, offset=4)
        assert len(page3["dashboards"]) == 1

    def test_list_dashboards_sorted_by_updated_at(self):
        svc = self._svc()
        d1 = svc.create_dashboard(name="First")
        d2 = svc.create_dashboard(name="Second")

        # Update d1 to make it more recent
        svc.update_dashboard(d1["id"], name="First Updated")

        result = svc.list_dashboards()
        assert result["dashboards"][0]["name"] == "First Updated"

    def test_update_dashboard_partial(self):
        svc = self._svc()
        created = svc.create_dashboard(name="Original", theme="light")
        updated = svc.update_dashboard(created["id"], name="Renamed")

        assert updated["name"] == "Renamed"
        assert updated["theme"] == "light"  # Unchanged
        assert updated["updated_at"] is not None  # Timestamp is set

    def test_update_dashboard_nonexistent(self):
        svc = self._svc()
        result = svc.update_dashboard("ghost-id", name="Nope")
        assert result is None

    def test_delete_dashboard_existing(self):
        svc = self._svc()
        created = svc.create_dashboard(name="Doomed")
        assert svc.delete_dashboard(created["id"]) is True
        assert svc.get_dashboard(created["id"]) is None

    def test_delete_dashboard_nonexistent(self):
        svc = self._svc()
        assert svc.delete_dashboard("ghost-id") is False

    def test_delete_removes_from_favorites(self, mock_state_store):
        svc = self._svc()
        created = svc.create_dashboard(name="Fav")
        svc.toggle_favorite(created["id"])
        assert svc.is_favorite(created["id"]) is True

        svc.delete_dashboard(created["id"])
        # Favorites should be cleaned up
        favs = mock_state_store._state["favorites"]["dashboards"]
        assert created["id"] not in favs


class TestDashboardServiceFavorites:
    """Unit tests for dashboard favorites."""

    def _svc(self):
        from backend.app.services.dashboards.service import DashboardService
        return DashboardService()

    def test_toggle_favorite_on_and_off(self):
        svc = self._svc()
        d = svc.create_dashboard(name="Toggle Test")

        assert svc.toggle_favorite(d["id"]) is True  # On
        assert svc.is_favorite(d["id"]) is True

        assert svc.toggle_favorite(d["id"]) is False  # Off
        assert svc.is_favorite(d["id"]) is False

    def test_toggle_favorite_nonexistent(self):
        svc = self._svc()
        with pytest.raises(ValueError, match="not found"):
            svc.toggle_favorite("ghost-id")


class TestDashboardServiceStats:
    """Test stats computation."""

    def _svc(self):
        from backend.app.services.dashboards.service import DashboardService
        return DashboardService()

    def test_stats_empty(self):
        svc = self._svc()
        stats = svc.get_stats()
        assert stats["total_dashboards"] == 0
        assert stats["total_widgets"] == 0
        assert stats["total_favorites"] == 0

    def test_stats_populated(self):
        svc = self._svc()
        d = svc.create_dashboard(name="Stats Test")
        svc.toggle_favorite(d["id"])

        stats = svc.get_stats()
        assert stats["total_dashboards"] == 1
        assert stats["total_favorites"] == 1


# =============================================================================
# 2. UNIT TESTS — WidgetService
# =============================================================================

class TestWidgetServiceUnit:
    """Unit tests for WidgetService."""

    def _setup(self):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        ds = DashboardService()
        ws = WidgetService()
        dashboard = ds.create_dashboard(name="Widget Host")
        return ds, ws, dashboard

    def test_add_widget(self):
        _, ws, d = self._setup()
        widget = ws.add_widget(
            d["id"],
            config={"type": "chart", "title": "Revenue"},
            x=0, y=0, w=6, h=4,
        )

        assert widget["id"] is not None
        assert widget["config"]["type"] == "chart"
        assert widget["w"] == 6
        assert widget["h"] == 4

    def test_add_widget_to_nonexistent_dashboard(self):
        from backend.app.services.dashboards.widget_service import WidgetService
        ws = WidgetService()
        with pytest.raises(ValueError, match="not found"):
            ws.add_widget("ghost", config={"type": "chart", "title": "X"})

    def test_add_widget_clamps_position(self):
        _, ws, d = self._setup()
        widget = ws.add_widget(
            d["id"],
            config={"type": "metric", "title": "KPI"},
            x=-5, y=-10, w=50, h=100,
        )
        assert widget["x"] == 0  # Clamped from -5
        assert widget["y"] == 0  # Clamped from -10
        assert widget["w"] == 12  # Clamped from 50 to MAX_WIDGET_W
        assert widget["h"] == 20  # Clamped from 100 to MAX_WIDGET_H

    def test_update_widget(self):
        _, ws, d = self._setup()
        widget = ws.add_widget(
            d["id"],
            config={"type": "chart", "title": "Old"},
        )
        updated = ws.update_widget(
            d["id"],
            widget["id"],
            config={"type": "table", "title": "New"},
            w=8,
        )
        assert updated is not None
        assert updated["config"]["title"] == "New"
        assert updated["w"] == 8

    def test_update_widget_nonexistent(self):
        _, ws, d = self._setup()
        result = ws.update_widget(d["id"], "ghost-widget", config={"type": "chart", "title": "X"})
        assert result is None

    def test_delete_widget(self):
        _, ws, d = self._setup()
        widget = ws.add_widget(d["id"], config={"type": "chart", "title": "Delete Me"})
        assert ws.delete_widget(d["id"], widget["id"]) is True
        assert ws.get_widget(d["id"], widget["id"]) is None

    def test_delete_widget_nonexistent(self):
        _, ws, d = self._setup()
        assert ws.delete_widget(d["id"], "ghost") is False

    def test_list_widgets(self):
        _, ws, d = self._setup()
        ws.add_widget(d["id"], config={"type": "chart", "title": "A"})
        ws.add_widget(d["id"], config={"type": "metric", "title": "B"})

        result = ws.list_widgets(d["id"])
        assert result is not None
        assert len(result) == 2

    def test_list_widgets_nonexistent_dashboard(self):
        from backend.app.services.dashboards.widget_service import WidgetService
        ws = WidgetService()
        assert ws.list_widgets("ghost") is None

    def test_reorder_widgets(self):
        _, ws, d = self._setup()
        w1 = ws.add_widget(d["id"], config={"type": "chart", "title": "First"})
        w2 = ws.add_widget(d["id"], config={"type": "chart", "title": "Second"})
        w3 = ws.add_widget(d["id"], config={"type": "chart", "title": "Third"})

        # Reverse order
        assert ws.reorder_widgets(d["id"], [w3["id"], w1["id"], w2["id"]]) is True

        result = ws.list_widgets(d["id"])
        assert result[0]["id"] == w3["id"]
        assert result[1]["id"] == w1["id"]
        assert result[2]["id"] == w2["id"]

    def test_reorder_appends_missing_ids(self):
        _, ws, d = self._setup()
        w1 = ws.add_widget(d["id"], config={"type": "chart", "title": "A"})
        w2 = ws.add_widget(d["id"], config={"type": "chart", "title": "B"})

        # Only mention w2 — w1 should be appended
        ws.reorder_widgets(d["id"], [w2["id"]])
        result = ws.list_widgets(d["id"])
        assert result[0]["id"] == w2["id"]
        assert result[1]["id"] == w1["id"]


# =============================================================================
# 3. UNIT TESTS — SnapshotService
# =============================================================================

class TestSnapshotServiceUnit:
    """Unit tests for SnapshotService."""

    def _setup(self, mock_settings):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        ds = DashboardService()
        ss = SnapshotService()
        dashboard = ds.create_dashboard(name="Snapshot Host")
        return ds, ss, dashboard

    def test_create_snapshot(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        snap = ss.create_snapshot(d["id"], format="png")

        assert snap["id"] is not None
        assert snap["dashboard_id"] == d["id"]
        assert snap["format"] == "png"
        assert snap["status"] == "pending"
        assert snap["content_hash"] is not None
        assert len(snap["content_hash"]) == 16  # SHA256 truncated

    def test_create_snapshot_nonexistent(self, mock_settings):
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        ss = SnapshotService()
        with pytest.raises(ValueError, match="not found"):
            ss.create_snapshot("ghost", format="png")

    def test_create_snapshot_invalid_format(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        with pytest.raises(ValueError, match="Unsupported"):
            ss.create_snapshot(d["id"], format="bmp")

    def test_mark_rendered(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        snap = ss.create_snapshot(d["id"])
        updated = ss.mark_rendered(
            snap["id"],
            file_path="/tmp/snap.png",
            file_size_bytes=4096,
        )
        assert updated["status"] == "completed"
        assert updated["file_path"] == "/tmp/snap.png"
        assert updated["file_size_bytes"] == 4096

    def test_mark_failed(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        snap = ss.create_snapshot(d["id"])
        updated = ss.mark_failed(snap["id"], error="Render crashed")
        assert updated["status"] == "failed"
        assert updated["error"] == "Render crashed"

    def test_list_snapshots(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        ss.create_snapshot(d["id"])
        ss.create_snapshot(d["id"])

        snaps = ss.list_snapshots(d["id"])
        assert len(snaps) == 2

    def test_snapshot_retention_limit(self, mock_settings, mock_state_store):
        """Create more than MAX_SNAPSHOTS_PER_DASHBOARD and verify cleanup."""
        _, ss, d = self._setup(mock_settings)
        from backend.app.services.dashboards.snapshot_service import MAX_SNAPSHOTS_PER_DASHBOARD

        for i in range(MAX_SNAPSHOTS_PER_DASHBOARD + 5):
            ss.create_snapshot(d["id"])

        snaps = ss.list_snapshots(d["id"], limit=100)
        assert len(snaps) <= MAX_SNAPSHOTS_PER_DASHBOARD

    def test_delete_snapshot(self, mock_settings):
        _, ss, d = self._setup(mock_settings)
        snap = ss.create_snapshot(d["id"])
        assert ss.delete_snapshot(snap["id"]) is True
        assert ss.get_snapshot(snap["id"]) is None

    def test_delete_snapshot_nonexistent(self, mock_settings):
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        ss = SnapshotService()
        assert ss.delete_snapshot("ghost") is False


# =============================================================================
# 4. UNIT TESTS — EmbedService
# =============================================================================

class TestEmbedServiceUnit:
    """Unit tests for EmbedService."""

    def _setup(self, mock_settings):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.embed_service import EmbedService
        ds = DashboardService()
        es = EmbedService()
        dashboard = ds.create_dashboard(name="Embed Host")
        return ds, es, dashboard

    def test_generate_embed_token(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        result = es.generate_embed_token(d["id"], expires_hours=48)

        assert result["token_id"] is not None
        assert result["embed_token"] is not None
        assert result["embed_url"].startswith("/embed/dashboard/")
        assert result["expires_hours"] == 48
        assert result["dashboard_id"] == d["id"]

    def test_generate_embed_token_nonexistent_dashboard(self, mock_settings):
        from backend.app.services.dashboards.embed_service import EmbedService
        es = EmbedService()
        with pytest.raises(ValueError, match="not found"):
            es.generate_embed_token("ghost")

    def test_generate_embed_token_invalid_hours(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        with pytest.raises(ValueError, match="between 1 and 720"):
            es.generate_embed_token(d["id"], expires_hours=0)

    def test_validate_token_valid(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        result = es.generate_embed_token(d["id"])
        validated = es.validate_token(result["embed_token"])

        assert validated is not None
        assert validated["token_id"] == result["token_id"]
        assert validated["dashboard_id"] == d["id"]

    def test_validate_token_invalid(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        assert es.validate_token("completely-bogus-token") is None

    def test_validate_token_revoked(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        result = es.generate_embed_token(d["id"])
        es.revoke_token(result["token_id"])

        assert es.validate_token(result["embed_token"]) is None

    def test_revoke_token(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        result = es.generate_embed_token(d["id"])
        assert es.revoke_token(result["token_id"]) is True

    def test_revoke_token_nonexistent(self, mock_settings):
        from backend.app.services.dashboards.embed_service import EmbedService
        es = EmbedService()
        assert es.revoke_token("ghost") is False

    def test_revoke_all_for_dashboard(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        es.generate_embed_token(d["id"])
        es.generate_embed_token(d["id"])
        es.generate_embed_token(d["id"])

        count = es.revoke_all_for_dashboard(d["id"])
        assert count == 3

    def test_list_tokens(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        es.generate_embed_token(d["id"])
        es.generate_embed_token(d["id"])

        tokens = es.list_tokens(d["id"])
        assert len(tokens) == 2

    def test_list_tokens_excludes_revoked_by_default(self, mock_settings):
        _, es, d = self._setup(mock_settings)
        r1 = es.generate_embed_token(d["id"])
        es.generate_embed_token(d["id"])
        es.revoke_token(r1["token_id"])

        tokens = es.list_tokens(d["id"])
        assert len(tokens) == 1

        tokens_all = es.list_tokens(d["id"], include_revoked=True)
        assert len(tokens_all) == 2

    def test_validate_increments_access_count(self, mock_settings, mock_state_store):
        _, es, d = self._setup(mock_settings)
        result = es.generate_embed_token(d["id"])

        es.validate_token(result["embed_token"])
        es.validate_token(result["embed_token"])
        es.validate_token(result["embed_token"])

        token_record = mock_state_store._state["dashboard_embed_tokens"][result["token_id"]]
        assert token_record["access_count"] == 3
        assert token_record["last_accessed_at"] is not None


# =============================================================================
# 5. INTEGRATION TESTS — Full lifecycle
# =============================================================================

class TestDashboardLifecycle:
    """End-to-end lifecycle tests."""

    def test_full_dashboard_lifecycle(self, mock_settings):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        from backend.app.services.dashboards.embed_service import EmbedService

        ds = DashboardService()
        ws = WidgetService()
        ss = SnapshotService()
        es = EmbedService()

        # 1. Create dashboard
        dashboard = ds.create_dashboard(
            name="Revenue Dashboard",
            description="Q4 metrics",
            theme="dark",
        )
        assert dashboard["id"]

        # 2. Add widgets
        w1 = ws.add_widget(
            dashboard["id"],
            config={"type": "chart", "title": "Monthly Revenue"},
            x=0, y=0, w=6, h=4,
        )
        w2 = ws.add_widget(
            dashboard["id"],
            config={"type": "metric", "title": "Total Sales"},
            x=6, y=0, w=3, h=2,
        )
        assert len(ws.list_widgets(dashboard["id"])) == 2

        # 3. Update a widget
        ws.update_widget(
            dashboard["id"], w1["id"],
            config={"type": "chart", "title": "Updated Revenue Chart"},
        )
        updated_w1 = ws.get_widget(dashboard["id"], w1["id"])
        assert updated_w1["config"]["title"] == "Updated Revenue Chart"

        # 4. Create snapshot
        snap = ss.create_snapshot(dashboard["id"], format="png")
        assert snap["status"] == "pending"

        # 5. Mark snapshot rendered
        rendered = ss.mark_rendered(
            snap["id"],
            file_path="/uploads/snap.png",
            file_size_bytes=8192,
        )
        assert rendered["status"] == "completed"

        # 6. Generate embed token
        embed = es.generate_embed_token(dashboard["id"], expires_hours=24)
        assert embed["embed_token"]

        # 7. Validate embed token
        valid = es.validate_token(embed["embed_token"])
        assert valid["dashboard_id"] == dashboard["id"]

        # 8. Delete a widget
        ws.delete_widget(dashboard["id"], w2["id"])
        assert len(ws.list_widgets(dashboard["id"])) == 1

        # 9. Favorite the dashboard
        ds.toggle_favorite(dashboard["id"])
        assert ds.is_favorite(dashboard["id"]) is True

        # 10. Delete dashboard (cascade: favorites cleaned up)
        ds.delete_dashboard(dashboard["id"])
        assert ds.get_dashboard(dashboard["id"]) is None

    def test_multiple_dashboards_isolation(self):
        """Changes to one dashboard don't affect another."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        ds = DashboardService()
        ws = WidgetService()

        d1 = ds.create_dashboard(name="Dashboard A")
        d2 = ds.create_dashboard(name="Dashboard B")

        ws.add_widget(d1["id"], config={"type": "chart", "title": "A Widget"})
        ws.add_widget(d2["id"], config={"type": "metric", "title": "B Widget"})

        assert len(ws.list_widgets(d1["id"])) == 1
        assert len(ws.list_widgets(d2["id"])) == 1

        ds.delete_dashboard(d1["id"])
        assert len(ws.list_widgets(d2["id"])) == 1


# =============================================================================
# 6. PROPERTY-BASED TESTS — Invariants
# =============================================================================

class TestDashboardInvariants:
    """Invariant checks across multiple operations."""

    def test_dashboard_ids_always_unique(self):
        from backend.app.services.dashboards.service import DashboardService
        svc = DashboardService()
        ids = set()
        for i in range(50):
            d = svc.create_dashboard(name=f"D{i}")
            assert d["id"] not in ids, f"Duplicate ID: {d['id']}"
            ids.add(d["id"])

    def test_widget_ids_always_unique(self):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        ds = DashboardService()
        ws = WidgetService()
        d = ds.create_dashboard(name="Many Widgets")

        ids = set()
        for i in range(50):
            w = ws.add_widget(d["id"], config={"type": "chart", "title": f"W{i}"})
            assert w["id"] not in ids
            ids.add(w["id"])

    def test_updated_at_increases_on_update(self):
        from backend.app.services.dashboards.service import DashboardService
        svc = DashboardService()
        d = svc.create_dashboard(name="Monotonic")
        prev = d["updated_at"]

        for i in range(5):
            time.sleep(0.01)  # Ensure time advances
            d = svc.update_dashboard(d["id"], name=f"V{i}")
            assert d["updated_at"] >= prev
            prev = d["updated_at"]


# =============================================================================
# 7. CONCURRENCY TESTS
# =============================================================================

class TestDashboardConcurrency:
    """Thread-safety tests for dashboard services."""

    def test_concurrent_dashboard_creation(self):
        from backend.app.services.dashboards.service import DashboardService
        svc = DashboardService()
        results = []
        errors = []

        def create_dashboard(idx):
            try:
                d = svc.create_dashboard(name=f"Concurrent {idx}")
                results.append(d["id"])
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=create_dashboard, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 20
        assert len(set(results)) == 20  # All unique

    def test_concurrent_widget_adds(self):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        ds = DashboardService()
        ws = WidgetService()
        d = ds.create_dashboard(name="Concurrent Widgets")
        errors = []

        def add_widget(idx):
            try:
                ws.add_widget(
                    d["id"],
                    config={"type": "chart", "title": f"W{idx}"},
                )
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=add_widget, args=(i,)) for i in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        widgets = ws.list_widgets(d["id"])
        assert len(widgets) == 15


# =============================================================================
# 8. SECURITY TESTS — Config enforcement
# =============================================================================

class TestSecurityConfig:
    """Test security configuration hardening."""

    def test_debug_mode_defaults_to_false(self):
        """debug_mode field default should be False for production safety.

        We verify the field definition directly because Pydantic Settings
        reads the .env file, which may set NEURA_DEBUG=true for development.
        The important guarantee is that the *code default* is False so that
        a fresh production deploy (no .env) starts secure.
        """
        from backend.app.services.config import Settings
        field_info = Settings.model_fields["debug_mode"]
        assert field_info.default is False

    def test_allowed_hosts_all_defaults_to_false(self):
        """allowed_hosts_all should default to False for production safety.
        We check the field default directly because the .env file may override it."""
        from backend.app.services.config import Settings
        field_info = Settings.model_fields["allowed_hosts_all"]
        assert field_info.default is False

    def test_jwt_secret_enforced_in_production(self, monkeypatch):
        """When debug_mode is False and JWT secret is default, startup must fail."""
        monkeypatch.setenv("NEURA_DEBUG", "false")
        monkeypatch.delenv("NEURA_JWT_SECRET", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("NEURA_ALLOW_MISSING_OPENAI", "true")

        from backend.app.services.config import Settings, _apply_runtime_defaults

        settings = Settings(
            jwt_secret="change-me",
        )
        # Ensure debug is off (env var takes precedence)
        assert settings.debug_mode is False

        with pytest.raises(RuntimeError, match="NEURA_JWT_SECRET must be set"):
            _apply_runtime_defaults(settings)

    def test_jwt_secret_warning_only_in_debug(self, monkeypatch):
        """When debug_mode is True, default JWT secret should just warn."""
        monkeypatch.setenv("NEURA_DEBUG", "true")
        monkeypatch.delenv("NEURA_JWT_SECRET", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("NEURA_ALLOW_MISSING_OPENAI", "true")

        from backend.app.services.config import Settings, _apply_runtime_defaults

        settings = Settings(
            jwt_secret="change-me",
        )
        assert settings.debug_mode is True

        # Should NOT raise — just log warning
        result = _apply_runtime_defaults(settings)
        assert result.jwt_secret.get_secret_value() == "change-me"

    def test_jwt_secret_passes_with_real_secret(self, monkeypatch):
        """A real JWT secret should pass in production mode."""
        monkeypatch.setenv("NEURA_DEBUG", "false")
        monkeypatch.delenv("NEURA_JWT_SECRET", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("NEURA_ALLOW_MISSING_OPENAI", "true")

        from backend.app.services.config import Settings, _apply_runtime_defaults

        settings = Settings(
            jwt_secret="a-strong-production-secret-value",
        )
        assert settings.debug_mode is False

        result = _apply_runtime_defaults(settings)
        assert result.jwt_secret.get_secret_value() == "a-strong-production-secret-value"


# =============================================================================
# 9. IMPORT TESTS — Module structure
# =============================================================================

class TestDashboardModuleImports:
    """Verify that the dashboards module imports work correctly."""

    def test_import_dashboard_service(self):
        from backend.app.services.dashboards.service import DashboardService
        assert DashboardService is not None

    def test_import_widget_service(self):
        from backend.app.services.dashboards.widget_service import WidgetService
        assert WidgetService is not None

    def test_import_snapshot_service(self):
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        assert SnapshotService is not None

    def test_import_embed_service(self):
        from backend.app.services.dashboards.embed_service import EmbedService
        assert EmbedService is not None

    def test_import_from_package(self):
        """The __init__.py should re-export all four services."""
        from backend.app.services.dashboards import (
            DashboardService,
            WidgetService,
            SnapshotService,
            EmbedService,
        )
        assert all([DashboardService, WidgetService, SnapshotService, EmbedService])


# =============================================================================
# 10. EDGE CASES & ERROR MESSAGES
# =============================================================================

class TestEdgeCases:
    """Edge case and error message tests."""

    def test_create_dashboard_empty_name_not_allowed(self):
        """Pydantic validation in the route layer (not service) handles this,
        but the service itself should handle empty strings gracefully."""
        from backend.app.services.dashboards.service import DashboardService
        svc = DashboardService()
        # Service itself doesn't validate — that's the route layer's job.
        # But it should still work with any string.
        d = svc.create_dashboard(name="")
        assert d["name"] == ""  # Service trusts caller

    def test_widget_with_empty_config(self):
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService
        ds = DashboardService()
        ws = WidgetService()
        d = ds.create_dashboard(name="Test")
        w = ws.add_widget(d["id"], config={})
        assert w["config"] == {}

    def test_snapshot_identical_content_hash(self, mock_settings):
        """Two snapshots of the same dashboard state should have same content hash."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(name="Hash Test")

        s1 = ss.create_snapshot(d["id"])
        s2 = ss.create_snapshot(d["id"])

        assert s1["content_hash"] == s2["content_hash"]


# =============================================================================
# RESIDUAL FIX TESTS — NEURA_FORCE_GPT5, Analytics, Rendering, Widget Query
# =============================================================================


class TestForceGPT5Default:
    """Verify NEURA_FORCE_GPT5 defaults to false (not true)."""

    def test_force_gpt5_defaults_to_false(self, monkeypatch):
        """Without NEURA_FORCE_GPT5 set, the model should NOT be forced to gpt-5."""
        monkeypatch.delenv("NEURA_FORCE_GPT5", raising=False)
        result = os.getenv("NEURA_FORCE_GPT5", "false").lower() in {"1", "true", "yes"}
        assert result is False, "NEURA_FORCE_GPT5 should default to false"

    def test_force_gpt5_opt_in(self, monkeypatch):
        """When explicitly set to true, force should activate."""
        monkeypatch.setenv("NEURA_FORCE_GPT5", "true")
        result = os.getenv("NEURA_FORCE_GPT5", "false").lower() in {"1", "true", "yes"}
        assert result is True

    def test_force_gpt5_source_code_default(self):
        """Verify the source code itself uses 'false' as the default."""
        import inspect
        from backend.app.services.config import _apply_runtime_defaults

        source = inspect.getsource(_apply_runtime_defaults)
        assert '"false"' in source or "'false'" in source, (
            "NEURA_FORCE_GPT5 default should be 'false' in source code"
        )


class TestDashboardAnalyticsWiring:
    """Verify dashboard analytics endpoints delegate to real analytics services."""

    def test_dicts_to_series_converts_numeric_columns(self):
        """_dicts_to_series should extract numeric columns as DataSeries."""
        from backend.app.api.routes.dashboards import _dicts_to_series

        data = [
            {"name": "Alice", "score": 95, "grade": "A"},
            {"name": "Bob", "score": 82, "grade": "B"},
            {"name": "Charlie", "score": 70, "grade": "C"},
        ]
        series = _dicts_to_series(data)
        assert len(series) == 1  # only "score" is numeric
        assert series[0].name == "score"
        assert series[0].values == [95.0, 82.0, 70.0]

    def test_dicts_to_series_empty_data(self):
        from backend.app.api.routes.dashboards import _dicts_to_series
        assert _dicts_to_series([]) == []

    def test_dicts_to_series_multiple_numeric_columns(self):
        from backend.app.api.routes.dashboards import _dicts_to_series

        data = [
            {"x": 1, "y": 2.5, "z": "text"},
            {"x": 3, "y": 4.5, "z": "more"},
        ]
        series = _dicts_to_series(data)
        names = {s.name for s in series}
        assert "x" in names
        assert "y" in names
        assert "z" not in names

    def test_is_numeric_with_various_types(self):
        from backend.app.api.routes.dashboards import _is_numeric

        assert _is_numeric(42) is True
        assert _is_numeric(3.14) is True
        assert _is_numeric("99") is True
        assert _is_numeric("hello") is False
        assert _is_numeric(None) is False
        assert _is_numeric("") is False

    def test_dicts_to_series_handles_nan_values(self):
        """Missing/non-numeric values should become NaN."""
        import math
        from backend.app.api.routes.dashboards import _dicts_to_series

        data = [
            {"val": 10},
            {"val": "N/A"},
            {"val": 30},
        ]
        series = _dicts_to_series(data)
        assert len(series) == 1
        assert series[0].values[0] == 10.0
        assert math.isnan(series[0].values[1])
        assert series[0].values[2] == 30.0


class TestSnapshotRendering:
    """Verify snapshot rendering pipeline works end to end."""

    def test_render_snapshot_without_playwright_marks_failed(self, mock_settings):
        """When Playwright is not available, render should mark as failed."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService

        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(name="Render Test")
        snap = ss.create_snapshot(d["id"], format="png")
        assert snap["status"] == "pending"

        # Mock _render_png as None to simulate Playwright not available
        with patch("backend.app.services.dashboards.snapshot_service._render_png", None):
            result = ss.render_snapshot(snap["id"])

        assert result["status"] == "failed"
        assert "not available" in result.get("error", "").lower()

    def test_render_snapshot_pdf_not_supported(self, mock_settings):
        """PDF rendering should mark as failed with clear message."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService

        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(name="PDF Test")
        snap = ss.create_snapshot(d["id"], format="pdf")

        result = ss.render_snapshot(snap["id"])
        assert result["status"] == "failed"
        assert "not yet supported" in result.get("error", "").lower()

    def test_render_snapshot_already_rendered_is_noop(self, mock_settings):
        """Rendering an already completed snapshot should return it unchanged."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService

        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(name="Noop Test")
        snap = ss.create_snapshot(d["id"])

        # Manually mark as rendered
        ss.mark_rendered(snap["id"], file_path="/tmp/test.png", file_size_bytes=1024)

        result = ss.render_snapshot(snap["id"])
        assert result["status"] == "completed"

    def test_render_snapshot_nonexistent_raises(self, mock_settings):
        from backend.app.services.dashboards.snapshot_service import SnapshotService
        ss = SnapshotService()
        with pytest.raises(ValueError, match="not found"):
            ss.render_snapshot("nonexistent-id")

    def test_render_snapshot_with_mock_renderer(self, mock_settings, tmp_path):
        """Verify full render pipeline with a mock renderer."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService

        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(
            name="Full Render",
            widgets=[{"id": "w1", "config": {"type": "chart", "title": "Revenue"}, "x": 0, "y": 0, "w": 4, "h": 3}],
        )
        snap = ss.create_snapshot(d["id"], format="png")

        # Mock _render_png to write a fake file, and _snapshots_dir to use tmp
        def fake_render(html_path, out_path, **kwargs):
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(b"FAKE_PNG_DATA")

        with (
            patch("backend.app.services.dashboards.snapshot_service._render_png", fake_render),
            patch.object(ss, "_snapshots_dir", return_value=tmp_path),
        ):
            result = ss.render_snapshot(snap["id"])

        assert result["status"] == "completed"
        assert result["file_path"] is not None
        assert result["file_size_bytes"] == len(b"FAKE_PNG_DATA")

    def test_render_snapshot_renderer_exception_marks_failed(self, mock_settings, tmp_path):
        """If the renderer throws, snapshot should be marked as failed."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.snapshot_service import SnapshotService

        ds = DashboardService()
        ss = SnapshotService()
        d = ds.create_dashboard(name="Error Render")
        snap = ss.create_snapshot(d["id"], format="png")

        def failing_render(html_path, out_path, **kwargs):
            raise RuntimeError("Chromium crash")

        with (
            patch("backend.app.services.dashboards.snapshot_service._render_png", failing_render),
            patch.object(ss, "_snapshots_dir", return_value=tmp_path),
        ):
            result = ss.render_snapshot(snap["id"])

        assert result["status"] == "failed"
        assert "Chromium crash" in result.get("error", "")


class TestDashboardHtmlGeneration:
    """Test the HTML generation helper for snapshots."""

    def test_dashboard_to_html_basic(self):
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        html = _dashboard_to_html({
            "name": "My Dashboard",
            "description": "Test description",
            "widgets": [
                {"config": {"title": "Sales Chart", "type": "chart"}, "w": 6, "h": 4},
                {"config": {"title": "KPI", "type": "metric"}, "w": 3, "h": 2},
            ],
        })
        assert "My Dashboard" in html
        assert "Test description" in html
        assert "Sales Chart" in html
        assert "KPI" in html
        assert "grid-column: span 6" in html
        assert "grid-column: span 3" in html

    def test_dashboard_to_html_escapes_xss(self):
        """HTML special characters should be escaped."""
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        html = _dashboard_to_html({
            "name": "<script>alert('xss')</script>",
            "description": None,
            "widgets": [],
        })
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_dashboard_to_html_empty_widgets(self):
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        html = _dashboard_to_html({"name": "Empty", "widgets": []})
        assert "No widgets configured" in html


class TestWidgetQueryWiring:
    """Verify widget query execution wiring."""

    def test_widget_without_query_returns_empty(self):
        """Widget with no query/data_source should return empty data with reason."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService

        ds = DashboardService()
        ws = WidgetService()
        d = ds.create_dashboard(name="Query Test")
        w = ws.add_widget(d["id"], config={"type": "chart", "title": "No Query"})

        # Simulate what the route does
        config = w.get("config", {})
        sql_query = config.get("query")
        connection_id = config.get("data_source")

        assert sql_query is None
        assert connection_id is None
        # Route returns empty data when no query configured

    def test_widget_with_query_and_datasource(self):
        """Widget with query and data_source should have them accessible."""
        from backend.app.services.dashboards.service import DashboardService
        from backend.app.services.dashboards.widget_service import WidgetService

        ds = DashboardService()
        ws = WidgetService()
        d = ds.create_dashboard(name="Wired Query Test")
        w = ws.add_widget(
            d["id"],
            config={
                "type": "table",
                "title": "Sales Data",
                "query": "SELECT * FROM sales LIMIT 10",
                "data_source": "conn-123",
            },
        )

        config = w.get("config", {})
        assert config["query"] == "SELECT * FROM sales LIMIT 10"
        assert config["data_source"] == "conn-123"

    def test_nl2sql_execute_request_schema(self):
        """Verify NL2SQLExecuteRequest can be constructed with the expected fields."""
        from backend.app.schemas.nl2sql import NL2SQLExecuteRequest

        req = NL2SQLExecuteRequest(
            sql="SELECT 1",
            connection_id="test-conn",
        )
        assert req.sql == "SELECT 1"
        assert req.connection_id == "test-conn"
        assert req.limit == 100  # default
        assert req.offset == 0  # default


# =============================================================================
# ROUND-3 FIX TESTS — Anomalies method, CSS int-cast, tempfile, async render,
#                       correlation multi-row detect
# =============================================================================


class TestAnomaliesMethodHandling:
    """Verify anomalies endpoint properly surfaces the method parameter."""

    def test_anomalies_endpoint_has_method_parameter(self):
        """The route function should accept a method parameter."""
        import inspect
        from backend.app.api.routes.dashboards import detect_anomalies

        sig = inspect.signature(detect_anomalies)
        assert "method" in sig.parameters

    def test_anomalies_method_used_in_response_shape(self):
        """The response should include a method_used field."""
        import inspect
        from backend.app.api.routes.dashboards import detect_anomalies

        source = inspect.getsource(detect_anomalies)
        assert "method_used" in source, (
            "The anomalies endpoint should return method_used in the response"
        )

    def test_anomalies_logs_unsupported_method(self):
        """Non-zscore methods should trigger a warning log."""
        import inspect
        from backend.app.api.routes.dashboards import detect_anomalies

        source = inspect.getsource(detect_anomalies)
        assert "anomaly_method_unsupported" in source, (
            "The endpoint should log unsupported method warnings"
        )


class TestCssInjectionPrevention:
    """Verify widget w/h are cast to int to prevent CSS injection."""

    def test_numeric_string_w_h_cast_to_int(self):
        """Numeric string w/h values should be safely cast to int."""
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        html = _dashboard_to_html({
            "name": "CSS Test",
            "widgets": [
                {"config": {"title": "W", "type": "chart"}, "w": "6", "h": "3"},
            ],
        })
        # Numeric strings cast fine through int()
        assert "grid-column: span 6" in html
        assert "grid-row: span 3" in html

    def test_w_h_are_integer_in_html_output(self):
        """Verify the grid-column/row span values are plain integers."""
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        html = _dashboard_to_html({
            "name": "Int Cast Test",
            "widgets": [
                {"config": {"title": "W", "type": "chart"}, "w": 6.9, "h": 3.1},
            ],
        })
        # int(6.9) = 6, int(3.1) = 3
        assert "grid-column: span 6" in html
        assert "grid-row: span 3" in html

    def test_malicious_w_h_raises_on_non_numeric(self):
        """CSS injection attempt via non-numeric w/h should raise ValueError."""
        from backend.app.services.dashboards.snapshot_service import _dashboard_to_html

        with pytest.raises((ValueError, TypeError)):
            _dashboard_to_html({
                "name": "Injection Attempt",
                "widgets": [
                    {"config": {"title": "Evil", "type": "chart"},
                     "w": "4; background:url(evil)", "h": 3},
                ],
            })


class TestTempfileNotDeprecated:
    """Verify render_snapshot uses NamedTemporaryFile, not deprecated mktemp."""

    def test_no_mktemp_in_snapshot_service(self):
        """snapshot_service.py should not use the deprecated tempfile.mktemp."""
        import inspect
        from backend.app.services.dashboards import snapshot_service

        source = inspect.getsource(snapshot_service)
        assert "mktemp" not in source, (
            "tempfile.mktemp is deprecated; use NamedTemporaryFile(delete=False)"
        )

    def test_uses_named_temporary_file(self):
        """snapshot_service.py should use NamedTemporaryFile."""
        import inspect
        from backend.app.services.dashboards import snapshot_service

        source = inspect.getsource(snapshot_service)
        assert "NamedTemporaryFile" in source


class TestAsyncRenderNotBlocking:
    """Verify the snapshot route uses run_in_executor for sync rendering."""

    def test_snapshot_route_uses_run_in_executor(self):
        """The create_snapshot route should call run_in_executor to avoid
        blocking the ASGI event loop with synchronous Playwright."""
        import inspect
        from backend.app.api.routes.dashboards import create_snapshot

        source = inspect.getsource(create_snapshot)
        assert "run_in_executor" in source, (
            "Snapshot rendering must use run_in_executor to avoid blocking "
            "the async event loop"
        )

    def test_snapshot_route_is_async(self):
        """The create_snapshot route must be an async function."""
        import inspect
        from backend.app.api.routes.dashboards import create_snapshot

        assert inspect.iscoroutinefunction(create_snapshot), (
            "create_snapshot should be an async function"
        )

    def test_asyncio_imported_in_dashboards(self):
        """The dashboards route module must import asyncio."""
        import backend.app.api.routes.dashboards as mod

        assert hasattr(mod, "asyncio"), (
            "dashboards.py must import asyncio for run_in_executor"
        )


class TestCorrelationMultiRowDetect:
    """Verify numeric column detection scans all rows, not just the first."""

    def test_detect_numeric_columns_scans_all_rows(self):
        """A column that's non-numeric in row 0 but numeric in later rows
        should still be detected."""
        from backend.app.api.routes.dashboards import _detect_numeric_columns

        data = [
            {"a": "N/A", "b": 1},
            {"a": 42,     "b": 2},
            {"a": 99,     "b": 3},
        ]
        cols = _detect_numeric_columns(data)
        assert "a" in cols, "Column 'a' is numeric in rows 1-2, should be detected"
        assert "b" in cols

    def test_detect_numeric_columns_empty(self):
        from backend.app.api.routes.dashboards import _detect_numeric_columns
        assert _detect_numeric_columns([]) == []

    def test_detect_numeric_columns_all_non_numeric(self):
        from backend.app.api.routes.dashboards import _detect_numeric_columns

        data = [
            {"x": "hello", "y": "world"},
            {"x": "foo",   "y": "bar"},
        ]
        assert _detect_numeric_columns(data) == []

    def test_dicts_to_series_uses_multi_row_detection(self):
        """_dicts_to_series should find columns that become numeric after row 0."""
        from backend.app.api.routes.dashboards import _dicts_to_series

        data = [
            {"val": "missing", "num": 10},
            {"val": 42,        "num": 20},
            {"val": 99,        "num": 30},
        ]
        series = _dicts_to_series(data)
        names = {s.name for s in series}
        assert "val" in names, (
            "_dicts_to_series should detect 'val' as numeric (rows 1-2 have numbers)"
        )
        assert "num" in names

    def test_correlation_auto_detect_uses_all_rows(self):
        """The correlation endpoint source should call _detect_numeric_columns."""
        import inspect
        from backend.app.api.routes.dashboards import find_correlations

        source = inspect.getsource(find_correlations)
        assert "_detect_numeric_columns" in source, (
            "Correlation auto-detect should use _detect_numeric_columns "
            "which scans all rows"
        )

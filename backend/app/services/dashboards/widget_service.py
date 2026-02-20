"""
Widget Service - Dashboard widget management via StateStore.

Handles adding, updating, removing, and reordering widgets within
dashboards.  Widget data is stored inside the parent dashboard record
(``dashboard["widgets"]`` list) for atomicity.

Design Principles:
- Widgets are embedded in dashboard records (no separate orphan risk)
- Widget IDs are UUID4 strings
- Position/size validated within sensible bounds
- Thread-safe via StateStore transactions
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import state_store

logger = logging.getLogger("neura.dashboards.widget_service")

# Grid constraints (12-column layout)
MAX_GRID_COLS = 12
MAX_GRID_ROWS = 100
MIN_WIDGET_SIZE = 1
MAX_WIDGET_W = 12
MAX_WIDGET_H = 20


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


class WidgetService:
    """Manage widgets embedded within dashboard records."""

    # ── Add widget ──────────────────────────────────────────────────────

    def add_widget(
        self,
        dashboard_id: str,
        *,
        config: Dict[str, Any],
        x: int = 0,
        y: int = 0,
        w: int = 4,
        h: int = 3,
    ) -> Dict[str, Any]:
        """Add a widget to a dashboard.  Returns the new widget dict.

        Raises ``ValueError`` if the dashboard does not exist.
        """
        widget_id = str(uuid.uuid4())
        widget: Dict[str, Any] = {
            "id": widget_id,
            "config": config,
            "x": _clamp(x, 0, MAX_GRID_COLS - 1),
            "y": _clamp(y, 0, MAX_GRID_ROWS - 1),
            "w": _clamp(w, MIN_WIDGET_SIZE, MAX_WIDGET_W),
            "h": _clamp(h, MIN_WIDGET_SIZE, MAX_WIDGET_H),
        }

        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            dashboard = dashboards.get(dashboard_id)
            if dashboard is None:
                raise ValueError(f"Dashboard {dashboard_id} not found")

            dashboard.setdefault("widgets", []).append(widget)
            dashboard["updated_at"] = _now_iso()
            state["dashboards"][dashboard_id] = dashboard

        logger.info(
            "widget_added",
            extra={
                "event": "widget_added",
                "dashboard_id": dashboard_id,
                "widget_id": widget_id,
            },
        )
        return widget

    # ── Update widget ───────────────────────────────────────────────────

    def update_widget(
        self,
        dashboard_id: str,
        widget_id: str,
        *,
        config: Optional[Dict[str, Any]] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a widget.  Returns updated widget or ``None`` if not found."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            dashboard = dashboards.get(dashboard_id)
            if dashboard is None:
                return None

            widgets: List[Dict[str, Any]] = dashboard.get("widgets", [])
            for widget in widgets:
                if widget.get("id") == widget_id:
                    if config is not None:
                        widget["config"] = config
                    if x is not None:
                        widget["x"] = _clamp(x, 0, MAX_GRID_COLS - 1)
                    if y is not None:
                        widget["y"] = _clamp(y, 0, MAX_GRID_ROWS - 1)
                    if w is not None:
                        widget["w"] = _clamp(w, MIN_WIDGET_SIZE, MAX_WIDGET_W)
                    if h is not None:
                        widget["h"] = _clamp(h, MIN_WIDGET_SIZE, MAX_WIDGET_H)

                    dashboard["updated_at"] = _now_iso()
                    state["dashboards"][dashboard_id] = dashboard

                    logger.info(
                        "widget_updated",
                        extra={
                            "event": "widget_updated",
                            "dashboard_id": dashboard_id,
                            "widget_id": widget_id,
                        },
                    )
                    return widget

        return None

    # ── Delete widget ───────────────────────────────────────────────────

    def delete_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove a widget.  Returns ``True`` if removed, ``False`` if absent."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            dashboard = dashboards.get(dashboard_id)
            if dashboard is None:
                return False

            original = dashboard.get("widgets", [])
            filtered = [w for w in original if w.get("id") != widget_id]

            if len(filtered) == len(original):
                return False

            dashboard["widgets"] = filtered
            dashboard["updated_at"] = _now_iso()
            state["dashboards"][dashboard_id] = dashboard

        logger.info(
            "widget_deleted",
            extra={
                "event": "widget_deleted",
                "dashboard_id": dashboard_id,
                "widget_id": widget_id,
            },
        )
        return True

    # ── Get widget ──────────────────────────────────────────────────────

    def get_widget(
        self, dashboard_id: str, widget_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return a single widget from a dashboard."""
        with state_store.transaction() as state:
            dashboard = state.get("dashboards", {}).get(dashboard_id)
            if dashboard is None:
                return None
            for widget in dashboard.get("widgets", []):
                if widget.get("id") == widget_id:
                    return widget
        return None

    # ── List widgets ────────────────────────────────────────────────────

    def list_widgets(self, dashboard_id: str) -> Optional[List[Dict[str, Any]]]:
        """Return all widgets for a dashboard, or ``None`` if dashboard missing."""
        with state_store.transaction() as state:
            dashboard = state.get("dashboards", {}).get(dashboard_id)
            if dashboard is None:
                return None
            return list(dashboard.get("widgets", []))

    # ── Reorder widgets ─────────────────────────────────────────────────

    def reorder_widgets(
        self,
        dashboard_id: str,
        widget_ids: List[str],
    ) -> bool:
        """Reorder widgets according to the provided ID list.

        Widget IDs not in ``widget_ids`` are appended at the end.
        Returns ``False`` if dashboard not found.
        """
        with state_store.transaction() as state:
            dashboard = state.get("dashboards", {}).get(dashboard_id)
            if dashboard is None:
                return False

            existing = {w["id"]: w for w in dashboard.get("widgets", [])}
            ordered: List[Dict[str, Any]] = []
            seen: set[str] = set()

            for wid in widget_ids:
                if wid in existing and wid not in seen:
                    ordered.append(existing[wid])
                    seen.add(wid)

            # Append any widgets not mentioned in the new order
            for wid, w in existing.items():
                if wid not in seen:
                    ordered.append(w)

            dashboard["widgets"] = ordered
            dashboard["updated_at"] = _now_iso()
            state["dashboards"][dashboard_id] = dashboard

        return True

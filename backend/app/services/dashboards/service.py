"""
Dashboard Service - Persistent dashboard CRUD via StateStore.

Replaces the in-memory dict storage from the routes layer with proper
state-store-backed persistence.  All dashboards survive server restarts.

Design Principles:
- State store atomic transactions for all writes
- Thread-safe via StateStore's internal RLock
- Timestamps are ISO-8601 UTC, generated server-side
- Dashboard IDs are UUID4 strings
"""
from __future__ import annotations

import copy
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import state_store

logger = logging.getLogger("neura.dashboards.service")


def _now_iso() -> str:
    """Return current UTC time as ISO string (second precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class DashboardService:
    """Persistent dashboard CRUD backed by the NeuraReport state store."""

    # ── Create ──────────────────────────────────────────────────────────

    def create_dashboard(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        theme: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new dashboard and persist it.

        Returns the full dashboard dict including generated ``id`` and
        timestamps.
        """
        dashboard_id = str(uuid.uuid4())
        now = _now_iso()

        dashboard: Dict[str, Any] = {
            "id": dashboard_id,
            "name": name,
            "description": description,
            "widgets": widgets or [],
            "filters": filters or [],
            "theme": theme,
            "refresh_interval": None,
            "metadata": {},
            "created_at": now,
            "updated_at": now,
        }

        with state_store.transaction() as state:
            state.setdefault("dashboards", {})
            state["dashboards"][dashboard_id] = dashboard

        logger.info(
            "dashboard_created",
            extra={"event": "dashboard_created", "dashboard_id": dashboard_id, "dashboard_name": name},
        )
        return dashboard

    # ── Read ────────────────────────────────────────────────────────────

    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Return a single dashboard by ID, or ``None`` if missing."""
        with state_store.transaction() as state:
            dashboard = state.get("dashboards", {}).get(dashboard_id)
            if dashboard is None:
                return None
            result = copy.deepcopy(dashboard)
            result.setdefault("metadata", {})
            return result

    def list_dashboards(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Return paginated list of dashboards, newest-updated first."""
        with state_store.transaction() as state:
            dashboards = copy.deepcopy(list(state.get("dashboards", {}).values()))

        # Ensure every dashboard has a metadata key (backfill for pre-existing)
        for d in dashboards:
            d.setdefault("metadata", {})
        dashboards.sort(key=lambda d: d.get("updated_at", ""), reverse=True)
        return {
            "dashboards": dashboards[offset : offset + limit],
            "total": len(dashboards),
            "limit": limit,
            "offset": offset,
        }

    # ── Update ──────────────────────────────────────────────────────────

    def update_dashboard(
        self,
        dashboard_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        theme: Optional[str] = None,
        refresh_interval: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing dashboard.  Returns ``None`` if not found."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            dashboard = dashboards.get(dashboard_id)
            if dashboard is None:
                return None

            if name is not None:
                dashboard["name"] = name
            if description is not None:
                dashboard["description"] = description
            if widgets is not None:
                dashboard["widgets"] = widgets
            if filters is not None:
                dashboard["filters"] = filters
            if theme is not None:
                dashboard["theme"] = theme
            if refresh_interval is not None:
                dashboard["refresh_interval"] = refresh_interval
            if metadata is not None:
                dashboard["metadata"] = metadata

            dashboard["updated_at"] = _now_iso()
            state["dashboards"][dashboard_id] = dashboard

        logger.info(
            "dashboard_updated",
            extra={"event": "dashboard_updated", "dashboard_id": dashboard_id},
        )
        return dashboard

    # ── Delete ──────────────────────────────────────────────────────────

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard.  Returns ``True`` if removed, ``False`` if absent."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            if dashboard_id not in dashboards:
                return False
            del dashboards[dashboard_id]

            # Also remove any widgets that reference this dashboard
            widgets = state.get("dashboard_widgets", {})
            orphan_ids = [
                wid for wid, w in widgets.items()
                if w.get("dashboard_id") == dashboard_id
            ]
            for wid in orphan_ids:
                del widgets[wid]

            # Remove from favorites
            favs = state.get("favorites", {})
            dash_favs = favs.get("dashboards", [])
            if dashboard_id in dash_favs:
                dash_favs.remove(dashboard_id)

        logger.info(
            "dashboard_deleted",
            extra={"event": "dashboard_deleted", "dashboard_id": dashboard_id},
        )
        return True

    # ── Favorites ───────────────────────────────────────────────────────

    def toggle_favorite(self, dashboard_id: str) -> bool:
        """Toggle favorite status.  Returns new ``is_favorite`` state."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            if dashboard_id not in dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")

            favs = state.setdefault("favorites", {})
            dash_favs: list = favs.setdefault("dashboards", [])

            if dashboard_id in dash_favs:
                dash_favs.remove(dashboard_id)
                is_fav = False
            else:
                dash_favs.append(dashboard_id)
                is_fav = True

        return is_fav

    def is_favorite(self, dashboard_id: str) -> bool:
        """Check whether a dashboard is favourited."""
        with state_store.transaction() as state:
            favs = state.get("favorites", {})
            return dashboard_id in favs.get("dashboards", [])

    # ── Templates ────────────────────────────────────────────────────────

    def list_templates(self) -> List[Dict[str, Any]]:
        """Return all saved dashboard templates."""
        with state_store.transaction() as state:
            templates = state.get("dashboard_templates", {})
            return copy.deepcopy(list(templates.values()))

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Return a single dashboard template by ID, or ``None``."""
        with state_store.transaction() as state:
            template = state.get("dashboard_templates", {}).get(template_id)
            return copy.deepcopy(template) if template else None

    def save_template(self, template: Dict[str, Any]) -> None:
        """Persist a dashboard template."""
        with state_store.transaction() as state:
            state.setdefault("dashboard_templates", {})
            state["dashboard_templates"][template["id"]] = template
        logger.info(
            "dashboard_template_saved",
            extra={"event": "dashboard_template_saved", "template_id": template["id"]},
        )

    # ── Stats ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Return dashboard-related statistics."""
        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            total_widgets = sum(
                len(d.get("widgets", []))
                for d in dashboards.values()
            )
            favs = state.get("favorites", {})
            total_favs = sum(len(v) for v in favs.values())

        return {
            "total_dashboards": len(dashboards),
            "total_widgets": total_widgets,
            "total_favorites": total_favs,
        }

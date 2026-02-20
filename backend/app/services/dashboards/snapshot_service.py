"""
Snapshot Service - Dashboard snapshot generation and storage.

Generates point-in-time snapshots of dashboards for export, sharing,
and audit trails.  Snapshots are stored as metadata in the state store;
the actual rendered bytes (PNG/PDF) are stored on the filesystem under
the uploads directory.

Design Principles:
- Snapshot metadata persisted in state store
- Rendered files stored on disk (not in JSON state)
- Snapshots are immutable once created
- Retention policy: keep last N snapshots per dashboard
"""
from __future__ import annotations

import hashlib
import html as html_mod
import json
import logging
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import state_store
from backend.app.services.config import get_settings

try:
    from backend.app.services.utils.render import render_html_to_png as _render_png
except ImportError:  # pragma: no cover
    _render_png = None  # type: ignore[assignment]

logger = logging.getLogger("neura.dashboards.snapshot_service")

MAX_SNAPSHOTS_PER_DASHBOARD = 20


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class SnapshotService:
    """Generate and manage dashboard snapshots."""

    def _snapshots_dir(self) -> Path:
        """Return (and lazily create) the snapshots directory."""
        settings = get_settings()
        base = settings.uploads_dir / "dashboard_snapshots"
        base.mkdir(parents=True, exist_ok=True)
        return base

    # ── Create snapshot ──────────────────────────────────────────────────

    def create_snapshot(
        self,
        dashboard_id: str,
        *,
        format: str = "png",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a snapshot record for a dashboard.

        The actual rendering (Playwright / wkhtmltoimage) is delegated
        to the render service if available.  This method stores the
        metadata and returns it immediately so callers can poll or
        stream the result.

        Raises ``ValueError`` if the dashboard does not exist.
        """
        if format not in ("png", "pdf"):
            raise ValueError(f"Unsupported snapshot format: {format}")

        snapshot_id = str(uuid.uuid4())
        now = _now_iso()

        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            dashboard = dashboards.get(dashboard_id)
            if dashboard is None:
                raise ValueError(f"Dashboard {dashboard_id} not found")

            # Capture current dashboard state as frozen data
            frozen = json.loads(json.dumps(dashboard, default=str))

            # Compute a content hash so identical dashboards produce
            # the same fingerprint (useful for deduplication).
            content_hash = hashlib.sha256(
                json.dumps(frozen, sort_keys=True).encode()
            ).hexdigest()[:16]

            snapshot: Dict[str, Any] = {
                "id": snapshot_id,
                "dashboard_id": dashboard_id,
                "title": title or f"Snapshot of {dashboard.get('name', 'Dashboard')}",
                "format": format,
                "status": "pending",
                "content_hash": content_hash,
                "file_path": None,
                "file_size_bytes": None,
                "dashboard_data": frozen,
                "created_at": now,
            }

            snapshots = state.setdefault("dashboard_snapshots", {})
            snapshots[snapshot_id] = snapshot

            # Enforce retention limit per dashboard
            dash_snaps = [
                s for s in snapshots.values()
                if s.get("dashboard_id") == dashboard_id
            ]
            if len(dash_snaps) > MAX_SNAPSHOTS_PER_DASHBOARD:
                dash_snaps.sort(key=lambda s: s.get("created_at", ""))
                to_remove = dash_snaps[: len(dash_snaps) - MAX_SNAPSHOTS_PER_DASHBOARD]
                for old in to_remove:
                    snapshots.pop(old["id"], None)

        logger.info(
            "snapshot_created",
            extra={
                "event": "snapshot_created",
                "snapshot_id": snapshot_id,
                "dashboard_id": dashboard_id,
                "format": format,
            },
        )
        return snapshot

    # ── Mark rendered ───────────────────────────────────────────────────

    def mark_rendered(
        self,
        snapshot_id: str,
        *,
        file_path: str,
        file_size_bytes: int,
    ) -> Optional[Dict[str, Any]]:
        """Update snapshot after rendering completes.

        Called by the render pipeline once the file is written to disk.
        """
        with state_store.transaction() as state:
            snapshots = state.get("dashboard_snapshots", {})
            snapshot = snapshots.get(snapshot_id)
            if snapshot is None:
                return None

            snapshot["status"] = "completed"
            snapshot["file_path"] = file_path
            snapshot["file_size_bytes"] = file_size_bytes
            state["dashboard_snapshots"][snapshot_id] = snapshot

        return snapshot

    def mark_failed(self, snapshot_id: str, *, error: str) -> Optional[Dict[str, Any]]:
        """Mark a snapshot as failed."""
        with state_store.transaction() as state:
            snapshots = state.get("dashboard_snapshots", {})
            snapshot = snapshots.get(snapshot_id)
            if snapshot is None:
                return None

            snapshot["status"] = "failed"
            snapshot["error"] = error
            state["dashboard_snapshots"][snapshot_id] = snapshot

        return snapshot

    # ── Read ────────────────────────────────────────────────────────────

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Return a snapshot by ID."""
        with state_store.transaction() as state:
            return state.get("dashboard_snapshots", {}).get(snapshot_id)

    def list_snapshots(
        self,
        dashboard_id: str,
        *,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Return snapshots for a dashboard, newest first."""
        with state_store.transaction() as state:
            all_snaps = state.get("dashboard_snapshots", {}).values()
            filtered = [
                s for s in all_snaps
                if s.get("dashboard_id") == dashboard_id
            ]

        filtered.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return filtered[:limit]

    # ── Delete ──────────────────────────────────────────────────────────

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot record and its file (if any)."""
        file_path: Optional[str] = None

        with state_store.transaction() as state:
            snapshots = state.get("dashboard_snapshots", {})
            snapshot = snapshots.pop(snapshot_id, None)
            if snapshot is None:
                return False
            file_path = snapshot.get("file_path")

        # Best-effort file cleanup
        if file_path:
            try:
                p = Path(file_path)
                if p.exists():
                    p.unlink()
            except OSError as exc:
                logger.warning(
                    "snapshot_file_cleanup_failed",
                    extra={"snapshot_id": snapshot_id, "error": str(exc)},
                )

        return True

    # ── Render ──────────────────────────────────────────────────────────

    def render_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Render a pending snapshot to its target format.

        Generates a simple HTML representation of the dashboard,
        renders it to PNG via Playwright (if available), and updates
        the snapshot record.

        Returns the updated snapshot dict.
        Raises ``RuntimeError`` if the renderer is unavailable.
        """
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot is None:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        if snapshot.get("status") != "pending":
            return snapshot  # already rendered or failed

        fmt = snapshot.get("format", "png")
        if fmt != "png":
            self.mark_failed(snapshot_id, error=f"Rendering format '{fmt}' not yet supported (only PNG)")
            return self.get_snapshot(snapshot_id) or snapshot

        if _render_png is None:
            self.mark_failed(snapshot_id, error="Playwright renderer not available")
            return self.get_snapshot(snapshot_id) or snapshot

        dashboard_data = snapshot.get("dashboard_data", {})
        out_dir = self._snapshots_dir()
        out_path = out_dir / f"{snapshot_id}.png"

        # Generate HTML to a temp file, render, then clean up
        html_content = _dashboard_to_html(dashboard_data)
        tmp_html = None
        try:
            tmp_fd = tempfile.NamedTemporaryFile(
                suffix=".html", dir=str(out_dir), delete=False, mode="w", encoding="utf-8",
            )
            tmp_html = Path(tmp_fd.name)
            tmp_fd.write(html_content)
            tmp_fd.close()

            _render_png(tmp_html, out_path)

            file_size = out_path.stat().st_size
            self.mark_rendered(
                snapshot_id,
                file_path=str(out_path),
                file_size_bytes=file_size,
            )
            logger.info(
                "snapshot_rendered",
                extra={
                    "event": "snapshot_rendered",
                    "snapshot_id": snapshot_id,
                    "file_size_bytes": file_size,
                },
            )
        except Exception as exc:
            self.mark_failed(snapshot_id, error="Snapshot rendering failed")
            logger.exception(
                "snapshot_render_failed",
                extra={
                    "event": "snapshot_render_failed",
                    "snapshot_id": snapshot_id,
                },
            )
        finally:
            if tmp_html and tmp_html.exists():
                try:
                    tmp_html.unlink()
                except OSError:
                    pass

        return self.get_snapshot(snapshot_id) or snapshot


def _dashboard_to_html(dashboard_data: Dict[str, Any]) -> str:
    """Generate a minimal HTML representation of a dashboard for rendering."""
    name = html_mod.escape(dashboard_data.get("name", "Dashboard"))
    desc = html_mod.escape(dashboard_data.get("description", "") or "")
    widgets = dashboard_data.get("widgets", [])

    widget_cards = []
    for w in widgets:
        config = w.get("config", {})
        w_title = html_mod.escape(config.get("title", "Widget"))
        w_type = html_mod.escape(config.get("type", "unknown"))
        # Cast to int to prevent CSS injection via non-integer values
        col_span = int(w.get("w", 4))
        row_span = int(w.get("h", 3))
        widget_cards.append(
            f'<div class="widget" style="grid-column: span {col_span}; '
            f'grid-row: span {row_span};">'
            f'<h3>{w_title}</h3>'
            f'<span class="badge">{w_type}</span>'
            f'</div>'
        )

    widgets_html = "\n".join(widget_cards) if widget_cards else "<p>No widgets configured.</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         margin: 40px; background: #f5f5f5; color: #333; }}
  h1 {{ margin-bottom: 4px; }}
  .desc {{ color: #666; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(12, 1fr);
           gap: 16px; }}
  .widget {{ background: #fff; border: 1px solid #ddd; border-radius: 8px;
             padding: 16px; min-height: 80px; }}
  .widget h3 {{ margin: 0 0 8px; font-size: 14px; }}
  .badge {{ display: inline-block; background: #e0e7ff; color: #3730a3;
            padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
</style>
</head>
<body>
<h1>{name}</h1>
<p class="desc">{desc}</p>
<div class="grid">
{widgets_html}
</div>
</body>
</html>"""

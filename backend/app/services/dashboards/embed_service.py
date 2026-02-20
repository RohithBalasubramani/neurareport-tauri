"""
Embed Service - Dashboard embedding via short-lived tokens.

Generates signed tokens that allow read-only dashboard access
without API-key authentication.  Tokens are stored in state so they
can be revoked and their usage audited.

Design Principles:
- HMAC-SHA256 signed tokens (no external JWT library required)
- Configurable TTL (1-720 hours)
- Per-dashboard token revocation
- Usage counting for analytics
- Tokens validated by constant-time comparison
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import state_store
from backend.app.services.config import get_settings

logger = logging.getLogger("neura.dashboards.embed_service")

MAX_TOKENS_PER_DASHBOARD = 50


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


class EmbedService:
    """Generate and validate dashboard embed tokens."""

    def _signing_key(self) -> str:
        """Return the HMAC signing key (derived from JWT secret)."""
        settings = get_settings()
        return settings.jwt_secret.get_secret_value()

    def _sign_token(self, payload: str) -> str:
        """Create HMAC-SHA256 signature for a payload string."""
        key = self._signing_key().encode("utf-8")
        return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    # ── Generate token ──────────────────────────────────────────────────

    def generate_embed_token(
        self,
        dashboard_id: str,
        *,
        expires_hours: int = 24,
        label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a new embed token for a dashboard.

        Returns a dict containing the token, embed URL, and metadata.
        Raises ``ValueError`` if the dashboard does not exist or
        ``expires_hours`` is out of range.
        """
        if not (1 <= expires_hours <= 720):
            raise ValueError("expires_hours must be between 1 and 720")

        token_id = str(uuid.uuid4())
        raw_token = secrets.token_urlsafe(32)
        now = _now_dt()
        expires_at = now + timedelta(hours=expires_hours)

        # Sign the token so we can verify without a DB lookup (optional fast path)
        signature = self._sign_token(f"{token_id}:{raw_token}:{dashboard_id}")
        full_token = f"{token_id}.{raw_token}.{signature[:16]}"

        with state_store.transaction() as state:
            dashboards = state.get("dashboards", {})
            if dashboard_id not in dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")

            tokens = state.setdefault("dashboard_embed_tokens", {})

            record: Dict[str, Any] = {
                "id": token_id,
                "dashboard_id": dashboard_id,
                "token_hash": hashlib.sha256(full_token.encode()).hexdigest(),
                "label": label or f"Embed token for {dashboards[dashboard_id].get('name', 'Dashboard')}",
                "expires_at": expires_at.isoformat(),
                "created_at": _now_iso(),
                "revoked": False,
                "access_count": 0,
                "last_accessed_at": None,
            }
            tokens[token_id] = record

            # Enforce per-dashboard token limit (remove oldest expired first)
            dash_tokens = [
                t for t in tokens.values()
                if t.get("dashboard_id") == dashboard_id
            ]
            if len(dash_tokens) > MAX_TOKENS_PER_DASHBOARD:
                dash_tokens.sort(key=lambda t: t.get("created_at", ""))
                to_remove = dash_tokens[: len(dash_tokens) - MAX_TOKENS_PER_DASHBOARD]
                for old in to_remove:
                    tokens.pop(old["id"], None)

        logger.info(
            "embed_token_generated",
            extra={
                "event": "embed_token_generated",
                "token_id": token_id,
                "dashboard_id": dashboard_id,
                "expires_hours": expires_hours,
            },
        )

        return {
            "token_id": token_id,
            "embed_token": full_token,
            "embed_url": f"/embed/dashboard/{dashboard_id}?token={full_token}",
            "expires_at": expires_at.isoformat(),
            "expires_hours": expires_hours,
            "dashboard_id": dashboard_id,
        }

    # ── Validate token ──────────────────────────────────────────────────

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an embed token.

        Returns the token record if valid, ``None`` if invalid/expired/revoked.
        Also increments the access counter.
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        with state_store.transaction() as state:
            tokens = state.get("dashboard_embed_tokens", {})

            for record in tokens.values():
                if not hmac.compare_digest(record.get("token_hash", ""), token_hash):
                    continue

                # Found matching token
                if record.get("revoked"):
                    return None

                expires_at = record.get("expires_at", "")
                if expires_at:
                    try:
                        exp_dt = datetime.fromisoformat(expires_at)
                        if _now_dt() > exp_dt:
                            return None
                    except (ValueError, TypeError):
                        return None

                # Update access stats
                record["access_count"] = record.get("access_count", 0) + 1
                record["last_accessed_at"] = _now_iso()

                return {
                    "token_id": record["id"],
                    "dashboard_id": record["dashboard_id"],
                    "label": record.get("label"),
                    "expires_at": record.get("expires_at"),
                }

        return None

    # ── Revoke token ────────────────────────────────────────────────────

    def revoke_token(self, token_id: str) -> bool:
        """Revoke an embed token.  Returns ``True`` if revoked."""
        with state_store.transaction() as state:
            tokens = state.get("dashboard_embed_tokens", {})
            record = tokens.get(token_id)
            if record is None:
                return False
            record["revoked"] = True

        logger.info(
            "embed_token_revoked",
            extra={"event": "embed_token_revoked", "token_id": token_id},
        )
        return True

    def revoke_all_for_dashboard(self, dashboard_id: str) -> int:
        """Revoke all tokens for a dashboard.  Returns count revoked."""
        count = 0
        with state_store.transaction() as state:
            tokens = state.get("dashboard_embed_tokens", {})
            for record in tokens.values():
                if (
                    record.get("dashboard_id") == dashboard_id
                    and not record.get("revoked")
                ):
                    record["revoked"] = True
                    count += 1
        return count

    # ── List tokens ─────────────────────────────────────────────────────

    def list_tokens(
        self,
        dashboard_id: str,
        *,
        include_revoked: bool = False,
    ) -> List[Dict[str, Any]]:
        """List embed tokens for a dashboard."""
        with state_store.transaction() as state:
            tokens = state.get("dashboard_embed_tokens", {}).values()
            filtered = [
                {
                    "token_id": t["id"],
                    "dashboard_id": t["dashboard_id"],
                    "label": t.get("label"),
                    "expires_at": t.get("expires_at"),
                    "revoked": t.get("revoked", False),
                    "access_count": t.get("access_count", 0),
                    "created_at": t.get("created_at"),
                    "last_accessed_at": t.get("last_accessed_at"),
                }
                for t in tokens
                if t.get("dashboard_id") == dashboard_id
                and (include_revoked or not t.get("revoked"))
            ]

        filtered.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        return filtered

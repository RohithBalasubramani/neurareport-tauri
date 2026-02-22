"""User settings and preferences API routes."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

logger = logging.getLogger("neura.settings")

router = APIRouter(dependencies=[Depends(require_api_key)])


class UpdatePreferencesRequest(BaseModel):
    updates: Optional[Dict[str, Any]] = None
    # Also accept flat keys for convenience (M11)
    timezone: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    default_connection: Optional[str] = None


def _collect_updates(request: UpdatePreferencesRequest) -> dict:
    """Merge updates dict and flat keys into a single dict."""
    updates = dict(request.updates or {})
    for key in ("timezone", "theme", "language", "default_connection"):
        val = getattr(request, key, None)
        if val is not None:
            updates[key] = val
    return updates


@router.get("")
async def get_settings():
    """Get current user preferences and settings."""
    prefs = state_access.get_user_preferences()
    return {"settings": prefs}


@router.put("")
async def update_settings(request: UpdatePreferencesRequest):
    """Update user preferences. Accepts {"updates": {...}} or flat keys."""
    updates = _collect_updates(request)
    if not updates:
        return {"settings": state_access.get_user_preferences()}
    updated = state_access.update_user_preferences(updates)
    return {"settings": updated}


# Alias router: /api/v1/preferences → same as /api/v1/settings (H3)
preferences_router = APIRouter(dependencies=[Depends(require_api_key)])


@preferences_router.get("")
async def get_preferences():
    """Get current user preferences (alias for /settings)."""
    prefs = state_access.get_user_preferences()
    return {"preferences": prefs}


@preferences_router.put("")
async def update_preferences(request: UpdatePreferencesRequest):
    """Update user preferences (alias for /settings)."""
    updates = _collect_updates(request)
    if not updates:
        return {"preferences": state_access.get_user_preferences()}
    updated = state_access.update_user_preferences(updates)
    return {"preferences": updated}


# =============================================================================
# SMTP / Email configuration endpoints
# =============================================================================

class SmtpSettingsRequest(BaseModel):
    host: Optional[str] = None
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    sender: Optional[str] = None
    use_tls: bool = True


@router.get("/smtp")
async def get_smtp_settings():
    """Get saved SMTP settings (password masked)."""
    prefs = state_access.get_user_preferences()
    smtp = dict(prefs.get("smtp") or {})
    # Mask password in response
    if smtp.get("password"):
        smtp["password_set"] = True
        smtp["password"] = "••••••••"
    else:
        smtp["password_set"] = False
    return {"smtp": smtp}


@router.put("/smtp")
async def save_smtp_settings(request: SmtpSettingsRequest):
    """Save SMTP settings to persistent state store and reload mailer."""
    smtp_data: Dict[str, Any] = {
        "host": (request.host or "").strip() or None,
        "port": request.port,
        "username": (request.username or "").strip() or None,
        "sender": (request.sender or "").strip() or None,
        "use_tls": request.use_tls,
    }
    # Only update password if a real value was provided (not the mask)
    if request.password and request.password != "••••••••":
        smtp_data["password"] = request.password
    else:
        # Keep existing password
        existing = (state_access.get_user_preferences().get("smtp") or {})
        if existing.get("password"):
            smtp_data["password"] = existing["password"]

    state_access.set_user_preference("smtp", smtp_data)
    logger.info("smtp_settings_saved", extra={"event": "smtp_settings_saved", "host": smtp_data.get("host")})

    # Reload mailer config from the updated state store
    from backend.app.services.utils.mailer import refresh_mailer_config
    refresh_mailer_config()

    # Return masked response
    resp = dict(smtp_data)
    if resp.get("password"):
        resp["password_set"] = True
        resp["password"] = "••••••••"
    else:
        resp["password_set"] = False
    return {"smtp": resp, "message": "SMTP settings saved"}


@router.post("/smtp/test")
async def test_smtp_settings():
    """Test current SMTP connection."""
    from backend.app.services.utils.mailer import _get_config
    import smtplib
    import ssl

    config = _get_config()
    if not config.enabled or not config.host:
        return {"status": "not_configured", "message": "SMTP not configured. Save settings first."}

    try:
        if config.use_tls:
            with smtplib.SMTP(config.host, config.port, timeout=10) as client:
                client.ehlo()
                context = ssl.create_default_context()
                client.starttls(context=context)
                client.ehlo()
                if config.username and config.password:
                    client.login(config.username, config.password)
                return {"status": "connected", "message": "SMTP connection successful"}
        else:
            with smtplib.SMTP(config.host, config.port, timeout=10) as client:
                client.ehlo()
                if config.username and config.password:
                    client.login(config.username, config.password)
                return {"status": "connected", "message": "SMTP connection successful"}
    except smtplib.SMTPAuthenticationError:
        return {"status": "auth_failed", "message": "Authentication failed. Check username/password."}
    except smtplib.SMTPConnectError:
        return {"status": "connection_failed", "message": "Could not connect to SMTP server."}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {e}"}

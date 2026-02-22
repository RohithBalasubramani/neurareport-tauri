"""User settings and preferences API routes."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

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

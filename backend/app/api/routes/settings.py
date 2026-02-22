"""User settings and preferences API routes."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


class UpdatePreferencesRequest(BaseModel):
    updates: Dict[str, Any]


@router.get("")
async def get_settings():
    """Get current user preferences and settings."""
    prefs = state_access.get_user_preferences()
    return {"settings": prefs}


@router.put("")
async def update_settings(request: UpdatePreferencesRequest):
    """Update user preferences."""
    updated = state_access.update_user_preferences(request.updates)
    return {"settings": updated}

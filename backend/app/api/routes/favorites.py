"""Favorites API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


class FavoriteRequest(BaseModel):
    entity_type: str
    entity_id: str


@router.get("")
async def list_favorites():
    """List all favorites grouped by entity type."""
    favorites = state_access.get_favorites()
    return {"favorites": favorites}


@router.post("")
async def add_favorite(request: FavoriteRequest):
    """Add an item to favorites."""
    added = state_access.add_favorite(request.entity_type, request.entity_id)
    return {"status": "ok", "added": added}


@router.delete("/{entity_type}/{entity_id}")
async def remove_favorite(entity_type: str, entity_id: str):
    """Remove an item from favorites."""
    removed = state_access.remove_favorite(entity_type, entity_id)
    return {"status": "ok", "removed": removed}

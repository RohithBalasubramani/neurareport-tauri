"""Favorites API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])

# Accept both singular and plural entity type names
_ENTITY_TYPE_MAP = {
    "template": "templates",
    "templates": "templates",
    "connection": "connections",
    "connections": "connections",
    "dashboard": "dashboards",
    "dashboards": "dashboards",
    "document": "documents",
    "documents": "documents",
}

_VALID_ENTITY_TYPES = set(_ENTITY_TYPE_MAP.values())


def _normalize_entity_type(raw: str) -> str:
    """Normalize entity type, accepting singular or plural.

    Raises HTTPException 422 for unknown entity types.
    """
    normalized = _ENTITY_TYPE_MAP.get(raw.lower().strip())
    if normalized is None:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid entity_type '{raw}'. Must be one of: {', '.join(sorted(_VALID_ENTITY_TYPES))}",
        )
    return normalized


class FavoriteRequest(BaseModel):
    entity_type: str
    entity_id: str = Field(..., max_length=500)


@router.get("")
async def list_favorites():
    """List all favorites grouped by entity type."""
    favorites = state_access.get_favorites()
    return {"favorites": favorites}


@router.post("")
async def add_favorite(request: FavoriteRequest):
    """Add an item to favorites."""
    entity_type = _normalize_entity_type(request.entity_type)
    added = state_access.add_favorite(entity_type, request.entity_id)
    return {"status": "ok", "added": added}


@router.delete("/{entity_type}/{entity_id}")
async def remove_favorite(entity_type: str, entity_id: str):
    """Remove an item from favorites."""
    normalized = _normalize_entity_type(entity_type)
    removed = state_access.remove_favorite(normalized, entity_id)
    return {"status": "ok", "removed": removed}

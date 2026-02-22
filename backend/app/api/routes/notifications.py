"""Notifications API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("")
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
):
    """List notifications."""
    notifications = state_access.get_notifications(limit=limit, unread_only=unread_only)
    return {"notifications": notifications, "total": len(notifications)}


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str):
    """Mark a notification as read."""
    state_access.mark_notification_read(notification_id)
    return {"status": "ok"}

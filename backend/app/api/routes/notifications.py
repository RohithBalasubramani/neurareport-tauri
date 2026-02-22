"""Notifications API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


class CreateNotificationRequest(BaseModel):
    """Create notification request body."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=2000)
    type: str = Field("info", pattern="^(info|warning|error|success)$")


@router.get("")
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
):
    """List notifications."""
    notifications = state_access.get_notifications(limit=limit, unread_only=unread_only)
    return {"notifications": notifications, "total": len(notifications)}


@router.post("")
async def create_notification(request: CreateNotificationRequest):
    """Create a new notification."""
    notification = state_access.add_notification(
        title=request.title,
        message=request.message,
        notification_type=request.type,
    )
    return {"status": "ok", "notification": notification}


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str):
    """Mark a notification as read."""
    result = state_access.mark_notification_read(notification_id)
    if result is False:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "notification_not_found", "message": "Notification not found."},
        )
    return {"status": "ok"}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete a notification."""
    result = state_access.delete_notification(notification_id)
    if result is False:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "notification_not_found", "message": "Notification not found."},
        )
    return {"status": "ok"}

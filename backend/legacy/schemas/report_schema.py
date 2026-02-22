from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ScheduleCreatePayload(BaseModel):
    template_id: str
    connection_id: str
    start_date: str
    end_date: str
    key_values: Optional[dict[str, Any]] = None
    batch_ids: Optional[list[str]] = None
    docx: bool = False
    xlsx: bool = False
    email_recipients: Optional[list[str]] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    frequency: str = "daily"
    interval_minutes: Optional[int] = None
    run_time: Optional[str] = None  # HH:MM (24h) — time of day to run
    name: Optional[str] = None
    active: bool = True


class ScheduleUpdatePayload(BaseModel):
    """All fields optional for partial updates."""
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    key_values: Optional[dict[str, Any]] = None
    batch_ids: Optional[list[str]] = None
    docx: Optional[bool] = None
    xlsx: Optional[bool] = None
    email_recipients: Optional[list[str]] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    frequency: Optional[str] = None
    interval_minutes: Optional[int] = None
    run_time: Optional[str] = None  # HH:MM (24h) — time of day to run
    active: Optional[bool] = None

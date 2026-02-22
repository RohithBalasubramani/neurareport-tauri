from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class RunPayload(BaseModel):
    template_id: str
    connection_id: Optional[str] = None
    start_date: str
    end_date: str
    batch_ids: Optional[list[str]] = None
    key_values: Optional[dict[str, Any]] = None
    brand_kit_id: Optional[str] = None
    docx: bool = False
    xlsx: Optional[bool] = None
    email_recipients: Optional[list[str]] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    schedule_id: Optional[str] = None
    schedule_name: Optional[str] = None


class DiscoverPayload(BaseModel):
    template_id: str
    connection_id: Optional[str] = None
    start_date: str
    end_date: str
    key_values: Optional[dict[str, Any]] = None

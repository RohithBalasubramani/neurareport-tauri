from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Optional

_SCHEDULE_INTERVALS = {
    "hourly": 60,
    "six_hours": 360,
    "daily": 1440,
    "weekly": 10080,
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_schedule_interval(frequency: str, override: Optional[int]) -> int:
    if override and override > 0:
        return max(int(override), 5)
    if not frequency:
        return 60
    key = frequency.strip().lower()
    return _SCHEDULE_INTERVALS.get(key, 60)


def clean_key_values(raw: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    if isinstance(raw, Mapping):
        for token, value in raw.items():
            name = str(token or "").strip()
            if not name or value is None:
                continue
            cleaned[name] = value
    return cleaned

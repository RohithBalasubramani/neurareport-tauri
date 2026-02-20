"""Core type definitions used throughout the system."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, NewType, Union

EntityId = NewType("EntityId", str)
Timestamp = NewType("Timestamp", datetime)

JSON = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
JSONObject = Dict[str, Any]
JSONArray = List[Any]

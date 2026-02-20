"""Catalog models for the widget intelligence pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ColumnStats:
    name: str = ""
    dtype: str = "double precision"
    unit: Optional[str] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    avg_val: Optional[float] = None
    latest_val: Optional[float] = None

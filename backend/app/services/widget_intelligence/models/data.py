"""Data profile model for the widget intelligence pipeline."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DataProfile:
    table_count: int = 0
    entity_count: int = 1
    numeric_column_count: int = 1
    has_timeseries: bool = True
    has_alerts: bool = False

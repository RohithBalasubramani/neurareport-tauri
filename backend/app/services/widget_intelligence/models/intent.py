"""Intent models for the widget intelligence pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QueryType(Enum):
    status = "status"
    overview = "overview"
    alert = "alert"
    trend = "trend"
    comparison = "comparison"
    analysis = "analysis"
    diagnostic = "diagnostic"
    forecast = "forecast"


class WidgetSize(Enum):
    compact = "compact"
    normal = "normal"
    expanded = "expanded"
    hero = "hero"


@dataclass
class ResolvedEntity:
    name: str = ""
    table_prefix: str = ""
    default_metric: str = ""
    default_unit: str = ""
    instances: list[str] = field(default_factory=list)
    is_primary: bool = False


@dataclass
class ParsedIntent:
    original_query: str = ""
    query_type: QueryType = QueryType.overview
    entities: list[ResolvedEntity] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    sub_questions: list[str] = field(default_factory=list)

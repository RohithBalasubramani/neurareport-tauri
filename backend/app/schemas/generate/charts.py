from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ChartSpec(BaseModel):
    id: Optional[str] = None
    type: str  # "bar", "line", "pie", "scatter"
    xField: str
    yFields: list[str]
    groupField: Optional[str] = None
    aggregation: Optional[str] = None
    chartTemplateId: Optional[str] = None
    style: Optional[dict[str, Any]] = None
    title: Optional[str] = None
    description: Optional[str] = None


class ChartSuggestPayload(BaseModel):
    connection_id: Optional[str] = None
    start_date: str
    end_date: str
    key_values: Optional[dict[str, Any]] = None
    question: str
    include_sample_data: bool = False


class ChartSuggestResponse(BaseModel):
    charts: list[ChartSpec]
    sample_data: Optional[list[dict[str, Any]]] = None


class SavedChartSpec(BaseModel):
    id: str
    template_id: str
    name: str
    spec: ChartSpec
    created_at: str
    updated_at: str


class SavedChartCreatePayload(BaseModel):
    template_id: str
    name: str
    spec: ChartSpec


class SavedChartUpdatePayload(BaseModel):
    name: Optional[str] = None
    spec: Optional[ChartSpec] = None

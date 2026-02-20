"""Service for automatic chart generation using AI."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.services.llm.client import get_llm_client
from backend.app.services.utils.llm import extract_json_array_from_llm_response

logger = logging.getLogger("neura.domain.charts")


class AutoChartService:
    """Service for automatic chart generation."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def analyze_data_for_charts(
        self,
        data: List[Dict[str, Any]],
        column_descriptions: Optional[Dict[str, str]] = None,
        max_suggestions: int = 3,
        correlation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze data and suggest appropriate chart visualizations.

        Args:
            data: Sample data rows
            column_descriptions: Optional descriptions for columns
            max_suggestions: Maximum number of chart suggestions
            correlation_id: Request correlation ID

        Returns:
            List of chart suggestions with configurations
        """
        logger.info("Analyzing data for chart suggestions", extra={"correlation_id": correlation_id})

        if not data:
            return []

        # Analyze columns
        columns = list(data[0].keys()) if data else []
        column_stats = {}

        for col in columns:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if not values:
                continue

            # Determine type
            sample = values[0]
            if isinstance(sample, (int, float)):
                col_type = "numeric"
            elif isinstance(sample, bool):
                col_type = "boolean"
            else:
                unique_ratio = len(set(str(v) for v in values)) / len(values)
                col_type = "categorical" if unique_ratio < 0.5 else "text"

            column_stats[col] = {
                "type": col_type,
                "unique_count": len(set(str(v) for v in values)),
                "sample_values": [str(v) for v in values[:3]],
            }

        # Build prompt
        prompt = f"""Analyze this data structure and suggest appropriate chart visualizations.

COLUMNS:
{column_stats}

{f"COLUMN DESCRIPTIONS: {column_descriptions}" if column_descriptions else ""}

Suggest up to {max_suggestions} charts. For each chart, provide:
- type: "bar", "line", "pie", or "scatter"
- title: Descriptive chart title
- xField: Column for X-axis
- yFields: Array of columns for Y-axis
- description: Why this visualization is useful

Return a JSON array:
[
  {{
    "type": "bar",
    "title": "Chart Title",
    "xField": "column_name",
    "yFields": ["value_column"],
    "description": "Shows distribution of values"
  }}
]

Return ONLY the JSON array."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="chart_suggestions",
                temperature=0.5,
            )

            content = response["choices"][0]["message"]["content"]
            suggestions = extract_json_array_from_llm_response(content, default=[])
            if suggestions:
                return suggestions[:max_suggestions]

        except Exception as exc:
            logger.error(f"Chart suggestion failed: {exc}")

        # Fallback: suggest basic charts
        numeric_cols = [c for c, s in column_stats.items() if s["type"] == "numeric"]
        categorical_cols = [c for c, s in column_stats.items() if s["type"] == "categorical"]

        suggestions = []
        if numeric_cols and categorical_cols:
            suggestions.append({
                "type": "bar",
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "xField": categorical_cols[0],
                "yFields": [numeric_cols[0]],
                "description": "Bar chart showing values by category",
            })

        return suggestions

    def generate_chart_config(
        self,
        data: List[Dict[str, Any]],
        chart_type: str,
        x_field: str,
        y_fields: List[str],
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a complete chart configuration."""
        return {
            "type": chart_type,
            "title": title or f"{', '.join(y_fields)} by {x_field}",
            "xField": x_field,
            "yFields": y_fields,
            "data": data,
            "config": {
                "responsive": True,
                "maintainAspectRatio": True,
            },
        }

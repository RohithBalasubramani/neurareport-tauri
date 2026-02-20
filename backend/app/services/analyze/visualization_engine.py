# mypy: ignore-errors
"""
Intelligent Visualization Engine - AI-powered chart generation and suggestions.

Features:
4.1 Auto-Generated Charts based on data patterns
4.2 Natural Language Chart Generation
4.3 Chart Intelligence (trends, anomalies, forecasts)
"""
from __future__ import annotations

import json
import logging
import math
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.analyze.enhanced_analysis import (
    ChartAnnotation,
    ChartDataSeries,
    ChartType,
    EnhancedChartSpec,
    EnhancedExtractedTable,
    ExtractedMetric,
    VisualizationSuggestion,
)
from backend.app.services.utils.llm import call_chat_completion, extract_json_from_llm_response
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.analyze.visualization")


# =============================================================================
# DATA PATTERN DETECTION
# =============================================================================

class DataPattern:
    """Detected data pattern for chart recommendation."""
    def __init__(
        self,
        pattern_type: str,
        columns: List[str],
        recommended_charts: List[ChartType],
        confidence: float,
        description: str,
    ):
        self.pattern_type = pattern_type
        self.columns = columns
        self.recommended_charts = recommended_charts
        self.confidence = confidence
        self.description = description


def detect_data_patterns(table: EnhancedExtractedTable) -> List[DataPattern]:
    """Detect data patterns in a table for chart recommendations."""
    patterns = []

    datetime_cols = []
    numeric_cols = []
    categorical_cols = []

    for idx, (header, dtype) in enumerate(zip(table.headers, table.data_types)):
        if dtype == "datetime":
            datetime_cols.append(header)
        elif dtype == "numeric":
            numeric_cols.append(header)
        else:
            # Check if categorical (limited unique values)
            unique_vals = set()
            for row in table.rows[:100]:
                if idx < len(row):
                    unique_vals.add(str(row[idx]))
            if len(unique_vals) <= 20:
                categorical_cols.append(header)

    # Time series pattern
    if datetime_cols and numeric_cols:
        patterns.append(DataPattern(
            pattern_type="time_series",
            columns=datetime_cols + numeric_cols,
            recommended_charts=[ChartType.LINE, ChartType.AREA, ChartType.BAR],
            confidence=0.9,
            description=f"Time series data with {len(numeric_cols)} numeric variables over time",
        ))

    # Category comparison pattern
    if categorical_cols and numeric_cols:
        patterns.append(DataPattern(
            pattern_type="category_comparison",
            columns=categorical_cols + numeric_cols,
            recommended_charts=[ChartType.BAR, ChartType.PIE, ChartType.TREEMAP],
            confidence=0.85,
            description=f"Categorical data with {len(numeric_cols)} metrics per category",
        ))

    # Distribution pattern
    if numeric_cols and len(table.rows) >= 10:
        patterns.append(DataPattern(
            pattern_type="distribution",
            columns=numeric_cols,
            recommended_charts=[ChartType.HISTOGRAM, ChartType.BOX],
            confidence=0.75,
            description=f"Numeric distribution analysis for {len(numeric_cols)} variables",
        ))

    # Correlation pattern (multiple numeric columns)
    if len(numeric_cols) >= 2:
        patterns.append(DataPattern(
            pattern_type="correlation",
            columns=numeric_cols,
            recommended_charts=[ChartType.SCATTER, ChartType.BUBBLE, ChartType.HEATMAP],
            confidence=0.7,
            description=f"Potential correlations between {len(numeric_cols)} numeric variables",
        ))

    # Hierarchical pattern
    if len(categorical_cols) >= 2 and numeric_cols:
        patterns.append(DataPattern(
            pattern_type="hierarchy",
            columns=categorical_cols + numeric_cols[:1],
            recommended_charts=[ChartType.SUNBURST, ChartType.TREEMAP],
            confidence=0.65,
            description="Hierarchical categorical data",
        ))

    # Progress/funnel pattern
    if len(numeric_cols) >= 3 and len(table.rows) <= 10:
        patterns.append(DataPattern(
            pattern_type="funnel",
            columns=numeric_cols,
            recommended_charts=[ChartType.FUNNEL, ChartType.WATERFALL],
            confidence=0.6,
            description="Sequential stage data suitable for funnel visualization",
        ))

    return patterns


# =============================================================================
# AUTO CHART GENERATION
# =============================================================================

def auto_generate_charts(
    tables: List[EnhancedExtractedTable],
    max_charts: int = 10,
) -> List[EnhancedChartSpec]:
    """Automatically generate charts based on detected data patterns."""
    charts = []

    for table in tables:
        if len(charts) >= max_charts:
            break

        patterns = detect_data_patterns(table)

        for pattern in patterns:
            if len(charts) >= max_charts:
                break

            chart = _create_chart_from_pattern(table, pattern)
            if chart:
                charts.append(chart)

    return charts


def _create_chart_from_pattern(
    table: EnhancedExtractedTable,
    pattern: DataPattern,
) -> Optional[EnhancedChartSpec]:
    """Create a chart specification from a detected pattern."""
    if not pattern.recommended_charts:
        return None

    chart_type = pattern.recommended_charts[0]

    # Determine x and y fields based on pattern type
    datetime_cols = [h for h, d in zip(table.headers, table.data_types) if d == "datetime"]
    numeric_cols = [h for h, d in zip(table.headers, table.data_types) if d == "numeric"]
    categorical_cols = [h for h, d in zip(table.headers, table.data_types) if d == "text"]

    x_field = ""
    y_fields = []

    if pattern.pattern_type == "time_series":
        x_field = datetime_cols[0] if datetime_cols else (categorical_cols[0] if categorical_cols else table.headers[0])
        y_fields = numeric_cols[:3]
    elif pattern.pattern_type == "category_comparison":
        x_field = categorical_cols[0] if categorical_cols else table.headers[0]
        y_fields = numeric_cols[:2]
    elif pattern.pattern_type == "correlation":
        x_field = numeric_cols[0]
        y_fields = [numeric_cols[1]] if len(numeric_cols) > 1 else []
    elif pattern.pattern_type == "distribution":
        x_field = numeric_cols[0]
        y_fields = []
    else:
        x_field = table.headers[0]
        y_fields = numeric_cols[:2] if numeric_cols else []

    if not x_field:
        return None

    # Build data from table
    data = []
    for row in table.rows[:500]:
        record = {}
        for idx, header in enumerate(table.headers):
            if idx < len(row):
                record[header] = row[idx]
        data.append(record)

    # Generate title
    title = f"{pattern.pattern_type.replace('_', ' ').title()}: {table.title or table.id}"

    return EnhancedChartSpec(
        id=f"auto_{chart_type.value}_{uuid.uuid4().hex[:8]}",
        type=chart_type,
        title=title,
        description=pattern.description,
        x_field=x_field,
        y_fields=y_fields,
        data=data,
        x_axis_label=x_field,
        y_axis_label=y_fields[0] if y_fields else None,
        show_legend=len(y_fields) > 1,
        ai_insights=[],
        source_table_id=table.id,
        confidence=pattern.confidence,
        suggested_by_ai=True,
    )


# =============================================================================
# NATURAL LANGUAGE CHART GENERATION
# =============================================================================

def generate_chart_from_natural_language(
    query: str,
    tables: List[EnhancedExtractedTable],
    metrics: List[ExtractedMetric] = None,
) -> List[EnhancedChartSpec]:
    """Generate charts from natural language query."""
    # Build context about available data
    context_parts = []
    for table in tables[:5]:
        context_parts.append(f"""Table: {table.title or table.id}
Columns: {', '.join([f'{h} ({d})' for h, d in zip(table.headers, table.data_types)])}
Rows: {table.row_count}
Sample: {table.rows[0] if table.rows else 'N/A'}""")

    context = "\n\n".join(context_parts)

    prompt = f"""Generate chart specifications based on this request.

User request: "{query}"

Available data:
{context}

Generate 1-3 appropriate charts. Return JSON array:
```json
[
  {{
    "chart_type": "line|bar|pie|scatter|area|histogram|box|heatmap|treemap|funnel|radar|bubble|sunburst|waterfall|gauge",
    "title": "Chart title",
    "description": "What this chart shows",
    "x_field": "column_name",
    "y_fields": ["column1", "column2"],
    "group_field": null,
    "x_axis_label": "X axis label",
    "y_axis_label": "Y axis label",
    "show_legend": true,
    "source_table": "table_id",
    "rationale": "Why this visualization is appropriate"
  }}
]
```

Match column names exactly as provided. Choose the most appropriate chart type for the data and request."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="nl_chart_generation",
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content or ""
        json_match = re.search(r'\[[\s\S]*\]', raw_text)

        if json_match:
            specs = json.loads(json_match.group())
            charts = []

            for spec in specs:
                try:
                    chart_type = ChartType[spec.get("chart_type", "bar").upper()]
                except KeyError:
                    chart_type = ChartType.BAR

                # Find source table and get data
                source_table_id = spec.get("source_table")
                source_table = next((t for t in tables if t.id == source_table_id or t.title == source_table_id), None)

                if not source_table and tables:
                    source_table = tables[0]

                data = []
                if source_table:
                    for row in source_table.rows[:500]:
                        record = {}
                        for idx, header in enumerate(source_table.headers):
                            if idx < len(row):
                                record[header] = row[idx]
                        data.append(record)

                charts.append(EnhancedChartSpec(
                    id=f"nl_{chart_type.value}_{uuid.uuid4().hex[:8]}",
                    type=chart_type,
                    title=spec.get("title", "Generated Chart"),
                    description=spec.get("description"),
                    x_field=spec.get("x_field", ""),
                    y_fields=spec.get("y_fields", []),
                    group_field=spec.get("group_field"),
                    data=data,
                    x_axis_label=spec.get("x_axis_label"),
                    y_axis_label=spec.get("y_axis_label"),
                    show_legend=spec.get("show_legend", True),
                    source_table_id=source_table.id if source_table else None,
                    ai_insights=[spec.get("rationale", "")],
                    confidence=0.85,
                    suggested_by_ai=True,
                ))

            return charts

    except Exception as e:
        logger.warning(f"NL chart generation failed: {e}")

    return []


# =============================================================================
# CHART INTELLIGENCE (TRENDS, ANOMALIES, FORECASTS)
# =============================================================================

def add_trend_line(chart: EnhancedChartSpec) -> EnhancedChartSpec:
    """Add trend line to a chart."""
    if not chart.data or not chart.y_fields:
        return chart

    y_field = chart.y_fields[0]
    x_field = chart.x_field

    # Extract numeric values
    values = []
    for i, record in enumerate(chart.data):
        try:
            y_val = float(str(record.get(y_field, 0)).replace(",", "").replace("$", "").replace("%", ""))
            values.append((i, y_val))
        except (ValueError, TypeError):
            pass

    if len(values) < 3:
        return chart

    # Simple linear regression
    n = len(values)
    sum_x = sum(x for x, _ in values)
    sum_y = sum(y for _, y in values)
    sum_xy = sum(x * y for x, y in values)
    sum_xx = sum(x * x for x, _ in values)

    denominator = n * sum_xx - sum_x * sum_x
    if denominator == 0:
        return chart

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n

    # Calculate R-squared
    mean_y = sum_y / n
    ss_tot = sum((y - mean_y) ** 2 for _, y in values)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in values)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    chart.trend_line = {
        "type": "linear",
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "r_squared": round(r_squared, 4),
        "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
    }

    # Add insight
    trend_desc = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    chart.ai_insights.append(
        f"Trend is {trend_desc} (slope: {slope:.2f}, R²: {r_squared:.2f})"
    )

    return chart


def add_forecast(chart: EnhancedChartSpec, periods: int = 3) -> EnhancedChartSpec:
    """Add simple forecast to a chart."""
    if not chart.trend_line or not chart.data:
        return chart

    slope = chart.trend_line.get("slope", 0)
    intercept = chart.trend_line.get("intercept", 0)

    last_x = len(chart.data) - 1
    forecast_values = []

    for i in range(1, periods + 1):
        x = last_x + i
        y = slope * x + intercept
        forecast_values.append({
            "period": f"+{i}",
            "value": round(y, 2),
            "lower_bound": round(y * 0.9, 2),
            "upper_bound": round(y * 1.1, 2),
        })

    chart.forecast = {
        "periods": periods,
        "method": "linear_extrapolation",
        "values": forecast_values,
        "confidence": 0.7,
    }

    chart.ai_insights.append(
        f"Forecast: Next {periods} periods projected based on linear trend"
    )

    return chart


def detect_anomalies(chart: EnhancedChartSpec) -> EnhancedChartSpec:
    """Detect anomalies in chart data."""
    if not chart.data or not chart.y_fields:
        return chart

    y_field = chart.y_fields[0]

    # Extract values
    values = []
    for i, record in enumerate(chart.data):
        try:
            y_val = float(str(record.get(y_field, 0)).replace(",", "").replace("$", "").replace("%", ""))
            values.append((i, y_val, record))
        except (ValueError, TypeError):
            pass

    if len(values) < 5:
        return chart

    # Calculate mean and std
    y_vals = [y for _, y, _ in values]
    mean = sum(y_vals) / len(y_vals)
    std = math.sqrt(sum((y - mean) ** 2 for y in y_vals) / len(y_vals))

    if std == 0:
        return chart

    # Find anomalies (beyond 2 standard deviations)
    anomalies = []
    for idx, y_val, record in values:
        z_score = abs((y_val - mean) / std)
        if z_score > 2:
            anomaly_type = "spike" if y_val > mean else "dip"
            anomalies.append({
                "index": idx,
                "value": y_val,
                "z_score": round(z_score, 2),
                "type": anomaly_type,
                "x_value": record.get(chart.x_field),
            })

            # Add annotation
            chart.annotations.append(ChartAnnotation(
                type="point",
                label=f"Anomaly: {anomaly_type}",
                value=y_val,
                position={"index": idx},
                style={"color": "red" if anomaly_type == "spike" else "orange"},
            ))

    chart.anomalies = anomalies

    if anomalies:
        chart.ai_insights.append(
            f"Detected {len(anomalies)} anomal{'y' if len(anomalies) == 1 else 'ies'} in the data"
        )

    return chart


def enhance_chart_with_intelligence(chart: EnhancedChartSpec) -> EnhancedChartSpec:
    """Apply all chart intelligence features."""
    chart = add_trend_line(chart)
    chart = detect_anomalies(chart)
    return chart


# =============================================================================
# CHART SUGGESTIONS
# =============================================================================

def generate_chart_suggestions(
    tables: List[EnhancedExtractedTable],
    metrics: List[ExtractedMetric] = None,
) -> List[VisualizationSuggestion]:
    """Generate visualization suggestions with rationale."""
    suggestions = []

    for table in tables[:5]:
        patterns = detect_data_patterns(table)

        for pattern in patterns:
            for chart_type in pattern.recommended_charts[:2]:
                chart = _create_chart_from_pattern(table, pattern)
                if chart:
                    chart.type = chart_type
                    chart = enhance_chart_with_intelligence(chart)

                    suggestions.append(VisualizationSuggestion(
                        chart_spec=chart,
                        rationale=f"{pattern.description}. {chart_type.value.title()} chart is ideal for visualizing {pattern.pattern_type.replace('_', ' ')} patterns.",
                        relevance_score=pattern.confidence,
                        complexity="simple" if chart_type in [ChartType.BAR, ChartType.LINE, ChartType.PIE] else "moderate",
                        insights_potential=chart.ai_insights,
                    ))

    # Sort by relevance
    suggestions.sort(key=lambda s: s.relevance_score, reverse=True)

    return suggestions[:10]


# =============================================================================
# LLM-POWERED CHART ANALYSIS
# =============================================================================

def analyze_chart_with_llm(chart: EnhancedChartSpec) -> EnhancedChartSpec:
    """Use LLM to generate insights about a chart."""
    # Build data summary
    data_summary = f"Chart: {chart.title}\nType: {chart.type.value}\n"
    data_summary += f"X-axis: {chart.x_field}\nY-axis: {', '.join(chart.y_fields)}\n"

    if chart.data:
        data_summary += f"Data points: {len(chart.data)}\n"
        data_summary += f"Sample data: {chart.data[:5]}"

    if chart.trend_line:
        data_summary += f"\nTrend: {chart.trend_line}"

    if chart.anomalies:
        data_summary += f"\nAnomalies: {chart.anomalies[:3]}"

    prompt = f"""Analyze this chart data and provide 3-5 key insights.

{data_summary}

Return JSON:
```json
{{
  "insights": [
    "Clear, actionable insight 1",
    "Clear, actionable insight 2",
    "Clear, actionable insight 3"
  ],
  "key_finding": "The single most important observation",
  "recommended_actions": ["Action 1", "Action 2"]
}}
```

Focus on patterns, trends, outliers, and business implications."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="chart_analysis",
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content or ""
        json_match = re.search(r'\{[\s\S]*\}', raw_text)

        if json_match:
            data = json.loads(json_match.group())
            chart.ai_insights.extend(data.get("insights", []))

            if data.get("key_finding"):
                chart.annotations.append(ChartAnnotation(
                    type="text",
                    label=data["key_finding"],
                    position={"location": "top"},
                ))

    except Exception as e:
        logger.warning(f"Chart analysis failed: {e}")

    return chart


# =============================================================================
# VISUALIZATION ENGINE ORCHESTRATOR
# =============================================================================

class VisualizationEngine:
    """Orchestrates all visualization features."""

    def generate_all_visualizations(
        self,
        tables: List[EnhancedExtractedTable],
        metrics: List[ExtractedMetric] = None,
        max_charts: int = 10,
    ) -> Dict[str, Any]:
        """Generate all visualizations for the data."""
        # Auto-generate charts
        auto_charts = auto_generate_charts(tables, max_charts)

        # Enhance with intelligence
        enhanced_charts = [enhance_chart_with_intelligence(c) for c in auto_charts]

        # Generate suggestions
        suggestions = generate_chart_suggestions(tables, metrics)

        return {
            "charts": enhanced_charts,
            "suggestions": suggestions,
        }

    def generate_from_query(
        self,
        query: str,
        tables: List[EnhancedExtractedTable],
        metrics: List[ExtractedMetric] = None,
    ) -> List[EnhancedChartSpec]:
        """Generate charts from natural language query."""
        charts = generate_chart_from_natural_language(query, tables, metrics)
        return [enhance_chart_with_intelligence(c) for c in charts]

    def add_intelligence_to_chart(
        self,
        chart: EnhancedChartSpec,
        include_forecast: bool = False,
        forecast_periods: int = 3,
    ) -> EnhancedChartSpec:
        """Add intelligence features to a chart."""
        chart = add_trend_line(chart)
        chart = detect_anomalies(chart)

        if include_forecast:
            chart = add_forecast(chart, forecast_periods)

        return analyze_chart_with_llm(chart)

"""
Data Shape Analyzer -- extract measurable properties from DataCatalog.

Computes a DataShapeProfile from ColumnStats at S06 time. Pure computation,
no LLM calls, no new DB queries. Runs in <1ms.

The shape profile drives variant selection via measurable data properties:
- variance/spread from ColumnStats (max-min)/|avg|
- cardinality (entity count, metric count, category count)
- temporal properties (density, span)
- metric type detection (cumulative, binary, phase, rate, percentage)
- structural properties (hierarchy, multiple sources)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataShapeProfile:
    """Measurable data properties extracted from catalog + profile."""

    # Cardinality
    entity_count: int = 1
    instance_count: int = 1
    metric_count: int = 1
    category_count: int = 1

    # Temporal
    has_timeseries: bool = True
    temporal_density: float = 0.0
    temporal_span_hours: float = 24.0

    # Value spread (from ColumnStats: (max-min)/|avg|)
    max_spread: float = 0.0
    mean_spread: float = 0.0
    has_high_variance: bool = False
    has_near_zero_variance: bool = True

    # Metric type detection
    has_cumulative_metric: bool = False
    has_rate_metric: bool = False
    has_percentage_metric: bool = False
    has_binary_metric: bool = False
    has_phase_data: bool = False
    has_temperature: bool = False
    has_flow_metric: bool = False

    # Structural
    has_hierarchy: bool = False
    has_multiple_sources: bool = False
    has_alerts: bool = False

    # Correlation indicators
    multi_numeric_potential: bool = False
    cross_entity_comparable: bool = False

    # Derived
    dominant_metric_type: str = "continuous"
    data_richness: str = "sparse"


def extract_data_shape(catalog, profile, intent=None) -> DataShapeProfile:
    """Extract DataShapeProfile from existing catalog data.

    Args:
        catalog: DataCatalog with enriched_tables containing ColumnStats.
        profile: DataProfile with entity_count, table_count, etc.
        intent: Optional ParsedIntent for additional context.

    Returns:
        DataShapeProfile with all measurable properties computed.
    """
    if catalog is None:
        ec = profile.entity_count if profile else 1
        mc = profile.numeric_column_count if profile else 1
        ts = profile.has_timeseries if profile else True
        al = profile.has_alerts if profile else False
        return DataShapeProfile(
            entity_count=ec,
            metric_count=mc,
            has_timeseries=ts,
            has_alerts=al,
            multi_numeric_potential=mc >= 3,
            data_richness="sparse" if mc <= 1 else ("moderate" if mc <= 4 else "rich"),
        )

    numeric_types = {"double precision", "real", "numeric", "float8", "integer", "bigint"}

    # Collect all numeric columns across all tables
    all_numeric_cols = []
    entity_types: set[str] = set()
    col_names_per_table: list[set[str]] = []

    for t in catalog.enriched_tables:
        if t.entity_type:
            entity_types.add(t.entity_type)
        numeric_cols = [c for c in t.columns if c.dtype in numeric_types]
        all_numeric_cols.extend(numeric_cols)
        col_names_per_table.append({c.name for c in numeric_cols})

    # --- Cardinality ---
    entity_count = profile.entity_count if profile else len(catalog.enriched_tables)
    instance_count = len(catalog.enriched_tables)
    metric_count = max(1, profile.numeric_column_count if profile else len(all_numeric_cols))
    category_count = max(1, len(entity_types))

    # --- Temporal ---
    has_timeseries = profile.has_timeseries if profile else (instance_count > 0)
    total_rows = sum(t.row_count for t in catalog.enriched_tables)
    temporal_density = round(total_rows / max(instance_count, 1) / 24.0, 2)

    # --- Value Spread ---
    spreads: list[float] = []
    for col in all_numeric_cols:
        if col.min_val is not None and col.max_val is not None and col.avg_val is not None:
            denom = abs(col.avg_val) if col.avg_val != 0 else 1.0
            spread = (col.max_val - col.min_val) / denom
            spreads.append(max(0.0, spread))

    max_spread = max(spreads) if spreads else 0.0
    mean_spread = (sum(spreads) / len(spreads)) if spreads else 0.0
    has_high_variance = max_spread > 0.5
    has_near_zero_variance = all(s < 0.05 for s in spreads) if spreads else True

    # --- Metric Type Detection ---
    has_cumulative = False
    has_rate = False
    has_percentage = False
    has_binary = False
    has_phase = False
    has_temperature = False
    has_flow = False

    col_names_lower: list[str] = []
    for col in all_numeric_cols:
        name_lower = col.name.lower()
        unit_lower = (col.unit or "").lower()
        col_names_lower.append(name_lower)

        # Cumulative: min~0, latest~max, unit in kWh/count/total
        if col.min_val is not None and col.max_val is not None and col.latest_val is not None:
            if col.min_val >= -0.01 and col.max_val > 0:
                ratio = abs(col.latest_val - col.max_val) / max(abs(col.max_val), 0.01)
                if ratio < 0.15:
                    if any(kw in unit_lower for kw in ("kwh", "mwh", "wh", "count", "total")):
                        has_cumulative = True
                    elif any(kw in name_lower for kw in ("cumulative", "total", "accumulated", "count")):
                        has_cumulative = True

        # Rate
        if any(kw in unit_lower for kw in ("/h", "/s", "/min", "rate", "per_hour")):
            has_rate = True

        # Percentage
        if "%" in unit_lower or "percent" in unit_lower:
            has_percentage = True
        elif col.min_val is not None and col.max_val is not None:
            if 0 <= (col.min_val or 0) and (col.max_val or 0) <= 100:
                if any(kw in name_lower for kw in ("efficiency", "utilization", "pct", "percent", "ratio")):
                    has_percentage = True

        # Binary
        if col.min_val is not None and col.max_val is not None:
            if col.min_val >= -0.01 and col.max_val <= 1.01 and col.max_val > 0:
                if any(kw in name_lower for kw in ("status", "state", "on", "off", "flag", "active", "running")):
                    has_binary = True

        # Temperature
        if any(kw in unit_lower for kw in ("celsius", "fahrenheit", "kelvin")):
            has_temperature = True
        elif unit_lower in ("c", "f", "k") and any(kw in name_lower for kw in ("temp", "temperature")):
            has_temperature = True
        elif any(kw in name_lower for kw in ("temperature", "temp_")):
            has_temperature = True

        # Flow
        if any(kw in unit_lower for kw in ("m3", "l/s", "l/min", "gpm", "cfm")):
            has_flow = True
        elif any(kw in name_lower for kw in ("flow", "flowrate", "flow_rate")):
            has_flow = True

    # Phase detection: 3+ columns with R/Y/B or L1/L2/L3 suffixes sharing a base name
    phase_suffixes = [
        ("_r", "_y", "_b"),
        ("_l1", "_l2", "_l3"),
        ("_phase_r", "_phase_y", "_phase_b"),
    ]
    base_counts: dict[str, set[str]] = {}
    for name in col_names_lower:
        for suffix_group in phase_suffixes:
            for suffix in suffix_group:
                if name.endswith(suffix):
                    base = name[: -len(suffix)]
                    base_counts.setdefault(base, set()).add(suffix)
    for base, suffixes_found in base_counts.items():
        if len(suffixes_found) >= 3:
            has_phase = True
            break

    # --- Structural ---
    has_hierarchy = len(getattr(catalog, "equipment_relationships", [])) > 0
    has_multiple_sources = entity_count >= 3
    has_alerts = (profile.has_alerts if profile else getattr(catalog, "has_alerts", False))

    # --- Correlation indicators ---
    multi_numeric_potential = metric_count >= 3
    cross_entity_comparable = False
    if len(col_names_per_table) >= 2:
        first = col_names_per_table[0]
        for other in col_names_per_table[1:]:
            if first & other:
                cross_entity_comparable = True
                break

    # --- Derived ---
    type_flags = {
        "binary": has_binary,
        "percentage": has_percentage,
        "cumulative": has_cumulative,
        "rate": has_rate,
    }
    active_types = [t for t, v in type_flags.items() if v]
    if len(active_types) >= 2:
        dominant_metric_type = "mixed"
    elif active_types:
        dominant_metric_type = active_types[0]
    else:
        dominant_metric_type = "continuous"

    if metric_count <= 1:
        data_richness = "sparse"
    elif metric_count <= 4:
        data_richness = "moderate"
    else:
        data_richness = "rich"

    return DataShapeProfile(
        entity_count=entity_count,
        instance_count=instance_count,
        metric_count=metric_count,
        category_count=category_count,
        has_timeseries=has_timeseries,
        temporal_density=temporal_density,
        temporal_span_hours=24.0,
        max_spread=round(max_spread, 4),
        mean_spread=round(mean_spread, 4),
        has_high_variance=has_high_variance,
        has_near_zero_variance=has_near_zero_variance,
        has_cumulative_metric=has_cumulative,
        has_rate_metric=has_rate,
        has_percentage_metric=has_percentage,
        has_binary_metric=has_binary,
        has_phase_data=has_phase,
        has_temperature=has_temperature,
        has_flow_metric=has_flow,
        has_hierarchy=has_hierarchy,
        has_multiple_sources=has_multiple_sources,
        has_alerts=has_alerts,
        multi_numeric_potential=multi_numeric_potential,
        cross_entity_comparable=cross_entity_comparable,
        dominant_metric_type=dominant_metric_type,
        data_richness=data_richness,
    )


def shape_to_text(shape: DataShapeProfile) -> str:
    """Format DataShapeProfile as concise text for DSPy input."""
    parts = [
        f"entity_count={shape.entity_count}",
        f"metric_count={shape.metric_count}",
        f"max_spread={shape.max_spread:.2f}",
        f"temporal_density={shape.temporal_density}/hr",
        f"dominant_metric_type={shape.dominant_metric_type}",
        f"data_richness={shape.data_richness}",
    ]
    flags: list[str] = []
    if shape.has_phase_data:
        flags.append("phase_data")
    if shape.has_cumulative_metric:
        flags.append("cumulative")
    if shape.has_binary_metric:
        flags.append("binary")
    if shape.has_hierarchy:
        flags.append("hierarchy")
    if shape.has_percentage_metric:
        flags.append("percentage")
    if shape.has_temperature:
        flags.append("temperature")
    if shape.has_flow_metric:
        flags.append("flow")
    if shape.has_rate_metric:
        flags.append("rate")
    if shape.has_alerts:
        flags.append("alerts")
    if shape.cross_entity_comparable:
        flags.append("cross_entity_comparable")
    if shape.has_high_variance:
        flags.append("high_variance")
    if shape.has_near_zero_variance:
        flags.append("near_zero_variance")
    if flags:
        parts.append(f"flags=[{', '.join(flags)}]")
    return ", ".join(parts)

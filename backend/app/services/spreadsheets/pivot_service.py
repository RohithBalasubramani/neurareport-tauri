"""
Pivot Table Service - Create and manage pivot tables.
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Optional

from pydantic import BaseModel

logger = logging.getLogger("neura.pivot")


class PivotValue(BaseModel):
    """Pivot table value aggregation configuration."""

    field: str
    aggregation: str = "SUM"  # SUM, COUNT, AVERAGE, MIN, MAX, COUNTUNIQUE
    alias: Optional[str] = None


class PivotFilter(BaseModel):
    """Pivot table filter."""

    field: str
    values: list[Any]
    exclude: bool = False


class PivotTableConfig(BaseModel):
    """Pivot table configuration."""

    id: str
    name: str
    source_sheet_id: str
    source_range: str
    row_fields: list[str] = []
    column_fields: list[str] = []
    value_fields: list[PivotValue] = []
    filters: list[PivotFilter] = []
    show_grand_totals: bool = True
    show_row_totals: bool = True
    show_col_totals: bool = True
    sort_rows_by: Optional[str] = None
    sort_rows_order: str = "asc"


class PivotTableResult(BaseModel):
    """Result of pivot table computation."""

    headers: list[str]
    rows: list[list[Any]]
    row_totals: Optional[list[Any]] = None
    column_totals: Optional[list[Any]] = None
    grand_total: Optional[Any] = None


class PivotService:
    """Service for creating and computing pivot tables."""

    AGGREGATIONS: dict[str, Callable[[list], Any]] = {
        "SUM": lambda values: sum(float(v) for v in values if v is not None),
        "COUNT": lambda values: len(values),
        "AVERAGE": lambda values: sum(float(v) for v in values if v is not None) / len(values) if values else 0,
        "MIN": lambda values: min(float(v) for v in values if v is not None) if values else None,
        "MAX": lambda values: max(float(v) for v in values if v is not None) if values else None,
        "COUNTUNIQUE": lambda values: len(set(values)),
    }

    def compute_pivot(
        self,
        data: list[dict[str, Any]],
        config: PivotTableConfig,
    ) -> PivotTableResult:
        """
        Compute pivot table from data.

        Args:
            data: List of row dictionaries with field values
            config: Pivot table configuration

        Returns:
            PivotTableResult with computed values
        """
        # Apply filters
        filtered_data = self._apply_filters(data, config.filters)

        if not filtered_data:
            return PivotTableResult(headers=[], rows=[])

        # Get unique values for row and column fields
        row_values = self._get_unique_values(filtered_data, config.row_fields)
        col_values = self._get_unique_values(filtered_data, config.column_fields)

        # Build pivot structure
        pivot_data = defaultdict(lambda: defaultdict(list))

        for row in filtered_data:
            row_key = tuple(row.get(f, "") for f in config.row_fields)
            col_key = tuple(row.get(f, "") for f in config.column_fields)

            for value_config in config.value_fields:
                val = row.get(value_config.field)
                if val is not None:
                    pivot_data[row_key][(col_key, value_config.field)].append(val)

        # Generate headers
        headers = list(config.row_fields)
        for col_combo in col_values:
            for value_config in config.value_fields:
                col_name = " - ".join(str(v) for v in col_combo) if col_combo else ""
                value_name = value_config.alias or f"{value_config.aggregation}({value_config.field})"
                if col_name:
                    headers.append(f"{col_name} | {value_name}")
                else:
                    headers.append(value_name)

        if config.show_row_totals:
            for value_config in config.value_fields:
                value_name = value_config.alias or f"{value_config.aggregation}({value_config.field})"
                headers.append(f"Total {value_name}")

        # Generate rows
        rows = []
        column_totals = defaultdict(list)

        for row_combo in row_values:
            row = list(row_combo)

            for col_combo in col_values:
                for value_config in config.value_fields:
                    values = pivot_data[row_combo].get((col_combo, value_config.field), [])
                    agg_func = self.AGGREGATIONS.get(value_config.aggregation.upper(), self.AGGREGATIONS["SUM"])
                    result = agg_func(values) if values else 0
                    row.append(result)

                    # Track for column totals
                    col_idx = len(row) - 1
                    column_totals[col_idx].extend(values)

            # Row totals
            if config.show_row_totals:
                for value_config in config.value_fields:
                    all_values = []
                    for col_combo in col_values:
                        all_values.extend(pivot_data[row_combo].get((col_combo, value_config.field), []))
                    agg_func = self.AGGREGATIONS.get(value_config.aggregation.upper(), self.AGGREGATIONS["SUM"])
                    row.append(agg_func(all_values) if all_values else 0)

            rows.append(row)

        # Sort rows if configured
        if config.sort_rows_by and config.sort_rows_by in config.row_fields:
            sort_idx = config.row_fields.index(config.sort_rows_by)
            reverse = config.sort_rows_order.lower() == "desc"
            rows.sort(key=lambda r: r[sort_idx] if r[sort_idx] is not None else "", reverse=reverse)

        # Compute column totals
        col_totals = None
        if config.show_col_totals and rows:
            col_totals = ["Total"] + [""] * (len(config.row_fields) - 1)
            for col_idx in range(len(config.row_fields), len(headers)):
                values = column_totals.get(col_idx, [])
                # Use first value config's aggregation for totals
                if config.value_fields:
                    agg_func = self.AGGREGATIONS.get(
                        config.value_fields[0].aggregation.upper(),
                        self.AGGREGATIONS["SUM"]
                    )
                    col_totals.append(agg_func(values) if values else 0)

        # Grand total
        grand_total = None
        if config.show_grand_totals and config.value_fields:
            all_values = []
            for row in filtered_data:
                val = row.get(config.value_fields[0].field)
                if val is not None:
                    all_values.append(val)
            agg_func = self.AGGREGATIONS.get(
                config.value_fields[0].aggregation.upper(),
                self.AGGREGATIONS["SUM"]
            )
            grand_total = agg_func(all_values) if all_values else 0

        return PivotTableResult(
            headers=headers,
            rows=rows,
            column_totals=col_totals,
            grand_total=grand_total,
        )

    def _apply_filters(
        self,
        data: list[dict[str, Any]],
        filters: list[PivotFilter],
    ) -> list[dict[str, Any]]:
        """Apply filters to data."""
        if not filters:
            return data

        filtered = []
        for row in data:
            include = True
            for f in filters:
                value = row.get(f.field)
                in_values = value in f.values
                if f.exclude:
                    if in_values:
                        include = False
                        break
                else:
                    if not in_values:
                        include = False
                        break
            if include:
                filtered.append(row)

        return filtered

    def _get_unique_values(
        self,
        data: list[dict[str, Any]],
        fields: list[str],
    ) -> list[tuple]:
        """Get unique value combinations for fields."""
        if not fields:
            return [()]

        seen = set()
        result = []

        for row in data:
            combo = tuple(row.get(f, "") for f in fields)
            if combo not in seen:
                seen.add(combo)
                result.append(combo)

        return sorted(result, key=lambda x: [str(v) for v in x])

    def data_to_records(
        self,
        data: list[list[Any]],
        headers: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """Convert 2D array to list of dictionaries."""
        if not data:
            return []

        if headers is None:
            headers = data[0]
            data = data[1:]

        return [
            {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
            for row in data
        ]

    def create_pivot_config(
        self,
        name: str,
        source_sheet_id: str,
        source_range: str,
        row_fields: list[str],
        column_fields: Optional[list[str]] = None,
        value_fields: Optional[list[dict[str, str]]] = None,
    ) -> PivotTableConfig:
        """Create a new pivot table configuration."""
        values = []
        if value_fields:
            for vf in value_fields:
                values.append(PivotValue(
                    field=vf.get("field", ""),
                    aggregation=vf.get("aggregation", "SUM"),
                    alias=vf.get("alias"),
                ))

        return PivotTableConfig(
            id=str(uuid.uuid4()),
            name=name,
            source_sheet_id=source_sheet_id,
            source_range=source_range,
            row_fields=row_fields,
            column_fields=column_fields or [],
            value_fields=values,
        )

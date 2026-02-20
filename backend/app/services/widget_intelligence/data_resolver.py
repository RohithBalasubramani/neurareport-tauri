"""
Widget Data Resolver — fetches live data from an active DB connection
using each widget's RAG strategy.

RAG Strategies:
  - single_metric:   SELECT one numeric column, aggregate over time
  - multi_metric:    SELECT multiple numeric columns for comparison
  - alert_query:     SELECT rows matching alert/warning conditions
  - narrative:       SELECT text content + aggregate summaries
  - flow_analysis:   SELECT source→target flows with values
  - events_in_range: SELECT time-ordered events in a date range
  - none:            No DB query — requires external data source
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("neura.widget_intelligence.data_resolver")


def _coerce(val):
    """Coerce numpy/pandas types to native Python for JSON serialization."""
    if val is None:
        return None
    t = type(val).__name__
    if "int" in t and t != "int":
        return int(val)
    if "float" in t and t != "float":
        return float(val)
    if "bool" in t and t != "bool":
        return bool(val)
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val


def _coerce_dict(d: dict) -> dict:
    """Recursively coerce all values in a dict."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = _coerce_dict(v)
        elif isinstance(v, list):
            out[k] = [_coerce_dict(i) if isinstance(i, dict) else _coerce(i) for i in v]
        else:
            out[k] = _coerce(v)
    return out


class WidgetDataResolver:
    """Resolves widget data from a database connection using RAG strategies."""

    def __init__(self):
        self._registry = None

    def _get_registry(self):
        if self._registry is None:
            from backend.app.services.widget_intelligence.widgets.base import WidgetRegistry
            self._registry = WidgetRegistry()
        return self._registry

    def resolve(
        self,
        connection_id: str,
        scenario: str,
        variant: Optional[str] = None,
        filters: Optional[dict] = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Fetch widget-appropriate data from the active DB connection.

        Returns a dict with:
          - data: formatted data ready for frontend rendering
          - source: connection_id used
          - strategy: RAG strategy applied
          - table_used: which DB table was queried
        """
        registry = self._get_registry()
        plugin = registry.get(scenario)
        if not plugin:
            return {"error": f"Unknown scenario: {scenario}", "data": {}}

        rag_strategy = plugin.meta.rag_strategy

        # Strategy: none — no DB query available
        if rag_strategy == "none":
            return {
                "data": {},
                "source": None,
                "strategy": "none",
                "table_used": None,
                "error": "This widget requires an external data source.",
            }

        # Get available tables and schema from the connection
        try:
            tables_info = self._get_connection_tables(connection_id)
        except Exception as e:
            logger.warning("Failed to load connection %s: %s", connection_id, e)
            return {
                "data": {},
                "source": connection_id,
                "strategy": rag_strategy,
                "table_used": None,
                "error": f"Connection failed: {e}",
            }

        if not tables_info:
            return {
                "data": {},
                "source": connection_id,
                "strategy": rag_strategy,
                "table_used": None,
                "error": "No tables found in connection.",
            }

        # Dispatch to strategy-specific resolver
        strategy_map = {
            "single_metric": self._resolve_single_metric,
            "multi_metric": self._resolve_multi_metric,
            "alert_query": self._resolve_alert_query,
            "narrative": self._resolve_narrative,
            "flow_analysis": self._resolve_flow_analysis,
            "events_in_range": self._resolve_events_in_range,
        }

        resolver_fn = strategy_map.get(rag_strategy, self._resolve_single_metric)

        try:
            raw_data = resolver_fn(connection_id, tables_info, plugin, filters, limit)
            # Check if the strategy resolver returned no usable data
            # (e.g. no numeric columns found) — detect by absence of _table_used
            has_data = "_table_used" in raw_data
            if not has_data:
                return {
                    "data": {},
                    "source": connection_id,
                    "strategy": rag_strategy,
                    "table_used": None,
                    "error": "No suitable data found in connection.",
                }
            # Format through the plugin, coerce numpy types for JSON
            formatted = _coerce_dict(plugin.format_data(raw_data))
            return {
                "data": formatted,
                "source": connection_id,
                "strategy": rag_strategy,
                "table_used": raw_data.get("_table_used"),
            }
        except Exception as e:
            logger.warning("Data resolution failed for %s: %s", scenario, e)
            return {
                "data": {},
                "source": connection_id,
                "strategy": rag_strategy,
                "table_used": None,
                "error": str(e),
            }

    # ── Connection helpers ─────────────────────────────────────────────────

    def _get_connection_tables(self, connection_id: str) -> list[dict]:
        """Get table names and columns from a connection."""
        from backend.app.repositories.connections.db_connection import (
            resolve_db_path, ensure_connection_loaded,
        )
        from backend.app.repositories.dataframes import sqlite_shim, dataframe_store

        db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
        ensure_connection_loaded(connection_id, db_path)

        tables = []
        with sqlite_shim.connect(str(db_path)) as con:
            # Get all tables
            cur = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            table_names = [row[0] for row in cur.fetchall()]

            for tname in table_names:
                try:
                    col_cur = con.execute(f"PRAGMA table_info('{tname}')")
                    columns = [
                        {"name": row[1], "type": row[2]}
                        for row in col_cur.fetchall()
                    ]
                    # Get row count
                    count_cur = con.execute(f"SELECT COUNT(*) FROM \"{tname}\"")
                    row_count = count_cur.fetchone()[0]
                    tables.append({
                        "name": tname,
                        "columns": columns,
                        "row_count": row_count,
                    })
                except Exception:
                    continue

        return tables

    def _execute_query(self, connection_id: str, sql: str, limit: int = 100) -> list[dict]:
        """Execute a read-only query and return rows as dicts.

        Note: SQL already contains LIMIT — do NOT pass limit to execute_query
        to avoid a double LIMIT clause.
        """
        from backend.app.repositories.connections.db_connection import execute_query
        result = execute_query(connection_id, sql, limit=None)
        columns = result["columns"]
        rows = result["rows"]
        return [dict(zip(columns, row)) for row in rows]

    def _find_best_table(
        self,
        tables_info: list[dict],
        prefer_numeric: bool = False,
        prefer_temporal: bool = False,
        prefer_text: bool = False,
    ) -> Optional[dict]:
        """Select the best table from the connection for a given strategy."""
        if not tables_info:
            return None

        scored = []
        for t in tables_info:
            score = t["row_count"]
            cols = t["columns"]
            num_cols = [c for c in cols if _is_numeric_type(c["type"])]
            text_cols = [c for c in cols if _is_text_type(c["type"])]
            date_cols = [c for c in cols if _is_date_type(c["type"]) or _is_date_name(c["name"])]

            if prefer_numeric and num_cols:
                score += len(num_cols) * 100
            if prefer_temporal and date_cols:
                score += len(date_cols) * 200
            if prefer_text and text_cols:
                score += len(text_cols) * 100
            scored.append((score, t))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    # ── Strategy resolvers ─────────────────────────────────────────────────

    def _resolve_single_metric(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Single metric: find first numeric column, return latest value + time series."""
        table = self._find_best_table(tables_info, prefer_numeric=True, prefer_temporal=True)
        if not table:
            return {}

        cols = table["columns"]
        num_cols = [c for c in cols if _is_numeric_type(c["type"])]
        date_cols = [c for c in cols if _is_date_type(c["type"]) or _is_date_name(c["name"])]

        if not num_cols:
            return {}

        metric_col = num_cols[0]["name"]
        order_col = date_cols[0]["name"] if date_cols else num_cols[0]["name"]

        sql = f'SELECT "{order_col}", "{metric_col}" FROM "{table["name"]}" ORDER BY "{order_col}" DESC LIMIT {limit}'
        rows = self._execute_query(connection_id, sql, limit)

        if not rows:
            return {}

        latest = rows[0]
        time_series = [
            {"time": str(r.get(order_col, "")), "value": r.get(metric_col, 0)}
            for r in reversed(rows)
        ]

        return {
            "value": latest.get(metric_col, 0),
            "units": _infer_unit(metric_col),
            "label": metric_col.replace("_", " ").title(),
            "timeSeries": time_series,
            "previousValue": rows[1].get(metric_col) if len(rows) > 1 else None,
            "_table_used": table["name"],
        }

    def _resolve_multi_metric(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Multi metric: select multiple numeric columns for comparison/distribution."""
        table = self._find_best_table(tables_info, prefer_numeric=True)
        if not table:
            return {}

        cols = table["columns"]
        num_cols = [c for c in cols if _is_numeric_type(c["type"])][:6]
        label_cols = [c for c in cols if _is_text_type(c["type"])]
        date_cols = [c for c in cols if _is_date_type(c["type"]) or _is_date_name(c["name"])]

        if not num_cols:
            return {}

        # Build select list
        select_cols = []
        if label_cols:
            select_cols.append(f'"{label_cols[0]["name"]}"')
        if date_cols:
            select_cols.append(f'"{date_cols[0]["name"]}"')
        for nc in num_cols:
            select_cols.append(f'"{nc["name"]}"')

        sql = f'SELECT {", ".join(select_cols)} FROM "{table["name"]}" LIMIT {limit}'
        rows = self._execute_query(connection_id, sql, limit)

        if not rows:
            return {}

        # Build labels and datasets
        label_key = label_cols[0]["name"] if label_cols else (date_cols[0]["name"] if date_cols else None)
        labels = [str(r.get(label_key, f"Row {i+1}")) for i, r in enumerate(rows)] if label_key else [f"Row {i+1}" for i in range(len(rows))]

        datasets = []
        for nc in num_cols:
            datasets.append({
                "label": nc["name"].replace("_", " ").title(),
                "data": [r.get(nc["name"], 0) for r in rows],
            })

        return {
            "labels": labels,
            "datasets": datasets,
            "_table_used": table["name"],
        }

    def _resolve_alert_query(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Alert query: find rows with status/severity/alert columns."""
        # Look for tables with alert-like columns
        alert_table = None
        for t in tables_info:
            col_names = [c["name"].lower() for c in t["columns"]]
            if any(kw in n for n in col_names for kw in ("alert", "warning", "status", "severity", "level")):
                alert_table = t
                break

        if not alert_table:
            alert_table = self._find_best_table(tables_info, prefer_text=True)

        if not alert_table:
            return {}

        sql = f'SELECT * FROM "{alert_table["name"]}" LIMIT {limit}'
        rows = self._execute_query(connection_id, sql, limit)

        if not rows:
            return {}

        # Map rows to alert/event format
        events = []
        for r in rows:
            event = {
                "message": _extract_text_field(r),
                "timestamp": _extract_date_field(r),
                "severity": _extract_severity(r),
            }
            events.append(event)

        return {
            "alerts": events,
            "events": events,
            "_table_used": alert_table["name"],
        }

    def _resolve_narrative(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Narrative: aggregate summaries from the largest table."""
        table = self._find_best_table(tables_info, prefer_numeric=True)
        if not table:
            return {}

        cols = table["columns"]
        num_cols = [c for c in cols if _is_numeric_type(c["type"])][:4]

        if not num_cols:
            return {}

        # Build aggregate query
        agg_parts = []
        for nc in num_cols:
            agg_parts.append(f'AVG("{nc["name"]}") as avg_{nc["name"]}')
            agg_parts.append(f'MIN("{nc["name"]}") as min_{nc["name"]}')
            agg_parts.append(f'MAX("{nc["name"]}") as max_{nc["name"]}')

        sql = f'SELECT COUNT(*) as total_rows, {", ".join(agg_parts)} FROM "{table["name"]}"'
        rows = self._execute_query(connection_id, sql, 1)

        if not rows:
            return {}

        row = rows[0]
        total = row.get("total_rows", 0)

        # Generate narrative text from aggregates
        highlights = []
        lines = [f"Dataset contains {total} records across {len(cols)} columns."]
        for nc in num_cols:
            name = nc["name"].replace("_", " ").title()
            avg = row.get(f"avg_{nc['name']}", 0)
            mn = row.get(f"min_{nc['name']}", 0)
            mx = row.get(f"max_{nc['name']}", 0)
            if avg is not None:
                lines.append(f"{name}: avg {_fmt_num(avg)}, range {_fmt_num(mn)} - {_fmt_num(mx)}.")
                highlights.append(f"{name}: {_fmt_num(avg)}")

        return {
            "title": f"Summary of {table['name']}",
            "text": " ".join(lines),
            "highlights": highlights,
            "_table_used": table["name"],
        }

    def _resolve_flow_analysis(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Flow analysis: look for source→target→value patterns."""
        # Try to find a table with source/target/from/to columns
        flow_table = None
        for t in tables_info:
            col_names = [c["name"].lower() for c in t["columns"]]
            if any(kw in " ".join(col_names) for kw in ("source", "from", "origin")):
                if any(kw in " ".join(col_names) for kw in ("target", "to", "destination")):
                    flow_table = t
                    break

        if not flow_table:
            flow_table = self._find_best_table(tables_info, prefer_numeric=True)

        if not flow_table:
            return {}

        sql = f'SELECT * FROM "{flow_table["name"]}" LIMIT {limit}'
        rows = self._execute_query(connection_id, sql, limit)

        if not rows:
            return {}

        return {
            "nodes": list({str(v) for r in rows for v in r.values() if isinstance(v, str)}),
            "links": rows[:20],
            "_table_used": flow_table["name"],
        }

    def _resolve_events_in_range(
        self, connection_id, tables_info, plugin, filters, limit
    ) -> dict:
        """Events in range: time-ordered events."""
        table = self._find_best_table(tables_info, prefer_temporal=True)
        if not table:
            return {}

        date_cols = [c for c in table["columns"] if _is_date_type(c["type"]) or _is_date_name(c["name"])]
        order_col = date_cols[0]["name"] if date_cols else table["columns"][0]["name"]

        sql = f'SELECT * FROM "{table["name"]}" ORDER BY "{order_col}" DESC LIMIT {limit}'
        rows = self._execute_query(connection_id, sql, limit)

        if not rows:
            return {}

        events = []
        for r in rows:
            events.append({
                "timestamp": _extract_date_field(r),
                "message": _extract_text_field(r),
                "title": _extract_text_field(r),
            })

        return {
            "events": events,
            "timeline": events,
            "_table_used": table["name"],
        }


# ── Helper functions ─────────────────────────────────────────────────────────

def _is_numeric_type(dtype: str) -> bool:
    dtype = dtype.upper()
    return any(kw in dtype for kw in ("INT", "REAL", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "NUMBER"))


def _is_text_type(dtype: str) -> bool:
    dtype = dtype.upper()
    return any(kw in dtype for kw in ("TEXT", "VARCHAR", "CHAR", "STRING", "CLOB"))


def _is_date_type(dtype: str) -> bool:
    dtype = dtype.upper()
    return any(kw in dtype for kw in ("DATE", "TIME", "TIMESTAMP"))


def _is_date_name(name: str) -> bool:
    name = name.lower()
    return any(kw in name for kw in ("date", "time", "timestamp", "created", "updated", "period", "month", "year"))


def _infer_unit(col_name: str) -> str:
    name = col_name.lower()
    if any(kw in name for kw in ("kwh", "energy")):
        return "kWh"
    if any(kw in name for kw in ("temp", "temperature")):
        return "°C"
    if any(kw in name for kw in ("pressure", "psi")):
        return "PSI"
    if any(kw in name for kw in ("percent", "pct", "rate")):
        return "%"
    if any(kw in name for kw in ("cost", "price", "amount", "revenue")):
        return "$"
    if any(kw in name for kw in ("count", "total", "quantity")):
        return ""
    return ""


def _extract_text_field(row: dict) -> str:
    """Extract the first plausible text field from a row."""
    for key in ("message", "text", "title", "name", "description", "label", "note"):
        if key in row and row[key]:
            return str(row[key])
    # Fall back to first string value
    for v in row.values():
        if isinstance(v, str) and len(v) > 2:
            return v
    return str(next(iter(row.values()), ""))


def _extract_date_field(row: dict) -> str:
    """Extract the first plausible date field from a row."""
    for key in row:
        if _is_date_name(key) and row[key]:
            return str(row[key])
    return ""


def _extract_severity(row: dict) -> str:
    """Extract severity/level from a row."""
    for key in ("severity", "level", "status", "priority"):
        if key in row and row[key]:
            val = str(row[key]).lower()
            if val in ("critical", "error", "high"):
                return "critical"
            if val in ("warning", "warn", "medium"):
                return "warning"
            if val in ("info", "low", "notice"):
                return "info"
            if val in ("ok", "normal", "good", "success"):
                return "ok"
            return val
    return "info"


def _fmt_num(val) -> str:
    """Format a number for narrative display."""
    if val is None:
        return "N/A"
    try:
        f = float(val)
        if abs(f) >= 1_000_000:
            return f"{f/1_000_000:.1f}M"
        if abs(f) >= 1_000:
            return f"{f/1_000:.1f}K"
        if f == int(f):
            return str(int(f))
        return f"{f:.2f}"
    except (ValueError, TypeError):
        return str(val)

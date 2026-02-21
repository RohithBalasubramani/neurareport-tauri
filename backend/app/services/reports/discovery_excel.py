# mypy: ignore-errors
"""Excel-specific batch discovery helpers mirroring the base pipeline.

Future Excel-only behavior (e.g., workbook metadata filters) can live
here without touching the PDF-focused discovery module.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import pandas as pd

from .contract_adapter import ContractAdapter
from .discovery_metrics import (
    build_batch_field_catalog_and_stats,
    build_batch_metrics,
    build_discovery_schema,
    build_resample_support,
)
from backend.app.repositories.dataframes import SQLiteDataFrameLoader

try:  # pragma: no cover - compatibility shim
    from ..mapping.auto_fill import build_or_load_contract  # type: ignore
except Exception:  # pragma: no cover
    try:
        from .auto_fill import build_or_load_contract  # type: ignore
    except Exception as exc:  # pragma: no cover

        def build_or_load_contract(*_args, _exc=exc, **_kwargs):  # type: ignore
            raise RuntimeError(
                "build_or_load_contract unavailable. Ensure mapping.auto_fill.build_or_load_contract exists."
            ) from _exc


_DATE_INPUT_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
)

_DIRECT_COLUMN_RE = re.compile(r"^\s*(?P<table>[A-Za-z_][\w]*)\s*\.\s*(?P<column>[A-Za-z_][\w]*)\s*$")


def _infer_primary_table(mapping_section: Mapping[str, str] | None) -> str | None:
    if not isinstance(mapping_section, Mapping):
        return None
    seen: list[str] = []
    for expr in mapping_section.values():
        if not isinstance(expr, str):
            continue
        match = _DIRECT_COLUMN_RE.match(expr.strip())
        if not match:
            continue
        table_name = match.group("table").strip(' "`[]')
        if not table_name or table_name.lower().startswith("params"):
            continue
        if table_name not in seen:
            seen.append(table_name)
    return seen[0] if seen else None


def _snap_end_of_day(dt: datetime) -> datetime:
    """If *dt* has no time component (midnight), snap to 23:59:59.999999.

    This ensures date-only end-dates like ``2026-02-19`` include all
    records on that day instead of only those at exactly midnight.
    """
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt


def _parse_date_like(value) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    iso_try = text.replace("Z", "+00:00")
    if " " in iso_try and "T" not in iso_try:
        iso_try = iso_try.replace(" ", "T", 1)
    try:
        return datetime.fromisoformat(iso_try)
    except ValueError:
        pass
    for fmt in _DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _stringify_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value)
    return text.strip()


def _coerce_datetime_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        result = series
    elif pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        finite = numeric[~pd.isna(numeric)]
        max_abs = finite.abs().max() if not finite.empty else None
        if max_abs is not None and max_abs > 32503680000:
            numeric = numeric / 1000.0
        result = pd.to_datetime(numeric, unit="s", errors="coerce")
    else:
        text = series.astype(str).str.strip()
        result = pd.to_datetime(text, errors="coerce")
    if hasattr(result, "dt"):
        try:
            return result.dt.tz_localize(None)
        except (AttributeError, TypeError):
            return result
    return result


def _apply_date_filter(df: pd.DataFrame, column: str, start: str, end: str) -> pd.DataFrame:
    if df is None or df.empty or not column or column not in df.columns:
        return df
    start_dt = _parse_date_like(start)
    end_dt = _parse_date_like(end)
    if start_dt is None or end_dt is None:
        return df
    end_dt = _snap_end_of_day(end_dt)
    dt_series = _coerce_datetime_series(df[column])
    mask = (dt_series >= start_dt) & (dt_series <= end_dt)
    return df.loc[mask.fillna(False)]


def _normalize_key_value(raw_value: Any) -> list[str]:
    if isinstance(raw_value, (list, tuple, set)):
        values: list[str] = []
        for item in raw_value:
            text = str(item or "").strip()
            if text and text not in values:
                values.append(text)
        return values
    text = str(raw_value or "").strip()
    return [text] if text else []


def _apply_value_filters(df: pd.DataFrame, filters: list[tuple[str, list[str]]]) -> pd.DataFrame:
    if df is None or df.empty or not filters:
        return df
    mask = pd.Series(True, index=df.index)
    for column, values in filters:
        if column not in df.columns:
            continue
        normalized = [str(val).strip() for val in values if str(val or "").strip()]
        if not normalized:
            continue
        series = df[column]
        if pd.api.types.is_numeric_dtype(series):
            try:
                numeric_values = [float(val) for val in normalized]
            except ValueError:
                numeric_values = None
            if numeric_values is not None:
                cmp = pd.to_numeric(series, errors="coerce").isin(numeric_values)
                mask &= cmp.fillna(False)
                continue
        cmp = series.astype(str).str.strip().isin(normalized)
        mask &= cmp.fillna(False)
    return df.loc[mask]


def _build_batch_index(df: pd.DataFrame, key_columns: List[str], *, use_rowid: bool = False) -> tuple[list[str], Counter[str]]:
    if df is None or df.empty:
        return [], Counter()
    working = df.reset_index(drop=True).copy()
    columns = list(key_columns)
    if use_rowid:
        working["__rowid__"] = working.index + 1
        columns = ["__rowid__"]
    if not columns:
        working["__bid__"] = ""
    elif len(columns) == 1:
        col = columns[0]
        if col not in working.columns:
            working[col] = None
        working["__bid__"] = working[col].apply(_stringify_value)
    else:
        for col in columns:
            if col not in working.columns:
                working[col] = None
        working["__bid__"] = working[columns].apply(lambda row: "|".join(_stringify_value(v) for v in row), axis=1)
    sort_cols = columns or ["__bid__"]
    working_sorted = working.sort_values(sort_cols, kind="mergesort")
    ordered_ids: list[str] = []
    seen: set[str] = set()
    for bid in working_sorted["__bid__"]:
        if bid not in seen:
            seen.add(bid)
            ordered_ids.append(bid)
    counts = Counter(working["__bid__"])
    return ordered_ids, counts


def _attach_batch_id(df: pd.DataFrame, key_columns: List[str], *, use_rowid: bool = False) -> pd.DataFrame:
    """
    Attach a "__bid__" column to the DataFrame using the join key columns.

    The logic mirrors _build_batch_index so later aggregations can group
    by the same batch ids without recomputing them.
    """
    if df is None or df.empty:
        return df

    working = df.reset_index(drop=True).copy()
    columns = list(key_columns)

    if use_rowid:
        working["__rowid__"] = working.index + 1
        columns = ["__rowid__"]

    if not columns:
        working["__bid__"] = ""
        return working

    for col in columns:
        if col not in working.columns:
            working[col] = None

    if len(columns) == 1:
        col = columns[0]
        working["__bid__"] = working[col].apply(_stringify_value)
    else:
        working["__bid__"] = working[columns].apply(lambda row: "|".join(_stringify_value(v) for v in row), axis=1)

    return working


def _build_batch_metadata(
    df: pd.DataFrame,
    key_columns: List[str],
    *,
    date_column: str | None = None,
    use_rowid: bool = False,
    label_columns: Sequence[str] | None = None,
) -> Dict[str, Dict[str, object]]:
    """
    Derive lightweight per-batch metadata for resampling and charting.

    For each batch id we compute:
      - time:  representative timestamp (earliest in the batch) when a date
               column is available.
      - category: a human-readable label based on the first key column.
      - labels for each key column (first non-empty value per batch).

    The returned mapping is keyed by batch id (the same id produced by
    _build_batch_index).
    """
    if df is None or df.empty:
        return {}

    working = df.reset_index(drop=True).copy()
    columns = list(key_columns)

    if use_rowid:
        working["__rowid__"] = working.index + 1
        columns = ["__rowid__"]

    if not columns:
        working["__bid__"] = ""
    elif len(columns) == 1:
        col = columns[0]
        if col not in working.columns:
            working[col] = None
        working["__bid__"] = working[col].apply(_stringify_value)
    else:
        for col in columns:
            if col not in working.columns:
                working[col] = None
        working["__bid__"] = working[columns].apply(
            lambda row: "|".join(_stringify_value(v) for v in row),
            axis=1,
        )

    metadata: Dict[str, Dict[str, object]] = {}

    # Time dimension: earliest timestamp per batch, if a usable column exists.
    if date_column and date_column in working.columns:
        try:
            dt_series = _coerce_datetime_series(working[date_column])
        except Exception:  # pragma: no cover - defensive
            dt_series = None
        if dt_series is not None:
            working["_nr_time"] = dt_series
            grouped_time = working.groupby("__bid__")["_nr_time"].min()
            for bid, ts in grouped_time.items():
                # pandas uses NaT for missing values; treat as absent.
                if ts is None or pd.isna(ts):
                    continue
                try:
                    # Both pandas.Timestamp and datetime.datetime implement isoformat.
                    iso_value = ts.isoformat()
                except Exception:  # pragma: no cover - defensive
                    continue
                metadata.setdefault(bid, {})["time"] = iso_value

    label_cols = [col for col in (label_columns or key_columns or []) if col and not str(col).startswith("__")]
    category_source = label_cols[0] if label_cols else None
    if category_source is None and columns and not str(columns[0]).startswith("__"):
        category_source = columns[0]

    for col in label_cols:
        if col not in working.columns:
            continue
        label_field = f"_nr_label_{col}"
        working[label_field] = working[col].apply(_stringify_value)
        grouped = working.groupby("__bid__")[label_field].first()
        for bid, raw_val in grouped.items():
            text = _stringify_value(raw_val)
            if not text:
                continue
            meta = metadata.setdefault(bid, {})
            meta[col] = text
            if category_source == col and "category" not in meta:
                meta["category"] = text

    if category_source and category_source in working.columns:
        working["_nr_category"] = working[category_source].apply(_stringify_value)
        grouped_cat = working.groupby("__bid__")["_nr_category"].first()
        for bid, cat in grouped_cat.items():
            text = _stringify_value(cat)
            if not text:
                continue
            metadata.setdefault(bid, {}).setdefault("category", text)

    return metadata


def discover_batches_and_counts(
    *,
    db_path: Path,
    contract: dict,
    start_date: str,
    end_date: str,
    key_values: Mapping[str, Any] | None = None,
) -> dict:
    """
    Discover distinct batch IDs and count:
      - parent: number of parent rows (i.e., batches) per id in range
      - rows:   number of child rows per id in range
    Returns:
      {
        "batches": [{"id": "...", "parent": <int>, "rows": <int>}...],
        "batches_count": <int>,   # number of parent batches
        "rows_total": <int>       # sum of child rows
      }
    """
    adapter = ContractAdapter(contract)
    join_cfg = contract.get("join") or {}
    date_columns = adapter.date_columns or (contract.get("date_columns") or {})
    mapping_section = adapter.mapping or (contract.get("mapping") or {})

    parent_table = adapter.parent_table or (join_cfg.get("parent_table") or "").strip()
    child_table = adapter.child_table or (join_cfg.get("child_table") or "").strip()
    parent_key = adapter.parent_key if adapter.parent_key is not None else join_cfg.get("parent_key")
    child_key = adapter.child_key if adapter.child_key is not None else join_cfg.get("child_key")

    if not parent_table:
        inferred_parent = _infer_primary_table(mapping_section)
        if inferred_parent:
            parent_table = inferred_parent

    if not parent_table:
        raise ValueError("contract.join.parent_table is required for discovery")

    parent_date = (date_columns.get(parent_table) or "").strip()
    child_date = (date_columns.get(child_table) or "").strip() if child_table else ""

    def _split_keys(raw_keys: object) -> List[str]:
        """
        Normalise the join key field from the contract. Handles strings, comma-separated
        strings, iterables, and scalars (e.g., integers). Returns a list of non-empty strings.
        """
        if raw_keys is None:
            return []
        if isinstance(raw_keys, (list, tuple, set)):
            items = raw_keys
        else:
            text = str(raw_keys).strip()
            if not text:
                return []
            if isinstance(raw_keys, str):
                if "," in text:
                    items = text.split(",")
                elif "|" in text:
                    items = text.split("|")
                else:
                    items = [text]
            else:
                items = [text]
        result: List[str] = []
        for item in items:
            token = str(item).strip()
            if token:
                result.append(token)
        return result

    pcols = _split_keys(parent_key)
    ccols = _split_keys(child_key)
    use_rowid = False

    if not pcols:
        if ccols:
            pcols = list(ccols)
        else:
            use_rowid = True
            pcols = ["__rowid__"]

    has_child = bool(child_table and ccols)

    categorical_fields: list[str] = []
    for col in pcols:
        col_text = str(col or "").strip()
        if col_text and not col_text.startswith("__") and col_text not in categorical_fields:
            categorical_fields.append(col_text)
    if has_child:
        for col in ccols:
            col_text = str(col or "").strip()
            if col_text and not col_text.startswith("__") and col_text not in categorical_fields:
                categorical_fields.append(col_text)

    # Support both SQLite and PostgreSQL connections via ConnectionRef
    if hasattr(db_path, 'is_postgresql') and db_path.is_postgresql:
        from backend.legacy.utils.connection_utils import get_loader_for_ref
        loader = get_loader_for_ref(db_path)
    else:
        loader = SQLiteDataFrameLoader(db_path)

    if not isinstance(key_values, Mapping):
        key_values = {}
    parent_filters: list[tuple[str, Any]] = []
    child_filters: list[tuple[str, Any]] = []

    def _split_table_and_column(expr_text: str, fallback_table: str) -> tuple[str, str]:
        expr_text = expr_text.strip()
        if "." in expr_text:
            table_name, column_name = expr_text.split(".", 1)
        else:
            table_name, column_name = fallback_table, expr_text
        table_name = table_name.strip(' "`[]').lower()
        column_name = column_name.strip(' "`[]')
        return table_name, column_name

    def _append_filter_target(expr_text: str, value: Any, collection: list[tuple[str, Any]], expected_table: str):
        if not expr_text or not expected_table:
            return
        table_name, column_name = _split_table_and_column(expr_text, expected_table)
        if table_name != expected_table.lower():
            return
        if not column_name:
            return
        normalized = _normalize_key_value(value)
        if not normalized:
            return
        for idx, (col, existing_values) in enumerate(collection):
            if col == column_name:
                existing_list = _normalize_key_value(existing_values)
                merged = existing_list + [item for item in normalized if item not in existing_list]
                collection[idx] = (col, merged)
                break
        else:
            collection.append((column_name, normalized))

    if key_values:
        parent_table_lc = parent_table.lower()
        child_table_lc = child_table.lower() if child_table else ""
        for token, raw_value in key_values.items():
            if raw_value is None:
                continue
            expr = mapping_section.get(token)
            if not isinstance(expr, str):
                continue
            expr_text = expr.strip()
            if not expr_text or expr_text.upper().startswith("PARAM:"):
                continue
            if "." not in expr_text:
                continue
            table_name, column_name = expr_text.split(".", 1)
            table_name = table_name.strip(' "`[]')
            column_name = column_name.strip(' "`[]')
            if not column_name:
                continue
            table_key = table_name.lower()
            if table_key == parent_table_lc:
                values = _normalize_key_value(raw_value)
                if values:
                    parent_filters.append((column_name, values))
            if has_child and table_key == child_table_lc:
                values = _normalize_key_value(raw_value)
                if values:
                    child_filters.append((column_name, values))

    if isinstance(key_values, Mapping):
        for token, expr in adapter.required_filters.items():
            value = key_values.get(token)
            if value is None:
                continue
            _append_filter_target(expr, value, parent_filters, parent_table)
            if has_child:
                _append_filter_target(expr, value, child_filters, child_table)
        for token, expr in adapter.optional_filters.items():
            value = key_values.get(token)
            if value in (None, ""):
                continue
            _append_filter_target(expr, value, parent_filters, parent_table)
            if has_child:
                _append_filter_target(expr, value, child_filters, child_table)
    parent_filter_pairs: list[tuple[str, list[str]]] = [
        (col, _normalize_key_value(values)) for col, values in parent_filters
    ]
    child_filter_pairs: list[tuple[str, list[str]]] = [
        (col, _normalize_key_value(values)) for col, values in child_filters
    ]
    try:
        parent_df = loader.frame(parent_table).copy()
    except Exception as exc:  # pragma: no cover - surfaced to caller
        raise RuntimeError(f"Failed to load parent table {parent_table!r}: {exc}") from exc

    child_df = None
    if has_child:
        try:
            child_df = loader.frame(child_table).copy()
        except Exception as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"Failed to load child table {child_table!r}: {exc}") from exc

    parent_df = _apply_date_filter(parent_df, parent_date, start_date, end_date)
    parent_df = _apply_value_filters(parent_df, parent_filter_pairs)

    if has_child and child_df is not None:
        child_df = _apply_date_filter(child_df, child_date, start_date, end_date)
        child_df = _apply_value_filters(child_df, child_filter_pairs)

    parent_df = _attach_batch_id(parent_df, pcols, use_rowid=use_rowid)
    parent_ids, parent_counts = _build_batch_index(parent_df, pcols, use_rowid=use_rowid)
    if has_child and child_df is not None:
        child_df = _attach_batch_id(child_df, ccols, use_rowid=False)
        child_ids, child_counts = _build_batch_index(child_df, ccols)
    else:
        child_ids, child_counts = [], Counter()

    if not parent_ids and child_ids:
        parent_ids = list(child_ids)

    # Lightweight metadata for resampling (time/category per batch id).
    batch_metadata: Dict[str, Dict[str, object]] = {}
    try:
        parent_meta = _build_batch_metadata(
            parent_df,
            pcols,
            date_column=parent_date or None,
            use_rowid=use_rowid,
            label_columns=pcols,
        )
        for bid, meta in parent_meta.items():
            batch_metadata.setdefault(bid, {}).update(meta)
    except Exception:  # pragma: no cover - defensive
        batch_metadata = {}

    if has_child and child_df is not None:
        try:
            child_meta = _build_batch_metadata(
                child_df,
                ccols,
                date_column=child_date or None,
                use_rowid=False,
                label_columns=ccols,
            )
            for bid, meta in child_meta.items():
                target = batch_metadata.setdefault(bid, {})
                if not isinstance(meta, Mapping):
                    continue
                for key, value in meta.items():
                    if value is None or (isinstance(value, str) and not str(value).strip()):
                        continue
                    if key == "time":
                        if "time" not in target:
                            target["time"] = value
                        continue
                    if key not in target:
                        target[key] = value
        except Exception:  # pragma: no cover - defensive
            # If metadata from child fails, keep whatever we have from parent.
            pass

    def _aggregate_numeric(df: pd.DataFrame | None, prefix: str) -> dict[str, dict[str, float]]:
        if df is None or df.empty or "__bid__" not in df.columns:
            return {}
        skip_cols = {"__bid__", "__rowid__"} | set(pcols) | set(ccols) | {parent_date, child_date}
        numeric_cols = [
            col for col in df.columns if col not in skip_cols and pd.api.types.is_numeric_dtype(df[col])
        ]
        aggregates: dict[str, dict[str, float]] = {}
        if not numeric_cols:
            return aggregates
        grouped = df.groupby("__bid__")
        for bid, group in grouped:
            entry: dict[str, float] = {}
            for col in numeric_cols:
                try:
                    entry[f"{prefix}{col}"] = float(pd.to_numeric(group[col], errors="coerce").sum())
                except Exception:
                    continue
            if entry:
                aggregates[str(bid)] = entry
        return aggregates

    def _aggregate_business_metrics(df: pd.DataFrame | None) -> dict[str, dict[str, float]]:
        if df is None or df.empty or "__bid__" not in df.columns:
            return {}
        metric_sources = {
            "revenue": "total_amount",
            "margin": "margin_amount",
            "cost": "cost_amount",
        }
        aggregates: dict[str, dict[str, float]] = {}
        grouped = df.groupby("__bid__")
        for bid, group in grouped:
            entry: dict[str, float] = {}
            for metric_name, column in metric_sources.items():
                if column not in group.columns:
                    continue
                numeric_series = pd.to_numeric(group[column], errors="coerce")
                entry[metric_name] = float(numeric_series.sum(skipna=True))
            revenue_col = metric_sources["revenue"]
            if revenue_col in group.columns:
                revenue_series = pd.to_numeric(group[revenue_col], errors="coerce")
                if revenue_series.count():
                    entry["avg_order_value"] = float(revenue_series.mean(skipna=True))
                else:
                    entry["avg_order_value"] = 0.0
            if entry:
                aggregates[str(bid)] = entry
        return aggregates

    aggregated_metrics: dict[str, dict[str, float]] = {}
    parent_aggs = _aggregate_numeric(parent_df, "parent_")
    for bid, vals in parent_aggs.items():
        aggregated_metrics.setdefault(bid, {}).update(vals)
    if has_child and child_df is not None:
        child_aggs = _aggregate_numeric(child_df, "child_")
        for bid, vals in child_aggs.items():
            aggregated_metrics.setdefault(bid, {}).update(vals)
        business_aggs = _aggregate_business_metrics(child_df)
        for bid, vals in business_aggs.items():
            aggregated_metrics.setdefault(bid, {}).update(vals)

    for bid, metrics_map in aggregated_metrics.items():
        target = batch_metadata.setdefault(bid, {})
        for key, value in metrics_map.items():
            target[key] = value

    batches: List[Dict[str, object]] = []
    rows_total = 0

    for bid in parent_ids:
        parent_cnt = int(parent_counts.get(bid, 0))
        if has_child:
            child_cnt = int(child_counts.get(bid, 0))
        else:
            child_cnt = parent_cnt
        rows_total += child_cnt
        batches.append({"id": bid, "parent": parent_cnt, "rows": child_cnt})

    if parent_date:
        time_source = f"{parent_table}.{parent_date}" if parent_table else parent_date
    elif child_date:
        time_source = f"{child_table}.{child_date}" if child_table else child_date
    else:
        time_source = None

    business_metric_names = {"revenue", "margin", "avg_order_value", "cost"}
    present_business_metrics: set[str] = set()
    for metrics_map in aggregated_metrics.values():
        for key in metrics_map:
            if key in business_metric_names:
                present_business_metrics.add(key)

    field_sources: dict[str, str] = {
        "batch_index": "discovery_order",
        "batch_id": "composite_key",
        "rows_per_parent": "computed",
    }
    if parent_table:
        field_sources["parent"] = parent_table
    if child_table:
        field_sources["rows"] = child_table
    elif parent_table:
        field_sources["rows"] = parent_table
    if time_source:
        field_sources["time"] = time_source
    if categorical_fields:
        for col in categorical_fields:
            if col in pcols and parent_table:
                field_sources.setdefault(col, f"{parent_table}.{col}")
            elif col in ccols and child_table:
                field_sources.setdefault(col, f"{child_table}.{col}")
        primary = categorical_fields[0]
        if primary in field_sources:
            field_sources.setdefault("category", field_sources.get(primary, "computed"))
    if child_table:
        child_source_map = {
            "revenue": f"{child_table}.total_amount",
            "margin": f"{child_table}.margin_amount",
            "avg_order_value": f"{child_table}.total_amount",
            "cost": f"{child_table}.cost_amount",
        }
        for metric_name, source in child_source_map.items():
            if metric_name in present_business_metrics:
                field_sources.setdefault(metric_name, source)

    # Collect extra numeric fields for metrics/catalog.
    extra_numeric_fields: list[str] = []
    for metric_fields in aggregated_metrics.values():
        for field_name in metric_fields.keys():
            if field_name not in extra_numeric_fields:
                extra_numeric_fields.append(field_name)

    field_catalog, stats = build_batch_field_catalog_and_stats(
        batches,
        time_source=time_source,
        categorical_fields=categorical_fields,
        numeric_fields=["rows", "parent", "rows_per_parent", *extra_numeric_fields],
        field_sources=field_sources,
    )

    def _collect_metric_stats(metric_name: str) -> dict[str, float] | None:
        values: list[float] = []
        for metrics_map in aggregated_metrics.values():
            if metric_name not in metrics_map:
                continue
            try:
                values.append(float(metrics_map[metric_name]))
            except Exception:
                continue
        if not values:
            return None
        total_val = float(sum(values))
        return {
            "min": float(min(values)),
            "max": float(max(values)),
            "avg": float(total_val / len(values)),
            "total": total_val,
        }

    business_metric_stats: dict[str, dict[str, float]] = {}
    for metric_name in sorted(present_business_metrics):
        metric_stat = _collect_metric_stats(metric_name)
        if metric_stat:
            business_metric_stats[metric_name] = metric_stat
    if business_metric_stats:
        stats.setdefault("metrics_stats", {}).update(business_metric_stats)

    discovery_schema = build_discovery_schema(field_catalog)
    if isinstance(discovery_schema, dict):
        default_metric_candidates = ["revenue", "margin", "avg_order_value", "cost"]
        metrics_list = discovery_schema.get("metrics") or []
        defaults = discovery_schema.setdefault("defaults", {})
        for candidate in default_metric_candidates:
            if any(m.get("name") == candidate for m in metrics_list):
                defaults["metric"] = candidate
                break

    batch_metrics = build_batch_metrics(
        batches,
        batch_metadata,
        extra_fields=[*categorical_fields, *extra_numeric_fields],
    )
    resample_support = build_resample_support(
        field_catalog,
        batch_metrics,
        schema=discovery_schema,
        default_metric=discovery_schema.get("defaults", {}).get("metric"),
        bucket_count=10,
    )

    return {
        "batches": batches,
        "batches_count": len(batches),
        "rows_total": rows_total,
        "batch_metadata": batch_metadata,
        "field_catalog": field_catalog,
        "batch_metrics": batch_metrics,
        "discovery_schema": discovery_schema,
        "numeric_bins": resample_support["numeric_bins"],
        "category_groups": resample_support["category_groups"],
        "data_stats": stats,
    }

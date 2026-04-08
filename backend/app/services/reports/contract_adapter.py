from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

_PARAM_RE = re.compile(r"PARAM:([A-Za-z0-9_]+)")
_DIRECT_COLUMN_RE = re.compile(r"^\s*(?P<table>[A-Za-z_][\w]*)\s*\.\s*(?P<column>[A-Za-z_][\w]*)\s*$")


def _ensure_mapping(value: Any) -> Dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    result: Dict[str, str] = {}
    for key, expr in value.items():
        if key is None:
            continue
        key_text = str(key).strip()
        if not key_text:
            continue
        expr_text = "" if expr is None else str(expr).strip()
        if not expr_text:
            continue
        result[key_text] = expr_text
    return result


def _ensure_mapping_mixed(value: Any) -> Dict[str, Any]:
    """Like _ensure_mapping but preserves dict/object values (for declarative ops)."""
    if not isinstance(value, Mapping):
        return {}
    result: Dict[str, Any] = {}
    for key, expr in value.items():
        if key is None:
            continue
        key_text = str(key).strip()
        if not key_text:
            continue
        if expr is None:
            continue
        # Preserve dicts (declarative ops) and numeric values as-is
        if isinstance(expr, (dict, int, float)):
            result[key_text] = expr
        else:
            expr_text = str(expr).strip()
            if expr_text:
                result[key_text] = expr_text
    return result


def _ensure_sequence(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def format_decimal_str(value: Any, max_decimals: int = 3) -> str:
    """
    Format numeric values with rounding up to max_decimals and trim trailing zeros.
    Non-numeric values are returned as-is (converted to string).
    """
    if value is None:
        return ""

    decimal_value: Optional[Decimal] = None
    if isinstance(value, Decimal):
        decimal_value = value
    else:
        text = str(value).strip()
        if not text:
            return ""
        try:
            decimal_value = Decimal(text)
        except (InvalidOperation, ValueError):
            return str(value)

    if not decimal_value.is_finite():
        logger.warning(
            "format_decimal_non_finite value=%s coerced_to=0",
            value,
            extra={"event": "format_decimal_non_finite", "original": str(value)},
        )
        return "0"

    if max_decimals <= 0:
        rounded = decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    else:
        quantizer = Decimal("1").scaleb(-max_decimals)
        rounded = decimal_value.quantize(quantizer, rounding=ROUND_HALF_UP)

    formatted = format(rounded, "f")
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    if formatted == "-0":
        formatted = "0"
    return formatted


def format_fixed_decimals(value: Any, decimals: int, max_decimals: int = 3) -> str:
    decimals = max(0, min(decimals, max_decimals))
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    if not number.is_finite():
        logger.debug(
            "format_fixed_decimals_non_finite value=%s coerced_to=0",
            value,
            extra={"event": "format_fixed_decimals_non_finite", "original": str(value)},
        )
        number = Decimal(0)
    quantizer = Decimal("1").scaleb(-decimals) if decimals else Decimal("1")
    rounded = number.quantize(quantizer, rounding=ROUND_HALF_UP)
    if rounded == 0:
        rounded = Decimal(0).quantize(quantizer, rounding=ROUND_HALF_UP) if decimals else Decimal(0)
    formatted = format(rounded, "f")
    if rounded == 0 and formatted.startswith("-"):
        formatted = formatted[1:]
    return formatted


@dataclass(frozen=True)
class FormatterSpec:
    kind: str
    arg: Optional[str] = None

    @staticmethod
    def parse(raw: str | None) -> Optional["FormatterSpec"]:
        if not raw:
            return None
        text = raw.strip()
        if not text:
            return None
        m = re.match(r"([a-zA-Z0-9_]+)(?:\((.*)\))?$", text)
        if not m:
            return None
        kind = m.group(1).lower()
        arg = m.group(2)
        return FormatterSpec(kind=kind, arg=arg)


class ContractAdapter:
    """
    Convenience wrapper around a Step-5 contract payload.

    Exposes normalised accessors and helper methods that the discovery and
    report generation flows can rely on without duplicating parsing logic.
    """

    def __init__(self, contract: Mapping[str, Any] | None):
        self._raw = contract or {}

        tokens = self._raw.get("tokens") or {}
        self._scalar_tokens = _ensure_sequence(tokens.get("scalars"))
        self._row_tokens = _ensure_sequence(tokens.get("row_tokens"))
        self._total_tokens = _ensure_sequence(tokens.get("totals"))

        join_block = self._raw.get("join") or {}
        self._parent_table = str(join_block.get("parent_table") or "").strip()
        self._child_table = str(join_block.get("child_table") or "").strip()
        self._parent_key = join_block.get("parent_key")
        self._child_key = join_block.get("child_key")

        self._date_columns = _ensure_mapping(self._raw.get("date_columns"))

        filters = self._raw.get("filters") or {}
        self._required_filters = _ensure_mapping(filters.get("required"))
        self._optional_filters = _ensure_mapping(filters.get("optional"))

        self._pre_aggregate = self._raw.get("pre_aggregate") or {}
        self._group_aggregate = self._raw.get("group_aggregate") or {}
        self._post_aggregate = self._raw.get("post_aggregate") or {}
        self._reshape_rules = self._raw.get("reshape_rules") or []
        self._row_computed = _ensure_mapping_mixed(self._raw.get("row_computed"))
        self._totals_math = _ensure_mapping_mixed(self._raw.get("totals_math"))
        self._formatters_raw = _ensure_mapping(self._raw.get("formatters"))

        order_by_block = self._raw.get("order_by") or {}
        self._order_by_rows = _ensure_sequence(order_by_block.get("rows"))
        self._row_order = _ensure_sequence(self._raw.get("row_order"))

        self._totals_mapping = _ensure_mapping_mixed(self._raw.get("totals"))
        self._mapping = _ensure_mapping(self._raw.get("mapping"))
        if not self._parent_table:
            inferred_parent = self._infer_parent_table(self._mapping)
            if inferred_parent:
                self._parent_table = inferred_parent

        self._param_tokens = self._discover_param_tokens()
        self._formatter_cache: Dict[str, FormatterSpec | None] = {}

    # ------------------------------------------------------------------ #
    # Basic properties
    # ------------------------------------------------------------------ #
    @property
    def mapping(self) -> Dict[str, str]:
        return dict(self._mapping)

    @property
    def scalar_tokens(self) -> List[str]:
        return list(self._scalar_tokens)

    @property
    def row_tokens(self) -> List[str]:
        return list(self._row_tokens)

    @property
    def total_tokens(self) -> List[str]:
        return list(self._total_tokens)

    @property
    def parent_table(self) -> str:
        return self._parent_table

    @property
    def child_table(self) -> str:
        return self._child_table

    @property
    def parent_key(self) -> Any:
        return self._parent_key

    @property
    def child_key(self) -> Any:
        return self._child_key

    @property
    def date_columns(self) -> Dict[str, str]:
        return dict(self._date_columns)

    @property
    def required_filters(self) -> Dict[str, str]:
        return dict(self._required_filters)

    @property
    def optional_filters(self) -> Dict[str, str]:
        return dict(self._optional_filters)

    @property
    def reshape_rules(self) -> Sequence[Mapping[str, Any]]:
        return list(self._reshape_rules)

    @property
    def row_computed(self) -> Dict[str, str]:
        return dict(self._row_computed)

    @property
    def totals_math(self) -> Dict[str, str]:
        return dict(self._totals_math)

    @property
    def formatters(self) -> Dict[str, str]:
        return dict(self._formatters_raw)

    @property
    def order_by_rows(self) -> List[str]:
        return list(self._order_by_rows)

    @property
    def row_order(self) -> List[str]:
        return list(self._row_order)

    @property
    def totals_mapping(self) -> Dict[str, str]:
        return dict(self._totals_mapping)

    @property
    def param_tokens(self) -> List[str]:
        return sorted(self._param_tokens)

    # ------------------------------------------------------------------ #
    # Formatting helpers
    # ------------------------------------------------------------------ #
    def get_formatter_spec(self, token: str) -> Optional[FormatterSpec]:
        if token in self._formatter_cache:
            return self._formatter_cache[token]
        raw = self._formatters_raw.get(token)
        spec = FormatterSpec.parse(raw)
        self._formatter_cache[token] = spec
        return spec

    def format_value(self, token: str, value: Any) -> str:
        spec = self.get_formatter_spec(token)
        if spec is None:
            if value is None:
                return ""
            if isinstance(value, (int, float, Decimal)):
                return format_decimal_str(value)
            if isinstance(value, str):
                candidate = value.strip()
                if not candidate:
                    return ""
                lowered = candidate.lower()
                if "." in candidate or "e" in lowered:
                    return format_decimal_str(candidate)
                return value
            return str(value)
        kind = spec.kind
        if value is None:
            return ""

        if kind == "number":
            decimals = 0
            if spec.arg:
                try:
                    decimals = int(spec.arg.strip())
                except ValueError:
                    decimals = 0
            return format_fixed_decimals(value, decimals, max_decimals=3)

        if kind == "percent":
            decimals = 0
            if spec.arg:
                try:
                    decimals = int(spec.arg.strip())
                except ValueError:
                    decimals = 0
            try:
                text = str(value).strip()
                if text.endswith("%"):
                    text = text[:-1].strip()
                number = Decimal(text)
            except (InvalidOperation, ValueError, TypeError):
                return str(value)
            if not number.is_finite():
                number = Decimal(0)
            if abs(number) <= 1:
                number *= Decimal(100)
            formatted = format_fixed_decimals(number, decimals, max_decimals=3)
            return f"{formatted}%"

        if kind == "date":
            fmt = (spec.arg or "YYYY-MM-DD").strip()
            return self._format_date_like(value, fmt)

        return str(value)

    @staticmethod
    def _format_date_like(value: Any, fmt: str) -> str:
        from datetime import datetime

        if value is None:
            return ""
        text = str(value).strip()
        if not text:
            return ""
        dt: Optional[datetime] = None
        for pattern in (
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
        ):
            try:
                dt = datetime.strptime(text, pattern)
                break
            except ValueError:
                continue
        if dt is None:
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return text

        fmt_map = {
            # Date only
            "DD/MM/YYYY": "%d/%m/%Y",
            "YYYY-MM-DD": "%Y-%m-%d",
            "DD-MM-YYYY": "%d-%m-%Y",
            "MM/DD/YYYY": "%m/%d/%Y",
            # Date + time
            "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
            "YYYY-MM-DD HH:MM": "%Y-%m-%d %H:%M",
            "DD/MM/YYYY HH:MM:SS": "%d/%m/%Y %H:%M:%S",
            "DD/MM/YYYY HH:MM": "%d/%m/%Y %H:%M",
            "MM/DD/YYYY HH:MM:SS": "%m/%d/%Y %H:%M:%S",
            "DD-MM-YYYY HH:MM:SS": "%d-%m-%Y %H:%M:%S",
            "DD-MM-YYYY HH:MM": "%d-%m-%Y %H:%M",
            # ISO 8601
            "ISO": "%Y-%m-%dT%H:%M:%S",
            "ISO8601": "%Y-%m-%dT%H:%M:%S",
        }
        fallback = "%Y-%m-%d %H:%M:%S" if "HH" in fmt.upper() else "%Y-%m-%d"
        pattern = fmt_map.get(fmt.upper(), fallback)
        return dt.strftime(pattern)

    @staticmethod
    def _infer_parent_table(mapping: Mapping[str, str]) -> Optional[str]:
        for expr in mapping.values():
            if not isinstance(expr, str):
                continue
            match = _DIRECT_COLUMN_RE.match(expr.strip())
            if not match:
                continue
            table_name = match.group("table").strip(' "`[]')
            if table_name and not table_name.lower().startswith("params"):
                return table_name
        return None

    # ------------------------------------------------------------------ #
    # DataFrame resolve methods
    # ------------------------------------------------------------------ #

    def _resolve_mapping_column(self, token: str) -> Optional[Tuple[str, str]]:
        """Return (table, column) from a token's mapping, or None if not a direct ref.

        Mappings like ``params.report_date`` are treated as parameter
        references (not real table.column lookups) and return ``None``.
        """
        expr = self._mapping.get(token, "")
        m = _DIRECT_COLUMN_RE.match(expr)
        if m:
            table = m.group("table")
            # params.xxx is a parameter reference, not a table.column
            if table.lower() == "params":
                return None
            return table, m.group("column")
        return None

    def _apply_date_filter_df(self, df, table: str, start_date: str | None, end_date: str | None):
        """Apply date range filter to a DataFrame using contract date_columns."""
        import pandas as pd
        from .discovery_excel import _coerce_datetime_series, _parse_date_like, _snap_end_of_day

        date_col = self._date_columns.get(table.lower()) or self._date_columns.get(table)
        if not date_col or date_col not in df.columns:
            return df
        if not start_date and not end_date:
            return df
        start_dt = _parse_date_like(start_date) if start_date else None
        end_dt = _parse_date_like(end_date) if end_date else None
        if start_dt is None and end_dt is None:
            return df
        if end_dt is not None:
            end_dt = _snap_end_of_day(end_dt)

        dt_series = _coerce_datetime_series(df[date_col])
        mask = pd.Series(True, index=df.index)
        if start_dt:
            mask = mask & (dt_series >= start_dt)
        if end_dt:
            mask = mask & (dt_series <= end_dt)
        return df.loc[mask.fillna(False)]

    @staticmethod
    def _normalize_numeric_str(s: str) -> str:
        """Normalize numeric strings: '1.0' → '1', '2.00' → '2', 'abc' → 'abc'."""
        try:
            f = float(s)
            if f == int(f):
                return str(int(f))
            return str(f)
        except (ValueError, TypeError):
            return s

    def _apply_value_filters_df(self, df, value_filters: Dict[str, list]):
        """Apply equality filters from contract optional_filters."""
        import pandas as pd

        if not value_filters:
            return df
        mask = pd.Series(True, index=df.index)
        for filter_key, filter_values in value_filters.items():
            col_expr = self._optional_filters.get(filter_key, "")
            m = _DIRECT_COLUMN_RE.match(col_expr)
            col_name = m.group("column") if m else filter_key
            if col_name not in df.columns:
                continue
            normalized = [str(v).strip() for v in filter_values if str(v or "").strip()]
            if not normalized:
                continue
            # Normalize both sides for numeric comparison (e.g. "1" matches "1.0")
            norm_set = set(normalized) | {self._normalize_numeric_str(v) for v in normalized}
            series = df[col_name].astype(str).str.strip()
            norm_series = series.map(self._normalize_numeric_str)
            mask = mask & (series.isin(norm_set) | norm_series.isin(norm_set))
        return df.loc[mask.fillna(False)]

    def _apply_pre_aggregate_df(self, df):
        """Collapse time-series into one row per batch (first_per_run strategy).

        Reads ``pre_aggregate`` from the contract:
          batch_column   – column that identifies the batch (e.g. OIL_BACTH_COUNT)
          timestamp_column – used for ordering within each batch
          strategy       – currently only "first_per_run"
          skip_value     – batch_column value to exclude (e.g. 0)
        """
        pa = self._pre_aggregate
        batch_col = pa.get("batch_column", "")
        ts_col = pa.get("timestamp_column", "")
        strategy = pa.get("strategy", "")
        skip_value = pa.get("skip_value")

        if not batch_col or batch_col not in df.columns:
            return df
        if df.empty:
            return df

        # Filter out rows matching skip_value
        if skip_value is not None:
            mask = df[batch_col].astype(str).str.strip() != str(skip_value).strip()
            df = df.loc[mask]
            if df.empty:
                return df

        if strategy == "first_per_run":
            # Sort by timestamp if available, then keep first row per batch
            if ts_col and ts_col in df.columns:
                df = df.sort_values(ts_col, ascending=True)
                # Capture last timestamp per batch as end_timestamp_utc
                # (before dedup removes them)
                end_ts = df.groupby(batch_col, sort=False)[ts_col].transform("last")
                df = df.copy()
                df["end_timestamp_utc"] = end_ts
            df = df.drop_duplicates(subset=[batch_col], keep="first")

        logger.info("pre_aggregate applied: %s → %d rows", strategy, len(df))
        return df

    def _apply_group_aggregate_df(self, df, override_config=None):
        """Aggregate across all batches (e.g. sum) to collapse N batch rows → 1 row.

        Reads ``group_aggregate`` from the contract (or override_config):
          strategy – "sum" (only supported strategy currently)
          columns  – list of columns to aggregate
        Non-aggregated columns keep first row values.
        """
        import pandas as pd

        ga = override_config if override_config is not None else self._group_aggregate
        strategy = ga.get("strategy", "")
        agg_columns = ga.get("columns", [])

        if not strategy or df.empty:
            return df

        if strategy != "group_by" and not agg_columns:
            return df

        if strategy == "sum":
            # Resolve actual column names in the DataFrame
            agg_map = {}
            for col in agg_columns:
                actual = self._resolve_df_col(df, col)
                if actual:
                    agg_map[actual] = "sum"

            if not agg_map:
                return df

            # Coerce aggregation columns to numeric
            for col in agg_map:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            # Build aggregation dict: sum for specified cols, first for everything else
            full_agg = {}
            for col in df.columns:
                if col in agg_map:
                    full_agg[col] = "sum"
                else:
                    full_agg[col] = "first"

            result = df.groupby(lambda _: 0, sort=False).agg(full_agg)
            result = result.reset_index(drop=True)
            logger.info("group_aggregate applied: %s → %d rows (from %d)", strategy, len(result), len(df))
            return result

        if strategy == "group_by":
            # Group by specified column(s), aggregate others, add count column.
            # Contract: group_columns (list), aggregations (dict col→func), count_as (str)
            group_columns = ga.get("group_columns", [])
            aggregations = ga.get("aggregations", {})
            count_as = ga.get("count_as", "__count__")

            if not group_columns:
                logger.warning("group_by strategy missing group_columns, skipping")
                return df

            # Resolve actual column names
            resolved_groups = []
            for gc in group_columns:
                actual = self._resolve_df_col(df, gc)
                if actual:
                    resolved_groups.append(actual)
                elif gc in df.columns:
                    resolved_groups.append(gc)

            if not resolved_groups:
                logger.warning("group_by: none of %s found in DataFrame", group_columns)
                return df

            # Build aggregation map
            agg_map = {}
            for col, func in aggregations.items():
                actual = self._resolve_df_col(df, col) or col
                if actual in df.columns:
                    if func == "min":
                        df[actual] = pd.to_numeric(df[actual], errors="coerce")
                    agg_map[actual] = func

            # Default: first for all non-group columns not in aggregations
            full_agg = {}
            for col in df.columns:
                if col in resolved_groups:
                    continue
                if col in agg_map:
                    full_agg[col] = agg_map[col]
                else:
                    full_agg[col] = "first"

            result = df.groupby(resolved_groups, sort=True).agg(full_agg)

            # Add count column
            counts = df.groupby(resolved_groups, sort=True).size()
            result[count_as] = counts.values

            result = result.reset_index()
            logger.info("group_aggregate applied: %s → %d rows (from %d)", strategy, len(result), len(df))
            return result

        logger.warning("group_aggregate strategy %r not supported, skipping", strategy)
        return df

    @staticmethod
    def _resolve_df_col(df, col: str) -> str | None:
        """Resolve a column name against a DataFrame, stripping table prefix
        and falling back to case-insensitive match if needed.

        Returns the actual DataFrame column name, or None if not found.
        """
        # Exact match first
        if col in df.columns:
            return col
        # Strip table prefix (e.g. "neuract__ANALYSER_TABLE.timestamp_utc" → "timestamp_utc")
        if "." in col:
            col = col.rsplit(".", 1)[1]
            if col in df.columns:
                return col
        # Case-insensitive fallback
        col_lower = col.lower()
        for actual in df.columns:
            if isinstance(actual, str) and actual.lower() == col_lower:
                return actual
        return None

    @staticmethod
    def _coerce_numeric(val):
        """Coerce a value or Series to numeric for arithmetic ops."""
        import pandas as pd
        if isinstance(val, pd.Series):
            return pd.to_numeric(val, errors="coerce").fillna(0)
        if isinstance(val, str):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0
        return val

    def _apply_declarative_op(self, df, op_spec) -> Any:
        """Interpret a declarative operation spec and return computed result.

        Supports both new-style dict ops and legacy SQL expression strings.
        """
        import pandas as pd

        if isinstance(op_spec, str):
            return self._interpret_legacy_computed(df, op_spec)

        if not isinstance(op_spec, dict):
            return None

        op = op_spec.get("op", "").lower()
        if op == "subtract":
            left = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("left", 0)))
            right = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("right", 0)))
            if left is None or right is None:
                return None
            return left - right
        elif op == "add":
            left = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("left", 0)))
            right = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("right", 0)))
            if left is None or right is None:
                return None
            return left + right
        elif op == "multiply":
            left = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("left", 0)))
            right = self._coerce_numeric(self._resolve_agg_or_col(df, op_spec.get("right", 0)))
            if left is None or right is None:
                return None
            return left * right
        elif op == "divide":
            num_spec = op_spec.get("numerator", op_spec.get("left", ""))
            den_spec = op_spec.get("denominator", op_spec.get("right", ""))
            num = self._coerce_numeric(self._resolve_agg_or_col(df, num_spec))
            den = self._coerce_numeric(self._resolve_agg_or_col(df, den_spec))
            if isinstance(den, (int, float)) and den == 0:
                return None
            if isinstance(num, pd.Series) and isinstance(den, pd.Series):
                return num / den.replace(0, float("nan"))
            return num / den if den else None
        elif op == "sum":
            col = op_spec.get("column", "")
            resolved = self._resolve_df_col(df, col)
            if resolved:
                return df[resolved].sum()
            return 0
        elif op == "mean":
            col = op_spec.get("column", "")
            resolved = self._resolve_df_col(df, col)
            if resolved:
                return df[resolved].mean()
            return 0
        elif op == "add_many":
            # Sum multiple columns row-wise: columns: ["col1", "col2", ...]
            cols = op_spec.get("columns", [])
            total = None
            for c in cols:
                rc = self._resolve_df_col(df, c)
                if rc:
                    series = pd.to_numeric(df[rc], errors="coerce").fillna(0)
                    total = series if total is None else total + series
            return total if total is not None else 0
        elif op == "count":
            col = op_spec.get("column", "")
            resolved = self._resolve_df_col(df, col)
            if resolved:
                return df[resolved].count()
            return len(df)
        elif op == "concat":
            cols = op_spec.get("columns", [])
            sep = op_spec.get("separator", " ")
            parts = []
            for c in cols:
                rc = self._resolve_df_col(df, c)
                if rc:
                    parts.append(df[rc].astype(str))
            if parts:
                result = parts[0]
                for p in parts[1:]:
                    result = result + sep + p
                return result
            return ""
        elif op == "format_date":
            col = op_spec.get("column", "")
            fmt = op_spec.get("format", "%Y-%m-%d")
            resolved = self._resolve_df_col(df, col)
            if resolved:
                from .discovery_excel import _coerce_datetime_series
                dt_s = _coerce_datetime_series(df[resolved])
                return dt_s.dt.strftime(fmt).fillna("")
            return ""
        elif op == "format_number":
            col = op_spec.get("column", "")
            decimals = op_spec.get("decimals", 2)
            resolved = self._resolve_df_col(df, col)
            if resolved:
                return df[resolved].round(decimals)
            return 0
        elif op == "format_hms":
            col = op_spec.get("column", "")
            resolved = self._resolve_df_col(df, col)
            if resolved:
                total_sec = int(pd.to_numeric(df[resolved], errors="coerce").sum())
            else:
                total_sec = 0
            h, rem = divmod(abs(total_sec), 3600)
            m, s = divmod(rem, 60)
            sign = "-" if total_sec < 0 else ""
            return f"{sign}{h}:{m:02d}:{s:02d}"
        else:
            logger.warning("unknown_declarative_op", extra={"op": op})
            return None

    def _resolve_agg_or_col(self, df, spec) -> Any:
        """Resolve a spec that can be a column name string, nested op dict, or numeric literal."""
        if isinstance(spec, (int, float)):
            return spec
        if isinstance(spec, str):
            resolved = self._resolve_df_col(df, spec)
            if resolved:
                return df[resolved]
            return 0
        if isinstance(spec, dict):
            return self._apply_declarative_op(df, spec)
        return 0

    def _interpret_legacy_computed(self, df, expr: str) -> Any:
        """Regex-based fallback for old SQL expressions like SUM(col1) - SUM(col2)."""
        import pandas as pd

        # Try simple column reference: table.column
        m = _DIRECT_COLUMN_RE.match(expr.strip())
        if m:
            col = m.group("column")
            if col in df.columns:
                return df[col]
            return None

        # Try SUM(column)
        sum_match = re.match(r"^\s*SUM\s*\(\s*(?:\w+\.)?(\w+)\s*\)\s*$", expr, re.IGNORECASE)
        if sum_match:
            col = sum_match.group(1)
            if col in df.columns:
                return df[col].sum()
            return 0

        # Try SUM(a) - SUM(b)
        diff_match = re.match(
            r"^\s*SUM\s*\(\s*(?:\w+\.)?(\w+)\s*\)\s*-\s*SUM\s*\(\s*(?:\w+\.)?(\w+)\s*\)\s*$",
            expr, re.IGNORECASE,
        )
        if diff_match:
            col_a, col_b = diff_match.group(1), diff_match.group(2)
            a = df[col_a].sum() if col_a in df.columns else 0
            b = df[col_b].sum() if col_b in df.columns else 0
            return a - b

        # Try SUM(a) / NULLIF(SUM(b), 0) or similar ratio
        ratio_match = re.match(
            r"^\s*SUM\s*\(\s*(?:\w+\.)?(\w+)\s*\)\s*/\s*(?:NULLIF\s*\()?\s*SUM\s*\(\s*(?:\w+\.)?(\w+)\s*\)\s*(?:,\s*0\s*\))?\s*$",
            expr, re.IGNORECASE,
        )
        if ratio_match:
            col_a, col_b = ratio_match.group(1), ratio_match.group(2)
            a = df[col_a].sum() if col_a in df.columns else 0
            b = df[col_b].sum() if col_b in df.columns else 0
            return a / b if b else None

        logger.warning("uninterpretable_legacy_computed", extra={"expr": expr})
        return None

    def resolve_header_data(
        self,
        loader,
        params: Dict[str, Any],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Dict[str, Any]:
        """Fetch scalar/header values via DataFrame access. Returns {token: value}."""
        result: Dict[str, Any] = {}
        header_tokens = _ensure_sequence(self._raw.get("header_tokens")) or self._scalar_tokens

        for token in header_tokens:
            # Check if it's a PARAM (PARAM:xxx format)
            mapping_expr = self._mapping.get(token, "")
            pm = _PARAM_RE.match(mapping_expr)
            if pm:
                param_name = pm.group(1)
                result[token] = params.get(param_name, "")
                continue

            # Check params.xxx dot-notation format
            dot_m = _DIRECT_COLUMN_RE.match(mapping_expr)
            if dot_m and dot_m.group("table").lower() == "params":
                param_name = dot_m.group("column")
                result[token] = params.get(param_name, "")
                continue

            ref = self._resolve_mapping_column(token)
            if not ref:
                result[token] = ""
                continue

            table, column = ref
            try:
                df = loader.frame(table)
            except Exception:
                result[token] = ""
                continue

            df = self._apply_date_filter_df(df, table, start_date, end_date)
            if df.empty:
                result[token] = ""
                continue
            # Exact match first, then case-insensitive fallback
            if column not in df.columns:
                col_lower = column.lower()
                matched = next(
                    (c for c in df.columns if isinstance(c, str) and c.lower() == col_lower),
                    None,
                )
                if matched:
                    column = matched
                else:
                    result[token] = ""
                    continue

            # Take first non-null value
            non_null = df[column].dropna()
            result[token] = str(non_null.iloc[0]) if not non_null.empty else ""

        return result

    def resolve_row_data(
        self,
        loader,
        params: Dict[str, Any],
        start_date: str | None = None,
        end_date: str | None = None,
        value_filters: Dict[str, list] | None = None,
    ):
        """Fetch row data via DataFrame filtering and return a DataFrame."""
        import pandas as pd

        row_tokens = _ensure_sequence(self._raw.get("row_tokens")) or self._row_tokens
        if not row_tokens:
            return pd.DataFrame()

        # Determine source table from first row token mapping reference,
        # falling back to parent_table.  Row tokens often live in the child
        # (detail) table, not the parent (header) table.
        source_table = None
        for tok in row_tokens:
            ref = self._resolve_mapping_column(tok)
            if ref:
                source_table = ref[0]
                break
        if not source_table:
            source_table = self._parent_table

        if not source_table:
            return pd.DataFrame()

        # Pre-filter at SQL level when date column is known to avoid loading
        # millions of rows into memory (e.g. 2.7M temperature rows).
        date_col = self._date_columns.get(source_table.lower()) or self._date_columns.get(source_table)
        try:
            if date_col and (start_date or end_date) and hasattr(loader, 'frame_date_filtered'):
                df = loader.frame_date_filtered(source_table, date_col, start_date, end_date).copy()
                logger.info("resolve_row_data: loaded %d rows from %s (SQL date-filtered)", len(df), source_table)
            else:
                df = loader.frame(source_table).copy()
                logger.info("resolve_row_data: loaded %d rows from %s (full)", len(df), source_table)
        except Exception:
            logger.exception("resolve_row_data: failed to load table %r", source_table)
            return pd.DataFrame()

        # Apply DataFrame-level date filter as safety net (handles timezone stripping, snap, etc.)
        df = self._apply_date_filter_df(df, source_table, start_date, end_date)
        logger.info("resolve_row_data: %d rows after date filter (start=%s end=%s)", len(df), start_date, end_date)

        # Apply value filters
        if value_filters:
            df = self._apply_value_filters_df(df, value_filters)

        # Apply pre_aggregate (collapse time-series into one row per batch)
        if self._pre_aggregate:
            df = self._apply_pre_aggregate_df(df)

        # Apply group_aggregate (sum across batches → single row)
        if self._group_aggregate:
            df = self._apply_group_aggregate_df(df)

        # Apply reshape rules if present
        melt_alias_set: set[str] = set()
        if self._reshape_rules:
            df = self._apply_reshape_df(df, loader, source_table)
            logger.info("resolve_row_data: %d rows after reshape", len(df))
            # Build set of reshape alias column names for fallback resolution
            for rule in self._reshape_rules:
                for col_spec in rule.get("columns", []):
                    alias = col_spec.get("as", "")
                    if alias:
                        melt_alias_set.add(alias)
                # WINDOW_DIFF produces output_columns directly
                for out_col in rule.get("output_columns", []):
                    if out_col:
                        melt_alias_set.add(out_col)

        # Apply post_aggregate (runs AFTER reshape, e.g. group melted rows by material)
        if self._post_aggregate:
            df = self._apply_group_aggregate_df(df, self._post_aggregate)

        # Build result with mapped columns.
        # Add computed columns back to df so subsequent computations can reference them.
        result_cols: Dict[str, Any] = {}
        for tok in row_tokens:
            resolved = False
            short = tok.removeprefix("row_") if tok.startswith("row_") else tok

            # 1. Try row_computed first (format_date, concat, etc. take priority)
            if tok in self._row_computed:
                computed = self._apply_declarative_op(df, self._row_computed[tok])
                if computed is not None:
                    result_cols[tok] = computed
                    resolved = True
                    # Feed computed column back to df under both token name and
                    # short name so subsequent ops can reference it
                    try:
                        df[tok] = computed
                        if short != tok:
                            df[short] = computed
                    except Exception:
                        pass

            # 1b. INDEX mapping → 1-based serial number
            if not resolved and self._mapping.get(tok) == "INDEX":
                result_cols[tok] = list(range(1, len(df) + 1))
                resolved = True

            # 1c. Direct column match (MELT alias IS the token name)
            if not resolved and tok in df.columns:
                result_cols[tok] = df[tok].values
                resolved = True

            # 2. Try direct mapping resolution (table.column)
            if not resolved:
                ref = self._resolve_mapping_column(tok)
                if ref:
                    _, col = ref
                    if col in df.columns:
                        result_cols[tok] = df[col].values
                        resolved = True
                    elif melt_alias_set and (short in df.columns or tok in df.columns):
                        # After MELT, columns are named by alias (full or stripped)
                        col_to_use = short if short in df.columns else tok
                        result_cols[tok] = df[col_to_use].values
                        resolved = True
                    else:
                        # Case-insensitive column fallback
                        col_lower = col.lower()
                        for actual_col in df.columns:
                            if isinstance(actual_col, str) and actual_col.lower() == col_lower:
                                result_cols[tok] = df[actual_col].values
                                resolved = True
                                break

            # 3. Try MELT alias match by stripped name or full token name
            if not resolved and melt_alias_set and (short in df.columns or tok in df.columns):
                col_to_use = short if short in df.columns else tok
                result_cols[tok] = df[col_to_use].values
                resolved = True

            # 4. Fallback
            if not resolved:
                mapping_expr = self._mapping.get(tok, "")
                logger.warning("row_token_unresolved", extra={
                    "event": "row_token_unresolved",
                    "token": tok,
                    "mapping_expr": mapping_expr,
                    "available_columns": list(df.columns)[:20],
                })
                result_cols[tok] = ""

        try:
            result_df = pd.DataFrame(result_cols)
        except ValueError:
            # All scalar values (e.g. every token unresolved → "") — wrap in list
            result_df = pd.DataFrame({k: [v] for k, v in result_cols.items()})

        # Carry forward __batch_idx__ and metadata columns for BLOCK_REPEAT grouping
        if melt_alias_set and "__batch_idx__" in df.columns:
            result_df["__batch_idx__"] = df["__batch_idx__"].values
            # Collect the set of all melted source columns
            _all_melted_src: set[str] = set()
            for rule in self._reshape_rules:
                for cs in rule.get("columns", []):
                    for f in cs.get("from", []):
                        if f != "INDEX" and "." in f:
                            _all_melted_src.add(f.split(".", 1)[1])
            for col in df.columns:
                if col.startswith("__") or col in _all_melted_src:
                    continue
                if col not in result_df.columns and col not in melt_alias_set:
                    result_df[f"__cf_{col}"] = df[col].values

        # Apply ordering
        order_cols = self._row_order or self._order_by_rows
        if order_cols:
            sort_by: list[str] = []
            ascending: list[bool] = []
            for clause in order_cols:
                parts = clause.strip().split()
                col_name = parts[0] if parts else ""
                if col_name in result_df.columns:
                    sort_by.append(col_name)
                    ascending.append(not (len(parts) > 1 and parts[1].upper() == "DESC"))
            if sort_by:
                result_df = result_df.sort_values(sort_by, ascending=ascending, ignore_index=True)

        return result_df

    def resolve_totals_data(self, rows_df) -> Dict[str, Any]:
        """Compute totals from the rows DataFrame using declarative specs."""
        import pandas as pd

        result: Dict[str, Any] = {}
        total_tokens = self._total_tokens
        totals_math = self._totals_math
        totals_mapping = self._totals_mapping

        # Add short aliases (strip row_ prefix) so totals_math can reference
        # "set_wt" even though column is "row_set_wt"
        if isinstance(rows_df, pd.DataFrame) and not rows_df.empty:
            for col in list(rows_df.columns):
                if col.startswith("row_"):
                    short = col.removeprefix("row_")
                    if short not in rows_df.columns:
                        rows_df = rows_df.copy()
                        rows_df[short] = rows_df[col]

        for tok in total_tokens or list(totals_math.keys()):
            if tok in totals_math:
                val = self._apply_declarative_op(rows_df, totals_math[tok])
                result[tok] = val if val is not None else ""
            elif tok in totals_mapping:
                val = self._apply_declarative_op(rows_df, totals_mapping[tok])
                result[tok] = val if val is not None else ""
            else:
                result[tok] = ""

        return result

    def _apply_reshape_df(self, df, loader, source_table: str):
        """Apply reshape rules (UNION_ALL / MELT) to produce long-form data."""
        import pandas as pd

        for rule in self._reshape_rules:
            strategy = str(rule.get("strategy", "")).upper()
            columns = rule.get("columns", [])

            if strategy == "UNION_ALL" and columns:
                frames: list[pd.DataFrame] = []
                # Each column spec: {"as": "alias", "from": ["col1", "col2", ...]}
                n_rows = len(columns[0].get("from", [])) if columns else 0
                for i in range(n_rows):
                    row_df = pd.DataFrame()
                    for col_spec in columns:
                        alias = col_spec.get("as", "")
                        sources = col_spec.get("from", [])
                        if i < len(sources):
                            src = sources[i]
                            # Source can be table.column or just column
                            if "." in src:
                                _, src_col = src.split(".", 1)
                            else:
                                src_col = src
                            if src_col in df.columns:
                                row_df[alias] = df[src_col].values
                            else:
                                row_df[alias] = ""
                    if not row_df.empty:
                        frames.append(row_df)

                if frames:
                    df = pd.concat(frames, ignore_index=True)
                    # Drop rows where all aliased columns are empty
                    alias_cols = [c.get("as", "") for c in columns if c.get("as")]
                    existing = [c for c in alias_cols if c in df.columns]
                    if existing:
                        df = df.dropna(subset=existing, how="all")
                        str_df = df[existing].fillna("").astype(str)
                        for c in str_df.columns:
                            str_df[c] = str_df[c].str.strip()
                        str_mask = (str_df != "").any(axis=1)
                        df = df.loc[str_mask].reset_index(drop=True)

            elif strategy == "MELT" and columns:
                # Melt: unpivot wide columns into long format.
                # Each column spec: {"as": "alias", "from": ["table.col1", "table.col2", ...]}
                # Special: {"as": "alias", "from": ["INDEX"]} → 1-based position index
                frames: list[pd.DataFrame] = []
                # Determine number of positions from the first non-INDEX column
                n_positions = 0
                for col_spec in columns:
                    froms = col_spec.get("from", [])
                    if froms and froms != ["INDEX"]:
                        n_positions = len(froms)
                        break

                # Tag each original row with a batch index for BLOCK_REPEAT grouping
                import numpy as np
                df["__batch_idx__"] = np.arange(len(df))

                for i in range(n_positions):
                    slice_df = pd.DataFrame()
                    for col_spec in columns:
                        alias = col_spec.get("as", "")
                        froms = col_spec.get("from", [])
                        if froms == ["INDEX"]:
                            # Generate 1-based index for each original row
                            slice_df[alias] = [i + 1] * len(df)
                        elif i < len(froms):
                            src = froms[i]
                            src_col = src.split(".", 1)[1] if "." in src else src
                            if src_col in df.columns:
                                slice_df[alias] = df[src_col].values
                            else:
                                # Not a column — treat as literal value (e.g. bin_number: "1", "2", ...)
                                slice_df[alias] = [src if src else ""] * len(df)
                    if not slice_df.empty:
                        # Carry forward non-melted columns (e.g. recipe_name, id, start_time)
                        melted_src_cols: set[str] = set()
                        for cs in columns:
                            for f in cs.get("from", []):
                                if f != "INDEX" and "." in f:
                                    melted_src_cols.add(f.split(".", 1)[1])
                        for orig_col in df.columns:
                            if orig_col not in melted_src_cols and orig_col not in slice_df.columns:
                                slice_df[orig_col] = df[orig_col].values
                        frames.append(slice_df)

                if frames:
                    df = pd.concat(frames, ignore_index=True)
                    # Drop rows where the primary alias (first non-INDEX) is null/empty
                    primary_alias = ""
                    for cs in columns:
                        if cs.get("from", []) != ["INDEX"]:
                            primary_alias = cs.get("as", "")
                            break
                    if primary_alias and primary_alias in df.columns:
                        mask = df[primary_alias].notna()
                        str_vals = df[primary_alias].astype(str).str.strip()
                        mask = mask & (str_vals != "") & (str_vals.str.lower() != "nan") & (str_vals.str.lower() != "none")
                        df = df.loc[mask].reset_index(drop=True)

            elif strategy == "SELECT" and columns:
                # SELECT: derive/rename columns, optionally group by + aggregate.
                # Each column spec: {"as": "alias", "from": ["table.col"]}
                # If from[0] is "date(table.col)" → extract date part.
                # If the rule has "group_by": true, group by derived columns
                # and SUM all numeric columns.
                from .discovery_excel import _coerce_datetime_series

                for col_spec in columns:
                    alias = col_spec.get("as", "")
                    sources = col_spec.get("from", [])
                    if not alias or not sources:
                        continue
                    src = sources[0]
                    # Handle date() wrapper
                    date_match = re.match(r"date\((.+)\)", src, re.IGNORECASE)
                    if date_match:
                        inner = date_match.group(1)
                        src_col = inner.split(".", 1)[1] if "." in inner else inner
                        if src_col in df.columns:
                            dt_s = _coerce_datetime_series(df[src_col])
                            df[alias] = dt_s.dt.strftime("%Y-%m-%d").fillna("")
                    else:
                        src_col = src.split(".", 1)[1] if "." in src else src
                        if src_col in df.columns:
                            df[alias] = df[src_col].values

                # If group_by hint is present, group by derived alias columns
                group_by_aliases = rule.get("group_by")
                if group_by_aliases:
                    if isinstance(group_by_aliases, bool):
                        # Auto-detect: group by all non-numeric derived columns
                        group_by_aliases = [
                            cs.get("as", "") for cs in columns
                            if cs.get("as", "") in df.columns
                            and not pd.api.types.is_numeric_dtype(df[cs["as"]])
                        ]
                    existing_groups = [g for g in group_by_aliases if g in df.columns]
                    if existing_groups:
                        agg_map = {}
                        for col in df.columns:
                            if col in existing_groups:
                                continue
                            if pd.api.types.is_numeric_dtype(df[col]):
                                agg_map[col] = "sum"
                            else:
                                agg_map[col] = "first"
                        df = df.groupby(existing_groups, sort=True).agg(agg_map).reset_index()
                        logger.info("select_group_by applied → %d rows", len(df))

            elif strategy == "WINDOW_DIFF":
                # Detect run intervals from cumulative counter changes.
                # column_groups: [{machine_name, columns: [HRS, MIN, SEC]}]
                # Produces rows: machine_name, run_date, start_time, end_time, duration_sec, shift_no, total_time
                df = self._apply_window_diff(df, rule, loader)

        return df

    def _apply_window_diff(self, df, rule: dict, loader) -> "pd.DataFrame":
        """Detect machine run intervals from RUNHOURS cumulative counters."""
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        column_groups = rule.get("column_groups", [])
        ts_col = rule.get("timestamp_column", "timestamp_utc")
        shift_boundaries = rule.get("shift_boundaries", {})

        if df.empty or not column_groups:
            return pd.DataFrame()

        # Ensure sorted by timestamp
        if ts_col in df.columns:
            df = df.sort_values(ts_col).reset_index(drop=True)

        intervals = []
        for group in column_groups:
            machine_name = group.get("machine_name", "")
            cols = group.get("columns", [])
            if not cols or not all(c in df.columns for c in cols):
                continue

            # Coerce to numeric
            for c in cols:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

            # Build composite value: HRS*3600 + MIN*60 + SEC
            composite = df[cols[0]] * 3600
            if len(cols) > 1:
                composite = composite + df[cols[1]] * 60
            if len(cols) > 2:
                composite = composite + df[cols[2]]

            # Detect changes: where composite value differs from previous
            diffs = composite.diff().fillna(0)
            is_changing = diffs != 0

            # Find intervals where machine is running (consecutive changing rows)
            timestamps = pd.to_datetime(df[ts_col], errors="coerce")
            run_start = None

            for idx in range(len(df)):
                if is_changing.iloc[idx]:
                    if run_start is None:
                        # Start of a run interval — use PREVIOUS timestamp as start
                        run_start = idx - 1 if idx > 0 else idx
                else:
                    if run_start is not None:
                        # End of run interval
                        start_ts = timestamps.iloc[run_start]
                        end_ts = timestamps.iloc[idx - 1] if idx > 0 else timestamps.iloc[idx]
                        if pd.notna(start_ts) and pd.notna(end_ts):
                            dur = int((end_ts - start_ts).total_seconds())
                            if dur > 0:
                                intervals.append(self._make_interval_row(
                                    machine_name, start_ts, end_ts, dur, shift_boundaries
                                ))
                        run_start = None

            # Close open interval at end
            if run_start is not None:
                start_ts = timestamps.iloc[run_start]
                end_ts = timestamps.iloc[len(df) - 1]
                if pd.notna(start_ts) and pd.notna(end_ts):
                    dur = int((end_ts - start_ts).total_seconds())
                    if dur > 0:
                        intervals.append(self._make_interval_row(
                            machine_name, start_ts, end_ts, dur, shift_boundaries
                        ))

        if not intervals:
            return pd.DataFrame(columns=[
                "machine_name", "run_date", "start_time", "end_time",
                "duration_sec", "shift_no", "total_time"
            ])

        result = pd.DataFrame(intervals)
        logger.info("WINDOW_DIFF applied: %d intervals from %d machine groups", len(result), len(column_groups))
        return result

    @staticmethod
    def _make_interval_row(machine_name, start_ts, end_ts, duration_sec, shift_boundaries):
        """Create a single interval row dict."""
        # Format times
        run_date = start_ts.strftime("%Y-%m-%d")
        start_time = start_ts.strftime("%H:%M:%S")
        end_time = end_ts.strftime("%H:%M:%S")

        # Format total_time as HH:MM:SS
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60
        total_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Determine shift number based on start_time hour
        shift_no = ""
        start_hour = start_ts.hour
        if shift_boundaries:
            if 6 <= start_hour < 14:
                shift_no = "1"
            elif 14 <= start_hour < 22:
                shift_no = "2"
            else:
                shift_no = "3"

        return {
            "machine_name": machine_name,
            "run_date": run_date,
            "start_time": start_time,
            "end_time": end_time,
            "duration_sec": duration_sec,
            "shift_no": shift_no,
            "total_time": total_time,
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _discover_param_tokens(self) -> List[str]:
        tokens: set[str] = set()
        for expr in self._mapping.values():
            for match in _PARAM_RE.findall(expr):
                tokens.add(match)
            # Also detect params.xxx dot-notation
            m = _DIRECT_COLUMN_RE.match(str(expr).strip())
            if m and m.group("table").lower() == "params":
                tokens.add(m.group("column"))
        for expr in self._required_filters.values():
            tokens.update(_PARAM_RE.findall(expr))
        for expr in self._optional_filters.values():
            tokens.update(_PARAM_RE.findall(expr))
        return list(tokens)

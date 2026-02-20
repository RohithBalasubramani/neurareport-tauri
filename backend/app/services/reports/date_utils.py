from __future__ import annotations

from pathlib import Path
from typing import Callable, Tuple

from backend.app.repositories.dataframes.sqlite_loader import get_loader


def get_col_type(db_path, table: str, col: str) -> str:
    """
    Return the inferred column type (uppercased) for table.col or '' when unavailable.
    Uses the shared DataFrame loader's dtype map instead of SQLite PRAGMA calls.
    """
    if not col or not table:
        return ""
    try:
        from backend.legacy.utils.connection_utils import get_loader_for_ref
        loader = get_loader_for_ref(db_path)
        return (loader.column_type(table, col) or "").upper()
    except Exception:
        return ""


def mk_between_pred_for_date(col: str, col_type: str) -> Tuple[str, Callable[[str, str], tuple]]:
    """
    Returns (predicate_sql, adapter) used to build BETWEEN date filters.
    The adapter receives (start, end) and returns a tuple of parameters.
    When the column is missing or unusable, the predicate degenerates to '1=1'
    and the adapter returns an empty tuple – preserving the existing fail-open behaviour.
    """
    if not col or not col_type:
        return "1=1", lambda _s, _e: tuple()

    t = col_type.upper()
    if "INT" in t:
        predicate = (
            f"(CASE WHEN ABS({col}) > 32503680000 THEN {col}/1000 ELSE {col} END) "
            f"BETWEEN strftime('%s', ?) AND strftime('%s', ?)"
        )
        return predicate, lambda start, end: (start, end)

    predicate = f"datetime({col}) BETWEEN datetime(?) AND datetime(?)"
    return predicate, lambda start, end: (start, end)


__all__ = ["get_col_type", "mk_between_pred_for_date"]

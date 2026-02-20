# mypy: ignore-errors
from __future__ import annotations

import logging
from backend.app.repositories.dataframes.sqlite_loader import get_loader
from backend.legacy.utils.connection_utils import get_loader_for_ref
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable

logger = logging.getLogger("neura.mapping")

UNRESOLVED = "UNRESOLVED"
INPUT_SAMPLE = "INPUT_SAMPLE"
REPORT_SELECTED_VALUE = "LATER_SELECTED"
REPORT_SELECTED_DISPLAY = "To Be Selected in report generator"
UNRESOLVED_CHOICES = {UNRESOLVED, INPUT_SAMPLE, REPORT_SELECTED_VALUE}


def _detect_measurement_table(tables: list[str], cols: Dict[str, list[str]]) -> str | None:
    """Return the name of a wide measurement table (e.g., neuract__Flowmeters) if present."""
    for table in tables:
        lower_name = table.lower()
        if "flowmeter" not in lower_name and "flowmeters" not in lower_name and not lower_name.startswith("neuract__"):
            continue
        column_names = cols.get(table) or []
        if len(column_names) < 3:
            continue
        timestamp_like = any("timestamp" in c.lower() or c.lower().endswith("_utc") for c in column_names)
        if timestamp_like:
            return table
    return None


def get_parent_child_info(db_path) -> Dict[str, object]:
    """Inspect the database and infer suitable parent/child tables.

    Behavior:
      - If there is exactly ONE user table, treat it as BOTH parent and child (single-table report).
      - Else, prefer ('batches', 'batch_lines') if present.
      - Else, pick the first table that declares a foreign key as child and its referenced table as parent.
      - If none of the above applies, raise a clear error.
    """
    loader = get_loader_for_ref(db_path)
    tables = loader.table_names()

    if not tables:
        raise RuntimeError("No user tables found in database.")

    # --- NEW: single-table fallback ---
    if len(tables) == 1:
        t = tables[0]
        cols = [
            row.get("name", "")
            for row in loader.pragma_table_info(t)
            if isinstance(row, dict) and row.get("name")
        ]
        return {
            "child table": t,
            "parent table": t,
            "child_columns": cols,
            "parent_columns": cols,
            "common_names": sorted(set(cols)),  # same table on both sides
        }

    # collect columns for all tables
    cols: Dict[str, list[str]] = {}
    for table in tables:
        try:
            cols[table] = [
                row.get("name", "")
                for row in loader.pragma_table_info(table)
                if isinstance(row, dict) and row.get("name")
            ]
        except Exception:
            cols[table] = []

    # Additional case: wide measurement tables (e.g., neuract__Flowmeters)
    measurement_table = _detect_measurement_table(tables, cols)
    if measurement_table:
        measurement_cols = cols.get(measurement_table, [])
        if not measurement_cols:
            measurement_cols = [
                row.get("name", "")
                for row in loader.pragma_table_info(measurement_table)
                if isinstance(row, dict) and row.get("name")
            ]
        timestamp_cols = [c for c in measurement_cols if "timestamp" in c.lower() or c.lower().endswith("_utc")]
        if not timestamp_cols and measurement_cols:
            timestamp_cols = [measurement_cols[0]]
        return {
            "child table": measurement_table,
            "parent table": measurement_table,
            "child_columns": measurement_cols,
            "parent_columns": measurement_cols,
            "common_names": sorted(set(timestamp_cols) if timestamp_cols else set(measurement_cols)),
        }

    # preferred pair by name
    preferred_child, preferred_parent = "batch_lines", "batches"
    if preferred_child in tables and preferred_parent in tables:
        child, parent = preferred_child, preferred_parent
    else:
        # first-FK-wins fallback
        child = parent = None
        for table in tables:
            try:
                rows = loader.foreign_keys(table)
            except Exception:
                rows = []
            if rows:
                child = table
                parent = rows[0].get("table") or None
                if parent:
                    break

    # --- Additive fallback A: column-overlap heuristic (no FK, multi-table) ---
    if not child or not parent:
        best_overlap: list[str] = []
        best_parent_candidate = None
        best_child_candidate = None
        table_pairs = [(t1, t2) for i, t1 in enumerate(tables) for t2 in tables[i + 1:]]
        for t1, t2 in table_pairs:
            cols_t1 = set(cols.get(t1, []))
            cols_t2 = set(cols.get(t2, []))
            overlap = sorted(cols_t1 & cols_t2)
            if len(overlap) > len(best_overlap):
                best_overlap = overlap
                # More columns → master/parent; fewer → detail/child
                if len(cols.get(t1, [])) >= len(cols.get(t2, [])):
                    best_parent_candidate, best_child_candidate = t1, t2
                else:
                    best_parent_candidate, best_child_candidate = t2, t1
        if best_overlap and best_parent_candidate and best_child_candidate:
            parent = best_parent_candidate
            child = best_child_candidate

    # --- Additive fallback B: largest table as single-table report ---
    if not child or not parent:
        largest = max(tables, key=lambda t: len(cols.get(t, [])))
        largest_cols = cols.get(largest, [])
        return {
            "child table": largest,
            "parent table": largest,
            "child_columns": largest_cols,
            "parent_columns": largest_cols,
            "common_names": sorted(set(largest_cols)),
        }

    child_cols = cols.get(child, [])
    parent_cols = cols.get(parent, [])
    common = sorted(set(child_cols).intersection(parent_cols))

    return {
        "child table": child,
        "parent table": parent,
        "child_columns": child_cols,
        "parent_columns": parent_cols,
        "common_names": common,
    }


def _choice_key(choice: str) -> str:
    return str(choice or "").strip()


def is_unresolved_choice(choice: str) -> bool:
    return _choice_key(choice) in UNRESOLVED_CHOICES


def approval_errors(
    mapping: Dict[str, str], unresolved_tokens: Iterable[str] = UNRESOLVED_CHOICES
) -> list[dict[str, str]]:
    """Return issues that should block approval (unresolved or duplicate mappings)."""
    unresolved_set = {_choice_key(tok) for tok in unresolved_tokens}
    reverse = defaultdict(list)
    issues: list[dict[str, str]] = []

    for label, choice in mapping.items():
        normalized = _choice_key(choice)
        if normalized in unresolved_set:
            issues.append({"label": label, "issue": normalized})
        else:
            reverse[normalized].append(label)

    for colid, labels in reverse.items():
        if len(labels) > 1:
            issues.append({"label": "; ".join(labels), "issue": f"Duplicate mapping to {colid}"})

    return issues

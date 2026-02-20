"""Legacy PDF discovery module that now delegates to the shared DataFrame flow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .discovery_excel import discover_batches_and_counts as _discover_batches_df

__all__ = ["discover_batches_and_counts"]


def discover_batches_and_counts(
    *,
    db_path: Path,
    contract: dict,
    start_date: str,
    end_date: str,
    key_values: Mapping[str, Any] | None = None,
) -> dict:
    """
    Wrapper retained for backwards compatibility with the PDF pipeline.
    Routes all discovery requests through the DataFrame-based implementation
    used by the Excel flow so both paths share identical behaviour.
    """
    return _discover_batches_df(
        db_path=db_path,
        contract=contract,
        start_date=start_date,
        end_date=end_date,
        key_values=key_values,
    )

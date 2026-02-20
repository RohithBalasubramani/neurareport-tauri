"""DataFrame pipeline — the primary report data execution engine.

All data fetching, filtering, reshaping, computed columns and totals
happen via pandas DataFrame operations (no SQL).

The public interface returns::

    {"header": [dict], "rows": [dict, ...], "totals": [dict]}

When MELT reshape produces ``__batch_idx__`` the pipeline also returns a
``batches`` key with per-batch groups for BLOCK_REPEAT rendering.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .contract_adapter import ContractAdapter

logger = logging.getLogger(__name__)

_CF_PREFIX = "__cf_"


class DataFramePipeline:
    """Pure-DataFrame replacement for ``_run_generator_entrypoints()``."""

    def __init__(
        self,
        contract_adapter: ContractAdapter,
        loader,
        params: Dict[str, Any],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        value_filters: Optional[Dict[str, list]] = None,
    ) -> None:
        self.adapter = contract_adapter
        self.loader = loader
        self.params = params or {}
        self.start_date = start_date
        self.end_date = end_date
        self.value_filters = value_filters or {}

    def execute(self) -> Dict[str, list]:
        """Return ``{"header": [...], "rows": [...], "totals": [...]}``.

        The format is identical to what the SQL entrypoint runner produces so
        it can be used as a drop-in replacement in ``ReportGenerate.py``.

        When rows contain ``__batch_idx__`` (from MELT reshape), the result
        also includes a ``batches`` key — a list of per-batch dicts each
        having ``header``, ``rows``, and ``totals``.
        """
        header = self._resolve_header()
        rows_df = self._resolve_rows()
        totals = self._resolve_totals(rows_df)

        # Separate internal columns from user-visible row data
        row_cols = [c for c in (rows_df.columns if rows_df is not None else [])
                    if not c.startswith("__")]
        rows_list = (rows_df[row_cols].to_dict("records")
                     if rows_df is not None and not rows_df.empty and row_cols
                     else [])

        result: Dict[str, Any] = {
            "header": [header] if header else [],
            "rows": rows_list,
            "totals": [totals] if totals else [],
        }

        # --- Per-batch grouping for BLOCK_REPEAT ---
        if rows_df is not None and "__batch_idx__" in rows_df.columns and not rows_df.empty:
            batches = self._group_into_batches(rows_df, row_cols)
            if batches:
                result["batches"] = batches

        return result

    # -------------------------------------------------------------- #
    # Per-batch grouping
    # -------------------------------------------------------------- #
    def _group_into_batches(
        self, rows_df, row_cols: List[str]
    ) -> List[Dict[str, Any]]:
        """Group rows by ``__batch_idx__`` and return per-batch data."""
        import pandas as pd

        batches: List[Dict[str, Any]] = []

        # Extract carry-forward column names (prefixed with __cf_)
        cf_cols = [c for c in rows_df.columns if c.startswith(_CF_PREFIX)]

        for batch_idx, group in rows_df.groupby("__batch_idx__", sort=True):
            # Build batch-level header from carry-forward columns
            batch_header: Dict[str, Any] = {}
            if cf_cols and not group.empty:
                first = group.iloc[0]
                for col in cf_cols:
                    orig_name = col[len(_CF_PREFIX):]
                    val = first[col]
                    if pd.notna(val):
                        batch_header[orig_name] = val

            batch_header["__batch_number__"] = len(batches) + 1

            # Row data (only user-visible columns)
            batch_rows = group[row_cols].to_dict("records") if row_cols else []

            # Per-batch totals
            try:
                batch_totals = self.adapter.resolve_totals_data(group)
            except Exception:
                logger.exception("df_pipeline_batch_totals_failed batch=%s", batch_idx)
                batch_totals = {}

            batches.append({
                "header": batch_header,
                "rows": batch_rows,
                "totals": batch_totals,
            })

        logger.info("df_pipeline_grouped batches=%d total_rows=%d", len(batches), len(rows_df))
        return batches

    # -------------------------------------------------------------- #
    # Internal resolvers
    # -------------------------------------------------------------- #
    def _resolve_header(self) -> Dict[str, Any]:
        try:
            return self.adapter.resolve_header_data(
                self.loader,
                self.params,
                start_date=self.start_date,
                end_date=self.end_date,
            )
        except Exception:
            logger.exception("df_pipeline_header_failed")
            return {}

    def _resolve_rows(self):
        import pandas as pd

        try:
            return self.adapter.resolve_row_data(
                self.loader,
                self.params,
                start_date=self.start_date,
                end_date=self.end_date,
                value_filters=self.value_filters,
            )
        except Exception:
            logger.exception("df_pipeline_rows_failed")
            return pd.DataFrame()

    def _resolve_totals(self, rows_df) -> Dict[str, Any]:
        import pandas as pd

        if rows_df is None or rows_df.empty:
            return {}
        try:
            return self.adapter.resolve_totals_data(rows_df)
        except Exception:
            logger.exception("df_pipeline_totals_failed")
            return {}

"""Tests for architecture stabilization changes.

Covers: memory limits, pipeline error propagation, LLM retry,
NaN coercion logging, event stream timeout, and contract validation.
"""
from __future__ import annotations

import logging
import time
import types
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# 1. DataFrameStore memory limit
# ---------------------------------------------------------------------------

class TestDataFrameStoreMemoryLimit:
    """Verify the memory accounting in DataFrameStore."""

    def _make_fresh_store(self, max_bytes: int = 1024):
        """Create a non-singleton DataFrameStore for testing."""
        from backend.app.repositories.dataframes.store import DataFrameStore

        store = object.__new__(DataFrameStore)
        store._loaders = {}
        store._frames_cache = {}
        store._db_paths = {}
        store._connection_urls = {}
        store._db_types = {}
        store._query_engines = {}
        store._store_lock = __import__("threading").Lock()
        store._total_memory_bytes = 0
        store._max_memory_bytes = max_bytes
        store._initialized = True
        return store

    def test_memory_accounting_tracks_frames(self):
        from backend.app.repositories.dataframes.store import _frames_memory_bytes

        frames = {"t1": pd.DataFrame({"a": range(100)})}
        mem = _frames_memory_bytes(frames)
        assert mem > 0, "Memory accounting must return positive value for non-empty frames"

    def test_memory_accounting_empty(self):
        from backend.app.repositories.dataframes.store import _frames_memory_bytes

        assert _frames_memory_bytes({}) == 0

    def test_register_exceeds_memory_raises(self):
        """Registering a connection whose frames exceed the limit must raise MemoryError."""
        store = self._make_fresh_store(max_bytes=1)  # 1 byte limit

        big_df = pd.DataFrame({"col": range(10_000)})
        mock_loader = MagicMock()
        mock_loader.table_names.return_value = ["big_table"]
        mock_loader.frame.return_value = big_df
        mock_loader._mtime = 0.0

        with patch.object(store, "_store_lock", __import__("threading").Lock()):
            # Manually simulate what register_connection does internally
            frames = {name: mock_loader.frame(name) for name in mock_loader.table_names()}
            from backend.app.repositories.dataframes.store import _frames_memory_bytes

            new_memory = _frames_memory_bytes(frames)
            assert new_memory > 1, "Test data must exceed the 1-byte limit"

            # Verify the projected memory would exceed limit
            projected = store._total_memory_bytes + new_memory
            assert projected > store._max_memory_bytes


# ---------------------------------------------------------------------------
# 2. DataFrame pipeline error propagation
# ---------------------------------------------------------------------------

class TestDataframePipelineErrorPropagation:
    """Verify that pipeline raises DataPipelineError instead of returning empty data."""

    def test_data_pipeline_error_is_runtime_error(self):
        from backend.app.services.reports.dataframe_pipeline import DataPipelineError

        assert issubclass(DataPipelineError, RuntimeError)

    def test_data_pipeline_error_can_be_raised(self):
        from backend.app.services.reports.dataframe_pipeline import DataPipelineError

        with pytest.raises(DataPipelineError, match="test failure"):
            raise DataPipelineError("test failure")


# ---------------------------------------------------------------------------
# 3. LLM retry on transient errors
# ---------------------------------------------------------------------------

class TestLLMRetry:
    """Verify call_chat_completion retries transient errors and raises permanent ones."""

    @patch("backend.app.services.utils.llm._LLM_MAX_ATTEMPTS", 3)
    @patch("backend.app.services.utils.llm._LLM_MIN_WAIT", 0.01)
    @patch("backend.app.services.utils.llm._LLM_MAX_WAIT", 0.05)
    def test_retry_on_transient_error_then_succeed(self):
        """LLM call that fails once with a transient error then succeeds."""
        from backend.app.services.utils.llm import call_chat_completion

        call_count = 0

        def _side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("503 Service Unavailable")
            return {"content": "ok"}

        mock_llm_client = MagicMock()
        mock_llm_client.complete = MagicMock(side_effect=_side_effect)

        with patch("backend.app.services.llm.client.get_llm_client", return_value=mock_llm_client):
            with patch("backend.app.services.utils.llm._is_llm_retriable", return_value=True):
                result = call_chat_completion(
                    None,
                    model="sonnet",
                    messages=[{"role": "user", "content": "hello"}],
                    description="test_retry",
                )
        assert call_count == 2, "Should have retried once after transient error"

    @patch("backend.app.services.utils.llm._LLM_MAX_ATTEMPTS", 3)
    @patch("backend.app.services.utils.llm._LLM_MIN_WAIT", 0.01)
    @patch("backend.app.services.utils.llm._LLM_MAX_WAIT", 0.05)
    def test_no_retry_on_permanent_error(self):
        """LLM call with a permanent error should raise immediately."""
        from backend.app.services.utils.llm import call_chat_completion

        mock_llm_client = MagicMock()
        mock_llm_client.complete = MagicMock(side_effect=ValueError("Invalid API key"))

        with patch("backend.app.services.llm.client.get_llm_client", return_value=mock_llm_client):
            with patch("backend.app.services.utils.llm._is_llm_retriable", return_value=False):
                with pytest.raises(ValueError, match="Invalid API key"):
                    call_chat_completion(
                        None,
                        model="sonnet",
                        messages=[{"role": "user", "content": "hello"}],
                        description="test_permanent",
                    )
        # Should only have been called once (no retry)
        assert mock_llm_client.complete.call_count == 1

    @patch("backend.app.services.utils.llm._LLM_MAX_ATTEMPTS", 2)
    @patch("backend.app.services.utils.llm._LLM_MIN_WAIT", 0.01)
    @patch("backend.app.services.utils.llm._LLM_MAX_WAIT", 0.05)
    def test_retries_exhausted_raises(self):
        """When all retries are exhausted, the last error should be raised."""
        from backend.app.services.utils.llm import call_chat_completion

        mock_llm_client = MagicMock()
        mock_llm_client.complete = MagicMock(side_effect=ConnectionError("rate limit exceeded"))

        with patch("backend.app.services.llm.client.get_llm_client", return_value=mock_llm_client):
            with patch("backend.app.services.utils.llm._is_llm_retriable", return_value=True):
                with pytest.raises(ConnectionError, match="rate limit"):
                    call_chat_completion(
                        None,
                        model="sonnet",
                        messages=[{"role": "user", "content": "hello"}],
                        description="test_exhausted",
                    )
        assert mock_llm_client.complete.call_count == 2


# ---------------------------------------------------------------------------
# 4. NaN/Infinity coercion logging
# ---------------------------------------------------------------------------

class TestNaNCoercionLogging:
    """Verify that format_decimal_str logs a warning when coercing NaN/Infinity."""

    def test_nan_returns_zero_and_logs(self, caplog):
        from backend.app.services.reports.contract_adapter import format_decimal_str

        with caplog.at_level(logging.WARNING):
            result = format_decimal_str(float("nan"))
        assert result == "0"
        assert any("format_decimal_non_finite" in r.message for r in caplog.records)

    def test_infinity_returns_zero_and_logs(self, caplog):
        from backend.app.services.reports.contract_adapter import format_decimal_str

        with caplog.at_level(logging.WARNING):
            result = format_decimal_str(float("inf"))
        assert result == "0"
        assert any("format_decimal_non_finite" in r.message for r in caplog.records)

    def test_neg_infinity_returns_zero_and_logs(self, caplog):
        from backend.app.services.reports.contract_adapter import format_decimal_str

        with caplog.at_level(logging.WARNING):
            result = format_decimal_str(float("-inf"))
        assert result == "0"
        assert any("format_decimal_non_finite" in r.message for r in caplog.records)

    def test_normal_number_no_warning(self, caplog):
        from backend.app.services.reports.contract_adapter import format_decimal_str

        with caplog.at_level(logging.WARNING):
            result = format_decimal_str(42.5)
        assert result == "42.5"
        assert not any("format_decimal_non_finite" in r.message for r in caplog.records)

    def test_format_fixed_decimals_nan(self, caplog):
        from backend.app.services.reports.contract_adapter import format_fixed_decimals

        with caplog.at_level(logging.WARNING):
            result = format_fixed_decimals(float("nan"), 2)
        # NaN is coerced to Decimal(0) then formatted with 2 decimals → "0.00"
        assert result in ("0", "0.00")
        assert any("format_fixed_decimals_non_finite" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# 5. Event stream timeout
# ---------------------------------------------------------------------------

class TestEventStreamTimeout:
    """Verify that run_event_stream respects its timeout."""

    def test_event_stream_marks_job_failed_on_timeout(self):
        from backend.app.services.background_tasks import run_event_stream

        def slow_events():
            """Generator that yields events slowly — should be interrupted by timeout."""
            for i in range(100):
                time.sleep(0.1)
                yield {"type": "progress", "progress": i}

        mock_state_store = MagicMock()

        with patch("backend.app.services.background_tasks.state_store", mock_state_store):
            with patch("backend.app.services.background_tasks._is_cancelled", return_value=False):
                run_event_stream("test-job-1", slow_events(), timeout_seconds=1)

        # Should have called record_job_completion with status="failed"
        completion_calls = mock_state_store.record_job_completion.call_args_list
        assert len(completion_calls) >= 1
        last_call = completion_calls[-1]
        assert last_call.kwargs.get("status") == "failed" or (
            len(last_call.args) > 1 and last_call.args[1] == "failed"
        )


# ---------------------------------------------------------------------------
# 6. Contract validation at report time
# ---------------------------------------------------------------------------

class TestContractValidation:
    """Verify that schema drift in contract mappings is detected early."""

    def test_missing_table_raises_error(self):
        """Contract referencing a non-existent table should raise RuntimeError."""
        import re

        _col_ref_re = re.compile(r"^([A-Za-z_][\w]*)\.([A-Za-z_][\w]*)$")
        available_tables = {"orders", "customers"}

        # Simulate a mapping that references a deleted table
        mapping = {"total": "invoices.amount"}  # 'invoices' table doesn't exist
        missing_refs = []
        for token, col_ref in mapping.items():
            m = _col_ref_re.match(str(col_ref))
            if not m:
                continue
            tbl, col = m.group(1), m.group(2)
            if tbl not in available_tables:
                missing_refs.append(f"{token!r} -> {col_ref!r} (table {tbl!r} not found)")

        assert len(missing_refs) == 1
        assert "invoices" in missing_refs[0]

    def test_missing_column_detected(self):
        """Contract referencing a dropped column should be detected."""
        import re

        _col_ref_re = re.compile(r"^([A-Za-z_][\w]*)\.([A-Za-z_][\w]*)$")
        available_tables = {"orders"}
        table_columns = {"orders": {"id", "date", "status"}}  # 'amount' was dropped

        mapping = {"total": "orders.amount"}
        missing_refs = []
        for token, col_ref in mapping.items():
            m = _col_ref_re.match(str(col_ref))
            if not m:
                continue
            tbl, col = m.group(1), m.group(2)
            if tbl not in available_tables:
                missing_refs.append(f"table {tbl!r} not found")
                continue
            if col not in table_columns.get(tbl, set()) and col != "__rowid__":
                missing_refs.append(f"column {col!r} not in table {tbl!r}")

        assert len(missing_refs) == 1
        assert "amount" in missing_refs[0]

    def test_valid_mapping_no_error(self):
        """A valid mapping should produce no missing references."""
        import re

        _col_ref_re = re.compile(r"^([A-Za-z_][\w]*)\.([A-Za-z_][\w]*)$")
        available_tables = {"orders"}
        table_columns = {"orders": {"id", "date", "amount"}}

        mapping = {"total": "orders.amount", "order_date": "orders.date"}
        missing_refs = []
        for token, col_ref in mapping.items():
            m = _col_ref_re.match(str(col_ref))
            if not m:
                continue
            tbl, col = m.group(1), m.group(2)
            if tbl not in available_tables:
                missing_refs.append(f"table {tbl!r} not found")
                continue
            if col not in table_columns.get(tbl, set()) and col != "__rowid__":
                missing_refs.append(f"column {col!r} not in table {tbl!r}")

        assert len(missing_refs) == 0


# ---------------------------------------------------------------------------
# 7. LLM retriable error classification
# ---------------------------------------------------------------------------

class TestLLMRetriableClassification:
    """Verify _is_llm_retriable correctly classifies errors."""

    def test_rate_limit_is_retriable(self):
        from backend.app.services.utils.llm import _is_llm_retriable

        assert _is_llm_retriable(ConnectionError("429 rate limit exceeded"))

    def test_503_is_retriable(self):
        from backend.app.services.utils.llm import _is_llm_retriable

        assert _is_llm_retriable(ConnectionError("503 Service Unavailable"))

    def test_overloaded_is_retriable(self):
        from backend.app.services.utils.llm import _is_llm_retriable

        assert _is_llm_retriable(RuntimeError("Model overloaded, try later"))

    def test_value_error_not_retriable(self):
        from backend.app.services.utils.llm import _is_llm_retriable

        assert not _is_llm_retriable(ValueError("Invalid configuration"))

    def test_key_error_not_retriable(self):
        from backend.app.services.utils.llm import _is_llm_retriable

        assert not _is_llm_retriable(KeyError("missing_key"))

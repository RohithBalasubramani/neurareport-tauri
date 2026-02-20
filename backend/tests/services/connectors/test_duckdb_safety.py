"""
Tests for DuckDB connector safety hardening.

Covers:
- _validate_identifier rejects SQL injection payloads
- _validate_identifier accepts valid identifiers and double-quotes them
- Path traversal blocked in connect()
- ConnectionError does not leak internal details
"""
from __future__ import annotations

import inspect

import pytest


# =============================================================================
# Identifier validation
# =============================================================================


class TestValidateIdentifier:
    """Tests for _validate_identifier in DuckDB connector."""

    def _fn(self):
        from backend.app.services.connectors.databases.duckdb import _validate_identifier
        return _validate_identifier

    def test_valid_simple_name(self):
        result = self._fn()("users", "table name")
        assert result == '"users"'

    def test_valid_underscored_name(self):
        result = self._fn()("my_table_2", "table name")
        assert result == '"my_table_2"'

    def test_rejects_sql_injection(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("users; DROP TABLE users --", "table name")

    def test_rejects_semicolons(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("a;b", "table name")

    def test_rejects_quotes(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()('a"b', "table name")

    def test_rejects_parens(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("a()", "table name")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("a b", "table name")

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("", "table name")

    def test_rejects_leading_digit(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("1abc", "table name")

    def test_rejects_hyphen(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("my-table", "table name")


# =============================================================================
# Parameterized queries (source inspection)
# =============================================================================


class TestParameterizedQueries:
    """Verify DuckDB methods use parameterised queries, not f-string interpolation."""

    def _source(self, method_name):
        from backend.app.services.connectors.databases.duckdb import DuckDBConnector
        return inspect.getsource(getattr(DuckDBConnector, method_name))

    def test_get_columns_uses_params(self):
        src = self._source("_get_columns")
        assert "?" in src, "_get_columns should use ? placeholders"
        # Should NOT do f-string table name interpolation
        assert "f\"" not in src or "table_name" not in src.split("f\"")[1] if "f\"" in src else True

    def test_load_parquet_uses_validate_identifier(self):
        src = self._source("load_parquet")
        assert "_validate_identifier" in src

    def test_load_parquet_uses_params(self):
        src = self._source("load_parquet")
        assert "read_parquet(?)" in src or "read_parquet( ?)" in src

    def test_load_csv_uses_validate_identifier(self):
        src = self._source("load_csv")
        assert "_validate_identifier" in src

    def test_load_csv_validates_delimiter(self):
        src = self._source("load_csv")
        assert 'len(delimiter)' in src

    def test_load_csv_uses_params(self):
        src = self._source("load_csv")
        assert "read_csv(?" in src


# =============================================================================
# Path traversal prevention
# =============================================================================


class TestPathTraversal:
    """Verify DuckDB connect() blocks path traversal."""

    def test_connect_source_rejects_dotdot(self):
        from backend.app.services.connectors.databases.duckdb import DuckDBConnector
        src = inspect.getsource(DuckDBConnector.connect)
        assert ".." in src, "connect() should check for '..' in path"


# =============================================================================
# Error sanitisation
# =============================================================================


class TestErrorSanitisation:
    """Verify ConnectionError does not leak internal details."""

    def test_connect_error_no_fstring_exception(self):
        from backend.app.services.connectors.databases.duckdb import DuckDBConnector
        src = inspect.getsource(DuckDBConnector.connect)
        # Should NOT contain f"Failed to connect...{e}" pattern
        assert "Failed to connect to DuckDB: {e}" not in src
        assert "Failed to connect to DuckDB\") from e" in src or "Failed to connect to DuckDB\")" in src

    def test_test_connection_error_generic(self):
        from backend.app.services.connectors.databases.duckdb import DuckDBConnector
        src = inspect.getsource(DuckDBConnector.test_connection)
        assert "Connection test failed" in src

"""
Tests for Snowflake connector safety hardening.

Covers:
- _quote_identifier rejects SQL injection payloads
- DESCRIBE TABLE uses quoted identifiers (not f-string interpolation)
- ConnectionError does not leak credentials
"""
from __future__ import annotations

import inspect

import pytest


# =============================================================================
# Identifier quoting
# =============================================================================


class TestQuoteIdentifier:
    """Tests for _quote_identifier in Snowflake connector."""

    def _fn(self):
        from backend.app.services.connectors.databases.snowflake import _quote_identifier
        return _quote_identifier

    def test_valid_identifier(self):
        assert self._fn()("orders", "table") == '"orders"'

    def test_valid_with_underscore(self):
        assert self._fn()("user_accounts", "table") == '"user_accounts"'

    def test_rejects_injection(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("orders; DROP TABLE orders--", "table")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("", "schema")

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()("my table", "table")

    def test_rejects_quotes(self):
        with pytest.raises(ValueError, match="Invalid SQL"):
            self._fn()('tab"le', "table")


# =============================================================================
# Source inspection — DESCRIBE TABLE
# =============================================================================


class TestDescribeTableSafety:
    """Verify DESCRIBE TABLE uses quoted identifiers."""

    def _get_columns_source(self):
        from backend.app.services.connectors.databases.snowflake import SnowflakeConnector
        return inspect.getsource(SnowflakeConnector._get_columns)

    def test_uses_quote_identifier(self):
        src = self._get_columns_source()
        assert "_quote_identifier" in src


# =============================================================================
# Error sanitisation
# =============================================================================


class TestCredentialLeak:
    """Verify ConnectionError does not leak passwords."""

    def test_connect_no_exception_in_message(self):
        from backend.app.services.connectors.databases.snowflake import SnowflakeConnector
        src = inspect.getsource(SnowflakeConnector.connect)
        # Must NOT leak {e} in ConnectionError
        assert "Failed to connect to Snowflake: {e}" not in src
        assert "Failed to connect to Snowflake\") from e" in src or "Failed to connect to Snowflake\")" in src

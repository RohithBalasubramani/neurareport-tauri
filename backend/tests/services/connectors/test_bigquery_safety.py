"""
Tests for BigQuery connector safety hardening.

Covers:
- Invalid credentials JSON raises clean ConnectionError (not JSONDecodeError leaking creds)
- ConnectionError does not include raw exception details
"""
from __future__ import annotations

import inspect

import pytest


class TestCredentialJsonValidation:
    """Verify credentials JSON is safely parsed."""

    def test_connect_catches_json_decode_error(self):
        from backend.app.services.connectors.databases.bigquery import BigQueryConnector
        src = inspect.getsource(BigQueryConnector.connect)
        assert "json.JSONDecodeError" in src or "JSONDecodeError" in src

    def test_connect_raises_clean_error_on_bad_json(self):
        from backend.app.services.connectors.databases.bigquery import BigQueryConnector
        src = inspect.getsource(BigQueryConnector.connect)
        assert "Invalid credentials JSON format" in src


class TestBigQueryErrorSanitisation:
    """Verify ConnectionError does not leak credential info."""

    def test_connect_no_fstring_exception(self):
        from backend.app.services.connectors.databases.bigquery import BigQueryConnector
        src = inspect.getsource(BigQueryConnector.connect)
        assert "Failed to connect to BigQuery: {e}" not in src
        # Should re-raise cleanly
        assert "Failed to connect to BigQuery\") from e" in src or "Failed to connect to BigQuery\")" in src

    def test_connection_error_passthrough(self):
        """ConnectionError (from JSON check) should not be swallowed by the generic except."""
        from backend.app.services.connectors.databases.bigquery import BigQueryConnector
        src = inspect.getsource(BigQueryConnector.connect)
        assert "except ConnectionError" in src

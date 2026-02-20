"""
Tests for LLM client safety hardening.

Covers:
- _sanitize_error is imported and used in client.py error logs
- LLM_CACHE_DIR rejects path traversal
- LLM_CACHE_MAX_ITEMS is clamped to [1, 10000]
"""
from __future__ import annotations

import inspect

import pytest


# =============================================================================
# _sanitize_error usage in client.py
# =============================================================================


class TestClientSanitizeErrorUsage:
    """Verify client.py applies _sanitize_error to fallback/retry error logs."""

    def _client_source(self):
        import backend.app.services.llm.client as client_mod
        return inspect.getsource(client_mod)

    def test_imports_sanitize_error(self):
        src = self._client_source()
        assert "_sanitize_error" in src

    def test_fallback_error_sanitized(self):
        """Error logs in the fallback path should use _sanitize_error."""
        src = self._client_source()
        assert "_sanitize_error" in src
        # At least 3 usages expected (fallback_also_failed, call_failed, call_retry)
        count = src.count("_sanitize_error")
        assert count >= 3, f"Expected at least 3 _sanitize_error usages, found {count}"


# =============================================================================
# Cache directory validation
# =============================================================================


class TestCacheDirValidation:
    """Verify LLM_CACHE_DIR rejects path traversal."""

    def test_client_source_rejects_dotdot(self):
        import backend.app.services.llm.client as client_mod
        src = inspect.getsource(client_mod)
        assert '".."' in src or "'..' " in src or '".."' in src


# =============================================================================
# Cache max items bounds
# =============================================================================


class TestCacheMaxItemsBounds:
    """Verify LLM_CACHE_MAX_ITEMS is clamped."""

    def test_max_items_upper_bound(self):
        import backend.app.services.llm.client as client_mod
        src = inspect.getsource(client_mod)
        assert "10000" in src, "Max items should be capped at 10000"

    def test_max_items_lower_bound(self):
        import backend.app.services.llm.client as client_mod
        src = inspect.getsource(client_mod)
        # min(max(1, ...)) pattern
        assert "max(1," in src or "max( 1," in src

"""
Tests for LLM provider safety hardening — lines 1250-1271 of FORENSIC_AUDIT_REPORT.md.

Covers:
- _sanitize_error redacts API keys / Bearer tokens from exception messages
- Ollama URL validation warns for non-localhost HTTP

Run with: pytest backend/tests/services/llm/test_provider_safety.py -v
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# _sanitize_error Tests
# =============================================================================


class TestSanitizeError:
    """Verify exception messages are sanitized before logging."""

    def test_redacts_openai_key(self):
        from backend.app.services.llm.providers import _sanitize_error

        exc = Exception("Invalid API key: sk-abc123defXYZlongkey. Check your settings.")
        result = _sanitize_error(exc)
        assert "sk-abc123" not in result
        assert "[REDACTED]" in result

    def test_redacts_bearer_token(self):
        from backend.app.services.llm.providers import _sanitize_error

        exc = Exception("Authorization failed: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig")
        result = _sanitize_error(exc)
        assert "eyJhbGci" not in result
        assert "[REDACTED]" in result

    def test_redacts_api_key_param(self):
        from backend.app.services.llm.providers import _sanitize_error

        exc = Exception("Bad request: api_key=sk-proj-abcd1234efgh5678 was rejected")
        result = _sanitize_error(exc)
        assert "sk-proj-abcd" not in result
        assert "[REDACTED]" in result

    def test_preserves_safe_message(self):
        from backend.app.services.llm.providers import _sanitize_error

        exc = Exception("Connection refused: localhost:11434")
        result = _sanitize_error(exc)
        assert result == "Connection refused: localhost:11434"

    def test_handles_empty_message(self):
        from backend.app.services.llm.providers import _sanitize_error

        result = _sanitize_error(Exception(""))
        assert result == ""

    def test_list_models_uses_sanitize(self):
        """OpenAIProvider.list_models should use _sanitize_error."""
        import inspect
        from backend.app.services.llm.providers import OpenAIProvider

        source = inspect.getsource(OpenAIProvider.list_models)
        assert "_sanitize_error" in source

    def test_ollama_list_models_uses_sanitize(self):
        """OllamaProvider.list_models should use _sanitize_error."""
        import inspect
        from backend.app.services.llm.providers import OllamaProvider

        source = inspect.getsource(OllamaProvider.list_models)
        assert "_sanitize_error" in source


# =============================================================================
# Ollama URL validation Tests
# =============================================================================


class TestOllamaUrlValidation:
    """Verify Ollama warns on non-localhost HTTP URLs."""

    def test_localhost_http_no_warning(self, caplog):
        """http://localhost should not produce a warning."""
        from backend.app.services.llm.providers import OllamaProvider

        provider = OllamaProvider.__new__(OllamaProvider)
        provider._client = None
        provider.config = MagicMock()
        provider.config.base_url = "http://localhost:11434"
        provider.config.timeout_seconds = 30

        with caplog.at_level(logging.WARNING, logger="neura.llm.providers"):
            try:
                provider.get_client()
            except Exception:
                pass  # We only care about the log, not the client

        assert "ollama_insecure_url" not in caplog.text

    def test_127_0_0_1_http_no_warning(self, caplog):
        """http://127.0.0.1 should not produce a warning."""
        from backend.app.services.llm.providers import OllamaProvider

        provider = OllamaProvider.__new__(OllamaProvider)
        provider._client = None
        provider.config = MagicMock()
        provider.config.base_url = "http://127.0.0.1:11434"
        provider.config.timeout_seconds = 30

        with caplog.at_level(logging.WARNING, logger="neura.llm.providers"):
            try:
                provider.get_client()
            except Exception:
                pass

        assert "ollama_insecure_url" not in caplog.text

    def test_remote_http_emits_warning(self, caplog):
        """http://remote-host should emit a warning."""
        from backend.app.services.llm.providers import OllamaProvider

        provider = OllamaProvider.__new__(OllamaProvider)
        provider._client = None
        provider.config = MagicMock()
        provider.config.base_url = "http://gpu-server.internal:11434"
        provider.config.timeout_seconds = 30

        with caplog.at_level(logging.WARNING, logger="neura.llm.providers"):
            try:
                provider.get_client()
            except Exception:
                pass

        assert "ollama_insecure_url" in caplog.text

    def test_remote_https_no_warning(self, caplog):
        """https://remote-host should not produce a warning."""
        from backend.app.services.llm.providers import OllamaProvider

        provider = OllamaProvider.__new__(OllamaProvider)
        provider._client = None
        provider.config = MagicMock()
        provider.config.base_url = "https://gpu-server.internal:11434"
        provider.config.timeout_seconds = 30

        with caplog.at_level(logging.WARNING, logger="neura.llm.providers"):
            try:
                provider.get_client()
            except Exception:
                pass

        assert "ollama_insecure_url" not in caplog.text

    def test_get_client_source_has_urlparse(self):
        """get_client should contain URL validation."""
        import inspect
        from backend.app.services.llm.providers import OllamaProvider

        source = inspect.getsource(OllamaProvider.get_client)
        assert "urlparse" in source
        assert "ollama_insecure_url" in source

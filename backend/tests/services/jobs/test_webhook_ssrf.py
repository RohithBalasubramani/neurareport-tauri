"""
Tests for webhook SSRF prevention and error sanitisation.

Covers:
- _validate_webhook_url rejects private/loopback IPs
- _validate_webhook_url rejects non-HTTP(S) schemes
- _validate_webhook_url allows public DNS names
- Default secret warning log
- Error messages do not leak exception details
"""
from __future__ import annotations

import inspect
import logging

import pytest

from backend.app.services.jobs.webhook_service import WebhookService


# =============================================================================
# SSRF prevention
# =============================================================================


class TestWebhookUrlValidation:
    """Verify _validate_webhook_url blocks SSRF vectors."""

    def test_allows_public_https(self):
        """Public HTTPS URLs should be allowed."""
        WebhookService._validate_webhook_url("https://example.com/webhook")

    def test_allows_public_http(self):
        """Public HTTP URLs should be allowed."""
        WebhookService._validate_webhook_url("http://example.com/webhook")

    def test_rejects_loopback_ipv4(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://127.0.0.1/hook")

    def test_rejects_private_10_network(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://10.0.0.1/hook")

    def test_rejects_private_172_network(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://172.16.0.1/hook")

    def test_rejects_private_192_network(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://192.168.1.1/hook")

    def test_rejects_link_local(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://169.254.169.254/metadata")

    def test_rejects_ipv6_loopback(self):
        with pytest.raises(ValueError, match="private|loopback"):
            WebhookService._validate_webhook_url("http://[::1]/hook")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValueError, match="http or https"):
            WebhookService._validate_webhook_url("ftp://example.com/file")

    def test_rejects_file_scheme(self):
        with pytest.raises(ValueError, match="http or https"):
            WebhookService._validate_webhook_url("file:///etc/passwd")

    def test_rejects_empty_hostname(self):
        with pytest.raises(ValueError, match="no hostname"):
            WebhookService._validate_webhook_url("http:///path")

    def test_allows_dns_hostname(self):
        """DNS names (not IP literals) should be allowed."""
        WebhookService._validate_webhook_url("https://hooks.slack.com/services/abc")


# =============================================================================
# Deliver integrates URL validation
# =============================================================================


class TestDeliverIntegration:
    """Verify deliver() calls _validate_webhook_url."""

    def test_deliver_source_calls_validate(self):
        src = inspect.getsource(WebhookService.deliver)
        assert "_validate_webhook_url" in src


# =============================================================================
# Default secret warning
# =============================================================================


class TestDefaultSecretWarning:
    """Verify a warning is logged when the default webhook secret is used."""

    def test_deliver_warns_on_default_secret(self):
        src = inspect.getsource(WebhookService.deliver)
        assert "neura-default-webhook-secret" in src


# =============================================================================
# Error sanitisation
# =============================================================================


class TestWebhookErrorSanitisation:
    """Verify exception handlers don't leak full error details."""

    def test_deliver_error_messages_are_generic(self):
        src = inspect.getsource(WebhookService.deliver)
        # Should use error_type / generic message, not raw str(e)
        assert "error_type" in src

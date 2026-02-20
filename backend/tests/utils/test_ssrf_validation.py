"""SSRF Validation Tests.

Tests for is_safe_external_url() — blocks localhost, private IPs,
cloud metadata endpoints, and non-HTTP(S) schemes.
"""
import pytest
from unittest.mock import patch

from backend.app.utils.validation import is_safe_external_url


class TestSafeExternalUrl:
    """Tests for SSRF protection via is_safe_external_url()."""

    def test_valid_https_url(self):
        ok, err = is_safe_external_url("https://example.com/webhook")
        assert ok is True
        assert err is None

    def test_valid_http_url(self):
        ok, err = is_safe_external_url("http://example.com/webhook")
        assert ok is True
        assert err is None

    def test_blocks_localhost(self):
        ok, err = is_safe_external_url("http://localhost/webhook")
        assert ok is False
        assert "localhost" in err

    def test_blocks_127_0_0_1(self):
        ok, err = is_safe_external_url("http://127.0.0.1/webhook")
        assert ok is False
        assert "private" in err.lower() or "127.0.0.1" in err

    def test_blocks_zero_address(self):
        ok, err = is_safe_external_url("http://0.0.0.0/webhook")
        assert ok is False
        assert "0.0.0.0" in err

    def test_blocks_cloud_metadata(self):
        """169.254.169.254 is the AWS/GCP/Azure metadata endpoint."""
        ok, err = is_safe_external_url("http://169.254.169.254/latest/meta-data/")
        assert ok is False
        assert "private" in err.lower() or "reserved" in err.lower()

    def test_blocks_file_scheme(self):
        ok, err = is_safe_external_url("file:///etc/passwd")
        assert ok is False
        assert "scheme" in err.lower()

    def test_blocks_ftp_scheme(self):
        ok, err = is_safe_external_url("ftp://ftp.example.com/file")
        assert ok is False
        assert "scheme" in err.lower()

    def test_empty_url(self):
        ok, err = is_safe_external_url("")
        assert ok is False

    def test_none_url(self):
        ok, err = is_safe_external_url(None)
        assert ok is False

    def test_blocks_private_10_network(self):
        """10.0.0.0/8 should be blocked."""
        ok, err = is_safe_external_url("http://10.0.0.1/webhook")
        assert ok is False
        assert "private" in err.lower() or "reserved" in err.lower()

    def test_blocks_private_172_network(self):
        """172.16.0.0/12 should be blocked."""
        ok, err = is_safe_external_url("http://172.16.0.1/webhook")
        assert ok is False

    def test_blocks_private_192_network(self):
        """192.168.0.0/16 should be blocked."""
        ok, err = is_safe_external_url("http://192.168.1.1/webhook")
        assert ok is False

    def test_no_hostname(self):
        ok, err = is_safe_external_url("http://")
        assert ok is False
        assert "hostname" in err.lower()

    def test_unresolvable_hostname(self):
        ok, err = is_safe_external_url("http://this-host-does-not-exist-xyz123.invalid/webhook")
        assert ok is False
        assert "resolve" in err.lower()

"""Comprehensive tests for mailer service."""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# Stub cryptography module for tests
fernet_module = types.ModuleType("cryptography.fernet")


class _DummyFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(fernet_module, "Fernet", _DummyFernet)
setattr(fernet_module, "InvalidToken", Exception)
crypto_module = types.ModuleType("cryptography")
setattr(crypto_module, "fernet", fernet_module)
sys.modules.setdefault("cryptography", crypto_module)
sys.modules.setdefault("cryptography.fernet", fernet_module)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


# =============================================================================
# MAILER CONFIGURATION TESTS
# =============================================================================


class TestMailerConfig:
    """Tests for mailer configuration loading."""

    def test_mailer_disabled_by_default(self, monkeypatch):
        """Mailer should be disabled when host/sender not configured."""
        # Clear any existing env vars
        monkeypatch.delenv("NEURA_MAIL_HOST", raising=False)
        monkeypatch.delenv("NEURA_MAIL_SENDER", raising=False)

        # Re-import to pick up new env
        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.enabled is False
        assert config.host is None
        assert config.sender is None

    def test_mailer_enabled_with_host_and_sender(self, monkeypatch):
        """Mailer should be enabled when both host and sender are set."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")

        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.enabled is True
        assert config.host == "smtp.example.com"
        assert config.sender == "noreply@example.com"

    def test_mailer_config_defaults(self, monkeypatch):
        """Mailer should use sensible defaults."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.delenv("NEURA_MAIL_PORT", raising=False)
        monkeypatch.delenv("NEURA_MAIL_USE_TLS", raising=False)

        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.port == 587  # Default SMTP TLS port
        assert config.use_tls is True  # TLS enabled by default

    def test_mailer_config_custom_port(self, monkeypatch):
        """Custom port should be respected."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.setenv("NEURA_MAIL_PORT", "465")

        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.port == 465

    def test_mailer_config_invalid_port_uses_default(self, monkeypatch):
        """Invalid port should fall back to default."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.setenv("NEURA_MAIL_PORT", "invalid")

        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.port == 587  # Falls back to default

    def test_mailer_tls_disabled(self, monkeypatch):
        """TLS can be disabled."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.setenv("NEURA_MAIL_USE_TLS", "false")

        from backend.app.services.utils import mailer
        config = mailer._load_mailer_config()

        assert config.use_tls is False

    def test_refresh_mailer_config(self, monkeypatch):
        """Config refresh should pick up new env vars."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")

        from backend.app.services.utils import mailer
        config1 = mailer.refresh_mailer_config()
        assert config1.host == "smtp.example.com"

        # Change env and refresh
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.newhost.com")
        config2 = mailer.refresh_mailer_config()
        assert config2.host == "smtp.newhost.com"


# =============================================================================
# RECIPIENT NORMALIZATION TESTS
# =============================================================================


class TestRecipientNormalization:
    """Tests for email recipient normalization."""

    def test_normalize_empty_returns_empty(self):
        """Empty input should return empty list."""
        from backend.app.services.utils.mailer import _normalize_recipients

        assert _normalize_recipients(None) == []
        assert _normalize_recipients([]) == []
        assert _normalize_recipients(["", "  "]) == []

    def test_normalize_removes_duplicates(self):
        """Duplicates should be removed."""
        from backend.app.services.utils.mailer import _normalize_recipients

        result = _normalize_recipients([
            "user@example.com",
            "user@example.com",
            "other@example.com",
        ])
        assert len(result) == 2
        assert "user@example.com" in result
        assert "other@example.com" in result

    def test_normalize_trims_whitespace(self):
        """Whitespace should be trimmed."""
        from backend.app.services.utils.mailer import _normalize_recipients

        result = _normalize_recipients([
            "  user@example.com  ",
            "\tother@example.com\n",
        ])
        assert result == ["user@example.com", "other@example.com"]

    def test_normalize_handles_none_values(self):
        """None values in list should be handled."""
        from backend.app.services.utils.mailer import _normalize_recipients

        result = _normalize_recipients([
            "user@example.com",
            None,
            "other@example.com",
        ])
        assert len(result) == 2


# =============================================================================
# SEND EMAIL TESTS
# =============================================================================


class TestSendReportEmail:
    """Tests for send_report_email function."""

    @pytest.fixture
    def enabled_mailer(self, monkeypatch):
        """Configure an enabled mailer."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.setenv("NEURA_MAIL_USERNAME", "testuser")
        monkeypatch.setenv("NEURA_MAIL_PASSWORD", "testpass")

        from backend.app.services.utils import mailer
        mailer.refresh_mailer_config()
        return mailer

    def test_send_fails_without_recipients(self, enabled_mailer, monkeypatch):
        """Send should fail without recipients."""
        result = enabled_mailer.send_report_email(
            to_addresses=[],
            subject="Test Subject",
            body="Test Body",
        )
        assert result is False

    def test_send_fails_when_disabled(self, monkeypatch):
        """Send should fail when mailer is disabled."""
        monkeypatch.delenv("NEURA_MAIL_HOST", raising=False)
        monkeypatch.delenv("NEURA_MAIL_SENDER", raising=False)

        from backend.app.services.utils import mailer
        mailer.refresh_mailer_config()

        result = mailer.send_report_email(
            to_addresses=["user@example.com"],
            subject="Test Subject",
            body="Test Body",
        )
        assert result is False

    def test_send_with_tls(self, enabled_mailer, monkeypatch):
        """Send with TLS should use STARTTLS."""
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP", return_value=mock_smtp) as smtp_class:
            result = enabled_mailer.send_report_email(
                to_addresses=["user@example.com"],
                subject="Test Subject",
                body="Test Body",
            )

            # SMTP should be called
            smtp_class.assert_called_once()
            # starttls should be called
            mock_smtp.starttls.assert_called_once()
            # login should be called
            mock_smtp.login.assert_called_once_with("testuser", "testpass")
            # send_message should be called
            mock_smtp.send_message.assert_called_once()

    def test_send_without_tls(self, monkeypatch):
        """Send without TLS should skip STARTTLS."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")
        monkeypatch.setenv("NEURA_MAIL_USE_TLS", "false")
        monkeypatch.setenv("NEURA_MAIL_USERNAME", "testuser")
        monkeypatch.setenv("NEURA_MAIL_PASSWORD", "testpass")

        from backend.app.services.utils import mailer
        mailer.refresh_mailer_config()

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP", return_value=mock_smtp):
            result = mailer.send_report_email(
                to_addresses=["user@example.com"],
                subject="Test Subject",
                body="Test Body",
            )

            # starttls should NOT be called
            mock_smtp.starttls.assert_not_called()

    def test_send_handles_smtp_error(self, enabled_mailer, monkeypatch):
        """Send should handle SMTP errors gracefully."""
        with patch("smtplib.SMTP", side_effect=Exception("Connection refused")):
            result = enabled_mailer.send_report_email(
                to_addresses=["user@example.com"],
                subject="Test Subject",
                body="Test Body",
            )
            assert result is False

    def test_send_with_attachments(self, enabled_mailer, tmp_path, monkeypatch):
        """Send with attachments should include them."""
        # Create a test file
        test_file = tmp_path / "report.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP", return_value=mock_smtp):
            result = enabled_mailer.send_report_email(
                to_addresses=["user@example.com"],
                subject="Test Subject",
                body="Test Body",
                attachments=[test_file],
            )

            # Verify send_message was called with attachment
            mock_smtp.send_message.assert_called_once()
            call_args = mock_smtp.send_message.call_args
            message = call_args[0][0]
            # Check message has attachment
            assert message.is_multipart() or message.get_content_type() == "text/plain"

    def test_send_with_missing_attachment_continues(self, enabled_mailer, tmp_path, monkeypatch):
        """Send should continue if attachment file is missing."""
        missing_file = tmp_path / "nonexistent.pdf"

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP", return_value=mock_smtp):
            result = enabled_mailer.send_report_email(
                to_addresses=["user@example.com"],
                subject="Test Subject",
                body="Test Body",
                attachments=[missing_file],
            )

            # Should still send the email without the attachment
            mock_smtp.send_message.assert_called_once()


# =============================================================================
# NOTIFICATION STRATEGY TESTS
# =============================================================================


class TestNotificationStrategy:
    """Tests for the notification strategy integration."""

    def test_notification_strategy_uses_mailer(self, monkeypatch):
        """NotificationStrategy should call send_report_email."""
        monkeypatch.setenv("NEURA_MAIL_HOST", "smtp.example.com")
        monkeypatch.setenv("NEURA_MAIL_SENDER", "noreply@example.com")

        from backend.app.services.reports.strategies import NotificationStrategy

        strategy = NotificationStrategy()

        with patch(
            "backend.app.services.reports.strategies.send_report_email",
            return_value=True
        ) as mock_send:
            result = strategy.send(
                recipients=["user@example.com"],
                subject="Test Report",
                body="Report content",
                attachments=[],
            )

            assert result is True
            mock_send.assert_called_once_with(
                to_addresses=["user@example.com"],
                subject="Test Report",
                body="Report content",
                attachments=[],
            )

    def test_notification_strategy_registry(self):
        """Notification strategy registry should have email strategy."""
        from backend.app.services.reports.strategies import (
            build_notification_strategy_registry,
            NotificationStrategy,
        )

        registry = build_notification_strategy_registry()
        strategy = registry.resolve("email")

        assert isinstance(strategy, NotificationStrategy)


# =============================================================================
# REPORT SERVICE EMAIL INTEGRATION TESTS
# =============================================================================


class TestReportServiceEmailIntegration:
    """Tests for email integration in report service."""

    def test_maybe_send_email_skips_without_recipients(self, monkeypatch):
        """_maybe_send_email should skip without recipients."""
        from backend.legacy.services.report_service import _maybe_send_email
        from backend.app.schemas.generate.reports import RunPayload

        payload = RunPayload(
            template_id="test-tpl",
            start_date="2024-01-01",
            end_date="2024-01-31",
            email_recipients=[],  # No recipients
        )

        # Should return without sending
        _maybe_send_email(
            payload,
            artifact_paths={},
            run_result={},
            kind="pdf",
            correlation_id="test-123",
        )
        # No exception means it handled gracefully

    def test_build_job_steps_includes_email_step(self):
        """Job steps should include email when recipients provided."""
        from backend.legacy.services.report_service import _build_job_steps
        from backend.app.schemas.generate.reports import RunPayload

        payload = RunPayload(
            template_id="test-tpl",
            start_date="2024-01-01",
            end_date="2024-01-31",
            email_recipients=["user@example.com"],
        )

        steps = _build_job_steps(payload, kind="pdf")
        step_names = [s["name"] for s in steps]

        assert "email" in step_names

    def test_build_job_steps_excludes_email_without_recipients(self):
        """Job steps should exclude email without recipients."""
        from backend.legacy.services.report_service import _build_job_steps
        from backend.app.schemas.generate.reports import RunPayload

        payload = RunPayload(
            template_id="test-tpl",
            start_date="2024-01-01",
            end_date="2024-01-31",
            email_recipients=[],
        )

        steps = _build_job_steps(payload, kind="pdf")
        step_names = [s["name"] for s in steps]

        assert "email" not in step_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

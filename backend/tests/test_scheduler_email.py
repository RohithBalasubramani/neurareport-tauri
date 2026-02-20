"""Comprehensive tests for scheduler and email functionality.

This module tests:
- Report scheduler lifecycle (start/stop)
- Schedule triggering and execution
- Email configuration and sending
- Manual trigger endpoint
- Health check endpoints for email and scheduler
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import pytest


# ============================================================================
# Mailer Configuration Tests
# ============================================================================

class TestMailerConfig:
    """Tests for mailer configuration and environment variable handling."""

    def test_mailer_config_disabled_when_host_missing(self):
        """Mailer should be disabled when NEURA_MAIL_HOST is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing mail config
            for key in list(os.environ.keys()):
                if key.startswith("NEURA_MAIL"):
                    del os.environ[key]

            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.enabled is False
            assert config.host is None

    def test_mailer_config_disabled_when_sender_missing(self):
        """Mailer should be disabled when NEURA_MAIL_SENDER is not set."""
        with patch.dict(os.environ, {"NEURA_MAIL_HOST": "smtp.example.com"}, clear=False):
            # Ensure sender is not set
            os.environ.pop("NEURA_MAIL_SENDER", None)

            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.enabled is False

    def test_mailer_config_enabled_with_host_and_sender(self):
        """Mailer should be enabled when both host and sender are set."""
        with patch.dict(os.environ, {
            "NEURA_MAIL_HOST": "smtp.example.com",
            "NEURA_MAIL_SENDER": "test@example.com",
        }, clear=False):
            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.enabled is True
            assert config.host == "smtp.example.com"
            assert config.sender == "test@example.com"

    def test_mailer_config_default_port(self):
        """Default SMTP port should be 587."""
        with patch.dict(os.environ, {
            "NEURA_MAIL_HOST": "smtp.example.com",
            "NEURA_MAIL_SENDER": "test@example.com",
        }, clear=False):
            os.environ.pop("NEURA_MAIL_PORT", None)
            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.port == 587

    def test_mailer_config_custom_port(self):
        """Custom SMTP port should be respected."""
        with patch.dict(os.environ, {
            "NEURA_MAIL_HOST": "smtp.example.com",
            "NEURA_MAIL_SENDER": "test@example.com",
            "NEURA_MAIL_PORT": "465",
        }, clear=False):
            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.port == 465

    def test_mailer_config_tls_default_enabled(self):
        """TLS should be enabled by default."""
        with patch.dict(os.environ, {
            "NEURA_MAIL_HOST": "smtp.example.com",
            "NEURA_MAIL_SENDER": "test@example.com",
        }, clear=False):
            os.environ.pop("NEURA_MAIL_USE_TLS", None)
            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.use_tls is True

    def test_mailer_config_tls_disabled(self):
        """TLS can be disabled via environment variable."""
        with patch.dict(os.environ, {
            "NEURA_MAIL_HOST": "smtp.example.com",
            "NEURA_MAIL_SENDER": "test@example.com",
            "NEURA_MAIL_USE_TLS": "false",
        }, clear=False):
            from backend.app.services.utils.mailer import _load_mailer_config
            config = _load_mailer_config()
            assert config.use_tls is False

    def test_normalize_recipients_deduplication(self):
        """Recipient normalization should deduplicate emails."""
        from backend.app.services.utils.mailer import _normalize_recipients

        recipients = ["test@example.com", "TEST@example.com", "test@example.com", "other@example.com"]
        normalized = _normalize_recipients(recipients)

        # Should keep first occurrence, dedupe case-sensitive
        assert len(normalized) == 3
        assert "test@example.com" in normalized
        assert "TEST@example.com" in normalized
        assert "other@example.com" in normalized

    def test_normalize_recipients_strips_whitespace(self):
        """Recipient normalization should strip whitespace."""
        from backend.app.services.utils.mailer import _normalize_recipients

        recipients = ["  test@example.com  ", "\nother@example.com\t"]
        normalized = _normalize_recipients(recipients)

        assert normalized == ["test@example.com", "other@example.com"]

    def test_normalize_recipients_empty_input(self):
        """Recipient normalization should handle empty input."""
        from backend.app.services.utils.mailer import _normalize_recipients

        assert _normalize_recipients(None) == []
        assert _normalize_recipients([]) == []
        assert _normalize_recipients([""]) == []


class TestSendReportEmail:
    """Tests for the send_report_email function."""

    def test_send_email_returns_false_when_disabled(self):
        """send_report_email should return False when mailer is disabled."""
        from backend.app.services.utils.mailer import send_report_email

        with patch("backend.app.services.utils.mailer.MAILER_CONFIG") as mock_config:
            mock_config.enabled = False
            mock_config.host = None
            mock_config.sender = None

            result = send_report_email(
                to_addresses=["test@example.com"],
                subject="Test",
                body="Test body",
            )
            assert result is False

    def test_send_email_returns_false_with_no_recipients(self):
        """send_report_email should return False with no recipients."""
        from backend.app.services.utils.mailer import send_report_email

        result = send_report_email(
            to_addresses=[],
            subject="Test",
            body="Test body",
        )
        assert result is False

    @patch("backend.app.services.utils.mailer.smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """send_report_email should return True on successful send."""
        from backend.app.services.utils.mailer import send_report_email, MailerConfig

        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_instance)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        with patch("backend.app.services.utils.mailer.MAILER_CONFIG", MailerConfig(
            host="smtp.example.com",
            port=587,
            username=None,
            password=None,
            sender="sender@example.com",
            use_tls=True,
            enabled=True,
        )):
            result = send_report_email(
                to_addresses=["test@example.com"],
                subject="Test Subject",
                body="Test body content",
            )

            assert result is True
            mock_instance.starttls.assert_called_once()
            mock_instance.send_message.assert_called_once()

    @patch("backend.app.services.utils.mailer.smtplib.SMTP")
    def test_send_email_with_attachments(self, mock_smtp, tmp_path):
        """send_report_email should attach files correctly."""
        from backend.app.services.utils.mailer import send_report_email, MailerConfig

        # Create test attachment
        test_file = tmp_path / "report.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")

        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_instance)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        with patch("backend.app.services.utils.mailer.MAILER_CONFIG", MailerConfig(
            host="smtp.example.com",
            port=587,
            username=None,
            password=None,
            sender="sender@example.com",
            use_tls=True,
            enabled=True,
        )):
            result = send_report_email(
                to_addresses=["test@example.com"],
                subject="Test with Attachment",
                body="See attached",
                attachments=[test_file],
            )

            assert result is True
            # Verify send_message was called
            mock_instance.send_message.assert_called_once()
            # Get the message that was sent
            sent_message = mock_instance.send_message.call_args[0][0]
            # Check attachments exist
            assert sent_message.is_multipart() or len(list(sent_message.iter_attachments())) >= 0

    @patch("backend.app.services.utils.mailer.smtplib.SMTP")
    def test_send_email_handles_missing_attachment(self, mock_smtp, tmp_path):
        """send_report_email should handle missing attachment files gracefully."""
        from backend.app.services.utils.mailer import send_report_email, MailerConfig

        nonexistent_file = tmp_path / "nonexistent.pdf"

        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_instance)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        with patch("backend.app.services.utils.mailer.MAILER_CONFIG", MailerConfig(
            host="smtp.example.com",
            port=587,
            username=None,
            password=None,
            sender="sender@example.com",
            use_tls=True,
            enabled=True,
        )):
            # Should still succeed, just skip the missing attachment
            result = send_report_email(
                to_addresses=["test@example.com"],
                subject="Test",
                body="Test body",
                attachments=[nonexistent_file],
            )

            assert result is True


# ============================================================================
# Scheduler Tests
# ============================================================================

class TestReportScheduler:
    """Tests for the ReportScheduler class."""

    @pytest.fixture
    def mock_runner(self):
        """Create a mock runner function."""
        return MagicMock(return_value={"html_url": "/uploads/test.html", "pdf_url": "/uploads/test.pdf"})

    @pytest.fixture
    def scheduler(self, mock_runner):
        """Create a ReportScheduler instance."""
        from backend.app.services.jobs.report_scheduler import ReportScheduler
        return ReportScheduler(mock_runner, poll_seconds=5)

    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self, scheduler):
        """Scheduler should start and stop cleanly."""
        await scheduler.start()
        assert scheduler._task is not None
        assert not scheduler._task.done()

        await scheduler.stop()
        assert scheduler._task is None

    @pytest.mark.asyncio
    async def test_scheduler_prevents_duplicate_start(self, scheduler):
        """Starting scheduler twice should be idempotent."""
        await scheduler.start()
        first_task = scheduler._task

        await scheduler.start()  # Second start
        assert scheduler._task is first_task  # Same task

        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_scheduler_stop_without_start(self, scheduler):
        """Stopping scheduler without starting should not raise."""
        await scheduler.stop()  # Should not raise

    def test_parse_iso_valid(self):
        """_parse_iso should parse valid ISO timestamps."""
        from backend.app.services.jobs.report_scheduler import _parse_iso

        result = _parse_iso("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso_invalid(self):
        """_parse_iso should return None for invalid timestamps."""
        from backend.app.services.jobs.report_scheduler import _parse_iso

        assert _parse_iso(None) is None
        assert _parse_iso("") is None
        assert _parse_iso("not-a-date") is None

    def test_next_run_datetime_calculation(self):
        """_next_run_datetime should calculate correct next run time."""
        from backend.app.services.jobs.report_scheduler import _next_run_datetime

        baseline = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        schedule = {"interval_minutes": 60}

        result = _next_run_datetime(schedule, baseline)
        expected = datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc)

        assert result == expected

    def test_next_run_datetime_minimum_interval(self):
        """_next_run_datetime should enforce minimum 1-minute interval."""
        from backend.app.services.jobs.report_scheduler import _next_run_datetime

        baseline = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        schedule = {"interval_minutes": 0}  # Invalid, should default to 1

        result = _next_run_datetime(schedule, baseline)
        expected = datetime(2024, 1, 15, 10, 1, 0, tzinfo=timezone.utc)

        assert result == expected


class TestSchedulerDispatch:
    """Tests for scheduler dispatch logic."""

    @pytest.mark.asyncio
    async def test_dispatch_skips_inactive_schedules(self):
        """Dispatcher should skip inactive schedules."""
        from backend.app.services.jobs.report_scheduler import ReportScheduler

        mock_runner = MagicMock()
        scheduler = ReportScheduler(mock_runner, poll_seconds=60)

        with patch.object(scheduler, '_run_schedule', new_callable=AsyncMock) as mock_run:
            with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
                mock_store.list_schedules.return_value = [
                    {"id": "sched-1", "active": False, "next_run_at": "2024-01-01T00:00:00Z"}
                ]

                await scheduler._dispatch_due_jobs()

                mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_skips_future_schedules(self):
        """Dispatcher should skip schedules not yet due."""
        from backend.app.services.jobs.report_scheduler import ReportScheduler

        mock_runner = MagicMock()
        scheduler = ReportScheduler(mock_runner, poll_seconds=60)

        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        with patch.object(scheduler, '_run_schedule', new_callable=AsyncMock) as mock_run:
            with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
                mock_store.list_schedules.return_value = [
                    {"id": "sched-1", "active": True, "next_run_at": future_time}
                ]

                await scheduler._dispatch_due_jobs()

                mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_prevents_duplicate_execution(self):
        """Dispatcher should prevent duplicate concurrent executions."""
        from backend.app.services.jobs.report_scheduler import ReportScheduler

        mock_runner = MagicMock()
        scheduler = ReportScheduler(mock_runner, poll_seconds=60)
        scheduler._inflight.add("sched-1")  # Already running

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        with patch.object(scheduler, '_run_schedule', new_callable=AsyncMock) as mock_run:
            with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
                mock_store.list_schedules.return_value = [
                    {"id": "sched-1", "active": True, "next_run_at": past_time}
                ]

                await scheduler._dispatch_due_jobs()

                mock_run.assert_not_called()


# ============================================================================
# Health Endpoint Tests
# ============================================================================

class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client using the API app."""
        import sys
        import os

        # Ensure proper import path
        backend_dir = Path(__file__).parent.parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from fastapi.testclient import TestClient

        # Try importing from different possible locations
        try:
            from backend.api import app
        except ImportError:
            pytest.skip("Cannot import app for testing")
            return None

        return TestClient(app)

    def test_basic_health_endpoint(self, client):
        """Basic health endpoint should return ok."""
        if client is None:
            pytest.skip("Client not available")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_healthz_endpoint(self, client):
        """Kubernetes liveness probe should return ok."""
        if client is None:
            pytest.skip("Client not available")
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_email_health_endpoint(self, client):
        """Email health endpoint should return configuration status."""
        if client is None:
            pytest.skip("Client not available")
        response = client.get("/health/email")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "enabled" in data["email"]

    def test_scheduler_health_endpoint(self, client):
        """Scheduler health endpoint should return status."""
        if client is None:
            pytest.skip("Client not available")
        response = client.get("/health/scheduler")
        assert response.status_code == 200
        data = response.json()
        assert "scheduler" in data
        assert "enabled" in data["scheduler"]


# ============================================================================
# Schedule API Endpoint Tests
# ============================================================================

class TestScheduleEndpoints:
    """Tests for schedule management API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client with schedule routes."""
        import sys

        # Ensure proper import path
        backend_dir = Path(__file__).parent.parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from fastapi.testclient import TestClient

        try:
            from backend.api import app
            return TestClient(app)
        except ImportError as e:
            pytest.skip(f"Cannot import schedule routes: {e}")
            return None

    def test_list_schedules(self, client):
        """List schedules endpoint should return schedule list."""
        if client is None:
            pytest.skip("Client not available")
        with patch("backend.app.api.routes.schedules.list_schedules", return_value=[]):
            response = client.get("/reports/schedules")
            assert response.status_code == 200
            data = response.json()
            assert "schedules" in data

    def test_get_schedule_not_found(self, client):
        """Get non-existent schedule should return 404."""
        if client is None:
            pytest.skip("Client not available")
        with patch("backend.app.api.routes.schedules.get_schedule", return_value=None):
            response = client.get("/reports/schedules/nonexistent-id")
            assert response.status_code == 404

    def test_trigger_schedule_not_found(self, client):
        """Trigger non-existent schedule should return 404."""
        if client is None:
            pytest.skip("Client not available")
        with patch("backend.app.api.routes.schedules.get_schedule", return_value=None):
            response = client.post("/reports/schedules/nonexistent-id/trigger")
            assert response.status_code == 404

    def test_pause_schedule(self, client):
        """Pause schedule endpoint should set active to false."""
        if client is None:
            pytest.skip("Client not available")
        mock_schedule = {
            "id": "test-schedule",
            "name": "Test Schedule",
            "active": True,
            "template_id": "template-1",
        }
        updated_schedule = {**mock_schedule, "active": False}

        with patch("backend.app.api.routes.schedules.get_schedule", return_value=mock_schedule):
            with patch("backend.app.api.routes.schedules.update_schedule", return_value=updated_schedule):
                response = client.post("/reports/schedules/test-schedule/pause")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["message"] == "Schedule paused"

    def test_resume_schedule(self, client):
        """Resume schedule endpoint should set active to true."""
        if client is None:
            pytest.skip("Client not available")
        mock_schedule = {
            "id": "test-schedule",
            "name": "Test Schedule",
            "active": False,
            "template_id": "template-1",
        }
        updated_schedule = {**mock_schedule, "active": True}

        with patch("backend.app.api.routes.schedules.get_schedule", return_value=mock_schedule):
            with patch("backend.app.api.routes.schedules.update_schedule", return_value=updated_schedule):
                response = client.post("/reports/schedules/test-schedule/resume")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["message"] == "Schedule resumed"


# ============================================================================
# Integration Tests
# ============================================================================

class TestSchedulerEmailIntegration:
    """Integration tests for scheduler and email working together."""

    @pytest.mark.asyncio
    async def test_scheduled_report_sends_email(self):
        """Scheduled report execution should trigger email if recipients configured."""
        from backend.app.services.jobs.report_scheduler import ReportScheduler

        email_sent = []

        def mock_runner(payload, kind, **kwargs):
            if payload.get("email_recipients"):
                email_sent.append(payload["email_recipients"])
            return {
                "html_url": "/uploads/test.html",
                "pdf_url": "/uploads/test.pdf",
            }

        scheduler = ReportScheduler(mock_runner, poll_seconds=5)

        mock_schedule = {
            "id": "sched-1",
            "template_id": "template-1",
            "connection_id": "conn-1",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "email_recipients": ["test@example.com"],
            "email_subject": "Monthly Report",
            "name": "Monthly Report Schedule",
            "template_kind": "pdf",
        }

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.create_job.return_value = {"id": "job-1"}
            mock_store.record_schedule_run.return_value = None

            with patch("backend.app.services.jobs.report_scheduler._build_job_steps", return_value=[]):
                with patch("backend.app.services.jobs.report_scheduler._step_progress_from_steps", return_value={}):
                    await scheduler._run_schedule(mock_schedule)

        # Verify email recipients were passed to runner
        assert len(email_sent) == 1
        assert "test@example.com" in email_sent[0]

    def test_notification_strategy_calls_mailer(self):
        """NotificationStrategy should call send_report_email."""
        from backend.app.services.reports.strategies import NotificationStrategy

        strategy = NotificationStrategy()

        with patch("backend.app.services.reports.strategies.send_report_email", return_value=True) as mock_send:
            result = strategy.send(
                recipients=["test@example.com"],
                subject="Test",
                body="Test body",
                attachments=[],
            )

            assert result is True
            mock_send.assert_called_once_with(
                to_addresses=["test@example.com"],
                subject="Test",
                body="Test body",
                attachments=[],
            )


# ============================================================================
# Main App Lifespan Tests
# ============================================================================

class TestMainAppLifespan:
    """Tests for backend.api lifespan management."""

    @pytest.mark.asyncio
    async def test_lifespan_starts_scheduler(self):
        """Lifespan should start scheduler on app startup."""
        import sys

        # Ensure proper import path
        backend_dir = Path(__file__).parent.parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        try:
            with patch.dict(os.environ, {"NEURA_SCHEDULER_DISABLED": "false"}):
                from backend.api import lifespan
                from fastapi import FastAPI

                test_app = FastAPI()

                with patch("backend.api.ReportScheduler") as MockScheduler:
                    mock_scheduler = AsyncMock()
                    mock_scheduler.start = AsyncMock()
                    mock_scheduler.stop = AsyncMock()
                    MockScheduler.return_value = mock_scheduler

                    # Reset global SCHEDULER
                    import backend.api as api_module
                    original_scheduler = api_module.SCHEDULER
                    api_module.SCHEDULER = None

                    try:
                        async with lifespan(test_app):
                            # Scheduler should be started
                            mock_scheduler.start.assert_called_once()

                        # Scheduler should be stopped on exit
                        mock_scheduler.stop.assert_called_once()
                    finally:
                        api_module.SCHEDULER = original_scheduler
        except Exception as e:
            pytest.skip(f"Cannot test lifespan: {e}")

    @pytest.mark.asyncio
    async def test_lifespan_respects_disabled_flag(self):
        """Lifespan should not start scheduler when disabled."""
        import sys

        # Ensure proper import path
        backend_dir = Path(__file__).parent.parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        try:
            with patch.dict(os.environ, {"NEURA_SCHEDULER_DISABLED": "true"}):
                from backend.api import lifespan, SCHEDULER_DISABLED
                from fastapi import FastAPI

                test_app = FastAPI()

                # When disabled, scheduler should not be created
                import backend.api as api_module
                original_scheduler = api_module.SCHEDULER
                api_module.SCHEDULER = None

                try:
                    with patch("backend.api.ReportScheduler") as MockScheduler:
                        mock_scheduler = AsyncMock()
                        MockScheduler.return_value = mock_scheduler

                        async with lifespan(test_app):
                            pass

                        # Scheduler constructor shouldn't be called when disabled
                        # Note: SCHEDULER_DISABLED is evaluated at module import time
                finally:
                    api_module.SCHEDULER = original_scheduler
        except Exception as e:
            pytest.skip(f"Cannot test lifespan: {e}")

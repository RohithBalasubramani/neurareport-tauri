"""
Tests for the webhook notification service.

Tests cover:
1. Signature computation
2. Successful delivery
3. Retry on failure
4. Client error handling (no retry)
5. Timeout handling
"""
import os
import pytest
import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure debug mode is enabled so WebhookService.__init__ does not raise
# RuntimeError about missing NEURA_WEBHOOK_SECRET in test environments.
os.environ.setdefault("NEURA_DEBUG", "true")

from backend.app.services.jobs.webhook_service import (
    WebhookService,
    WebhookPayload,
    WebhookResult,
    send_job_webhook,
)


class TestWebhookPayload:
    """Tests for WebhookPayload structure."""

    def test_payload_to_dict(self):
        """Payload should serialize to dictionary."""
        payload = WebhookPayload(
            job_id="job-123",
            status="succeeded",
            template_id="template-456",
            template_name="My Report",
            artifacts={"pdf_url": "/uploads/report.pdf"},
            error=None,
            completed_at="2026-01-26T12:00:00Z",
            retry_count=0,
        )

        result = payload.to_dict()

        assert result["event"] == "job.completed"
        assert result["job_id"] == "job-123"
        assert result["status"] == "succeeded"
        assert result["template_id"] == "template-456"
        assert result["artifacts"] == {"pdf_url": "/uploads/report.pdf"}
        assert "timestamp" in result

    def test_payload_with_error(self):
        """Failed job payload should include error."""
        payload = WebhookPayload(
            job_id="job-123",
            status="failed",
            template_id="template-456",
            template_name=None,
            artifacts={},
            error="Connection timeout",
            completed_at="2026-01-26T12:00:00Z",
            retry_count=2,
        )

        result = payload.to_dict()

        assert result["status"] == "failed"
        assert result["error"] == "Connection timeout"
        assert result["retry_count"] == 2


class TestWebhookSignature:
    """Tests for webhook signature computation."""

    def test_signature_is_hmac_sha256(self):
        """Signature should be HMAC-SHA256."""
        service = WebhookService()
        payload = {"job_id": "123", "status": "succeeded"}
        secret = "my-secret"

        signature = service.compute_signature(payload, secret)

        # Verify by computing manually (must match service serialization:
        # sort_keys=True, default=str)
        expected = hmac.new(
            secret.encode("utf-8"),
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        assert signature == expected

    def test_signature_is_deterministic(self):
        """Same payload and secret should produce same signature."""
        service = WebhookService()
        payload = {"a": 1, "b": 2}
        secret = "test-secret"

        sig1 = service.compute_signature(payload, secret)
        sig2 = service.compute_signature(payload, secret)

        assert sig1 == sig2

    def test_signature_varies_with_secret(self):
        """Different secrets should produce different signatures."""
        service = WebhookService()
        payload = {"job_id": "123"}

        sig1 = service.compute_signature(payload, "secret-1")
        sig2 = service.compute_signature(payload, "secret-2")

        assert sig1 != sig2


class TestWebhookHeaders:
    """Tests for webhook request headers."""

    def test_headers_include_signature(self):
        """Headers should include the signature."""
        service = WebhookService()
        payload = {"job_id": "123"}
        secret = "test"

        headers = service.build_headers(payload, secret)

        assert "X-NeuraReport-Signature" in headers
        assert headers["X-NeuraReport-Signature"].startswith("sha256=")

    def test_headers_include_event_type(self):
        """Headers should include event type."""
        service = WebhookService()
        headers = service.build_headers({}, "secret")

        assert headers["X-NeuraReport-Event"] == "job.completed"

    def test_headers_include_content_type(self):
        """Headers should include content type."""
        service = WebhookService()
        headers = service.build_headers({}, "secret")

        assert headers["Content-Type"] == "application/json"


class TestWebhookDelivery:
    """Tests for webhook delivery logic."""

    @pytest.mark.asyncio
    async def test_successful_delivery(self):
        """Successful webhook delivery should return success."""
        service = WebhookService(max_retries=3)
        payload = WebhookPayload(
            job_id="job-123",
            status="succeeded",
            template_id="tpl",
            template_name="Test",
            artifacts={},
            error=None,
            completed_at=None,
            retry_count=0,
        )

        with patch("backend.app.services.jobs.webhook_service.httpx") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient.return_value = mock_client

            result = await service.deliver(
                "https://example.com/webhook",
                payload,
                "secret",
            )

        assert result.success is True
        assert result.status_code == 200
        assert result.attempts == 1

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """Server errors (5xx) should trigger retry."""
        service = WebhookService(max_retries=3, initial_backoff_seconds=0.01)
        payload = WebhookPayload(
            job_id="job-123",
            status="failed",
            template_id="tpl",
            template_name="Test",
            artifacts={},
            error="error",
            completed_at=None,
            retry_count=0,
        )

        with patch("backend.app.services.jobs.webhook_service.httpx") as mock_httpx:
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 503
            mock_response_fail.text = "Service Unavailable"

            mock_response_success = MagicMock()
            mock_response_success.status_code = 200
            mock_response_success.text = "OK"

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=[
                mock_response_fail,
                mock_response_fail,
                mock_response_success,
            ])
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient.return_value = mock_client

            result = await service.deliver(
                "https://example.com/webhook",
                payload,
                "secret",
            )

        assert result.success is True
        assert result.attempts == 3  # Took 3 attempts

    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self):
        """Client errors (4xx) should not retry."""
        service = WebhookService(max_retries=3, initial_backoff_seconds=0.01)
        payload = WebhookPayload(
            job_id="job-123",
            status="succeeded",
            template_id="tpl",
            template_name="Test",
            artifacts={},
            error=None,
            completed_at=None,
            retry_count=0,
        )

        with patch("backend.app.services.jobs.webhook_service.httpx") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient.return_value = mock_client

            result = await service.deliver(
                "https://example.com/webhook",
                payload,
                "secret",
            )

        assert result.success is False
        assert result.status_code == 404
        assert result.attempts == 1  # No retry

    @pytest.mark.asyncio
    async def test_empty_url_returns_error(self):
        """Empty webhook URL should return error without making request."""
        service = WebhookService()
        payload = WebhookPayload(
            job_id="job-123",
            status="succeeded",
            template_id="tpl",
            template_name="Test",
            artifacts={},
            error=None,
            completed_at=None,
            retry_count=0,
        )

        result = await service.deliver("", payload, "secret")

        assert result.success is False
        assert result.attempts == 0
        assert "No webhook URL" in result.error


class TestSendJobWebhook:
    """Tests for the convenience function send_job_webhook."""

    @pytest.mark.asyncio
    async def test_send_job_webhook_extracts_fields(self):
        """send_job_webhook should extract fields from job dict."""
        job = {
            "id": "job-123",
            "status": "succeeded",
            "templateId": "tpl-456",
            "templateName": "My Report",
            "result": {"artifacts": {"pdf_url": "/report.pdf"}},
            "error": None,
            "finishedAt": "2026-01-26T12:00:00Z",
            "retryCount": 0,
            "webhookUrl": "https://example.com/hook",
            "webhook_secret": "secret123",
        }

        with patch("backend.app.services.jobs.webhook_service.httpx") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient.return_value = mock_client

            result = await send_job_webhook(job)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_send_job_webhook_no_url(self):
        """Jobs without webhook URL should succeed without sending."""
        job = {
            "id": "job-123",
            "status": "succeeded",
        }

        result = await send_job_webhook(job)

        assert result.success is True
        assert result.attempts == 0


class TestWebhookResult:
    """Tests for WebhookResult structure."""

    def test_success_result(self):
        """Successful result should have correct fields."""
        result = WebhookResult(
            success=True,
            status_code=200,
            attempts=1,
            error=None,
            response_body="OK",
        )

        assert result.success is True
        assert result.status_code == 200
        assert result.error is None

    def test_failure_result(self):
        """Failed result should include error."""
        result = WebhookResult(
            success=False,
            status_code=500,
            attempts=3,
            error="Server error: 500",
        )

        assert result.success is False
        assert result.error == "Server error: 500"
        assert result.attempts == 3

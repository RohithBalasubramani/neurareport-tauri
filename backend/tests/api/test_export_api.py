"""Export API Route Tests.

Comprehensive tests for document export and distribution endpoints.
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.export import router
from backend.app.api.middleware import limiter
from backend.app.services.security import require_api_key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_export_job(
    document_id: str = "doc-1",
    fmt: str = "pdf",
    options: dict | None = None,
    status: str = "pending",
) -> dict:
    """Build a fake export job dict matching the shape returned by ExportService."""
    return {
        "job_id": str(uuid.uuid4()),
        "document_id": document_id,
        "format": fmt,
        "options": options or {},
        "status": status,
        "created_at": _now(),
        "completed_at": None,
        "download_url": None,
        "file_size": None,
        "error": None,
    }


def _make_bulk_job(
    document_ids: list[str] | None = None,
    fmt: str = "pdf",
) -> dict:
    """Build a fake bulk-export job dict."""
    job_id = str(uuid.uuid4())
    return {
        "job_id": job_id,
        "document_ids": document_ids or ["doc-1", "doc-2"],
        "format": fmt,
        "status": "completed",
        "created_at": _now(),
        "completed_at": _now(),
        "download_url": f"/uploads/exports/export_{job_id}.zip",
        "file_size": 2048,
    }


def _make_distribution_job(
    channel: str = "email",
    document_id: str = "doc-1",
    **extra,
) -> dict:
    """Build a fake distribution job dict."""
    base = {
        "job_id": str(uuid.uuid4()),
        "channel": channel,
        "document_id": document_id,
        "status": "sent",
        "sent_at": _now(),
    }
    base.update(extra)
    return base


def _make_embed_result(document_id: str = "doc-1") -> dict:
    """Build a fake embed-token result dict."""
    token = "fake-token-abc123"
    return {
        "token": token,
        "embed_url": f"/embed/{token}",
        "embed_code": f'<iframe src="/embed/{token}" width="800" height="600" frameborder="0"></iframe>',
        "expires_at": None,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_export_service():
    """Create an AsyncMock that stands in for the module-level export_service."""
    svc = AsyncMock()
    svc.create_export_job = AsyncMock(side_effect=lambda **kw: _make_export_job(
        document_id=kw.get("document_id", "doc-1"),
        fmt=kw.get("format", "pdf"),
        options=kw.get("options", {}),
    ))
    svc.bulk_export = AsyncMock(side_effect=lambda **kw: _make_bulk_job(
        document_ids=kw.get("document_ids"),
        fmt=kw.get("format", "pdf"),
    ))
    svc.get_export_job = AsyncMock(return_value=None)
    svc.generate_embed_token = AsyncMock(side_effect=lambda **kw: _make_embed_result(
        document_id=kw.get("document_id", "doc-1"),
    ))
    return svc


@pytest.fixture
def mock_distribution_service():
    """Create an AsyncMock that stands in for the module-level distribution_service."""
    svc = AsyncMock()
    svc.send_email = AsyncMock(side_effect=lambda **kw: _make_distribution_job(
        channel="email",
        document_id=kw.get("document_id", "doc-1"),
        recipients=kw.get("recipients", []),
        recipients_count=len(kw.get("recipients", [])),
    ))
    svc.publish_to_portal = AsyncMock(side_effect=lambda **kw: _make_distribution_job(
        channel="portal",
        document_id=kw.get("document_id", "doc-1"),
        portal_path=kw.get("portal_path", "/reports"),
        portal_url=f"/portal/{kw.get('portal_path', 'reports')}/{kw.get('document_id', 'doc-1')}",
        public=kw.get("options", {}).get("public", False),
        status="published",
    ))
    svc.send_to_slack = AsyncMock(side_effect=lambda **kw: _make_distribution_job(
        channel="slack",
        document_id=kw.get("document_id", "doc-1"),
        slack_channel=kw.get("channel", "#general"),
    ))
    svc.send_to_teams = AsyncMock(side_effect=lambda **kw: _make_distribution_job(
        channel="teams",
        document_id=kw.get("document_id", "doc-1"),
    ))
    svc.send_webhook = AsyncMock(side_effect=lambda **kw: _make_distribution_job(
        channel="webhook",
        document_id=kw.get("document_id", "doc-1"),
        webhook_url=kw.get("webhook_url", "https://example.com/hook"),
        response_status=200,
    ))
    return svc


@pytest.fixture
def app(mock_export_service, mock_distribution_service):
    """Create a FastAPI app with export routes and dependency overrides."""
    _app = FastAPI()

    # Override the API key dependency so tests run without credentials.
    _app.dependency_overrides[require_api_key] = lambda: None
    # Disable rate limiting in tests
    limiter.enabled = False

    _app.include_router(router, prefix="/export")

    # Patch the module-level singletons so the route handlers use our mocks.
    import backend.app.api.routes.export as _route_mod

    _orig_export = _route_mod.export_service
    _orig_distrib = _route_mod.distribution_service
    _route_mod.export_service = mock_export_service
    _route_mod.distribution_service = mock_distribution_service

    # Patch DNS resolution so test URLs (*.example.com) resolve to a
    # public IP instead of failing or hitting a private address.
    _real_getaddrinfo = __import__("socket").getaddrinfo

    def _mock_getaddrinfo(host, port, *args, **kwargs):
        if host and "example.com" in host:
            import socket
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]
        return _real_getaddrinfo(host, port, *args, **kwargs)

    with patch("socket.getaddrinfo", side_effect=_mock_getaddrinfo):
        yield _app

    _route_mod.export_service = _orig_export
    _route_mod.distribution_service = _orig_distrib
    limiter.enabled = True


@pytest.fixture
def client(app):
    """TestClient bound to the test app."""
    return TestClient(app)


# ============================================================================
# FORMAT EXPORT ENDPOINTS
# ============================================================================


class TestExportToPDF:
    def test_creates_pdf_job(self, client, mock_export_service):
        resp = client.post("/export/doc-100/pdf")
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_id"] == "doc-100"
        assert data["format"] == "pdf"
        assert data["status"] == "pending"
        mock_export_service.create_export_job.assert_awaited_once()

    def test_pdf_with_options(self, client, mock_export_service):
        opts = {"watermark": "DRAFT", "page_numbers": True}
        resp = client.post("/export/doc-100/pdf", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"] == opts

    def test_pdf_with_empty_options(self, client, mock_export_service):
        resp = client.post("/export/doc-100/pdf", json=None)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"] == {}

    def test_pdf_job_has_required_fields(self, client):
        resp = client.post("/export/doc-1/pdf")
        data = resp.json()
        for field in ("job_id", "document_id", "format", "status", "created_at"):
            assert field in data


class TestExportToPDFA:
    def test_creates_pdfa_job(self, client, mock_export_service):
        resp = client.post("/export/doc-200/pdfa")
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "pdfa"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "pdfa"

    def test_pdfa_sets_compliance_flag(self, client, mock_export_service):
        resp = client.post("/export/doc-200/pdfa")
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["pdfa_compliant"] is True

    def test_pdfa_preserves_user_options(self, client, mock_export_service):
        resp = client.post("/export/doc-200/pdfa", json={"watermark": "ARCHIVE"})
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["watermark"] == "ARCHIVE"
        assert call_kwargs["options"]["pdfa_compliant"] is True


class TestExportToDOCX:
    def test_creates_docx_job(self, client, mock_export_service):
        resp = client.post("/export/doc-300/docx")
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "docx"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "docx"

    def test_docx_with_options(self, client, mock_export_service):
        opts = {"track_changes": True}
        resp = client.post("/export/doc-300/docx", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["track_changes"] is True


class TestExportToPPTX:
    def test_creates_pptx_job(self, client, mock_export_service):
        resp = client.post("/export/doc-400/pptx")
        assert resp.status_code == 200
        assert resp.json()["format"] == "pptx"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "pptx"

    def test_pptx_with_layout_option(self, client, mock_export_service):
        opts = {"slide_layout": "blank", "include_speaker_notes": True}
        resp = client.post("/export/doc-400/pptx", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["slide_layout"] == "blank"


class TestExportToEPUB:
    def test_creates_epub_job(self, client, mock_export_service):
        resp = client.post("/export/doc-500/epub")
        assert resp.status_code == 200
        assert resp.json()["format"] == "epub"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "epub"

    def test_epub_with_metadata_options(self, client, mock_export_service):
        opts = {"author": "Alice", "isbn": "978-3-16-148410-0"}
        resp = client.post("/export/doc-500/epub", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["author"] == "Alice"


class TestExportToLaTeX:
    def test_creates_latex_job(self, client, mock_export_service):
        resp = client.post("/export/doc-600/latex")
        assert resp.status_code == 200
        assert resp.json()["format"] == "latex"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "latex"

    def test_latex_with_document_class(self, client, mock_export_service):
        opts = {"document_class": "report", "bibliography_style": "plain"}
        resp = client.post("/export/doc-600/latex", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["document_class"] == "report"


class TestExportToMarkdown:
    def test_creates_markdown_job(self, client, mock_export_service):
        resp = client.post("/export/doc-700/markdown")
        assert resp.status_code == 200
        assert resp.json()["format"] == "markdown"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "markdown"

    def test_markdown_with_flavor(self, client, mock_export_service):
        opts = {"flavor": "commonmark", "include_frontmatter": False}
        resp = client.post("/export/doc-700/markdown", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["flavor"] == "commonmark"


class TestExportToHTML:
    def test_creates_html_job(self, client, mock_export_service):
        resp = client.post("/export/doc-800/html")
        assert resp.status_code == 200
        assert resp.json()["format"] == "html"
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["format"] == "html"

    def test_html_with_standalone_option(self, client, mock_export_service):
        opts = {"standalone": False}
        resp = client.post("/export/doc-800/html", json=opts)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"]["standalone"] is False


class TestAllFormatsParameterized:
    """Parametrized test that exercises every format endpoint in one sweep."""

    @pytest.mark.parametrize(
        "path_suffix,expected_format",
        [
            ("pdf", "pdf"),
            ("pdfa", "pdfa"),
            ("docx", "docx"),
            ("pptx", "pptx"),
            ("epub", "epub"),
            ("latex", "latex"),
            ("markdown", "markdown"),
            ("html", "html"),
        ],
    )
    def test_format_endpoint_returns_correct_format(
        self, client, mock_export_service, path_suffix, expected_format,
    ):
        resp = client.post(f"/export/doc-param/{path_suffix}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == expected_format
        assert data["document_id"] == "doc-param"
        assert data["status"] == "pending"

    @pytest.mark.parametrize(
        "path_suffix",
        ["pdf", "pdfa", "docx", "pptx", "epub", "latex", "markdown", "html"],
    )
    def test_format_endpoint_accepts_no_body(self, client, path_suffix):
        """Endpoints should work when called without a JSON body."""
        resp = client.post(f"/export/any-doc/{path_suffix}")
        assert resp.status_code == 200


# ============================================================================
# BULK EXPORT
# ============================================================================


class TestBulkExport:
    def test_bulk_export_creates_zip(self, client, mock_export_service):
        payload = {
            "document_ids": ["doc-a", "doc-b", "doc-c"],
            "format": "pdf",
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["download_url"].endswith(".zip")
        assert data["file_size"] > 0
        mock_export_service.bulk_export.assert_awaited_once()

    def test_bulk_export_passes_format_value(self, client, mock_export_service):
        payload = {
            "document_ids": ["doc-1"],
            "format": "docx",
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.bulk_export.call_args.kwargs
        assert call_kwargs["format"] == "docx"

    def test_bulk_export_with_options(self, client, mock_export_service):
        payload = {
            "document_ids": ["doc-1", "doc-2"],
            "format": "pdf",
            "options": {"quality": "high", "watermark": "BULK"},
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.bulk_export.call_args.kwargs
        assert call_kwargs["options"]["quality"] == "high"

    def test_bulk_export_with_single_document(self, client, mock_export_service):
        payload = {
            "document_ids": ["doc-only"],
            "format": "html",
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 200

    def test_bulk_export_requires_document_ids(self, client):
        payload = {"format": "pdf"}
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 422  # validation error

    def test_bulk_export_requires_format(self, client):
        payload = {"document_ids": ["doc-1"]}
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 422

    def test_bulk_export_rejects_invalid_format(self, client):
        payload = {
            "document_ids": ["doc-1"],
            "format": "not-a-format",
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 422

    @pytest.mark.parametrize("fmt", ["pdf", "pdfa", "docx", "pptx", "epub", "latex", "markdown", "html"])
    def test_bulk_export_accepts_all_valid_formats(self, client, fmt):
        payload = {
            "document_ids": ["doc-1"],
            "format": fmt,
        }
        resp = client.post("/export/bulk", json=payload)
        assert resp.status_code == 200


# ============================================================================
# JOB STATUS
# ============================================================================


class TestGetExportJob:
    def test_get_existing_job(self, client, mock_export_service):
        job = _make_export_job(document_id="doc-42", fmt="pdf", status="completed")
        mock_export_service.get_export_job.return_value = job
        resp = client.get(f"/export/jobs/{job['job_id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job["job_id"]
        assert data["status"] == "completed"

    def test_get_nonexistent_job_returns_404(self, client, mock_export_service):
        mock_export_service.get_export_job.return_value = None
        resp = client.get("/export/jobs/does-not-exist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Export job not found"

    def test_get_job_returns_all_fields(self, client, mock_export_service):
        job = _make_export_job(document_id="doc-77", fmt="docx")
        job["download_url"] = "/uploads/exports/result.docx"
        job["file_size"] = 12345
        mock_export_service.get_export_job.return_value = job
        resp = client.get(f"/export/jobs/{job['job_id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["download_url"] == "/uploads/exports/result.docx"
        assert data["file_size"] == 12345

    def test_get_pending_job(self, client, mock_export_service):
        job = _make_export_job(status="pending")
        mock_export_service.get_export_job.return_value = job
        resp = client.get(f"/export/jobs/{job['job_id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending"

    def test_get_failed_job(self, client, mock_export_service):
        job = _make_export_job(status="failed")
        job["error"] = "Conversion timeout"
        mock_export_service.get_export_job.return_value = job
        resp = client.get(f"/export/jobs/{job['job_id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "failed"
        assert resp.json()["error"] == "Conversion timeout"


# ============================================================================
# DISTRIBUTION - EMAIL CAMPAIGN
# ============================================================================


class TestEmailCampaign:
    def test_email_campaign_basic(self, client, mock_distribution_service):
        payload = {
            "document_ids": ["doc-1", "doc-2"],
            "recipients": ["alice@test.com", "bob@test.com"],
            "subject": "Monthly Report",
            "message": "Please find the attached reports.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["documents_sent"] == 2
        assert data["recipients_count"] == 2
        assert len(data["results"]) == 2
        assert data["campaign_id"] is not None

    def test_email_campaign_single_document(self, client, mock_distribution_service):
        payload = {
            "document_ids": ["doc-only"],
            "recipients": ["user@test.com"],
            "subject": "Single Report",
            "message": "Here is your report.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["documents_sent"] == 1
        assert data["recipients_count"] == 1

    def test_email_campaign_calls_service_per_doc(self, client, mock_distribution_service):
        payload = {
            "document_ids": ["doc-a", "doc-b", "doc-c"],
            "recipients": ["x@test.com"],
            "subject": "Batch",
            "message": "Batch send.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        assert mock_distribution_service.send_email.await_count == 3

    def test_email_campaign_passes_subject_and_message(self, client, mock_distribution_service):
        payload = {
            "document_ids": ["doc-1"],
            "recipients": ["r@test.com"],
            "subject": "Important Subject",
            "message": "Body text here.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_email.call_args.kwargs
        assert call_kwargs["subject"] == "Important Subject"
        assert call_kwargs["message"] == "Body text here."

    def test_email_campaign_requires_fields(self, client):
        # Missing required fields
        resp = client.post("/export/distribution/email-campaign", json={})
        assert resp.status_code == 422

    def test_email_campaign_requires_recipients(self, client):
        payload = {
            "document_ids": ["doc-1"],
            "subject": "Test",
            "message": "Test",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 422


# ============================================================================
# DISTRIBUTION - PORTAL PUBLISH
# ============================================================================


class TestPortalPublish:
    def test_publish_basic(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-portal",
            "portal_path": "/reports/q4",
        }
        resp = client.post("/export/distribution/portal/doc-portal", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "portal"
        assert data["status"] == "published"
        mock_distribution_service.publish_to_portal.assert_awaited_once()

    def test_publish_with_full_options(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-portal",
            "portal_path": "/reports/annual",
            "title": "Annual Report 2025",
            "description": "Full annual report with financial data.",
            "tags": ["finance", "annual", "2025"],
            "public": True,
            "password": "secret123",
        }
        resp = client.post("/export/distribution/portal/doc-portal", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.publish_to_portal.call_args.kwargs
        assert call_kwargs["portal_path"] == "/reports/annual"
        opts = call_kwargs["options"]
        assert opts["title"] == "Annual Report 2025"
        assert opts["public"] is True
        assert opts["password"] == "secret123"
        assert opts["tags"] == ["finance", "annual", "2025"]

    def test_publish_private_by_default(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-1",
            "portal_path": "/reports/private",
        }
        resp = client.post("/export/distribution/portal/doc-1", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.publish_to_portal.call_args.kwargs
        assert call_kwargs["options"]["public"] is False

    def test_publish_requires_portal_path(self, client):
        payload = {"document_id": "doc-1"}
        resp = client.post("/export/distribution/portal/doc-1", json=payload)
        assert resp.status_code == 422


# ============================================================================
# DISTRIBUTION - EMBED GENERATION
# ============================================================================


class TestGenerateEmbed:
    def test_embed_returns_code_url_token(self, client, mock_export_service):
        payload = {"document_id": "doc-embed"}
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "embed_code" in data
        assert "embed_url" in data
        assert "token" in data
        assert "<iframe" in data["embed_code"]

    def test_embed_default_dimensions(self, client, mock_export_service):
        payload = {"document_id": "doc-embed"}
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.generate_embed_token.call_args.kwargs
        opts = call_kwargs["options"]
        assert opts["width"] == 800
        assert opts["height"] == 600

    def test_embed_custom_dimensions(self, client, mock_export_service):
        payload = {
            "document_id": "doc-embed",
            "width": 1024,
            "height": 768,
        }
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.generate_embed_token.call_args.kwargs
        opts = call_kwargs["options"]
        assert opts["width"] == 1024
        assert opts["height"] == 768

    def test_embed_with_permissions(self, client, mock_export_service):
        payload = {
            "document_id": "doc-embed",
            "allow_download": True,
            "allow_print": True,
            "show_toolbar": False,
            "theme": "dark",
        }
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.generate_embed_token.call_args.kwargs
        opts = call_kwargs["options"]
        assert opts["allow_download"] is True
        assert opts["allow_print"] is True
        assert opts["show_toolbar"] is False
        assert opts["theme"] == "dark"

    def test_embed_defaults_for_permissions(self, client, mock_export_service):
        payload = {"document_id": "doc-embed"}
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_export_service.generate_embed_token.call_args.kwargs
        opts = call_kwargs["options"]
        assert opts["allow_download"] is False
        assert opts["allow_print"] is False
        assert opts["show_toolbar"] is True
        assert opts["theme"] == "light"


# ============================================================================
# DISTRIBUTION - SLACK
# ============================================================================


class TestSlackDistribution:
    def test_send_to_slack(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-slack",
            "channel": "#reports",
        }
        resp = client.post("/export/distribution/slack", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "slack"
        assert data["status"] == "sent"
        mock_distribution_service.send_to_slack.assert_awaited_once()

    def test_send_to_slack_with_message(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-slack",
            "channel": "#general",
            "message": "Check out this report!",
        }
        resp = client.post("/export/distribution/slack", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_to_slack.call_args.kwargs
        assert call_kwargs["message"] == "Check out this report!"
        assert call_kwargs["channel"] == "#general"

    def test_slack_requires_channel(self, client):
        payload = {"document_id": "doc-1"}
        resp = client.post("/export/distribution/slack", json=payload)
        assert resp.status_code == 422

    def test_slack_requires_document_id(self, client):
        payload = {"channel": "#general"}
        resp = client.post("/export/distribution/slack", json=payload)
        assert resp.status_code == 422


# ============================================================================
# DISTRIBUTION - TEAMS
# ============================================================================


class TestTeamsDistribution:
    def test_send_to_teams(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-teams",
            "webhook_url": "https://outlook.office.com/webhook/abc123",
        }
        resp = client.post("/export/distribution/teams", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "teams"
        assert data["status"] == "sent"
        mock_distribution_service.send_to_teams.assert_awaited_once()

    def test_send_to_teams_with_title_and_message(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-teams",
            "webhook_url": "https://outlook.office.com/webhook/xyz",
            "title": "Q4 Report Ready",
            "message": "The quarterly report has been generated.",
        }
        resp = client.post("/export/distribution/teams", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_to_teams.call_args.kwargs
        assert call_kwargs["title"] == "Q4 Report Ready"
        assert call_kwargs["message"] == "The quarterly report has been generated."
        assert call_kwargs["webhook_url"] == "https://outlook.office.com/webhook/xyz"

    def test_teams_requires_webhook_url(self, client):
        payload = {"document_id": "doc-1"}
        resp = client.post("/export/distribution/teams", json=payload)
        assert resp.status_code == 422

    def test_teams_requires_document_id(self, client):
        payload = {"webhook_url": "https://example.com/hook"}
        resp = client.post("/export/distribution/teams", json=payload)
        assert resp.status_code == 422


# ============================================================================
# DISTRIBUTION - WEBHOOK
# ============================================================================


class TestWebhookDistribution:
    def test_send_webhook(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-hook",
            "webhook_url": "https://api.example.com/ingest",
        }
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["channel"] == "webhook"
        assert data["status"] == "sent"
        mock_distribution_service.send_webhook.assert_awaited_once()

    def test_webhook_default_method_is_post(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-hook",
            "webhook_url": "https://api.example.com/ingest",
        }
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_webhook.call_args.kwargs
        assert call_kwargs["method"] == "POST"

    def test_webhook_custom_method(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-hook",
            "webhook_url": "https://api.example.com/ingest",
            "method": "PUT",
        }
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_webhook.call_args.kwargs
        assert call_kwargs["method"] == "PUT"

    def test_webhook_with_custom_headers(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-hook",
            "webhook_url": "https://api.example.com/ingest",
            "headers": {
                "Authorization": "Bearer token123",
                "X-Custom": "value",
            },
        }
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_webhook.call_args.kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer token123"
        assert call_kwargs["headers"]["X-Custom"] == "value"

    def test_webhook_empty_headers_default(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-hook",
            "webhook_url": "https://api.example.com/ingest",
        }
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.send_webhook.call_args.kwargs
        assert call_kwargs["headers"] == {}

    def test_webhook_requires_url(self, client):
        payload = {"document_id": "doc-1"}
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422

    def test_webhook_requires_document_id(self, client):
        payload = {"webhook_url": "https://example.com/hook"}
        resp = client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    def test_document_id_with_special_characters(self, client, mock_export_service):
        """Document IDs containing hyphens and underscores should work."""
        resp = client.post("/export/doc-with-hyphens_and_underscores/pdf")
        assert resp.status_code == 200
        assert resp.json()["document_id"] == "doc-with-hyphens_and_underscores"

    def test_export_job_not_found_returns_proper_error(self, client, mock_export_service):
        mock_export_service.get_export_job.return_value = None
        resp = client.get("/export/jobs/nonexistent-uuid-value")
        assert resp.status_code == 404
        assert "Export job not found" in resp.json()["detail"]

    def test_export_with_empty_dict_options(self, client, mock_export_service):
        resp = client.post("/export/doc-1/pdf", json={})
        assert resp.status_code == 200
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["options"] == {}

    def test_email_campaign_many_recipients(self, client, mock_distribution_service):
        recipients = [f"user{i}@test.com" for i in range(50)]
        payload = {
            "document_ids": ["doc-1"],
            "recipients": recipients,
            "subject": "Bulk send",
            "message": "Mass email.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        assert resp.json()["recipients_count"] == 50

    def test_email_campaign_many_documents(self, client, mock_distribution_service):
        doc_ids = [f"doc-{i}" for i in range(10)]
        payload = {
            "document_ids": doc_ids,
            "recipients": ["admin@test.com"],
            "subject": "Multi-doc",
            "message": "Multiple docs.",
        }
        resp = client.post("/export/distribution/email-campaign", json=payload)
        assert resp.status_code == 200
        assert resp.json()["documents_sent"] == 10
        assert mock_distribution_service.send_email.await_count == 10

    def test_portal_publish_with_empty_tags(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-1",
            "portal_path": "/empty-tags",
            "tags": [],
        }
        resp = client.post("/export/distribution/portal/doc-1", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_distribution_service.publish_to_portal.call_args.kwargs
        assert call_kwargs["options"]["tags"] == []

    def test_embed_url_contains_token(self, client, mock_export_service):
        payload = {"document_id": "doc-embed"}
        resp = client.post("/export/distribution/embed/doc-embed", json=payload)
        data = resp.json()
        assert data["token"] in data["embed_url"]
        assert data["token"] in data["embed_code"]

    def test_get_job_with_processing_status(self, client, mock_export_service):
        job = _make_export_job(status="processing")
        mock_export_service.get_export_job.return_value = job
        resp = client.get(f"/export/jobs/{job['job_id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"


# ============================================================================
# MOCK INTERACTION VERIFICATION
# ============================================================================


class TestServiceInteraction:
    """Verify the route layer calls services with the correct arguments."""

    def test_pdf_passes_document_id_and_format(self, client, mock_export_service):
        client.post("/export/my-doc-id/pdf")
        mock_export_service.create_export_job.assert_awaited_once_with(
            document_id="my-doc-id",
            format="pdf",
            options={},
        )

    def test_pdfa_passes_compliance_in_options(self, client, mock_export_service):
        client.post("/export/archival-doc/pdfa")
        call_kwargs = mock_export_service.create_export_job.call_args.kwargs
        assert call_kwargs["document_id"] == "archival-doc"
        assert call_kwargs["format"] == "pdfa"
        assert call_kwargs["options"]["pdfa_compliant"] is True

    def test_bulk_passes_enum_value(self, client, mock_export_service):
        payload = {
            "document_ids": ["d1", "d2"],
            "format": "epub",
            "options": {"quality": "low"},
        }
        client.post("/export/bulk", json=payload)
        mock_export_service.bulk_export.assert_awaited_once_with(
            document_ids=["d1", "d2"],
            format="epub",
            options={"quality": "low"},
        )

    def test_slack_passes_all_params(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-s",
            "channel": "#data-team",
            "message": "New report available.",
        }
        client.post("/export/distribution/slack", json=payload)
        mock_distribution_service.send_to_slack.assert_awaited_once_with(
            document_id="doc-s",
            channel="#data-team",
            message="New report available.",
        )

    def test_teams_passes_all_params(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-t",
            "webhook_url": "https://teams.example.com/hook",
            "title": "Report Title",
            "message": "Report body.",
        }
        client.post("/export/distribution/teams", json=payload)
        mock_distribution_service.send_to_teams.assert_awaited_once_with(
            document_id="doc-t",
            webhook_url="https://teams.example.com/hook",
            title="Report Title",
            message="Report body.",
        )

    def test_webhook_passes_all_params(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-w",
            "webhook_url": "https://hook.example.com/receive",
            "method": "PATCH",
            "headers": {"X-Key": "val"},
        }
        client.post("/export/distribution/webhook", json=payload)
        mock_distribution_service.send_webhook.assert_awaited_once_with(
            document_id="doc-w",
            webhook_url="https://hook.example.com/receive",
            method="PATCH",
            headers={"X-Key": "val"},
        )

    def test_portal_passes_options_dict(self, client, mock_distribution_service):
        payload = {
            "document_id": "doc-p",
            "portal_path": "/public/reports",
            "title": "Report",
            "description": "A description.",
            "tags": ["tag1"],
            "public": True,
            "password": "pw",
        }
        client.post("/export/distribution/portal/doc-p", json=payload)
        call_kwargs = mock_distribution_service.publish_to_portal.call_args.kwargs
        assert call_kwargs["document_id"] == "doc-p"
        assert call_kwargs["portal_path"] == "/public/reports"
        opts = call_kwargs["options"]
        assert opts["title"] == "Report"
        assert opts["description"] == "A description."
        assert opts["tags"] == ["tag1"]
        assert opts["public"] is True
        assert opts["password"] == "pw"

    def test_embed_passes_options(self, client, mock_export_service):
        payload = {
            "document_id": "doc-e",
            "width": 1200,
            "height": 900,
            "allow_download": True,
            "allow_print": False,
            "show_toolbar": True,
            "theme": "dark",
        }
        client.post("/export/distribution/embed/doc-e", json=payload)
        mock_export_service.generate_embed_token.assert_awaited_once_with(
            document_id="doc-e",
            options={
                "width": 1200,
                "height": 900,
                "allow_download": True,
                "allow_print": False,
                "show_toolbar": True,
                "theme": "dark",
            },
        )

    def test_email_campaign_calls_once_per_document(self, client, mock_distribution_service):
        payload = {
            "document_ids": ["a", "b"],
            "recipients": ["u@test.com"],
            "subject": "S",
            "message": "M",
        }
        client.post("/export/distribution/email-campaign", json=payload)
        assert mock_distribution_service.send_email.await_count == 2
        # Verify each document_id was sent
        calls = mock_distribution_service.send_email.call_args_list
        sent_doc_ids = [c.kwargs["document_id"] for c in calls]
        assert sent_doc_ids == ["a", "b"]


# ============================================================================
# SSRF PROTECTION TESTS
# ============================================================================


@pytest.fixture
def ssrf_client(mock_export_service, mock_distribution_service):
    """TestClient with real SSRF validation (no is_safe_external_url mock)."""
    from backend.app.api.middleware import limiter

    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/export")

    import backend.app.api.routes.export as _route_mod
    _orig_export = _route_mod.export_service
    _orig_distrib = _route_mod.distribution_service
    _route_mod.export_service = mock_export_service
    _route_mod.distribution_service = mock_distribution_service

    limiter.enabled = False
    yield TestClient(_app)
    limiter.enabled = True

    _route_mod.export_service = _orig_export
    _route_mod.distribution_service = _orig_distrib


class TestSSRFProtection:
    """Webhook URLs must be validated against SSRF attacks."""

    def test_webhook_rejects_localhost(self, ssrf_client):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "http://localhost/evil",
        }
        resp = ssrf_client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422

    def test_webhook_rejects_127_0_0_1(self, ssrf_client):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "http://127.0.0.1:8080/steal",
        }
        resp = ssrf_client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422

    def test_webhook_rejects_metadata_endpoint(self, ssrf_client):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "http://169.254.169.254/latest/meta-data/",
        }
        resp = ssrf_client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422

    def test_teams_rejects_localhost(self, ssrf_client):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "http://localhost:3000/teams",
        }
        resp = ssrf_client.post("/export/distribution/teams", json=payload)
        assert resp.status_code == 422

    def test_webhook_rejects_file_scheme(self, ssrf_client):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "file:///etc/passwd",
        }
        resp = ssrf_client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 422

    @patch(
        "socket.getaddrinfo",
        return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
    )
    def test_webhook_allows_valid_external_url(self, _mock_dns, ssrf_client, mock_distribution_service):
        payload = {
            "document_id": "doc-1",
            "webhook_url": "https://api.example.com/ingest",
        }
        resp = ssrf_client.post("/export/distribution/webhook", json=payload)
        assert resp.status_code == 200

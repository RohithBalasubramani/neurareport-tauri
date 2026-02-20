"""Comprehensive tests for backend.app.utils.errors and error_handlers.

Coverage layers:
  1. Unit tests — AppError/DomainError construction, attributes, inheritance
  2. Integration tests — FastAPI error handler end-to-end via TestClient
  3. Property-based — random codes/messages never crash error classes
  4. Failure injection — edge-case payloads, missing attributes
  5. Concurrency — not applicable (stateless exception types)
  6. Security / abuse — no internal detail leakage in generic handler
  7. Usability — realistic service error patterns
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.app.utils.errors import AppError, DomainError
from backend.app.api.error_handlers import (
    add_exception_handlers,
    app_error_handler,
    generic_error_handler,
    http_error_handler,
)


# ==========================================================================
# 1. UNIT TESTS — AppError
# ==========================================================================

class TestAppError:
    def test_basic_construction(self):
        err = AppError(code="not_found", message="Item not found", status_code=404)
        assert err.code == "not_found"
        assert err.message == "Item not found"
        assert err.status_code == 404
        assert err.detail is None

    def test_with_detail(self):
        err = AppError(code="validation", message="Bad input", status_code=422, detail="field X")
        assert err.detail == "field X"

    def test_default_status_code(self):
        err = AppError(code="bad_request", message="bad")
        assert err.status_code == 400

    def test_is_exception(self):
        err = AppError(code="err", message="test")
        assert isinstance(err, Exception)

    def test_str_representation(self):
        err = AppError(code="err", message="Something went wrong")
        assert "Something went wrong" in str(err)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(AppError) as exc_info:
            raise AppError(code="test_raise", message="raised", status_code=500)
        assert exc_info.value.code == "test_raise"
        assert exc_info.value.status_code == 500


class TestDomainError:
    def test_basic_construction(self):
        err = DomainError(code="domain_err", message="Domain issue")
        assert err.code == "domain_err"
        assert err.message == "Domain issue"
        assert err.status_code == 400
        assert err.detail is None

    def test_with_all_fields(self):
        err = DomainError(code="import_fail", message="Import failed", status_code=422, detail="line 5")
        assert err.code == "import_fail"
        assert err.status_code == 422
        assert err.detail == "line 5"

    def test_is_app_error(self):
        err = DomainError(code="x", message="y")
        assert isinstance(err, AppError)
        assert isinstance(err, Exception)

    def test_can_be_caught_as_app_error(self):
        with pytest.raises(AppError):
            raise DomainError(code="sub", message="subclass")

    def test_subclass_inherits(self):
        """Concrete domain errors can subclass DomainError."""
        from backend.app.services.templates.errors import TemplateImportError
        err = TemplateImportError(code="template_import", message="failed")
        assert isinstance(err, DomainError)
        assert isinstance(err, AppError)


# ==========================================================================
# 2. INTEGRATION TESTS — Error handlers via TestClient
# ==========================================================================

@pytest.fixture
def error_app():
    """FastAPI app with error handlers and test routes."""
    app = FastAPI()
    add_exception_handlers(app)

    @app.get("/raise-app-error")
    async def raise_app_error():
        raise AppError(code="test_code", message="Test message", status_code=409)

    @app.get("/raise-app-error-with-detail")
    async def raise_app_error_detail():
        raise AppError(code="validation_error", message="Invalid input", status_code=422, detail="field 'name' is required")

    @app.get("/raise-domain-error")
    async def raise_domain_error():
        raise DomainError(code="domain_issue", message="Domain problem", status_code=403)

    @app.get("/raise-http-exception")
    async def raise_http_exception():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/raise-http-exception-dict")
    async def raise_http_exception_dict():
        raise HTTPException(status_code=400, detail={"status": "error", "code": "custom", "message": "Custom error"})

    @app.get("/raise-unhandled")
    async def raise_unhandled():
        raise RuntimeError("Unexpected crash!")

    @app.get("/success")
    async def success():
        return {"ok": True}

    return app


@pytest.fixture
def error_client(error_app):
    return TestClient(error_app, raise_server_exceptions=False)


class TestAppErrorHandler:
    def test_app_error_response(self, error_client):
        resp = error_client.get("/raise-app-error")
        assert resp.status_code == 409
        body = resp.json()
        assert body["status"] == "error"
        assert body["code"] == "test_code"
        assert body["message"] == "Test message"
        assert "detail" not in body  # None detail omitted

    def test_app_error_with_detail(self, error_client):
        resp = error_client.get("/raise-app-error-with-detail")
        assert resp.status_code == 422
        body = resp.json()
        assert body["detail"] == "field 'name' is required"

    def test_domain_error_handled_as_app_error(self, error_client):
        resp = error_client.get("/raise-domain-error")
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "domain_issue"


class TestHTTPExceptionHandler:
    def test_http_exception_string_detail(self, error_client):
        resp = error_client.get("/raise-http-exception")
        assert resp.status_code == 404
        body = resp.json()
        assert body["status"] == "error"
        assert body["code"] == "http_404"
        assert body["message"] == "Not found"

    def test_http_exception_dict_detail(self, error_client):
        resp = error_client.get("/raise-http-exception-dict")
        assert resp.status_code == 400
        body = resp.json()
        assert body["status"] == "error"
        assert body["code"] == "custom"
        assert body["message"] == "Custom error"


class TestGenericErrorHandler:
    def test_unhandled_exception_returns_500(self, error_client):
        resp = error_client.get("/raise-unhandled")
        assert resp.status_code == 500
        body = resp.json()
        assert body["status"] == "error"
        assert body["code"] == "internal_error"

    def test_no_internal_details_leaked(self, error_client):
        resp = error_client.get("/raise-unhandled")
        body = resp.json()
        # Must NOT contain the actual exception message
        assert "Unexpected crash" not in body.get("message", "")
        assert "RuntimeError" not in str(body)

    def test_generic_message_is_user_friendly(self, error_client):
        resp = error_client.get("/raise-unhandled")
        body = resp.json()
        assert "unexpected error" in body["message"].lower()


class TestCorrelationIdPropagation:
    def test_correlation_id_in_app_error(self, error_app):
        """Correlation ID from request.state appears in error response."""
        @error_app.middleware("http")
        async def set_correlation_id(request: Request, call_next):
            request.state.correlation_id = "corr-12345"
            return await call_next(request)

        client = TestClient(error_app, raise_server_exceptions=False)
        resp = client.get("/raise-app-error")
        body = resp.json()
        assert body.get("correlation_id") == "corr-12345"

    def test_correlation_id_in_generic_error(self, error_app):
        @error_app.middleware("http")
        async def set_correlation_id(request: Request, call_next):
            request.state.correlation_id = "corr-99999"
            return await call_next(request)

        client = TestClient(error_app, raise_server_exceptions=False)
        resp = client.get("/raise-unhandled")
        body = resp.json()
        assert body.get("correlation_id") == "corr-99999"


# ==========================================================================
# 3. PROPERTY-BASED / FUZZ TESTS
# ==========================================================================

class TestPropertyBased:
    @given(
        code=st.text(min_size=1, max_size=100),
        message=st.text(min_size=1, max_size=500),
        status=st.integers(min_value=100, max_value=599),
    )
    @settings(max_examples=100)
    def test_app_error_never_crashes(self, code, message, status):
        err = AppError(code=code, message=message, status_code=status)
        assert err.code == code
        assert err.message == message
        assert err.status_code == status

    @given(
        code=st.text(min_size=1, max_size=100),
        message=st.text(min_size=1, max_size=500),
    )
    @settings(max_examples=100)
    def test_domain_error_never_crashes(self, code, message):
        err = DomainError(code=code, message=message)
        assert isinstance(err, AppError)


# ==========================================================================
# 4. FAILURE INJECTION — Edge-case payloads
# ==========================================================================

class TestEdgeCases:
    def test_empty_code(self):
        err = AppError(code="", message="empty code")
        assert err.code == ""

    def test_very_long_message(self):
        msg = "x" * 10000
        err = AppError(code="long", message=msg)
        assert len(err.message) == 10000

    def test_unicode_message(self):
        err = AppError(code="unicode", message="Fehler: Datei nicht gefunden 🇩🇪")
        assert "Fehler" in err.message

    def test_none_detail_not_in_dict(self, error_client):
        resp = error_client.get("/raise-app-error")
        body = resp.json()
        assert "detail" not in body

    def test_success_not_affected(self, error_client):
        resp = error_client.get("/success")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}


# ==========================================================================
# 6. SECURITY — No information leakage
# ==========================================================================

class TestSecurityLeakage:
    def test_traceback_not_in_response(self, error_client):
        resp = error_client.get("/raise-unhandled")
        body_str = resp.text
        assert "Traceback" not in body_str
        assert "raise_unhandled" not in body_str

    def test_file_paths_not_in_response(self, error_client):
        resp = error_client.get("/raise-unhandled")
        body_str = resp.text
        assert "backend/" not in body_str
        assert ".py" not in body_str


# ==========================================================================
# 7. USABILITY — Realistic patterns
# ==========================================================================

class TestRealisticPatterns:
    def test_not_found_pattern(self):
        err = AppError(code="connection_not_found", message="Connection not found", status_code=404)
        assert err.status_code == 404

    def test_unauthorized_pattern(self):
        err = AppError(code="unauthorized", message="Invalid API key", status_code=401)
        assert err.status_code == 401

    def test_validation_pattern(self):
        err = AppError(
            code="validation_error",
            message="SQL query is not read-only",
            status_code=400,
            detail="Query contains blocked keyword: DROP",
        )
        assert err.status_code == 400
        assert "DROP" in err.detail

    def test_conflict_pattern(self):
        err = AppError(code="duplicate_key", message="Connection already exists", status_code=409)
        assert err.status_code == 409

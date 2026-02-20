"""Health API Route Tests.

Comprehensive tests for health, readiness, liveness, and diagnostic endpoints.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.health import router


@pytest.fixture
def app():
    _app = FastAPI()
    _app.include_router(router)
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


# =============================================================================
# BASIC HEALTH / LIVENESS
# =============================================================================


class TestBasicHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_healthz_liveness_probe(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# =============================================================================
# READINESS PROBES
# =============================================================================


class TestReadiness:
    def test_ready_when_dirs_accessible(self, client):
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_check:
            mock_check.return_value = {"status": "healthy", "path": "/tmp/test", "writable": True}
            resp = client.get("/ready")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ready"

    def test_not_ready_when_dir_error(self, client):
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_check:
            mock_check.return_value = {"status": "error", "message": "Not accessible"}
            resp = client.get("/ready")
            data = resp.json()
            assert data["status"] == "not_ready"

    def test_readyz_alias(self, client):
        """readyz is alias for ready."""
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_check:
            mock_check.return_value = {"status": "healthy", "path": "/tmp", "writable": True}
            resp = client.get("/readyz")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ready"


# =============================================================================
# TOKEN USAGE
# =============================================================================


class TestTokenUsage:
    def test_token_usage_returns_stats(self, client):
        mock_stats = {
            "total_input_tokens": 500,
            "total_output_tokens": 300,
            "total_tokens": 800,
            "estimated_cost_usd": 0.02,
            "request_count": 10,
        }
        with patch("backend.app.api.routes.health.get_global_usage_stats",
                    return_value=mock_stats, create=True):
            # The endpoint imports lazily, so patch the import path
            with patch.dict("sys.modules", {
                "backend.app.services.llm.client": MagicMock(
                    get_global_usage_stats=MagicMock(return_value=mock_stats)
                )
            }):
                resp = client.get("/health/token-usage")
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] in ("ok", "error")

    def test_token_usage_handles_error(self, client):
        with patch.dict("sys.modules", {
            "backend.app.services.llm.client": MagicMock(
                get_global_usage_stats=MagicMock(side_effect=Exception("no stats"))
            )
        }):
            resp = client.get("/health/token-usage")
            assert resp.status_code == 200
            data = resp.json()
            # Even on error, returns a response with usage defaults
            assert "usage" in data


# =============================================================================
# DETAILED HEALTH
# =============================================================================


class TestDetailedHealth:
    def test_detailed_returns_checks(self, client):
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.excel_uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()
        mock_settings.openai_api_key = "sk-test123"
        mock_settings.api_key = "test-key"
        mock_settings.rate_limit_enabled = True
        mock_settings.rate_limit_requests = 100
        mock_settings.rate_limit_window_seconds = 60
        mock_settings.request_timeout_seconds = 30
        mock_settings.max_upload_bytes = 10 * 1024 * 1024
        mock_settings.max_zip_entries = 100
        mock_settings.max_zip_uncompressed_bytes = 500 * 1024 * 1024
        mock_settings.template_import_max_concurrency = 4
        mock_settings.analysis_max_concurrency = 8
        mock_settings.debug_mode = False
        mock_settings.api_version = "1.0.0"

        mock_cache = MagicMock()
        mock_cache.size.return_value = 5
        mock_cache.max_items = 100
        mock_cache.ttl_seconds = 300

        mock_state_store = MagicMock()
        mock_state_store.backend_name = "sqlite"
        mock_state_store.backend_fallback = False

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_dir, \
             patch("backend.app.api.routes.health._check_openai_connection") as mock_openai, \
             patch("backend.app.api.routes.health._analysis_cache", return_value=mock_cache), \
             patch("backend.app.api.routes.health._get_memory_usage") as mock_mem, \
             patch("backend.app.api.routes.health.state_access") as mock_sa:

            mock_dir.return_value = {"status": "healthy", "path": "/tmp", "writable": True}
            mock_openai.return_value = {"status": "configured", "message": "OK"}
            mock_mem.return_value = {"status": "healthy", "rss_mb": 50.0}
            mock_sa.get_state_store.return_value = mock_state_store

            resp = client.get("/health/detailed")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert "checks" in data
            assert "uploads_dir" in data["checks"]
            assert "openai" in data["checks"]
            assert "analysis_cache" in data["checks"]
            assert "memory" in data["checks"]
            assert "configuration" in data["checks"]
            assert data["version"] == "1.0.0"

    def test_detailed_degraded_with_issues(self, client):
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.excel_uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()
        mock_settings.openai_api_key = None
        mock_settings.api_key = None
        mock_settings.rate_limit_enabled = False
        mock_settings.rate_limit_requests = 100
        mock_settings.rate_limit_window_seconds = 60
        mock_settings.request_timeout_seconds = 30
        mock_settings.max_upload_bytes = 10 * 1024 * 1024
        mock_settings.max_zip_entries = 100
        mock_settings.max_zip_uncompressed_bytes = 500 * 1024 * 1024
        mock_settings.template_import_max_concurrency = 4
        mock_settings.analysis_max_concurrency = 8
        mock_settings.debug_mode = False
        mock_settings.api_version = "1.0.0"

        mock_cache = MagicMock()
        mock_cache.size.return_value = 0
        mock_cache.max_items = 100
        mock_cache.ttl_seconds = 300

        mock_state_store = MagicMock()

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_dir, \
             patch("backend.app.api.routes.health._check_openai_connection") as mock_openai, \
             patch("backend.app.api.routes.health._analysis_cache", return_value=mock_cache), \
             patch("backend.app.api.routes.health._get_memory_usage") as mock_mem, \
             patch("backend.app.api.routes.health.state_access") as mock_sa:

            # Uploads dir is broken
            def dir_check(path):
                if path == mock_settings.uploads_dir:
                    return {"status": "error", "message": "Not accessible"}
                return {"status": "healthy", "path": "/tmp", "writable": True}

            mock_dir.side_effect = dir_check
            mock_openai.return_value = {"status": "error", "message": "API error"}
            mock_mem.return_value = {"status": "healthy"}
            mock_sa.get_state_store.return_value = mock_state_store

            resp = client.get("/health/detailed")
            data = resp.json()
            assert data["status"] == "degraded"
            assert len(data["issues"]) >= 1


# =============================================================================
# EMAIL HEALTH
# =============================================================================


class TestEmailHealth:
    def test_email_configured(self, client):
        mock_config = MagicMock()
        mock_config.enabled = True
        mock_config.host = "smtp.example.com"
        mock_config.sender = "noreply@example.com"
        mock_config.username = "user"
        mock_config.password = "pass"
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config):
            resp = client.get("/health/email")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert data["email"]["enabled"] is True

    def test_email_not_configured(self, client):
        mock_config = MagicMock()
        mock_config.enabled = False
        mock_config.host = ""
        mock_config.sender = ""
        mock_config.username = ""
        mock_config.password = ""
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config):
            resp = client.get("/health/email")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "warning"

    def test_email_connection_test_skipped(self, client):
        mock_config = MagicMock()
        mock_config.enabled = False
        mock_config.host = ""
        mock_config.sender = ""
        mock_config.username = ""
        mock_config.password = ""
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config):
            resp = client.get("/health/email/test")
            assert resp.status_code == 200
            data = resp.json()
            assert data["connection_test"]["status"] == "skipped"

    def test_email_refresh(self, client):
        mock_config = MagicMock()
        mock_config.enabled = False
        mock_config.host = ""
        mock_config.sender = ""
        mock_config.username = ""
        mock_config.password = ""
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config), \
             patch("backend.app.api.routes.health.refresh_mailer_config") as mock_refresh:
            resp = client.post("/health/email/refresh")
            assert resp.status_code == 200
            assert resp.json()["message"] == "Email configuration refreshed"
            mock_refresh.assert_called_once()


# =============================================================================
# SCHEDULER HEALTH
# =============================================================================


class TestSchedulerHealth:
    def test_scheduler_disabled(self, client):
        with patch.dict(os.environ, {"NEURA_SCHEDULER_DISABLED": "true"}):
            with patch("backend.app.api.routes.health.state_access") as mock_sa:
                mock_sa.list_schedules.return_value = []
                resp = client.get("/health/scheduler")
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "disabled"
                assert data["scheduler"]["enabled"] is False

    def test_scheduler_enabled_not_running(self, client):
        with patch.dict(os.environ, {"NEURA_SCHEDULER_DISABLED": "false"}, clear=False):
            with patch("backend.app.api.routes.health.state_access") as mock_sa:
                mock_sa.list_schedules.return_value = []
                resp = client.get("/health/scheduler")
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "warning"
                assert data["scheduler"]["running"] is False

    def test_scheduler_with_schedules(self, client):
        from datetime import datetime, timezone, timedelta
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        with patch.dict(os.environ, {"NEURA_SCHEDULER_DISABLED": "false"}, clear=False):
            with patch("backend.app.api.routes.health.state_access") as mock_sa:
                mock_sa.list_schedules.return_value = [
                    {"active": True, "next_run_at": future, "name": "Daily Report"},
                    {"active": False, "next_run_at": None, "name": "Disabled Job"},
                ]
                resp = client.get("/health/scheduler")
                assert resp.status_code == 200
                data = resp.json()
                assert data["schedules"]["total"] == 2
                assert data["schedules"]["active"] == 1
                assert data["schedules"]["next_run"]["schedule_name"] == "Daily Report"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


class TestHelperFunctions:
    def test_check_directory_access_healthy(self, tmp_path):
        from backend.app.api.routes.health import _check_directory_access
        result = _check_directory_access(tmp_path)
        assert result["status"] == "healthy"
        assert result["writable"] is True

    def test_check_directory_access_not_exists(self, tmp_path):
        from backend.app.api.routes.health import _check_directory_access
        result = _check_directory_access(tmp_path / "nonexistent")
        assert result["status"] == "warning"
        assert "does not exist" in result["message"]

    def test_check_directory_access_not_directory(self, tmp_path):
        from backend.app.api.routes.health import _check_directory_access
        file_path = tmp_path / "file.txt"
        file_path.write_text("hello")
        result = _check_directory_access(file_path)
        assert result["status"] == "error"
        assert "not a directory" in result["message"]

    def test_check_openai_not_configured(self):
        from backend.app.api.routes.health import _check_openai_connection
        mock_settings = MagicMock()
        mock_settings.openai_api_key = ""
        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings):
            result = _check_openai_connection()
            assert result["status"] == "not_configured"

    def test_check_openai_configured(self):
        from backend.app.api.routes.health import _check_openai_connection
        mock_settings = MagicMock()
        mock_settings.openai_api_key = "sk-test-key-1234567890"
        mock_client = MagicMock()
        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.services.templates.TemplateVerify.get_openai_client", return_value=mock_client):
            result = _check_openai_connection()
            assert result["status"] == "configured"
            assert result["message"] == "OpenAI client initialized"

    def test_check_email_config_enabled(self):
        from backend.app.api.routes.health import _check_email_config
        mock_config = MagicMock()
        mock_config.enabled = True
        mock_config.host = "smtp.example.com"
        mock_config.sender = "noreply@example.com"
        mock_config.username = "user"
        mock_config.password = "pass"
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config):
            result = _check_email_config()
            assert result["status"] == "configured"
            assert result["enabled"] is True
            assert "nor***@example.com" in result["sender_masked"]

    def test_check_email_config_disabled(self):
        from backend.app.api.routes.health import _check_email_config
        mock_config = MagicMock()
        mock_config.enabled = False
        mock_config.host = ""
        mock_config.sender = ""
        mock_config.username = ""
        mock_config.password = ""
        mock_config.use_tls = True
        mock_config.port = 587

        with patch("backend.app.api.routes.health.MAILER_CONFIG", mock_config):
            result = _check_email_config()
            assert result["status"] == "not_configured"
            assert "missing_env_vars" in result

    def test_memory_usage(self):
        from backend.app.api.routes.health import _get_memory_usage
        result = _get_memory_usage()
        assert result["status"] in ("healthy", "unknown")


# =============================================================================
# SECURITY TESTS
# =============================================================================


class TestDetailedHealthSecurity:
    """Tests that /health/detailed requires auth and doesn't leak secrets."""

    def test_detailed_has_auth_dependency(self):
        """Verify /health/detailed has require_api_key wired as dependency."""
        from backend.app.services.security import require_api_key as _rk
        # Find the /health/detailed route
        for route in router.routes:
            if hasattr(route, "path") and route.path == "/health/detailed":
                dep_callables = [d.dependency for d in route.dependencies]
                assert _rk in dep_callables
                return
        pytest.fail("Route /health/detailed not found")

    def test_detailed_no_raw_paths_leaked(self, client):
        """Directory checks should not contain raw filesystem paths."""
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.excel_uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()
        mock_settings.openai_api_key = "sk-test"
        mock_settings.api_key = "test-key"
        mock_settings.rate_limit_enabled = True
        mock_settings.rate_limit_requests = 100
        mock_settings.rate_limit_window_seconds = 60
        mock_settings.request_timeout_seconds = 30
        mock_settings.max_upload_bytes = 10 * 1024 * 1024
        mock_settings.api_version = "1.0.0"

        mock_cache = MagicMock()
        mock_cache.size.return_value = 5
        mock_cache.max_items = 100
        mock_cache.ttl_seconds = 300

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_dir, \
             patch("backend.app.api.routes.health._check_openai_connection") as mock_openai, \
             patch("backend.app.api.routes.health._analysis_cache", return_value=mock_cache), \
             patch("backend.app.api.routes.health._get_memory_usage") as mock_mem:

            mock_dir.return_value = {"status": "healthy", "path": "/secret/path", "writable": True}
            mock_openai.return_value = {"status": "configured", "message": "OK"}
            mock_mem.return_value = {"status": "healthy"}

            # Override auth for this test
            from backend.app.services.security import require_api_key as _rk
            auth_app = FastAPI()
            auth_app.dependency_overrides[_rk] = lambda: None
            auth_app.include_router(router)
            auth_client = TestClient(auth_app)

            resp = auth_client.get("/health/detailed")
            assert resp.status_code == 200
            data = resp.json()

            # Directory checks should be redacted (no "path" key)
            for dir_key in ("uploads_dir", "state_dir", "excel_uploads_dir"):
                if dir_key in data["checks"]:
                    assert "path" not in data["checks"][dir_key]

    def test_detailed_no_api_key_prefix_leaked(self, client):
        """OpenAI check should NOT include key_prefix."""
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.excel_uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()
        mock_settings.openai_api_key = "sk-test123"
        mock_settings.api_key = "test-key"
        mock_settings.rate_limit_enabled = True
        mock_settings.rate_limit_requests = 100
        mock_settings.rate_limit_window_seconds = 60
        mock_settings.request_timeout_seconds = 30
        mock_settings.max_upload_bytes = 10 * 1024 * 1024
        mock_settings.api_version = "1.0.0"

        mock_cache = MagicMock()
        mock_cache.size.return_value = 0
        mock_cache.max_items = 100
        mock_cache.ttl_seconds = 300

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_dir, \
             patch("backend.app.api.routes.health._check_openai_connection") as mock_openai, \
             patch("backend.app.api.routes.health._analysis_cache", return_value=mock_cache), \
             patch("backend.app.api.routes.health._get_memory_usage") as mock_mem:

            mock_dir.return_value = {"status": "healthy", "path": "/tmp", "writable": True}
            mock_openai.return_value = {"status": "configured", "message": "OK"}
            mock_mem.return_value = {"status": "healthy"}

            from backend.app.services.security import require_api_key as _rk
            auth_app = FastAPI()
            auth_app.dependency_overrides[_rk] = lambda: None
            auth_app.include_router(router)
            auth_client = TestClient(auth_app)

            resp = auth_client.get("/health/detailed")
            data = resp.json()
            openai_check = data["checks"].get("openai", {})
            assert "key_prefix" not in openai_check

    def test_detailed_no_debug_mode_in_config(self, client):
        """Configuration should not expose debug_mode."""
        mock_settings = MagicMock()
        mock_settings.uploads_dir = MagicMock()
        mock_settings.excel_uploads_dir = MagicMock()
        mock_settings.state_dir = MagicMock()
        mock_settings.openai_api_key = "sk-test"
        mock_settings.api_key = "test-key"
        mock_settings.rate_limit_enabled = True
        mock_settings.rate_limit_requests = 100
        mock_settings.rate_limit_window_seconds = 60
        mock_settings.request_timeout_seconds = 30
        mock_settings.max_upload_bytes = 10 * 1024 * 1024
        mock_settings.debug_mode = True
        mock_settings.api_version = "1.0.0"

        mock_cache = MagicMock()
        mock_cache.size.return_value = 0
        mock_cache.max_items = 100
        mock_cache.ttl_seconds = 300

        with patch("backend.app.api.routes.health.get_settings", return_value=mock_settings), \
             patch("backend.app.api.routes.health._check_directory_access") as mock_dir, \
             patch("backend.app.api.routes.health._check_openai_connection") as mock_openai, \
             patch("backend.app.api.routes.health._analysis_cache", return_value=mock_cache), \
             patch("backend.app.api.routes.health._get_memory_usage") as mock_mem:

            mock_dir.return_value = {"status": "healthy", "path": "/tmp", "writable": True}
            mock_openai.return_value = {"status": "configured", "message": "OK"}
            mock_mem.return_value = {"status": "healthy"}

            from backend.app.services.security import require_api_key as _rk
            auth_app = FastAPI()
            auth_app.dependency_overrides[_rk] = lambda: None
            auth_app.include_router(router)
            auth_client = TestClient(auth_app)

            resp = auth_client.get("/health/detailed")
            config = resp.json()["checks"].get("configuration", {})
            assert "debug_mode" not in config
            assert "state_backend" not in config

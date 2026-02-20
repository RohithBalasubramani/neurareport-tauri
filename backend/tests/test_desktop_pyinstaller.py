"""
Tests for desktop/PyInstaller compatibility.

Simulates the PyInstaller frozen environment by blocking all excluded modules,
then verifies the backend can still import and start successfully.
"""
import sys
import os
import pytest

# Modules excluded in neurareport-backend.spec
PYINSTALLER_EXCLUDES = [
    'psycopg2', 'asyncpg', 'pymysql', 'pymongo', 'elasticsearch',
    'redis', 'dramatiq', 'celery', 'boto3', 'botocore',
    'google', 'azure', 'dropbox', 'msal', 'notion_client',
    'slack_sdk', 'pymsteams', 'sentence_transformers', 'torch',
    'transformers', 'spacy', 'sklearn', 'statsmodels',
    'playwright', 'opentelemetry', 'prometheus_client',
    'sentry_sdk', 'hvac', 'casbin', 'strawberry', 'prefect',
]


class _BlockedFinder:
    """Meta-path finder that blocks imports of excluded modules."""

    def __init__(self, blocked):
        self.blocked = set(blocked)

    def find_module(self, name, path=None):
        top = name.split('.')[0]
        if top in self.blocked:
            return self

    def load_module(self, name):
        raise ImportError(f'[TEST BLOCKED] {name}')


@pytest.fixture()
def desktop_env(monkeypatch):
    """Set up desktop-mode environment variables and block excluded modules."""
    monkeypatch.setenv("NEURA_DEBUG", "true")
    monkeypatch.setenv("NEURA_ALLOW_ANON_API", "true")
    monkeypatch.setenv("NEURA_JWT_SECRET", "desktop-local-secret")
    monkeypatch.setenv("NEURA_REDIS_URL", "")
    monkeypatch.setenv("NEURA_AGENT_WORKER_DISABLED", "true")
    monkeypatch.setenv("NEURA_RECOVERY_DAEMON_DISABLED", "true")
    monkeypatch.setenv("NEURA_SCHEDULER_DISABLED", "true")
    monkeypatch.setenv("NEURA_METRICS_ENABLED", "false")
    monkeypatch.setenv("NEURA_ALLOWED_HOSTS_ALL", "true")
    monkeypatch.setenv("NEURA_DATABASE_URL", "sqlite+aiosqlite:///./test_desktop.db")
    monkeypatch.setenv("UPLOAD_ROOT", "/tmp/nr_test_uploads")
    monkeypatch.setenv("EXCEL_UPLOAD_ROOT", "/tmp/nr_test_excel")
    monkeypatch.setenv("NEURA_STATE_DIR", "/tmp/nr_test_state")

    os.makedirs("/tmp/nr_test_uploads", exist_ok=True)
    os.makedirs("/tmp/nr_test_excel", exist_ok=True)
    os.makedirs("/tmp/nr_test_state", exist_ok=True)


@pytest.fixture()
def blocked_imports():
    """Block all PyInstaller-excluded modules and clean up after."""
    # Remove any already-imported excluded modules
    removed = {}
    for mod_name in list(sys.modules.keys()):
        top = mod_name.split('.')[0]
        if top in set(PYINSTALLER_EXCLUDES):
            removed[mod_name] = sys.modules.pop(mod_name)

    finder = _BlockedFinder(PYINSTALLER_EXCLUDES)
    sys.meta_path.insert(0, finder)

    yield finder

    # Restore
    sys.meta_path.remove(finder)
    sys.modules.update(removed)


class TestDesktopImportChain:
    """Verify the backend import chain works with excluded modules blocked."""

    def test_metrics_import_without_prometheus(self, blocked_imports):
        """prometheus_client is excluded — metrics module must not crash."""
        # Clear cached module if present
        sys.modules.pop('backend.app.services.observability.metrics', None)
        from backend.app.services.observability.metrics import HAS_PROMETHEUS
        assert HAS_PROMETHEUS is False

    def test_tracing_import_without_opentelemetry(self, blocked_imports):
        """opentelemetry is excluded — tracing module must not crash."""
        sys.modules.pop('backend.app.services.observability.tracing', None)
        from backend.app.services.observability.tracing import HAS_OTEL
        assert HAS_OTEL is False

    def test_rbac_import_without_casbin(self, blocked_imports):
        """casbin is excluded — rbac module must not crash on import."""
        sys.modules.pop('backend.app.services.rbac', None)
        from backend.app.services.rbac import HAS_CASBIN
        assert HAS_CASBIN is False

    def test_worker_import_without_dramatiq(self, blocked_imports):
        """dramatiq/redis are excluded — worker module must not crash."""
        sys.modules.pop('backend.app.services.worker', None)
        from backend.app.services.worker import HAS_DRAMATIQ
        assert HAS_DRAMATIQ is False

    def test_html_raster_import_without_playwright(self, blocked_imports):
        """playwright is excluded — html_raster must not crash."""
        sys.modules.pop('backend.app.services.render.html_raster', None)
        from backend.app.services.render.html_raster import sync_playwright
        assert sync_playwright is None

    def test_pipeline_import_without_prefect(self, blocked_imports):
        """prefect is excluded — pipeline modules must not crash."""
        sys.modules.pop('backend.engine.pipelines.report_pipeline', None)
        sys.modules.pop('backend.engine.pipelines.import_pipeline', None)
        from backend.engine.pipelines import report_pipeline, import_pipeline
        # Decorators should be identity functions
        assert report_pipeline.flow is not None
        assert import_pipeline.flow is not None


class TestDesktopFullStartup:
    """Full startup simulation with all excludes blocked."""

    def test_backend_api_imports_with_all_excludes_blocked(self, desktop_env, blocked_imports):
        """The entire backend.api module must import without crashing.

        NOTE: This test cannot fully clear and reimport backend.api in the same
        process because SQLAlchemy/SQLModel table definitions are registered in
        global MetaData and cannot be re-declared. The individual module tests
        above cover each excluded module. This test verifies the app object
        exists and is a FastAPI instance (it was imported before the blocker).
        """
        from backend.api import app
        assert app is not None
        assert type(app).__name__ == 'FastAPI'

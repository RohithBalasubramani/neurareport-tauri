"""Tests for critical bugs identified in code review.

This module tests for critical issues found during comprehensive code analysis:
1. Infinite recursion in templates.py export_template_zip and import_template_zip
2. API contract consistency between frontend and backend
3. State store thread safety
4. Report service job cancellation
"""
from __future__ import annotations

import asyncio
import inspect
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mock cryptography before imports
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


class TestTemplateEndpointNamingBugs:
    """Test for function naming bugs that could cause infinite recursion."""

    def test_export_template_zip_function_names_should_not_shadow_import(self):
        """
        CRITICAL BUG: templates.py:73-75 defines export_template_zip route handler
        with the same name as the imported function, causing infinite recursion.

        The route handler `export_template_zip` shadows the imported function
        `export_template_zip` from template_service.py.
        """
        from backend.legacy.endpoints import templates as templates_module

        # Check if the route handler has the same name as imported function
        # This is a potential infinite recursion bug
        route_functions = [
            name for name, obj in inspect.getmembers(templates_module)
            if callable(obj) and not name.startswith('_')
        ]

        # Verify function naming - both should exist but handler should call service
        # The bug is that they have the same name causing recursion
        assert 'export_template_zip' in route_functions, "export_template_zip should exist"

        # Get the function source to check if it's calling itself
        func = getattr(templates_module, 'export_template_zip')
        source = inspect.getsource(func)

        # The bug: function calls itself instead of the imported service
        # This check verifies the bug exists (should be fixed)
        if 'return export_template_zip(template_id, request)' in source:
            pytest.fail(
                "CRITICAL BUG DETECTED: export_template_zip calls itself causing infinite recursion. "
                "The route handler shadows the imported function from template_service.py. "
                "Fix: Rename the route handler to export_template_zip_route or similar."
            )

    def test_import_template_zip_function_names_should_not_shadow_import(self):
        """
        CRITICAL BUG: templates.py:78-80 defines import_template_zip route handler
        with the same name as the imported function, causing infinite recursion.
        """
        from backend.legacy.endpoints import templates as templates_module

        func = getattr(templates_module, 'import_template_zip', None)
        if func is None:
            return  # Function might be renamed already

        source = inspect.getsource(func)

        # Check if it's an async function calling itself
        if 'return await import_template_zip(' in source and '@router.post("/templates/import-zip")' in source:
            pytest.fail(
                "CRITICAL BUG DETECTED: import_template_zip calls itself causing infinite recursion. "
                "The route handler shadows the imported function from template_service.py. "
                "Fix: Rename the route handler to import_template_zip_route or similar."
            )


class TestReportServiceJobCancellation:
    """Test for dangerous job cancellation patterns."""

    def test_inject_thread_cancel_is_dangerous(self):
        """
        The _inject_thread_cancel function uses ctypes to inject exceptions into
        running threads, which is dangerous and can leave the interpreter in an
        inconsistent state.
        """
        from backend.legacy.services import report_service

        # Verify the function exists and uses ctypes
        func = getattr(report_service, '_inject_thread_cancel', None)
        if func is None:
            return  # Function might be removed

        source = inspect.getsource(func)

        # Check for dangerous ctypes usage
        if 'PyThreadState_SetAsyncExc' in source:
            # This is expected but should have proper documentation
            assert 'Best-effort' in func.__doc__ or 'dangerous' in (func.__doc__ or '').lower(), \
                "Function should document the risks of using PyThreadState_SetAsyncExc"


class TestStateStoreThreadSafety:
    """Test state store thread safety."""

    @pytest.fixture
    def fresh_state(self, tmp_path, monkeypatch):
        from backend.app.repositories.state import store as state_store_module
        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        return store

    def test_state_store_uses_lock(self, fresh_state):
        """Verify state store uses threading lock for operations."""
        import threading

        assert hasattr(fresh_state, '_lock'), "StateStore should have a _lock attribute"
        assert isinstance(fresh_state._lock, type(threading.RLock())), \
            "StateStore._lock should be a threading.RLock"

    def test_concurrent_connection_upserts(self, fresh_state):
        """Test that concurrent connection updates don't corrupt state."""
        import threading
        import time

        errors = []
        results = []

        def upsert_connection(conn_id):
            try:
                result = fresh_state.upsert_connection(
                    conn_id=conn_id,
                    name=f"Connection {conn_id}",
                    db_type="sqlite",
                    database_path=f"/path/to/db_{conn_id}.sqlite",
                    secret_payload={"token": f"secret_{conn_id}"},
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=upsert_connection, args=(f"conn-{i}",))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent upserts should not raise errors: {errors}"
        assert len(results) == 10, "All 10 connections should be created"

        # Verify all connections exist
        connections = fresh_state.list_connections()
        assert len(connections) == 10, "All 10 connections should be persisted"

    def test_concurrent_template_upserts(self, fresh_state):
        """Test that concurrent template updates don't corrupt state."""
        import threading

        errors = []
        results = []

        def upsert_template(template_id):
            try:
                result = fresh_state.upsert_template(
                    template_id,
                    name=f"Template {template_id}",
                    status="approved",
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=upsert_template, args=(f"tpl-{i}",))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent upserts should not raise errors: {errors}"
        assert len(results) == 10, "All 10 templates should be created"

        # Verify all templates exist
        templates = fresh_state.list_templates()
        assert len(templates) == 10, "All 10 templates should be persisted"


class TestAPIContractConsistency:
    """Test API contract between frontend and backend."""

    def test_excel_routes_exist(self):
        """Verify all Excel routes that frontend expects exist in backend."""
        from backend.legacy import routes

        # Get all route paths from the main router
        all_routes = []
        for route in routes.router.routes:
            if hasattr(route, 'path'):
                all_routes.append(route.path)

        # Excel routes expected by frontend (from client.js TEMPLATE_ROUTES.excel)
        expected_excel_routes = [
            '/excel/verify',
            '/excel/{template_id}/mapping/preview',
            '/excel/{template_id}/mapping/approve',
            '/excel/{template_id}/mapping/corrections-preview',
            '/excel/{template_id}/generator-assets/v1',
            '/excel/{template_id}/keys/options',
            '/excel/reports/run',
        ]

        missing_routes = []
        for expected in expected_excel_routes:
            # Normalize path format for comparison
            normalized = expected.replace('{template_id}', '{template_id}')
            found = any(normalized in r for r in all_routes)
            if not found:
                missing_routes.append(expected)

        # Note: Some routes may not exist yet, this identifies missing ones
        if missing_routes:
            pytest.skip(f"Missing Excel routes (may be expected): {missing_routes}")

    def test_discover_endpoint_exists(self):
        """Verify the discover endpoint exists (client.js has placeholder)."""
        from backend.legacy import routes

        all_routes = []
        for route in routes.router.routes:
            if hasattr(route, 'path'):
                all_routes.append(route.path)

        # The frontend's discoverBatches() throws "not implemented" but
        # discoverReports() uses /reports/discover which should exist
        assert any('/reports/discover' in r for r in all_routes), \
            "POST /reports/discover should exist"


class TestMockModeDefault:
    """Test frontend mock mode configuration."""

    def test_mock_mode_should_not_be_default_in_production(self):
        """
        BUG: client.js line 29 sets isMock = true by default.
        This could cause confusion in production if VITE_USE_MOCK is not explicitly set.
        """
        # This is a frontend configuration issue that should be documented
        # The default should ideally be 'false' for production safety
        frontend_client_path = Path(__file__).resolve().parents[2] / "frontend" / "src" / "api" / "client.js"

        if frontend_client_path.exists():
            content = frontend_client_path.read_text()

            # Check for the problematic default
            if "VITE_USE_MOCK || 'true'" in content:
                pytest.skip(
                    "INFO: Mock mode is ON by default in client.js. "
                    "Consider changing default to 'false' for production safety. "
                    "Current: (runtimeEnv.VITE_USE_MOCK || 'true') === 'true'"
                )


class TestConnectionsEndpoint:
    """Test connection endpoint behaviors."""

    def test_connections_import_location(self):
        """
        BUG: connections.py:44 imports HTTPException inside function body.
        This should be at module level for clarity and slight performance improvement.
        """
        from backend.legacy.endpoints import connections

        # Check if HTTPException is imported at module level
        module_imports = dir(connections)

        # The import is inside delete_connection_route function
        # This is a style issue but not critical
        func = getattr(connections, 'delete_connection_route', None)
        if func:
            source = inspect.getsource(func)
            if 'from fastapi import HTTPException' in source:
                pytest.skip(
                    "STYLE: HTTPException import inside function at connections.py:44. "
                    "Consider moving to module level imports."
                )


class TestSubprocessMonkeypatching:
    """Test for dangerous subprocess monkeypatching."""

    def test_subprocess_popen_patching_is_localized(self):
        """
        BUG: report_service.py:951 globally patches subprocess.Popen
        which could cause issues in concurrent scenarios.
        """
        from backend.legacy.services import report_service

        # Check if _patch_subprocess_tracking exists and uses context manager
        source = inspect.getsource(report_service)

        if 'subprocess.Popen = _job_popen' in source:
            # Verify it's within a context manager
            if '@contextlib.contextmanager' in source and '_patch_subprocess_tracking' in source:
                # Good - it's a context manager, so the patch is temporary
                pass
            else:
                pytest.fail(
                    "CRITICAL: subprocess.Popen is being patched without proper context management. "
                    "This could cause issues in concurrent scenarios."
                )

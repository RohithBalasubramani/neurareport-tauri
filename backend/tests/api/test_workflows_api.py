"""Workflow API Route Tests.

Tests for authentication, route path ordering, and exception handling.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.workflows import router
from backend.app.services.security import require_api_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_workflow_service():
    svc = AsyncMock()
    svc.get_pending_approvals = AsyncMock(return_value=[])
    svc.get_execution = AsyncMock(return_value=None)
    svc.approve_execution = AsyncMock(return_value=None)
    svc.get_workflow = AsyncMock(return_value=None)
    svc.list_workflows = AsyncMock(return_value=([], 0))
    svc.create_workflow = AsyncMock()
    svc.update_workflow = AsyncMock(return_value=None)
    svc.delete_workflow = AsyncMock(return_value=False)
    svc.execute_workflow = AsyncMock()
    svc.list_executions = AsyncMock(return_value=[])
    return svc


@pytest.fixture
def app_with_auth():
    """App WITHOUT auth override — tests that auth is required."""
    _app = FastAPI()
    _app.include_router(router, prefix="/workflows")
    return _app


@pytest.fixture
def app(mock_workflow_service):
    """App with auth overridden and mocked service."""
    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/workflows")

    import backend.app.api.routes.workflows as mod
    original = mod.workflow_service
    mod.workflow_service = mock_workflow_service
    yield _app
    mod.workflow_service = original


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def client_no_auth(app_with_auth):
    return TestClient(app_with_auth)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


class TestWorkflowAuth:
    """Workflow routes have API key authentication wired up."""

    def test_router_has_auth_dependency(self):
        """Verify the router declares require_api_key as a dependency."""
        from backend.app.api.routes.workflows import router as wf_router
        dep_callables = [d.dependency for d in wf_router.dependencies]
        assert require_api_key in dep_callables


# ---------------------------------------------------------------------------
# Route path conflict (static vs parameterized)
# ---------------------------------------------------------------------------


class TestRoutePathConflict:
    """Static-prefix routes must resolve before parameterized /{workflow_id}."""

    def test_pending_approvals_not_captured_by_workflow_id(self, client, mock_workflow_service):
        """GET /workflows/approvals/pending should hit the approvals endpoint,
        NOT be interpreted as GET /workflows/{workflow_id} with workflow_id='approvals'."""
        mock_workflow_service.get_pending_approvals.return_value = [
            {"id": "approval-1", "status": "pending"}
        ]
        resp = client.get("/workflows/approvals/pending")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        mock_workflow_service.get_pending_approvals.assert_awaited_once()

    def test_execution_not_captured_by_workflow_id(self, client, mock_workflow_service):
        """GET /workflows/executions/{id} should hit the execution endpoint."""
        mock_workflow_service.get_execution.return_value = {
            "id": "exec-1",
            "workflow_id": "wf-1",
            "status": "completed",
            "input_data": {},
            "output_data": None,
            "node_results": [],
            "error": None,
            "started_at": "2025-01-01T00:00:00Z",
            "finished_at": None,
        }
        resp = client.get("/workflows/executions/exec-1")
        assert resp.status_code == 200
        mock_workflow_service.get_execution.assert_awaited_once_with("exec-1")


# ---------------------------------------------------------------------------
# Exception handling
# ---------------------------------------------------------------------------


class TestWorkflowExceptionHandling:
    """Execute workflow should return generic 500 on unexpected errors."""

    def test_execute_value_error_returns_404(self, client, mock_workflow_service):
        mock_workflow_service.execute_workflow.side_effect = ValueError("Workflow not found")
        resp = client.post(
            "/workflows/wf-1/execute",
            json={"input_data": {}, "async_execution": False},
        )
        assert resp.status_code == 404

    def test_execute_unexpected_error_returns_500(self, client, mock_workflow_service):
        mock_workflow_service.execute_workflow.side_effect = RuntimeError("Unexpected crash")
        resp = client.post(
            "/workflows/wf-1/execute",
            json={"input_data": {}, "async_execution": False},
        )
        assert resp.status_code == 500
        detail = resp.json()["detail"]
        # Should NOT leak the raw exception message
        assert "Unexpected crash" not in detail
        assert "internal error" in detail.lower()

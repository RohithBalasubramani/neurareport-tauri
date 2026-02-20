"""Tests for observability module (OpenTelemetry + Prometheus)."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.services.observability import init_observability, init_metrics


class TestPrometheusMetrics:
    """Test Prometheus metrics endpoint."""

    def test_metrics_endpoint_created(self):
        app = FastAPI()
        result = init_metrics(app, enabled=True)
        assert result is True

        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "neurareport_build_info" in response.text

    def test_metrics_disabled(self):
        app = FastAPI()
        result = init_metrics(app, enabled=False)
        assert result is False

    def test_metrics_stored_on_app_state(self):
        app = FastAPI()
        init_metrics(app, enabled=True)
        assert hasattr(app.state, "metrics")
        assert "request_count" in app.state.metrics
        assert "request_latency" in app.state.metrics
        assert "llm_tokens" in app.state.metrics
        assert "agent_tasks" in app.state.metrics


class TestObservabilityInit:
    """Test combined observability initialization."""

    def test_init_without_endpoints(self):
        app = FastAPI()
        result = init_observability(app, otlp_endpoint=None, metrics_enabled=True)
        assert result["tracing"] is False
        assert result["metrics"] is True

    def test_init_fully_disabled(self):
        app = FastAPI()
        result = init_observability(app, otlp_endpoint=None, metrics_enabled=False)
        assert result["tracing"] is False
        assert result["metrics"] is False

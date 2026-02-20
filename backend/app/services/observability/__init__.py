"""Observability module: OpenTelemetry tracing + Prometheus metrics."""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI

logger = logging.getLogger("neura.observability")


def init_metrics(app: FastAPI, *, enabled: bool = True) -> bool:
    """Initialize Prometheus metrics and mount the /metrics endpoint."""
    if not enabled:
        return False

    from .metrics import (
        PrometheusMiddleware,
        metrics_endpoint,
        REQUESTS_TOTAL,
        REQUESTS_DURATION,
        LLM_TOKEN_USAGE,
        REPORTS_GENERATED,
    )

    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])

    app.state.metrics = {
        "request_count": REQUESTS_TOTAL,
        "request_latency": REQUESTS_DURATION,
        "llm_tokens": LLM_TOKEN_USAGE,
        "agent_tasks": REPORTS_GENERATED,
    }

    logger.info("metrics_initialized", extra={"event": "metrics_initialized"})
    return True


def init_tracing(app: FastAPI, *, otlp_endpoint: str | None = None) -> bool:
    """Initialize OpenTelemetry tracing only."""
    if not otlp_endpoint:
        return False
    try:
        from .tracing import setup_tracing
        setup_tracing(app, otlp_endpoint=otlp_endpoint)
        return True
    except Exception as exc:
        logger.warning("tracing_init_failed", extra={"event": "tracing_init_failed", "error": str(exc)})
        return False


def init_observability(
    app: FastAPI,
    *,
    otlp_endpoint: str | None = None,
    metrics_enabled: bool = True,
) -> Dict[str, Any]:
    """Initialize both tracing and metrics for the application."""
    result: Dict[str, Any] = {"tracing": False, "metrics": False}

    result["tracing"] = init_tracing(app, otlp_endpoint=otlp_endpoint)

    result["metrics"] = init_metrics(app, enabled=metrics_enabled)
    return result

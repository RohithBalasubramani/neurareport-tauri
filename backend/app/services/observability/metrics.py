"""
Prometheus metrics middleware for FastAPI.

Captures:
- Request count, response count by status code
- Request duration histogram with trace ID exemplars
- Exception count, in-progress gauge
- Custom business metrics (reports, LLM, queue depth)

Based on: blueswen/fastapi-observability PrometheusMiddleware
"""
from __future__ import annotations

import time
import logging
from typing import Tuple

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

try:
    from opentelemetry import trace as otel_trace
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

from prometheus_client import Counter, Gauge, Histogram, Info, REGISTRY
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST, generate_latest

logger = logging.getLogger("neura.observability.metrics")

# ---- HTTP Metrics ----
REQUESTS_TOTAL = Counter("fastapi_requests_total", "Total requests", ["method", "path", "app_name"])
RESPONSES_TOTAL = Counter("fastapi_responses_total", "Total responses", ["method", "path", "status_code", "app_name"])
REQUESTS_DURATION = Histogram(
    "fastapi_requests_duration_seconds", "Request duration",
    ["method", "path", "app_name"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
EXCEPTIONS_TOTAL = Counter("fastapi_exceptions_total", "Exceptions", ["method", "path", "exception_type", "app_name"])
REQUESTS_IN_PROGRESS = Gauge("fastapi_requests_in_progress", "In-progress requests", ["method", "path", "app_name"])

# ---- Business Metrics ----
REPORTS_GENERATED = Counter("neurareport_reports_generated_total", "Reports generated", ["report_type", "status"])
LLM_INFERENCE_DURATION = Histogram(
    "neurareport_llm_inference_seconds", "LLM inference time",
    ["model", "operation"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
)
LLM_TOKEN_USAGE = Counter("neurareport_llm_tokens_total", "LLM tokens consumed", ["model", "token_type"])
QUEUE_DEPTH = Gauge("neurareport_queue_depth", "Queue depth", ["queue_name"])
ACTIVE_WEBSOCKETS = Gauge("neurareport_active_websocket_connections", "WebSocket connections", ["connection_type"])
BUILD_INFO = Info("neurareport_build", "Build info")


def init_app_info(version: str = "dev", commit: str = "unknown", app_name: str = "neurareport-backend") -> None:
    """Initialize the APP_INFO gauge with version and build metadata."""
    BUILD_INFO.info({"version": version, "commit": commit, "app_name": app_name})


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_name: str = "neurareport-backend"):
        super().__init__(app)
        self.app_name = app_name
        # Populate build info from settings if available
        try:
            from backend.app.services.config import get_settings
            settings = get_settings()
            init_app_info(version=settings.version, commit=settings.commit, app_name=app_name)
        except Exception:
            BUILD_INFO.info({"version": "dev", "app_name": app_name})

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path, is_handled = self._get_path(request)

        # Filter out /metrics endpoint from access log metrics
        if path == "/metrics":
            return await call_next(request)

        if not is_handled:
            return await call_next(request)

        REQUESTS_IN_PROGRESS.labels(method=method, path=path, app_name=self.app_name).inc()
        REQUESTS_TOTAL.labels(method=method, path=path, app_name=self.app_name).inc()

        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS_TOTAL.labels(method=method, path=path, exception_type=type(e).__name__, app_name=self.app_name).inc()
            raise
        else:
            status_code = response.status_code
            after_time = time.perf_counter()
            exemplar = {}
            if HAS_OTEL:
                span = otel_trace.get_current_span()
                trace_id = otel_trace.format_trace_id(span.get_span_context().trace_id)
                exemplar = {"TraceID": trace_id}
            REQUESTS_DURATION.labels(method=method, path=path, app_name=self.app_name).observe(
                after_time - before_time, exemplar=exemplar if exemplar.get("TraceID") else None,
            )
        finally:
            RESPONSES_TOTAL.labels(method=method, path=path, status_code=status_code, app_name=self.app_name).inc()
            REQUESTS_IN_PROGRESS.labels(method=method, path=path, app_name=self.app_name).dec()
        return response

    @staticmethod
    def _get_path(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True
        return request.url.path, False


def metrics_endpoint(request: Request) -> Response:
    return Response(generate_latest(REGISTRY), headers={"Content-Type": CONTENT_TYPE_LATEST})

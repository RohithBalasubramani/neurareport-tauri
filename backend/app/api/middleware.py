from __future__ import annotations

import asyncio
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.datastructures import MutableHeaders
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from backend.app.api.idempotency import IdempotencyMiddleware, IdempotencyStore
from backend.app.services.observability.metrics import PrometheusMiddleware, metrics_endpoint
from backend.app.services.utils.context import set_correlation_id
from backend.app.services.config import Settings
from .ux_governance import UXGovernanceMiddleware, IntentHeaders

logger = logging.getLogger("neura.api")

# Paths whose request_start / request_complete logs are suppressed to avoid
# bloating the log file with high-frequency polling noise.
_QUIET_PATHS: frozenset[str] = frozenset({
    "/api/v1/health",
    "/api/v1/health/ready",
    "/health",
    "/api/v1/jobs",
})

def _get_client_key(request: Request) -> str:
    """Get unique client identifier for rate limiting."""
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"key:{api_key[:16]}"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Use last entry (closest to trusted proxy)
        ip = forwarded.split(",")[-1].strip()
        if ip:
            return ip
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def _format_rate_limit(requests: int, window_seconds: int) -> str:
    if window_seconds <= 1:
        return f"{requests}/second"
    if window_seconds == 60:
        return f"{requests}/minute"
    if window_seconds == 3600:
        return f"{requests}/hour"
    if window_seconds == 86400:
        return f"{requests}/day"
    return f"{requests}/{window_seconds} second"


def _build_default_limits(settings: Settings) -> list[str]:
    limits: list[str] = []
    if settings.rate_limit_requests > 0 and settings.rate_limit_window_seconds > 0:
        limits.append(_format_rate_limit(settings.rate_limit_requests, settings.rate_limit_window_seconds))
    if settings.rate_limit_burst > 0:
        limits.append(f"{settings.rate_limit_burst}/second")
    return limits


limiter = Limiter(key_func=_get_client_key, default_limits=[], headers_enabled=True)

# Rate limit tier constants for per-endpoint rate limiting
RATE_LIMIT_AI = "5/minute"           # AI generation, LLM calls (most expensive)
RATE_LIMIT_STRICT = "10/minute"      # Ingestion, color generation
RATE_LIMIT_STANDARD = "60/minute"    # Standard mutations, exports
RATE_LIMIT_READ = "120/minute"       # Read-heavy endpoints, search, list
RATE_LIMIT_HEALTH = "300/minute"     # Health checks


def _configure_limiter(settings: Settings) -> None:
    limiter.default_limits = _build_default_limits(settings)


class SecurityHeadersMiddleware:
    """Pure ASGI middleware to add security headers to all responses.

    Migrated from BaseHTTPMiddleware for better performance:
    - No per-request task overhead
    - No memory spooling of response body
    - Preserves contextvars propagation
    """

    def __init__(self, app: ASGIApp, debug_mode: bool = False, csp_connect_origins: list[str] | None = None):
        self.app = app
        self.debug_mode = debug_mode
        self.csp_connect_origins = csp_connect_origins or []
        # Pre-compute CSP since it doesn't change per-request
        self._csp = self._build_csp(debug_mode, self.csp_connect_origins)

    @staticmethod
    def _build_csp(debug_mode: bool, connect_origins: list[str]) -> str:
        """Build Content Security Policy string with configurable connect-src."""
        csp_parts = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'" if debug_mode else "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
        ]

        connect_src_origins = ["'self'"]
        if debug_mode:
            connect_src_origins.extend([
                "http://localhost:*",
                "http://127.0.0.1:*",
                "ws://localhost:*",
                "ws://127.0.0.1:*"
            ])
        connect_src_origins.extend(connect_origins)
        csp_parts.append(f"connect-src {' '.join(connect_src_origins)}")

        return "; ".join(csp_parts)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Frame-Options"] = "DENY"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Content-Security-Policy"] = self._csp
                headers["Permissions-Policy"] = (
                    "geolocation=(), microphone=(), camera=()"
                )
            await send(message)

        await self.app(scope, receive, send_with_security_headers)


class RequestTimeoutMiddleware:
    """Pure ASGI middleware to enforce request timeout."""

    def __init__(self, app: ASGIApp, timeout_seconds: int = 300):
        self.app = app
        self.timeout_seconds = timeout_seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        timeout = self.timeout_seconds
        if "/stream" in path or "/upload" in path:
            timeout = timeout * 2

        try:
            await asyncio.wait_for(
                self.app(scope, receive, send),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error(
                "request_timeout",
                extra={
                    "event": "request_timeout",
                    "path": path,
                    "method": scope.get("method", ""),
                    "timeout": timeout,
                },
            )
            body = (
                b'{"status":"error","code":"request_timeout",'
                b'"message":"Request timed out. Please try again.",'
                b'"timeout_seconds":' + str(timeout).encode() + b'}'
            )
            await send({
                "type": "http.response.start",
                "status": 504,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })


class CorrelationIdMiddleware:
    """Pure ASGI middleware for correlation ID and request logging.

    Migrated from BaseHTTPMiddleware to:
    - Preserve contextvars propagation
    - Avoid memory spooling of response body
    - Eliminate per-request task overhead
    - Use time.monotonic() for accurate elapsed measurements
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract or generate correlation ID from raw ASGI headers
        headers_raw = dict(scope.get("headers", []))
        correlation_id = (
            headers_raw.get(b"x-correlation-id", b"").decode()
            or uuid.uuid4().hex
        )

        scope["correlation_id"] = correlation_id
        set_correlation_id(correlation_id)

        path = scope.get("path", "")
        method = scope.get("method", "")
        started = time.monotonic()

        # Suppress verbose logging for high-frequency polling endpoints
        _quiet = path.rstrip("/") in _QUIET_PATHS or path.rstrip("/").startswith(("/api/v1/jobs", "/api/v1/health"))

        if not _quiet:
            logger.info(
                "request_start",
                extra={
                    "event": "request_start",
                    "path": path,
                    "method": method,
                    "correlation_id": correlation_id,
                },
            )

        status_code = 0

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                headers = MutableHeaders(scope=message)
                headers["X-Correlation-ID"] = correlation_id
                headers.setdefault("X-Content-Type-Options", "nosniff")
                content_type = headers.get("content-type", "")
                if content_type.startswith(
                    ("application/json", "text/html", "application/x-ndjson")
                ):
                    headers.setdefault("Cache-Control", "no-store")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            elapsed = int((time.monotonic() - started) * 1000)
            logger.exception(
                "request_error",
                extra={
                    "event": "request_error",
                    "path": path,
                    "method": method,
                    "elapsed_ms": elapsed,
                    "correlation_id": correlation_id,
                },
            )
            set_correlation_id(None)
            raise

        elapsed = int((time.monotonic() - started) * 1000)
        if not _quiet:
            logger.info(
                "request_complete",
                extra={
                    "event": "request_complete",
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "elapsed_ms": elapsed,
                    "correlation_id": correlation_id,
                },
            )
        set_correlation_id(None)


def add_middlewares(app: FastAPI, settings: Settings) -> None:
    """Configure all application middlewares.

    NOTE: Middleware is executed in REVERSE order of addition.
    The LAST middleware added is the FIRST to process requests.
    CORS must be added LAST so it handles OPTIONS preflight requests FIRST.
    """

    # Correlation ID and logging middleware (added first, executes last)
    app.add_middleware(CorrelationIdMiddleware)

    # Prometheus metrics middleware (after correlation ID, before other middleware)
    if settings.metrics_enabled:
        app.add_middleware(PrometheusMiddleware, app_name=settings.app_name)
        app.add_route("/metrics", metrics_endpoint, methods=["GET"])
        logger.info("metrics_enabled", extra={"event": "metrics_enabled", "app_name": settings.app_name})

    # OpenTelemetry tracing (conditional on OTLP endpoint being configured)
    if settings.otlp_endpoint:
        from backend.app.services.observability.tracing import setup_tracing
        deployment_env = "development" if settings.debug_mode else "production"
        setup_tracing(
            app=app,
            service_name=settings.app_name,
            otlp_endpoint=settings.otlp_endpoint,
            service_version=settings.version,
            deployment_environment=deployment_env,
        )

    # UX Governance middleware - enforces intent headers on mutating requests
    # Set strict_mode=False initially to log warnings without rejecting requests
    # Change to strict_mode=True when frontend is fully compliant
    app.add_middleware(
        UXGovernanceMiddleware,
        strict_mode=settings.ux_governance_strict if hasattr(settings, 'ux_governance_strict') else False,
    )

    # Rate limiting middleware
    if settings.rate_limit_enabled:
        _configure_limiter(settings)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

    # Request timeout middleware
    app.add_middleware(
        RequestTimeoutMiddleware,
        timeout_seconds=settings.request_timeout_seconds,
    )

    # Security headers middleware - pass debug mode and CSP origins
    app.add_middleware(
        SecurityHeadersMiddleware,
        debug_mode=settings.debug_mode,
        csp_connect_origins=settings.csp_connect_origins
    )

    # Trusted host middleware - configure properly in production
    if settings.allowed_hosts_all:
        allowed_hosts = ["*"]
    else:
        allowed_hosts = settings.trusted_hosts
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    if settings.idempotency_enabled:
        app.add_middleware(
            IdempotencyMiddleware,
            store=IdempotencyStore(),
            ttl_seconds=settings.idempotency_ttl_seconds,
        )

    # CORS middleware - MUST be added LAST so it executes FIRST
    # This ensures OPTIONS preflight requests are handled before any other middleware
    cors_headers = [
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "X-Correlation-ID",
        "Idempotency-Key",
        "X-Idempotency-Key",  # Legacy header name
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Cache-Control",
        "Pragma",
        # UX Governance headers
        IntentHeaders.INTENT_ID,
        IntentHeaders.INTENT_TYPE,
        IntentHeaders.INTENT_LABEL,
        IntentHeaders.IDEMPOTENCY_KEY,
        IntentHeaders.REVERSIBILITY,
        IntentHeaders.USER_SESSION,
        IntentHeaders.USER_ACTION,
        IntentHeaders.WORKFLOW_ID,
        IntentHeaders.WORKFLOW_STEP,
    ]
    cors_expose = [
        "X-Correlation-ID",
        "X-RateLimit-Remaining",
        "X-RateLimit-Limit",
        "Idempotency-Replay",
        "X-Intent-Processed",
    ]
    cors_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    if settings.debug_mode:
        # In debug mode, use regex to allow any localhost/127.0.0.1 origin
        # Note: allow_credentials=True is incompatible with allow_origins=["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
            allow_methods=cors_methods,
            allow_headers=cors_headers,
            allow_credentials=True,
            expose_headers=cors_expose,
        )
    else:
        # In production, use explicit origin list
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=cors_methods,
            allow_headers=cors_headers,
            allow_credentials=True,
            expose_headers=cors_expose,
        )

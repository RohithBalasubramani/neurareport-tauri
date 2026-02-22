from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request

logger = logging.getLogger(__name__)

from backend.app.services.security import require_api_key

from backend.app.services.config import Settings, get_settings
from backend.app.api.middleware import limiter
from backend.app.services.analyze.document_analysis_service import _analysis_cache
from backend.app.services.utils.mailer import _get_config as _get_mailer_config, refresh_mailer_config
from backend.app.services import state_access

router = APIRouter()


def _check_directory_access(path: Path) -> Dict[str, Any]:
    """Check if a directory is accessible for read/write operations."""
    try:
        if not path.exists():
            return {"status": "warning", "message": "Directory does not exist", "path": str(path)}
        if not path.is_dir():
            return {"status": "error", "message": "Path is not a directory", "path": str(path)}
        # Try to list directory contents
        list(path.iterdir())
        # Check write access
        test_file = path / f".health_check_{os.getpid()}"
        try:
            test_file.write_text("health check")
            test_file.unlink()
            return {"status": "healthy", "path": str(path), "writable": True}
        except (OSError, PermissionError):
            return {"status": "warning", "path": str(path), "writable": False, "message": "Read-only access"}
    except Exception as e:
        logger.warning("directory_check_failed", extra={"path": str(path), "error": str(e)})
        return {"status": "error", "message": "Directory check failed", "path": str(path)}


def _check_claude_code_cli() -> Dict[str, Any]:
    """Check if Claude Code CLI is available."""
    import subprocess
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {
                "status": "available",
                "message": "Claude Code CLI is available",
            }
        return {"status": "error", "message": "Claude Code CLI not responding"}
    except Exception as e:
        logger.warning("claude_cli_check_failed", extra={"error": str(e)})
        return {"status": "error", "message": "Claude Code CLI check failed"}


def _check_openai_connection(settings: Settings | None = None) -> Dict[str, Any]:
    """Best-effort check that OpenAI is configured (and optionally reachable).

    This is intentionally lightweight: in many environments OpenAI is a fallback
    provider, and we don't want health checks to block on external calls.
    """
    if settings is None:
        settings = get_settings()
    if not getattr(settings, "openai_api_key", None):
        return {"status": "not_configured", "message": "OpenAI API key not configured"}
    try:
        # Backwards-compatible: core "verification" code still exposes
        # TemplateVerify.get_openai_client(), even though the backend may be a
        # different provider (Claude Code CLI via unified client).
        from backend.app.services.templates import TemplateVerify

        client = TemplateVerify.get_openai_client()
        if client is None:
            return {"status": "error", "message": "OpenAI client initialization failed"}
        return {"status": "configured", "message": "OpenAI client initialized"}
    except Exception:
        logger.exception("openai_health_check_failed")
        return {"status": "error", "message": "OpenAI health check failed"}


def _get_memory_usage() -> Dict[str, Any]:
    """Get current process memory usage."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "max_rss_mb": usage.ru_maxrss / 1024 if hasattr(usage, 'ru_maxrss') else None,
            "status": "healthy",
        }
    except ImportError:
        # resource module not available on Windows
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            return {
                "rss_mb": mem_info.rss / 1024 / 1024,
                "vms_mb": mem_info.vms / 1024 / 1024,
                "status": "healthy",
            }
        except ImportError:
            return {"status": "unknown", "message": "Memory stats not available"}


def _check_database() -> Dict[str, Any]:
    """Check state store is reachable."""
    try:
        store = state_access.get_state_store()
        backend_name = getattr(store, "backend_name", store.__class__.__name__)
        backend_fallback = bool(getattr(store, "backend_fallback", False))
        stats = store.get_stats() if hasattr(store, "get_stats") else None
        return {
            "status": "healthy",
            "backend_name": backend_name,
            "backend_fallback": backend_fallback,
            "stats": stats,
        }
    except Exception:
        logger.exception("database_health_check_failed")
        return {"status": "error", "message": "Database health check failed"}


@limiter.exempt
@router.get("/health")
async def health(request: Request) -> Dict[str, Any]:
    """Basic health check - fast, for load balancer probes."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@limiter.exempt
@router.get("/healthz")
async def healthz() -> Dict[str, str]:
    """Kubernetes-style liveness probe."""
    return {"status": "ok"}


@limiter.exempt
@router.get("/ready")
async def ready() -> Dict[str, Any]:
    """Kubernetes-style readiness probe - checks if app can serve requests."""
    settings = get_settings()
    checks = {}
    overall_status = "ready"

    # Check uploads directory
    uploads_check = _check_directory_access(settings.uploads_dir)
    checks["uploads_dir"] = uploads_check
    if uploads_check["status"] == "error":
        overall_status = "not_ready"

    # Check state directory
    state_check = _check_directory_access(settings.state_dir)
    checks["state_dir"] = state_check
    if state_check["status"] == "error":
        overall_status = "not_ready"

    return {
        "status": overall_status,
        "checks": checks,
    }


@limiter.exempt
@router.get("/readyz")
async def readyz() -> Dict[str, Any]:
    """Compatibility alias for readiness probe."""
    return await ready()


@limiter.exempt
@router.get("/health/token-usage")
async def token_usage(request: Request) -> Dict[str, Any]:
    """Get LLM token usage statistics."""
    try:
        from backend.app.services.llm.client import get_global_usage_stats
        stats = get_global_usage_stats()
        return {
            "status": "ok",
            "usage": stats,
            "correlation_id": getattr(request.state, "correlation_id", None),
        }
    except Exception as e:
        logger.warning("token_usage_check_failed", extra={"error": str(e)})
        return {
            "status": "error",
            "message": "Token usage retrieval failed",
            "usage": {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "request_count": 0,
            },
            "correlation_id": getattr(request.state, "correlation_id", None),
        }


def _redact_directory_check(check: Dict[str, Any]) -> Dict[str, Any]:
    """Remove raw paths from directory health checks."""
    return {
        "status": check["status"],
        "writable": check.get("writable"),
    }


@limiter.exempt
@router.get("/health/detailed", dependencies=[Depends(require_api_key)])
async def health_detailed(
    request: Request,
) -> Dict[str, Any]:
    """Comprehensive health check with all dependencies."""
    started = time.time()
    settings = get_settings()

    checks: Dict[str, Any] = {}
    issues: list[str] = []

    # Check critical directories (redact paths)
    uploads_check = _check_directory_access(settings.uploads_dir)
    checks["uploads_dir"] = _redact_directory_check(uploads_check)
    if uploads_check["status"] == "error":
        issues.append("Uploads directory not accessible")

    checks["excel_uploads_dir"] = _redact_directory_check(
        _check_directory_access(settings.excel_uploads_dir)
    )

    state_check = _check_directory_access(settings.state_dir)
    checks["state_dir"] = _redact_directory_check(state_check)
    if state_check["status"] == "error":
        issues.append("State directory not accessible")

    # Check Claude Code CLI
    checks["llm"] = _check_claude_code_cli()

    # Check OpenAI (optional/fallback provider)
    checks["openai"] = _check_openai_connection(settings)
    if checks["openai"]["status"] == "error":
        issues.append("OpenAI connectivity failed")

    # Check cache status
    cache = _analysis_cache()
    checks["analysis_cache"] = {
        "status": "healthy",
        "current_size": cache.size(),
        "max_size": cache.max_items,
        "ttl_seconds": cache.ttl_seconds,
    }

    # Database connectivity (state store + auth SQLite)
    checks["database"] = _check_database()

    # Memory usage
    checks["memory"] = _get_memory_usage()

    # API configuration (redact sensitive details)
    checks["configuration"] = {
        "api_key_configured": settings.api_key is not None,
        "rate_limiting_enabled": settings.rate_limit_enabled,
        "rate_limit": f"{settings.rate_limit_requests}/{settings.rate_limit_window_seconds}s",
        "request_timeout": settings.request_timeout_seconds,
        "max_upload_size_mb": settings.max_upload_bytes / 1024 / 1024,
    }

    elapsed_ms = int((time.time() - started) * 1000)

    overall_status = "healthy" if not issues else "degraded"

    return {
        "status": overall_status,
        "version": settings.api_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response_time_ms": elapsed_ms,
        "checks": checks,
        "issues": issues if issues else None,
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


def _check_email_config() -> Dict[str, Any]:
    """Check email/SMTP configuration status."""
    config = _get_mailer_config()
    result: Dict[str, Any] = {
        "enabled": config.enabled,
        "host_configured": bool(config.host),
        "sender_configured": bool(config.sender),
        "auth_configured": bool(config.username and config.password),
        "use_tls": config.use_tls,
        "port": config.port,
    }

    if not config.enabled:
        result["status"] = "not_configured"
        missing = []
        if not config.host:
            missing.append("NEURA_MAIL_HOST")
        if not config.sender:
            missing.append("NEURA_MAIL_SENDER")
        result["missing_env_vars"] = missing
        result["message"] = f"Email disabled. Set {', '.join(missing)} to enable."
    else:
        result["status"] = "configured"
        result["host"] = config.host
        # Mask sender partially for security
        if config.sender:
            parts = config.sender.split("@")
            if len(parts) == 2:
                masked = parts[0][:3] + "***@" + parts[1]
                result["sender_masked"] = masked
            else:
                result["sender_masked"] = config.sender[:5] + "***"

    return result


def _test_smtp_connection() -> Dict[str, Any]:
    """Attempt to connect to SMTP server (without sending email)."""
    config = _get_mailer_config()
    if not config.enabled or not config.host:
        return {"status": "skipped", "reason": "email_not_configured"}

    import smtplib
    import ssl

    try:
        if config.use_tls:
            with smtplib.SMTP(config.host, config.port, timeout=10) as client:
                client.ehlo()
                context = ssl.create_default_context()
                client.starttls(context=context)
                client.ehlo()
                if config.username and config.password:
                    client.login(config.username, config.password)
                return {"status": "connected", "message": "SMTP connection successful"}
        else:
            with smtplib.SMTP(config.host, config.port, timeout=10) as client:
                client.ehlo()
                if config.username and config.password:
                    client.login(config.username, config.password)
                return {"status": "connected", "message": "SMTP connection successful"}
    except smtplib.SMTPAuthenticationError as e:
        logger.warning("smtp_auth_failed", extra={"error": str(e)})
        return {"status": "auth_failed", "message": "SMTP authentication failed"}
    except smtplib.SMTPConnectError as e:
        logger.warning("smtp_connect_failed", extra={"error": str(e)})
        return {"status": "connection_failed", "message": "Could not connect to SMTP server"}
    except Exception as e:
        logger.warning("smtp_test_failed", extra={"error": str(e)})
        return {"status": "error", "message": "SMTP connection test failed"}


@limiter.exempt
@router.get("/health/email")
async def email_health(request: Request) -> Dict[str, Any]:
    """Check email/SMTP configuration and optionally test connection."""
    config_status = _check_email_config()
    return {
        "status": "ok" if config_status.get("status") == "configured" else "warning",
        "email": config_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@limiter.exempt
@router.get("/health/email/test")
async def email_connection_test(request: Request) -> Dict[str, Any]:
    """Test SMTP connection (without sending an email)."""
    config_status = _check_email_config()
    connection_test = _test_smtp_connection()

    overall_status = "ok"
    if config_status.get("status") != "configured":
        overall_status = "warning"
    elif connection_test.get("status") != "connected":
        overall_status = "error"

    return {
        "status": overall_status,
        "email": config_status,
        "connection_test": connection_test,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@limiter.exempt
@router.post("/health/email/refresh")
async def refresh_email_config(request: Request) -> Dict[str, Any]:
    """Refresh email configuration from environment variables."""
    refresh_mailer_config()
    config_status = _check_email_config()
    return {
        "status": "ok",
        "message": "Email configuration refreshed",
        "email": config_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@limiter.exempt
@router.get("/health/scheduler")
async def scheduler_health(request: Request) -> Dict[str, Any]:
    """Check scheduler status with detailed information."""
    scheduler_disabled = os.getenv("NEURA_SCHEDULER_DISABLED", "false").lower() == "true"
    poll_interval = int(os.getenv("NEURA_SCHEDULER_INTERVAL", "60") or "60")

    # Try to get scheduler instance from main app
    scheduler_running = False
    inflight_jobs: list[str] = []
    scheduler_instance = None

    try:
        import backend.api as api_module
        scheduler_instance = getattr(api_module, "SCHEDULER", None)
        if scheduler_instance is not None:
            scheduler_running = scheduler_instance._task is not None and not scheduler_instance._task.done()
            inflight_jobs = list(scheduler_instance._inflight)
    except Exception:
        pass

    # Get schedule statistics
    schedules_info = {"total": 0, "active": 0, "next_run": None}
    try:
        schedules = state_access.list_schedules()
        schedules_info["total"] = len(schedules)
        schedules_info["active"] = sum(1 for s in schedules if s.get("active", True))

        # Find next scheduled run
        now = datetime.now(timezone.utc)
        next_runs = []
        for s in schedules:
            if s.get("active", True) and s.get("next_run_at"):
                try:
                    next_run = datetime.fromisoformat(s["next_run_at"].replace("Z", "+00:00"))
                    next_runs.append((next_run, s.get("name", s.get("id"))))
                except Exception:
                    pass

        if next_runs:
            next_runs.sort(key=lambda x: x[0])
            next_run_time, next_run_name = next_runs[0]
            schedules_info["next_run"] = {
                "schedule_name": next_run_name,
                "next_run_at": next_run_time.isoformat(),
                "in_seconds": max(0, int((next_run_time - now).total_seconds())),
            }
    except Exception:
        pass

    status = "ok"
    message = None
    if scheduler_disabled:
        status = "disabled"
        message = "Scheduler is disabled via NEURA_SCHEDULER_DISABLED environment variable"
    elif not scheduler_running:
        status = "warning"
        message = "Scheduler is enabled but not currently running"

    return {
        "status": status,
        "message": message,
        "scheduler": {
            "enabled": not scheduler_disabled,
            "running": scheduler_running,
            "poll_interval_seconds": poll_interval,
            "inflight_jobs": inflight_jobs,
        },
        "schedules": schedules_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }

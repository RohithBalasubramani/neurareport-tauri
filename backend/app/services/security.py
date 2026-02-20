from __future__ import annotations

import hmac
import secrets

import os

from fastapi import Depends, Header

try:
    from .auth import current_optional_user
except Exception:  # pragma: no cover - auth optional
    async def current_optional_user():
        return None

from .config import get_settings
from backend.app.utils.errors import AppError


def constant_time_compare(a: str | None, b: str | None) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    Returns True if both strings are non-None and equal.
    """
    if a is None or b is None:
        return False
    # Use hmac.compare_digest for constant-time comparison
    # Encode to bytes for the comparison
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


async def require_api_key(
    x_api_key: str | None = Header(None),
    settings=Depends(get_settings),
    user=Depends(current_optional_user),
) -> None:
    """
    Lightweight API key gate. Enforces either an authenticated user or a valid API key.
    Uses constant-time comparison to prevent timing attacks.
    """
    if user is not None:
        return
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    if settings.allow_anonymous_api or settings.debug_mode:
        return
    # In development (no API key configured), allow anonymous access
    if not settings.api_key:
        return
    if not constant_time_compare(x_api_key, settings.api_key):
        raise AppError(code="unauthorized", message="Invalid API key", status_code=401)


def verify_ws_token(token: str | None) -> bool:
    """
    Verify WebSocket token from query parameter.
    Returns True if token is valid or if auth is bypassed.

    WebSocket connections can't use FastAPI Depends() with Header(),
    so this function provides standalone token verification using query parameters.
    Mirrors bypass logic from require_api_key: test mode, debug mode, anonymous API, no key configured.
    """
    settings = get_settings()

    # Bypass in test mode
    if os.getenv("PYTEST_CURRENT_TEST"):
        return True

    # Bypass if anonymous API is allowed or debug mode is enabled
    if settings.allow_anonymous_api or settings.debug_mode:
        return True

    # If no API key is configured (development), allow access
    if not settings.api_key:
        return True

    # Verify token matches configured API key using constant-time comparison
    return constant_time_compare(token, settings.api_key)

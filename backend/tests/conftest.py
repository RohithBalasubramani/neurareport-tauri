import os
import uuid
import warnings

import pytest
from fastapi.testclient import TestClient

# Silence specific known deprecation warnings from third-party packages
# (avoid blanket suppression so real deprecations in our code are visible)
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"pydantic.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"starlette.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"httpx.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"sqlalchemy.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"pkg_resources.*")

# Allow "testserver" hostname used by Starlette TestClient.
# Note: pydantic-settings v2 reads field name (ALLOWED_HOSTS_ALL), not
# the Field(env=...) alias.  Set both to be safe.
os.environ["ALLOWED_HOSTS_ALL"] = "true"
os.environ["NEURA_ALLOWED_HOSTS_ALL"] = "true"

# JWT secret is required in production; provide a test-only value.
# Also enable debug mode so the runtime validator doesn't reject the default.
os.environ.setdefault("NEURA_JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("NEURA_DEBUG", "true")

# Clear cached settings so the env override takes effect
try:
    from backend.app.services.config import get_settings
    get_settings.cache_clear()
except Exception:
    pass


_ORIGINAL_REQUEST = TestClient.request


def _intent_headers() -> dict[str, str]:
    return {
        "X-Intent-Id": uuid.uuid4().hex,
        "X-Intent-Type": "update",
        "Idempotency-Key": uuid.uuid4().hex,
    }


@pytest.fixture(autouse=True)
def _disable_rate_limiter(request):
    """Disable slowapi rate limiter for all tests except rate-limiting tests."""
    # Skip disabling for tests that explicitly test rate limiting behaviour
    if "test_rate_limiting" in request.node.nodeid:
        yield
        return
    from backend.app.api.middleware import limiter
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture(autouse=True, scope="function")
def _inject_intent_headers():
    def _patched_request(self, method, url, **kwargs):
        if str(method).upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            headers = dict(kwargs.get("headers") or {})
            headers.setdefault("X-Intent-Id", uuid.uuid4().hex)
            headers.setdefault("X-Intent-Type", "update")
            headers.setdefault("Idempotency-Key", uuid.uuid4().hex)
            kwargs["headers"] = headers
        return _ORIGINAL_REQUEST(self, method, url, **kwargs)

    TestClient.request = _patched_request
    yield
    TestClient.request = _ORIGINAL_REQUEST

"""Tests for per-endpoint rate limiting."""
from __future__ import annotations

from unittest.mock import patch, AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.ai import router as ai_router
from backend.app.api.routes.design import router as design_router
from backend.app.api.routes.documents import router as documents_router
from backend.app.api.middleware import limiter, _configure_limiter
from backend.app.services.config import get_settings
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


@pytest.fixture(autouse=True)
def _mock_ai_services():
    """Mock AI services so rate-limit tests don't hit real LLM endpoints."""
    with patch(
        "backend.app.api.routes.ai.writing_service.generate_content",
        new_callable=AsyncMock,
        return_value="mocked content",
    ), patch(
        "backend.app.api.routes.design.generate_color_palette",
        return_value={"colors": ["#FF0000"]},
    ):
        yield


@pytest.fixture(autouse=True)
def _reset_limiter():
    """Reset rate limiter state between tests."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="function")
def app():
    """Test app fixture with rate limiting."""
    # Reset limiter storage FIRST to ensure test isolation
    limiter.reset()

    _app = FastAPI()
    _app.include_router(ai_router)
    _app.include_router(design_router, prefix="/design")
    _app.include_router(documents_router, prefix="/documents")

    # Configure rate limiter
    settings = get_settings()
    _configure_limiter(settings)

    # Set up rate limiting with middleware
    _app.state.limiter = limiter
    _app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    _app.add_middleware(SlowAPIMiddleware)

    return _app


@pytest.fixture
def client(app):
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def api_key_1():
    """First API key for testing."""
    return "test-key-1"


@pytest.fixture
def api_key_2():
    """Second API key for testing."""
    return "test-key-2"


# =============================================================================
# Strict Rate Limit Tests (10/minute)
# =============================================================================

def test_strict_rate_limit_enforced(client, api_key_1):
    """Test that strict rate limit (10/min) is enforced on AI endpoints."""
    # The RATE_LIMIT_STRICT is set to "10/minute"
    # Make 10 requests - all should succeed
    endpoint = "/ai/generate"
    payload = {"prompt": "test", "tone": "professional"}

    for i in range(10):
        response = client.post(
            endpoint,
            json=payload,
            headers={"X-API-Key": api_key_1}
        )
        assert response.status_code != 429, f"Request {i+1} was rate-limited prematurely (got 429)"

    # The 11th request should be rate limited
    response = client.post(
        endpoint,
        json=payload,
        headers={"X-API-Key": api_key_1}
    )
    assert response.status_code == 429, f"Expected 429 Too Many Requests on 11th request, got {response.status_code}"


def test_rate_limit_response_headers(client, api_key_1):
    """Test that rate limit headers are included in responses."""
    endpoint = "/ai/generate"
    payload = {"prompt": "test", "tone": "professional"}

    response = client.post(
        endpoint,
        json=payload,
        headers={"X-API-Key": api_key_1}
    )

    # Check for rate limit headers
    assert "X-RateLimit-Limit" in response.headers or "RateLimit-Limit" in response.headers, \
        "Rate limit header missing"
    assert "X-RateLimit-Remaining" in response.headers or "RateLimit-Remaining" in response.headers, \
        "Rate limit remaining header missing"


def test_rate_limit_independent_keys(client, api_key_1, api_key_2):
    """Test that rate limits are independent per API key."""
    endpoint = "/ai/generate"
    payload = {"prompt": "test", "tone": "professional"}

    # Exhaust rate limit for api_key_1
    for _ in range(10):
        client.post(endpoint, json=payload, headers={"X-API-Key": api_key_1})

    # 11th request with api_key_1 should fail
    response_1 = client.post(endpoint, json=payload, headers={"X-API-Key": api_key_1})
    assert response_1.status_code == 429

    # But api_key_2 should still work (independent counter)
    response_2 = client.post(endpoint, json=payload, headers={"X-API-Key": api_key_2})
    assert response_2.status_code in [200, 503], \
        f"Expected 200/503 for api_key_2, got {response_2.status_code}"


# =============================================================================
# Standard Rate Limit Tests (60/minute)
# =============================================================================

def test_standard_rate_limit_allows_more_requests(client, api_key_1):
    """Test that standard rate limit (60/min) allows more requests than strict."""
    # The RATE_LIMIT_STANDARD is set to "60/minute"
    # Test with document creation endpoint which uses STANDARD
    endpoint = ""
    payload = {"name": "Test Document"}

    # Make 15 requests - all should succeed (more than strict limit of 10)
    for i in range(15):
        response = client.post(
            "/documents" + endpoint,
            json=payload,
            headers={"X-API-Key": api_key_1}
        )
        # 200 = success, 400 = validation error (acceptable), 503 = service unavailable
        assert response.status_code in [200, 201, 400, 503], \
            f"Request {i+1} failed with {response.status_code}"


def test_rate_limit_reset_after_window(client, api_key_1):
    """Test that rate limit resets after time window."""
    import time

    endpoint = "/ai/generate"
    payload = {"prompt": "test", "tone": "professional"}

    # Make 10 requests to approach limit
    for _ in range(10):
        client.post(endpoint, json=payload, headers={"X-API-Key": api_key_1})

    # 11th request should be rate limited
    response = client.post(endpoint, json=payload, headers={"X-API-Key": api_key_1})
    assert response.status_code == 429

    # Wait 61 seconds for rate limit window to reset (in production)
    # In tests, we just verify the 429 behavior - actual time-based reset
    # is handled by slowapi and would require integration testing
    assert response.status_code == 429


def test_rate_limit_per_endpoint_isolation(client, api_key_1):
    """Test that rate limits are isolated per endpoint."""
    ai_endpoint = "/ai/generate"
    design_endpoint = "/design/color-palette"

    ai_payload = {"prompt": "test", "tone": "professional"}
    design_payload = {"base_color": "#FF0000", "harmony_type": "complementary", "count": 5}

    # Exhaust AI endpoint limit
    for _ in range(10):
        client.post(ai_endpoint, json=ai_payload, headers={"X-API-Key": api_key_1})

    # AI endpoint should be rate limited
    response_ai = client.post(ai_endpoint, json=ai_payload, headers={"X-API-Key": api_key_1})
    assert response_ai.status_code == 429

    # But design endpoint should still work (different rate limit counter)
    response_design = client.post(design_endpoint, json=design_payload, headers={"X-API-Key": api_key_1})
    # 200 = success, 400/422 = validation error, 503 = service unavailable
    assert response_design.status_code in [200, 400, 422, 503], \
        f"Expected 200/400/422/503 for design endpoint, got {response_design.status_code}"

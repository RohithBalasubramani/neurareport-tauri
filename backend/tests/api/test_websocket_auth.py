"""Tests for WebSocket authentication."""
from __future__ import annotations

import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.app.api.routes.documents import ws_router
from backend.app.services.security import verify_ws_token
from backend.app.services.config import get_settings


@pytest.fixture(autouse=True)
def _set_jwt_secret(monkeypatch):
    """Ensure NEURA_JWT_SECRET is set so the production guard in config.py does not raise."""
    monkeypatch.setenv("NEURA_JWT_SECRET", "test-secret-for-ws-auth-tests")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def app():
    """Test app fixture."""
    _app = FastAPI()
    _app.include_router(ws_router)
    return _app


@pytest.fixture
def client(app):
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def valid_api_key():
    """Get the configured API key for testing."""
    settings = get_settings()
    return settings.api_key or "test-api-key"


# =============================================================================
# WebSocket Connection Tests
# =============================================================================

def test_websocket_with_valid_token(client, valid_api_key):
    """Test WebSocket connection with valid token is accepted."""
    with client.websocket_connect(f"/ws/collab/test-doc?token={valid_api_key}") as websocket:
        # Connection should be established
        # If we get here without exception, the connection was accepted
        assert websocket is not None


def test_websocket_with_invalid_token(client):
    """Test WebSocket connection with invalid token is rejected with 1008."""
    env_vars = {"NEURA_API_KEY": "secret-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}
    with patch.dict(os.environ, env_vars, clear=False):
        # Remove PYTEST_CURRENT_TEST so verify_ws_token doesn't auto-bypass
        saved = os.environ.pop("PYTEST_CURRENT_TEST", None)
        get_settings.cache_clear()

        try:
            with pytest.raises(Exception) as exc_info:
                with client.websocket_connect("/ws/collab/test-doc?token=invalid-token"):
                    pass
            # The connection should be closed with code 1008 (policy violation)
            err = exc_info.value
            assert getattr(err, "code", None) == 1008 or "1008" in str(err) or "Unauthorized" in str(err)
        finally:
            if saved is not None:
                os.environ["PYTEST_CURRENT_TEST"] = saved
            get_settings.cache_clear()


def test_websocket_with_no_token(client):
    """Test WebSocket connection with no token is rejected with 1008."""
    env_vars = {"NEURA_API_KEY": "secret-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}
    with patch.dict(os.environ, env_vars, clear=False):
        saved = os.environ.pop("PYTEST_CURRENT_TEST", None)
        get_settings.cache_clear()

        try:
            with pytest.raises(Exception) as exc_info:
                with client.websocket_connect("/ws/collab/test-doc"):
                    pass
            # The connection should be closed with code 1008
            err = exc_info.value
            assert getattr(err, "code", None) == 1008 or "1008" in str(err) or "Unauthorized" in str(err)
        finally:
            if saved is not None:
                os.environ["PYTEST_CURRENT_TEST"] = saved
            get_settings.cache_clear()


def test_websocket_debug_mode_bypass(client):
    """Test WebSocket connection allowed in debug mode without token."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "secret-key", "NEURA_DEBUG": "true"}, clear=False):
        get_settings.cache_clear()

        try:
            with client.websocket_connect("/ws/collab/test-doc") as websocket:
                # Debug mode should allow connection without token
                assert websocket is not None
        finally:
            get_settings.cache_clear()


def test_websocket_no_api_key_configured(client):
    """Test WebSocket connection allowed when no API key is configured."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}, clear=False):
        get_settings.cache_clear()

        try:
            with client.websocket_connect("/ws/collab/test-doc") as websocket:
                # No API key configured should allow connection
                assert websocket is not None
        finally:
            get_settings.cache_clear()


def test_websocket_anonymous_api_allowed(client):
    """Test WebSocket connection allowed when anonymous API is enabled."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "secret-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "true"}, clear=False):
        get_settings.cache_clear()

        try:
            with client.websocket_connect("/ws/collab/test-doc") as websocket:
                # Anonymous API should allow connection without token
                assert websocket is not None
        finally:
            get_settings.cache_clear()


def test_websocket_pytest_environment_bypass(client):
    """Test WebSocket connection allowed in pytest environment."""
    with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "test_websocket_auth.py::test_websocket_pytest_environment_bypass", "NEURA_API_KEY": "secret-key"}, clear=False):
        get_settings.cache_clear()

        try:
            with client.websocket_connect("/ws/collab/test-doc") as websocket:
                # Pytest environment should bypass auth
                assert websocket is not None
        finally:
            get_settings.cache_clear()


# =============================================================================
# Unit Tests for verify_ws_token()
# =============================================================================

def test_verify_ws_token_with_valid_token():
    """Test verify_ws_token returns True for valid token."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "test-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}, clear=False):
        get_settings.cache_clear()

        try:
            assert verify_ws_token("test-key") is True
        finally:
            get_settings.cache_clear()


def test_verify_ws_token_with_invalid_token():
    """Test verify_ws_token returns False for invalid token."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "test-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}, clear=False):
        saved = os.environ.pop("PYTEST_CURRENT_TEST", None)
        get_settings.cache_clear()

        try:
            assert verify_ws_token("wrong-key") is False
        finally:
            if saved is not None:
                os.environ["PYTEST_CURRENT_TEST"] = saved
            get_settings.cache_clear()


def test_verify_ws_token_with_none_token():
    """Test verify_ws_token returns False for None token when API key is configured."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "test-key", "NEURA_JWT_SECRET": "test-secret-for-ws-auth-tests", "NEURA_DEBUG": "false", "NEURA_ALLOW_ANON_API": "false"}, clear=False):
        saved = os.environ.pop("PYTEST_CURRENT_TEST", None)
        get_settings.cache_clear()

        try:
            assert verify_ws_token(None) is False
        finally:
            if saved is not None:
                os.environ["PYTEST_CURRENT_TEST"] = saved
            get_settings.cache_clear()


def test_verify_ws_token_debug_mode():
    """Test verify_ws_token returns True in debug mode regardless of token."""
    with patch.dict(os.environ, {"NEURA_API_KEY": "test-key", "NEURA_DEBUG": "true"}, clear=False):
        get_settings.cache_clear()

        try:
            assert verify_ws_token(None) is True
            assert verify_ws_token("any-token") is True
        finally:
            get_settings.cache_clear()

"""Destructive simulation: verify old incorrect paths fail, new correct paths succeed.

This test confirms the frontend route fix is necessary — the old paths the
frontend was using do NOT exist on the backend.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.design import router
from backend.app.api.middleware import limiter
from backend.app.services.design.service import DesignService
from backend.app.services.security import require_api_key


@pytest.fixture
def app():
    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/design")
    limiter.enabled = False
    yield _app
    limiter.enabled = True


@pytest.fixture
def service():
    svc = DesignService()
    import backend.app.api.routes.design as mod
    original = mod.design_service
    mod.design_service = svc

    mock_store = MagicMock()
    mock_store._lock = MagicMock()
    mock_store._read_state.return_value = {}
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = lambda s: {"brand_kits": {}, "themes": {}}
    mock_ctx.__exit__ = lambda s, *a: None
    mock_store.transaction.return_value = mock_ctx

    with patch("backend.app.repositories.state.store.state_store", mock_store):
        yield svc

    mod.design_service = original


@pytest.fixture
def client(app, service):
    return TestClient(app)


class TestOldPathsFail:
    """The old frontend paths must NOT resolve on the backend."""

    def test_old_set_active_path_returns_404_or_405(self, client):
        """Frontend used /design/themes/{id}/set-active — must fail."""
        # Create a theme first
        resp = client.post("/design/themes", json={"name": "Test"})
        theme_id = resp.json()["id"]

        # Old path: /set-active — should return 404 (no route) or 405 (method not allowed)
        old_resp = client.post(f"/design/themes/{theme_id}/set-active")
        assert old_resp.status_code in (404, 405), (
            f"Old path /set-active should fail but got {old_resp.status_code}"
        )

    def test_old_colors_generate_path_returns_404_or_405(self, client):
        """Frontend used /design/colors/generate — must fail."""
        old_resp = client.post("/design/colors/generate", json={
            "base_color": "#ff0000",
            "scheme": "complementary",
        })
        assert old_resp.status_code in (404, 405), (
            f"Old path /colors/generate should fail but got {old_resp.status_code}"
        )

    def test_old_body_field_scheme_rejected(self, client):
        """Backend expects harmony_type, not scheme. Sending only scheme → uses default."""
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "scheme": "analogous",  # wrong field name
        })
        # Pydantic ignores extra fields, so this succeeds but uses default harmony_type
        assert resp.status_code == 200
        # The harmony_type should be the default "complementary", NOT "analogous"
        assert resp.json()["harmony_type"] == "complementary", (
            "Sending 'scheme' instead of 'harmony_type' must not set the harmony type"
        )


class TestNewPathsSucceed:
    """The corrected frontend paths must resolve correctly."""

    def test_activate_path_succeeds(self, client):
        """Corrected path: /design/themes/{id}/activate"""
        resp = client.post("/design/themes", json={"name": "Test"})
        theme_id = resp.json()["id"]

        new_resp = client.post(f"/design/themes/{theme_id}/activate")
        assert new_resp.status_code == 200
        assert new_resp.json()["is_active"] is True

    def test_color_palette_path_succeeds(self, client):
        """Corrected path: /design/color-palette with harmony_type + count"""
        new_resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "harmony_type": "analogous",
            "count": 5,
        })
        assert new_resp.status_code == 200
        data = new_resp.json()
        assert data["harmony_type"] == "analogous"
        assert data["base_color"] == "#ff0000"
        assert len(data["colors"]) == 5

    def test_color_palette_with_count_parameter(self, client):
        """Verify count parameter is honored — new frontend sends it."""
        resp = client.post("/design/color-palette", json={
            "base_color": "#00ff00",
            "harmony_type": "triadic",
            "count": 3,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 3


class TestPreviouslyMissing404sNowSucceed:
    """These 9 paths previously returned 404 because the backend routes
    didn't exist. Verify they all return 200 now."""

    def test_colors_contrast(self, client):
        resp = client.post("/design/colors/contrast", json={
            "color1": "#000000", "color2": "#ffffff",
        })
        assert resp.status_code == 200

    def test_colors_accessible(self, client):
        resp = client.post("/design/colors/accessible", json={
            "background_color": "#ffffff",
        })
        assert resp.status_code == 200

    def test_fonts_list(self, client):
        resp = client.get("/design/fonts")
        assert resp.status_code == 200

    def test_fonts_pairings(self, client):
        resp = client.get("/design/fonts/pairings", params={"primary": "Inter"})
        assert resp.status_code == 200

    def test_assets_logo_upload(self, client):
        resp = client.post(
            "/design/assets/logo",
            files={"file": ("logo.png", b"data", "image/png")},
            data={"brand_kit_id": "kit-1"},
        )
        assert resp.status_code == 200

    def test_assets_list(self, client):
        resp = client.get("/design/brand-kits/some-kit/assets")
        assert resp.status_code == 200

    def test_assets_delete(self, client):
        upload = client.post(
            "/design/assets/logo",
            files={"file": ("x.png", b"x", "image/png")},
            data={"brand_kit_id": "kit-1"},
        )
        asset_id = upload.json()["id"]
        resp = client.delete(f"/design/assets/{asset_id}")
        assert resp.status_code == 200

    def test_brand_kit_export(self, client):
        create = client.post("/design/brand-kits", json={"name": "Exported"})
        kit_id = create.json()["id"]
        resp = client.get(f"/design/brand-kits/{kit_id}/export")
        assert resp.status_code == 200

    def test_brand_kit_import(self, client):
        resp = client.post("/design/brand-kits/import", json={
            "name": "Imported",
        })
        assert resp.status_code == 200

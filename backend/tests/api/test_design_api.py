"""Design API Route Tests.

Comprehensive tests for brand kit, theme, and color palette endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.design import router
from backend.app.api.middleware import limiter
from backend.app.services.design.service import DesignService
from backend.app.services.security import require_api_key


@pytest.fixture
def app():
    """Create a fresh FastAPI app with design routes."""
    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/design")
    # Disable rate limiting in tests to avoid false failures
    limiter.enabled = False
    yield _app
    limiter.enabled = True


@pytest.fixture
def app_no_auth():
    """App WITHOUT auth override - for testing auth enforcement."""
    _app = FastAPI()
    _app.include_router(router, prefix="/design")
    return _app


@pytest.fixture
def service():
    """Create a fresh DesignService and patch the module-level singleton.
    Also mock the state_store to prevent persistent data leaking across tests.
    """
    svc = DesignService()
    import backend.app.api.routes.design as mod
    original = mod.design_service
    mod.design_service = svc

    # Mock state_store to prevent file-system state leaks.
    # The store is lazily imported inside methods, so patch at its source module.
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
    """Create a test client with a fresh service."""
    return TestClient(app)


def _brand_kit_payload(**overrides):
    base = {
        "name": "Test Brand",
        "description": "A test brand kit",
        "primary_color": "#1976d2",
        "secondary_color": "#dc004e",
        "accent_color": "#ff9800",
    }
    base.update(overrides)
    return base


def _theme_payload(**overrides):
    base = {
        "name": "Test Theme",
        "description": "A test theme",
        "mode": "light",
        "colors": {"primary": "#1976d2", "background": "#ffffff"},
    }
    base.update(overrides)
    return base


# =============================================================================
# BRAND KIT CRUD
# =============================================================================


class TestBrandKitCreate:
    def test_create_brand_kit(self, client):
        resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Brand"
        assert data["primary_color"] == "#1976d2"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_first_kit_is_default(self, client):
        resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        assert resp.json()["is_default"] is True

    def test_second_kit_not_default(self, client):
        client.post("/design/brand-kits", json=_brand_kit_payload(name="First"))
        resp = client.post("/design/brand-kits", json=_brand_kit_payload(name="Second"))
        assert resp.json()["is_default"] is False

    def test_create_with_colors(self, client):
        colors = [
            {"name": "Brand Blue", "hex": "#0066cc"},
            {"name": "Brand Red", "hex": "#cc0000", "rgb": [204, 0, 0]},
        ]
        resp = client.post("/design/brand-kits", json=_brand_kit_payload(colors=colors))
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 2

    def test_create_with_typography(self, client):
        typo = {"font_family": "Roboto", "base_size": 14, "scale_ratio": 1.5}
        resp = client.post("/design/brand-kits", json=_brand_kit_payload(typography=typo))
        assert resp.status_code == 200
        assert resp.json()["typography"]["font_family"] == "Roboto"

    def test_create_with_logos(self, client):
        resp = client.post("/design/brand-kits", json=_brand_kit_payload(
            logo_url="https://example.com/logo.png",
            logo_dark_url="https://example.com/logo-dark.png",
            favicon_url="https://example.com/favicon.ico",
        ))
        assert resp.status_code == 200
        data = resp.json()
        assert data["logo_url"] == "https://example.com/logo.png"
        assert data["logo_dark_url"] == "https://example.com/logo-dark.png"
        assert data["favicon_url"] == "https://example.com/favicon.ico"

    def test_create_minimal(self, client):
        """Only name is required."""
        resp = client.post("/design/brand-kits", json={"name": "Minimal"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Minimal"
        assert data["primary_color"] == "#1976d2"  # default


class TestBrandKitRead:
    def test_get_brand_kit(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        resp = client.get(f"/design/brand-kits/{kit_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == kit_id

    def test_get_nonexistent_brand_kit(self, client):
        resp = client.get("/design/brand-kits/nonexistent-id")
        assert resp.status_code == 404

    def test_list_brand_kits_empty(self, client):
        resp = client.get("/design/brand-kits")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_brand_kits(self, client):
        client.post("/design/brand-kits", json=_brand_kit_payload(name="Kit A"))
        client.post("/design/brand-kits", json=_brand_kit_payload(name="Kit B"))
        resp = client.get("/design/brand-kits")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestBrandKitUpdate:
    def test_update_brand_kit(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        resp = client.put(f"/design/brand-kits/{kit_id}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_update_colors(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        resp = client.put(f"/design/brand-kits/{kit_id}", json={
            "primary_color": "#ff0000",
            "secondary_color": "#00ff00",
        })
        assert resp.status_code == 200
        assert resp.json()["primary_color"] == "#ff0000"
        assert resp.json()["secondary_color"] == "#00ff00"

    def test_update_nonexistent(self, client):
        resp = client.put("/design/brand-kits/fake-id", json={"name": "X"})
        assert resp.status_code == 404

    def test_partial_update_preserves_other_fields(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        original_color = create_resp.json()["primary_color"]

        resp = client.put(f"/design/brand-kits/{kit_id}", json={"name": "New Name Only"})
        assert resp.json()["name"] == "New Name Only"
        assert resp.json()["primary_color"] == original_color


class TestBrandKitDelete:
    def test_delete_brand_kit(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        resp = client.delete(f"/design/brand-kits/{kit_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        # Verify it's gone
        get_resp = client.get(f"/design/brand-kits/{kit_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/design/brand-kits/no-such-id")
        assert resp.status_code == 404

    def test_delete_default_clears_default(self, client, service):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        assert service._default_brand_kit_id == kit_id

        client.delete(f"/design/brand-kits/{kit_id}")
        assert service._default_brand_kit_id is None


class TestBrandKitSetDefault:
    def test_set_default(self, client):
        r1 = client.post("/design/brand-kits", json=_brand_kit_payload(name="A")).json()
        r2 = client.post("/design/brand-kits", json=_brand_kit_payload(name="B")).json()

        # First kit is default
        assert r1["is_default"] is True
        assert r2["is_default"] is False

        # Set second as default
        resp = client.post(f"/design/brand-kits/{r2['id']}/set-default")
        assert resp.status_code == 200
        assert resp.json()["is_default"] is True

        # First should no longer be default
        get_first = client.get(f"/design/brand-kits/{r1['id']}")
        assert get_first.json()["is_default"] is False

    def test_set_default_nonexistent(self, client):
        resp = client.post("/design/brand-kits/bad-id/set-default")
        assert resp.status_code == 404


class TestApplyBrandKit:
    def test_apply_brand_kit(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]

        resp = client.post(f"/design/brand-kits/{kit_id}/apply", json={
            "document_id": "doc-123",
            "elements": ["header", "footer"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["document_id"] == "doc-123"
        assert data["elements_applied"] == ["header", "footer"]

    def test_apply_all_elements(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]

        resp = client.post(f"/design/brand-kits/{kit_id}/apply", json={
            "document_id": "doc-456",
        })
        assert resp.status_code == 200
        assert resp.json()["elements_applied"] == ["all"]

    def test_apply_nonexistent_kit(self, client):
        resp = client.post("/design/brand-kits/bad-id/apply", json={
            "document_id": "doc-123",
        })
        assert resp.status_code == 400


# =============================================================================
# COLOR PALETTE
# =============================================================================


class TestColorPalette:
    def test_complementary(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "harmony_type": "complementary",
            "count": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["base_color"] == "#ff0000"
        assert data["harmony_type"] == "complementary"
        assert len(data["colors"]) == 5

    def test_analogous(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#0000ff",
            "harmony_type": "analogous",
            "count": 5,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 5

    def test_triadic(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#00ff00",
            "harmony_type": "triadic",
            "count": 3,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 3

    def test_split_complementary(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff6600",
            "harmony_type": "split-complementary",
            "count": 5,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 5

    def test_tetradic(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#9900cc",
            "harmony_type": "tetradic",
            "count": 4,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 4

    def test_base_color_always_first(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#aabbcc",
            "harmony_type": "complementary",
            "count": 3,
        })
        colors = resp.json()["colors"]
        assert colors[0]["hex"] == "#aabbcc"
        assert colors[0]["name"] == "Base"

    def test_default_count(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#123456",
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 5

    def test_colors_have_hex_and_name(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "harmony_type": "triadic",
            "count": 3,
        })
        for color in resp.json()["colors"]:
            assert "hex" in color
            assert "name" in color
            assert color["hex"].startswith("#")

    def test_count_limits_output(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "harmony_type": "tetradic",
            "count": 2,
        })
        assert len(resp.json()["colors"]) == 2


# =============================================================================
# THEME CRUD
# =============================================================================


class TestThemeCreate:
    def test_create_theme(self, client):
        resp = client.post("/design/themes", json=_theme_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Theme"
        assert data["mode"] == "light"
        assert "id" in data

    def test_first_theme_is_active(self, client):
        resp = client.post("/design/themes", json=_theme_payload())
        assert resp.json()["is_active"] is True

    def test_second_theme_not_active(self, client):
        client.post("/design/themes", json=_theme_payload(name="First"))
        resp = client.post("/design/themes", json=_theme_payload(name="Second"))
        assert resp.json()["is_active"] is False

    def test_create_dark_theme(self, client):
        resp = client.post("/design/themes", json=_theme_payload(
            name="Dark Mode",
            mode="dark",
            colors={"primary": "#bb86fc", "background": "#121212"},
        ))
        assert resp.status_code == 200
        assert resp.json()["mode"] == "dark"

    def test_create_with_all_options(self, client):
        resp = client.post("/design/themes", json={
            "name": "Full Theme",
            "description": "Complete theme",
            "brand_kit_id": "kit-123",
            "mode": "auto",
            "colors": {"primary": "#fff"},
            "typography": {"font": "Arial"},
            "spacing": {"unit": "8px"},
            "borders": {"radius": "4px"},
            "shadows": {"elevation": "2"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["brand_kit_id"] == "kit-123"
        assert data["typography"]["font"] == "Arial"
        assert data["spacing"]["unit"] == "8px"

    def test_create_minimal(self, client):
        resp = client.post("/design/themes", json={"name": "Bare"})
        assert resp.status_code == 200
        assert resp.json()["colors"] == {}


class TestThemeRead:
    def test_get_theme(self, client):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        resp = client.get(f"/design/themes/{theme_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == theme_id

    def test_get_nonexistent(self, client):
        resp = client.get("/design/themes/no-such-id")
        assert resp.status_code == 404

    def test_list_themes_empty(self, client):
        resp = client.get("/design/themes")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_themes(self, client):
        client.post("/design/themes", json=_theme_payload(name="T1"))
        client.post("/design/themes", json=_theme_payload(name="T2"))
        resp = client.get("/design/themes")
        assert len(resp.json()) == 2


class TestThemeUpdate:
    def test_update_theme(self, client):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        resp = client.put(f"/design/themes/{theme_id}", json={"name": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    def test_update_mode(self, client):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        resp = client.put(f"/design/themes/{theme_id}", json={"mode": "dark"})
        assert resp.json()["mode"] == "dark"

    def test_update_nonexistent(self, client):
        resp = client.put("/design/themes/fake-id", json={"name": "X"})
        assert resp.status_code == 404

    def test_partial_update_preserves_fields(self, client):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        original_mode = create_resp.json()["mode"]

        resp = client.put(f"/design/themes/{theme_id}", json={"name": "New Name"})
        assert resp.json()["mode"] == original_mode


class TestThemeDelete:
    def test_delete_theme(self, client):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        resp = client.delete(f"/design/themes/{theme_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        get_resp = client.get(f"/design/themes/{theme_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/design/themes/no-such-id")
        assert resp.status_code == 404

    def test_delete_active_clears_active(self, client, service):
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        assert service._active_theme_id == theme_id

        client.delete(f"/design/themes/{theme_id}")
        assert service._active_theme_id is None


class TestThemeActivate:
    def test_activate_theme(self, client):
        t1 = client.post("/design/themes", json=_theme_payload(name="A")).json()
        t2 = client.post("/design/themes", json=_theme_payload(name="B")).json()

        assert t1["is_active"] is True
        assert t2["is_active"] is False

        resp = client.post(f"/design/themes/{t2['id']}/activate")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

        get_first = client.get(f"/design/themes/{t1['id']}")
        assert get_first.json()["is_active"] is False

    def test_activate_nonexistent(self, client):
        resp = client.post("/design/themes/bad-id/activate")
        assert resp.status_code == 404


# =============================================================================
# SERVICE UNIT TESTS
# =============================================================================


class TestDesignServiceUnit:
    @pytest.mark.asyncio
    async def test_generate_color_palette_all_harmonies(self):
        svc = DesignService()
        for harmony in ["complementary", "analogous", "triadic", "split-complementary", "tetradic"]:
            result = svc.generate_color_palette("#ff0000", harmony, 5)
            assert result.base_color == "#ff0000"
            assert len(result.colors) == 5

    @pytest.mark.asyncio
    async def test_set_default_clears_previous(self):
        svc = DesignService()
        from backend.app.schemas.design.brand_kit import BrandKitCreate
        k1 = await svc.create_brand_kit(BrandKitCreate(name="A"))
        k2 = await svc.create_brand_kit(BrandKitCreate(name="B"))
        assert k1.is_default is True
        assert k2.is_default is False

        result = await svc.set_default_brand_kit(k2.id)
        assert result.is_default is True

        refreshed = await svc.get_brand_kit(k1.id)
        assert refreshed.is_default is False

    @pytest.mark.asyncio
    async def test_set_active_theme_clears_previous(self):
        svc = DesignService()
        from backend.app.schemas.design.brand_kit import ThemeCreate
        t1 = await svc.create_theme(ThemeCreate(name="A"))
        t2 = await svc.create_theme(ThemeCreate(name="B"))
        assert t1.is_active is True
        assert t2.is_active is False

        result = await svc.set_active_theme(t2.id)
        assert result.is_active is True

        refreshed = await svc.get_theme(t1.id)
        assert refreshed.is_active is False

    @pytest.mark.asyncio
    async def test_apply_nonexistent_kit(self):
        svc = DesignService()
        result = await svc.apply_brand_kit("no-such-id", "doc-1")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_delete_returns_false_for_missing(self):
        svc = DesignService()
        assert await svc.delete_brand_kit("nope") is False
        assert await svc.delete_theme("nope") is False

    @pytest.mark.asyncio
    async def test_update_returns_none_for_missing(self):
        svc = DesignService()
        from backend.app.schemas.design.brand_kit import BrandKitUpdate, ThemeUpdate
        assert await svc.update_brand_kit("x", BrandKitUpdate(name="Y")) is None
        assert await svc.update_theme("x", ThemeUpdate(name="Y")) is None


class TestColorConversions:
    """Test color utility functions."""

    def test_hex_to_rgb(self):
        from backend.app.services.design.service import _hex_to_rgb
        assert _hex_to_rgb("#ff0000") == (255, 0, 0)
        assert _hex_to_rgb("#00ff00") == (0, 255, 0)
        assert _hex_to_rgb("#0000ff") == (0, 0, 255)
        assert _hex_to_rgb("ffffff") == (255, 255, 255)  # no hash

    def test_rgb_to_hex(self):
        from backend.app.services.design.service import _rgb_to_hex
        assert _rgb_to_hex((255, 0, 0)) == "#ff0000"
        assert _rgb_to_hex((0, 0, 0)) == "#000000"

    def test_roundtrip(self):
        from backend.app.services.design.service import _hex_to_rgb, _rgb_to_hex
        original = "#1a2b3c"
        assert _rgb_to_hex(_hex_to_rgb(original)) == original

    def test_hsl_roundtrip(self):
        from backend.app.services.design.service import _rgb_to_hsl, _hsl_to_rgb
        rgb = (128, 64, 192)
        h, s, l = _rgb_to_hsl(*rgb)
        back = _hsl_to_rgb(h, s, l)
        # Allow ±1 for rounding
        for a, b in zip(rgb, back):
            assert abs(a - b) <= 1


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    def test_multiple_deletes_same_kit(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        client.delete(f"/design/brand-kits/{kit_id}")
        resp = client.delete(f"/design/brand-kits/{kit_id}")
        assert resp.status_code == 404

    def test_update_after_delete(self, client):
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        client.delete(f"/design/brand-kits/{kit_id}")
        resp = client.put(f"/design/brand-kits/{kit_id}", json={"name": "Ghost"})
        assert resp.status_code == 404

    def test_create_many_kits(self, client):
        for i in range(20):
            resp = client.post("/design/brand-kits", json=_brand_kit_payload(name=f"Kit {i}"))
            assert resp.status_code == 200

        resp = client.get("/design/brand-kits")
        assert len(resp.json()) == 20

    def test_create_many_themes(self, client):
        for i in range(20):
            resp = client.post("/design/themes", json=_theme_payload(name=f"Theme {i}"))
            assert resp.status_code == 200

        resp = client.get("/design/themes")
        assert len(resp.json()) == 20

    def test_color_palette_count_1(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "count": 1,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 1

    def test_color_palette_large_count(self, client):
        resp = client.post("/design/color-palette", json={
            "base_color": "#ff0000",
            "harmony_type": "complementary",
            "count": 20,
        })
        assert resp.status_code == 200
        assert len(resp.json()["colors"]) == 20

    def test_set_default_already_default(self, client):
        """Setting default on already-default kit should be idempotent."""
        create_resp = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create_resp.json()["id"]
        resp = client.post(f"/design/brand-kits/{kit_id}/set-default")
        assert resp.status_code == 200
        assert resp.json()["is_default"] is True

    def test_activate_already_active_theme(self, client):
        """Activating already-active theme should be idempotent."""
        create_resp = client.post("/design/themes", json=_theme_payload())
        theme_id = create_resp.json()["id"]
        resp = client.post(f"/design/themes/{theme_id}/activate")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True


# =============================================================================
# SECURITY TESTS
# =============================================================================


class TestDesignAuth:
    """Design routes have API key authentication wired up."""

    def test_router_has_auth_dependency(self):
        """Verify the router declares require_api_key as a dependency."""
        from backend.app.api.routes.design import router as design_router
        from backend.app.services.security import require_api_key
        dep_callables = [d.dependency for d in design_router.dependencies]
        assert require_api_key in dep_callables


class TestDesignPagination:
    """Pagination parameter constraints."""

    def test_brand_kits_limit_too_high(self, client):
        resp = client.get("/design/brand-kits?limit=999")
        assert resp.status_code == 422

    def test_brand_kits_limit_zero(self, client):
        resp = client.get("/design/brand-kits?limit=0")
        assert resp.status_code == 422

    def test_brand_kits_offset_negative(self, client):
        resp = client.get("/design/brand-kits?offset=-1")
        assert resp.status_code == 422

    def test_themes_limit_too_high(self, client):
        resp = client.get("/design/themes?limit=999")
        assert resp.status_code == 422

    def test_themes_default_pagination(self, client):
        resp = client.get("/design/themes")
        assert resp.status_code == 200


# =============================================================================
# COLOR CONTRAST
# =============================================================================


class TestColorContrast:
    def test_black_on_white(self, client):
        resp = client.post("/design/colors/contrast", json={
            "color1": "#000000",
            "color2": "#ffffff",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["contrast_ratio"] == 21.0
        assert data["wcag_aa_normal"] is True
        assert data["wcag_aa_large"] is True
        assert data["wcag_aaa_normal"] is True
        assert data["wcag_aaa_large"] is True

    def test_same_color_is_1(self, client):
        resp = client.post("/design/colors/contrast", json={
            "color1": "#ff0000",
            "color2": "#ff0000",
        })
        assert resp.status_code == 200
        assert resp.json()["contrast_ratio"] == 1.0

    def test_low_contrast_fails_wcag(self, client):
        # Light gray on white — poor contrast
        resp = client.post("/design/colors/contrast", json={
            "color1": "#cccccc",
            "color2": "#ffffff",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["wcag_aa_normal"] is False
        assert data["wcag_aaa_normal"] is False

    def test_response_includes_input_colors(self, client):
        resp = client.post("/design/colors/contrast", json={
            "color1": "#1a2b3c",
            "color2": "#f0e0d0",
        })
        data = resp.json()
        assert data["color1"] == "#1a2b3c"
        assert data["color2"] == "#f0e0d0"


# =============================================================================
# ACCESSIBLE COLORS
# =============================================================================


class TestAccessibleColors:
    def test_white_background(self, client):
        resp = client.post("/design/colors/accessible", json={
            "background_color": "#ffffff",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["background_color"] == "#ffffff"
        assert len(data["colors"]) > 0
        # All suggestions must meet WCAG AA (4.5:1)
        for c in data["colors"]:
            assert c["contrast_ratio"] >= 4.5

    def test_dark_background(self, client):
        resp = client.post("/design/colors/accessible", json={
            "background_color": "#000000",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["colors"]) > 0
        for c in data["colors"]:
            assert c["contrast_ratio"] >= 4.5

    def test_sorted_by_contrast(self, client):
        resp = client.post("/design/colors/accessible", json={
            "background_color": "#ffffff",
        })
        ratios = [c["contrast_ratio"] for c in resp.json()["colors"]]
        assert ratios == sorted(ratios, reverse=True)


# =============================================================================
# FONTS
# =============================================================================


class TestFonts:
    def test_list_fonts(self, client):
        resp = client.get("/design/fonts")
        assert resp.status_code == 200
        fonts = resp.json()
        assert len(fonts) > 0
        for f in fonts:
            assert "name" in f
            assert "category" in f
            assert "weights" in f

    def test_fonts_include_inter(self, client):
        resp = client.get("/design/fonts")
        names = [f["name"] for f in resp.json()]
        assert "Inter" in names

    def test_font_categories(self, client):
        resp = client.get("/design/fonts")
        categories = {f["category"] for f in resp.json()}
        # Should have at least sans-serif, serif, monospace
        assert "sans-serif" in categories
        assert "serif" in categories
        assert "monospace" in categories


class TestFontPairings:
    def test_pairings_for_serif(self, client):
        resp = client.get("/design/fonts/pairings", params={"primary": "Merriweather"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["primary"] == "Merriweather"
        assert len(data["pairings"]) > 0
        for p in data["pairings"]:
            assert "font" in p
            assert "category" in p
            assert "reason" in p

    def test_pairings_for_sans_serif(self, client):
        resp = client.get("/design/fonts/pairings", params={"primary": "Inter"})
        assert resp.status_code == 200
        assert len(resp.json()["pairings"]) > 0

    def test_pairings_for_unknown_font(self, client):
        """Unknown fonts get default sans-serif pairings."""
        resp = client.get("/design/fonts/pairings", params={"primary": "UnknownFont"})
        assert resp.status_code == 200
        assert len(resp.json()["pairings"]) > 0

    def test_pairings_requires_primary(self, client):
        resp = client.get("/design/fonts/pairings")
        assert resp.status_code == 422  # missing required query param


# =============================================================================
# ASSETS
# =============================================================================


class TestAssets:
    def test_upload_logo(self, client):
        resp = client.post(
            "/design/assets/logo",
            files={"file": ("logo.png", b"fake-png-content", "image/png")},
            data={"brand_kit_id": "kit-123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "logo.png"
        assert data["brand_kit_id"] == "kit-123"
        assert data["asset_type"] == "logo"
        assert data["size_bytes"] == len(b"fake-png-content")
        assert "id" in data
        assert "created_at" in data

    def test_list_assets_empty(self, client):
        resp = client.get("/design/brand-kits/no-kit/assets")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_assets_after_upload(self, client):
        client.post(
            "/design/assets/logo",
            files={"file": ("logo1.png", b"data1", "image/png")},
            data={"brand_kit_id": "kit-abc"},
        )
        client.post(
            "/design/assets/logo",
            files={"file": ("logo2.png", b"data2", "image/png")},
            data={"brand_kit_id": "kit-abc"},
        )
        resp = client.get("/design/brand-kits/kit-abc/assets")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_asset(self, client):
        upload = client.post(
            "/design/assets/logo",
            files={"file": ("logo.png", b"data", "image/png")},
            data={"brand_kit_id": "kit-del"},
        )
        asset_id = upload.json()["id"]

        resp = client.delete(f"/design/assets/{asset_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        # Verify gone
        assets = client.get("/design/brand-kits/kit-del/assets")
        assert len(assets.json()) == 0

    def test_delete_nonexistent_asset(self, client):
        resp = client.delete("/design/assets/no-such-asset")
        assert resp.status_code == 404

    def test_assets_filtered_by_kit(self, client):
        """Assets for one kit don't appear in another's list."""
        client.post(
            "/design/assets/logo",
            files={"file": ("a.png", b"data", "image/png")},
            data={"brand_kit_id": "kit-A"},
        )
        client.post(
            "/design/assets/logo",
            files={"file": ("b.png", b"data", "image/png")},
            data={"brand_kit_id": "kit-B"},
        )
        resp_a = client.get("/design/brand-kits/kit-A/assets")
        resp_b = client.get("/design/brand-kits/kit-B/assets")
        assert len(resp_a.json()) == 1
        assert len(resp_b.json()) == 1


# =============================================================================
# EXPORT / IMPORT
# =============================================================================


class TestExportImport:
    def test_export_brand_kit(self, client):
        create = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create.json()["id"]

        resp = client.get(f"/design/brand-kits/{kit_id}/export")
        assert resp.status_code == 200
        data = resp.json()
        assert data["format"] == "json"
        assert data["brand_kit"]["id"] == kit_id
        assert data["brand_kit"]["name"] == "Test Brand"

    def test_export_nonexistent(self, client):
        resp = client.get("/design/brand-kits/no-kit/export")
        assert resp.status_code == 404

    def test_export_with_format_param(self, client):
        create = client.post("/design/brand-kits", json=_brand_kit_payload())
        kit_id = create.json()["id"]

        resp = client.get(f"/design/brand-kits/{kit_id}/export", params={"format": "css"})
        assert resp.status_code == 200
        assert resp.json()["format"] == "css"

    def test_import_brand_kit(self, client):
        resp = client.post("/design/brand-kits/import", json={
            "name": "Imported Kit",
            "primary_color": "#aabbcc",
            "secondary_color": "#112233",
            "accent_color": "#ff9900",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Imported Kit"
        assert data["primary_color"] == "#aabbcc"
        assert "id" in data

    def test_import_minimal(self, client):
        resp = client.post("/design/brand-kits/import", json={
            "name": "Bare Import",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bare Import"

    def test_roundtrip_export_import(self, client):
        """Export then import should produce equivalent kit."""
        create = client.post("/design/brand-kits", json=_brand_kit_payload(
            name="Roundtrip",
            primary_color="#112233",
        ))
        kit_id = create.json()["id"]

        exported = client.get(f"/design/brand-kits/{kit_id}/export").json()
        kit_data = exported["brand_kit"]

        imported = client.post("/design/brand-kits/import", json=kit_data).json()
        assert imported["name"] == "Roundtrip"
        assert imported["primary_color"] == "#112233"
        assert imported["id"] != kit_id  # new ID assigned

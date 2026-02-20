"""Data Enrichment API Route Tests.

Comprehensive tests for enrichment source management, data enrichment,
preview, cache operations, and authentication guard endpoints.
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.enrichment import router, get_service
from backend.app.services.enrichment.service import EnrichmentService
from backend.app.services.security import require_api_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_service():
    """Create a fully-mocked EnrichmentService."""
    svc = MagicMock(spec=EnrichmentService)
    # Default return values for sync methods
    svc.list_sources.return_value = []
    svc.get_available_source_types.return_value = []
    svc.get_source.return_value = None
    svc.delete_source.return_value = False
    svc.get_cache_stats.return_value = {}
    svc.clear_cache.return_value = 0
    # Async methods need AsyncMock
    svc.simple_enrich = AsyncMock(return_value={
        "enriched_data": [],
        "total_rows": 0,
        "enriched_rows": 0,
        "processing_time_ms": 0,
    })
    svc.simple_preview = AsyncMock(return_value={
        "preview": [],
        "total_rows": 0,
        "enriched_rows": 0,
        "processing_time_ms": 0,
    })
    return svc


@pytest.fixture
def client(mock_service):
    """TestClient with the enrichment router mounted and dependencies overridden."""
    app = FastAPI()
    app.include_router(router, prefix="/enrichment")

    # Bypass the API key requirement
    app.dependency_overrides[require_api_key] = lambda: None
    # Return the mock service instead of creating a new one
    app.dependency_overrides[get_service] = lambda: mock_service

    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_data(n=3):
    """Return n rows of sample enrichment data."""
    return [{"company_name": f"Company {i}", "address": f"{i} Main St"} for i in range(n)]


def _make_custom_source_obj(**overrides):
    """Create a mock custom source object with .dict() and .model_dump() support."""
    defaults = {
        "id": "custom-abc",
        "name": "Custom Source",
        "type": "custom",
        "description": "A custom source",
        "enabled": True,
        "config": {},
        "cache_ttl_hours": 24,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }
    defaults.update(overrides)
    obj = MagicMock()
    obj.dict.return_value = defaults
    obj.model_dump.return_value = defaults
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ===================================================================
# 1. List Sources  (GET /enrichment/sources)
# ===================================================================

class TestListSources:
    """GET /enrichment/sources"""

    def test_list_sources_returns_builtin_only(self, client, mock_service):
        """When no custom sources exist, only built-in sources are returned."""
        mock_service.list_sources.return_value = []
        resp = client.get("/enrichment/sources")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert len(body["sources"]) == 3

    def test_list_sources_builtin_ids(self, client, mock_service):
        """Built-in source IDs should be company, address, exchange."""
        mock_service.list_sources.return_value = []
        resp = client.get("/enrichment/sources")
        ids = [s["id"] for s in resp.json()["sources"]]
        assert "company" in ids
        assert "address" in ids
        assert "exchange" in ids

    def test_list_sources_builtin_structure(self, client, mock_service):
        """Each built-in source should have required keys."""
        mock_service.list_sources.return_value = []
        resp = client.get("/enrichment/sources")
        for source in resp.json()["sources"]:
            assert "id" in source
            assert "name" in source
            assert "type" in source
            assert "description" in source
            assert "required_fields" in source
            assert "output_fields" in source

    def test_list_sources_includes_custom(self, client, mock_service):
        """Custom sources are appended after built-in sources."""
        custom = _make_custom_source_obj(id="custom-1", name="My Custom")
        mock_service.list_sources.return_value = [custom]
        resp = client.get("/enrichment/sources")
        body = resp.json()
        assert len(body["sources"]) == 4
        assert body["sources"][-1]["id"] == "custom-1"
        assert body["sources"][-1]["name"] == "My Custom"

    def test_list_sources_multiple_custom(self, client, mock_service):
        """Multiple custom sources are all appended."""
        custom_a = _make_custom_source_obj(id="cust-a", name="Custom A")
        custom_b = _make_custom_source_obj(id="cust-b", name="Custom B")
        mock_service.list_sources.return_value = [custom_a, custom_b]
        resp = client.get("/enrichment/sources")
        body = resp.json()
        assert len(body["sources"]) == 5
        custom_ids = [s["id"] for s in body["sources"][3:]]
        assert "cust-a" in custom_ids
        assert "cust-b" in custom_ids

    def test_list_sources_has_correlation_id(self, client, mock_service):
        """Response should include correlation_id key."""
        resp = client.get("/enrichment/sources")
        assert "correlation_id" in resp.json()


# ===================================================================
# 2. List Source Types  (GET /enrichment/source-types)
# ===================================================================

class TestListSourceTypes:
    """GET /enrichment/source-types"""

    def test_list_source_types_success(self, client, mock_service):
        mock_service.get_available_source_types.return_value = [
            {"type": "company_info", "name": "Company Info", "supported_fields": ["industry"]},
        ]
        resp = client.get("/enrichment/source-types")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert len(body["source_types"]) == 1
        assert body["source_types"][0]["type"] == "company_info"

    def test_list_source_types_empty(self, client, mock_service):
        mock_service.get_available_source_types.return_value = []
        resp = client.get("/enrichment/source-types")
        assert resp.status_code == 200
        assert resp.json()["source_types"] == []

    def test_list_source_types_has_correlation_id(self, client, mock_service):
        resp = client.get("/enrichment/source-types")
        assert "correlation_id" in resp.json()

    def test_list_source_types_multiple(self, client, mock_service):
        types = [
            {"type": "company_info", "name": "Company Info", "supported_fields": ["industry"]},
            {"type": "address", "name": "Address", "supported_fields": ["city"]},
            {"type": "exchange_rate", "name": "Exchange Rate", "supported_fields": ["rate"]},
        ]
        mock_service.get_available_source_types.return_value = types
        resp = client.get("/enrichment/source-types")
        assert len(resp.json()["source_types"]) == 3


# ===================================================================
# 3. Enrich Data  (POST /enrichment/enrich)
# ===================================================================

class TestEnrichData:
    """POST /enrichment/enrich"""

    def test_enrich_success(self, client, mock_service):
        data = _sample_data(2)
        enriched = [
            {**row, "industry": "Tech"} for row in data
        ]
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": enriched,
            "total_rows": 2,
            "enriched_rows": 2,
            "processing_time_ms": 42,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["total_rows"] == 2
        assert body["enriched_rows"] == 2
        assert body["processing_time_ms"] == 42
        assert len(body["enriched_data"]) == 2

    def test_enrich_with_options(self, client, mock_service):
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"amount": 100, "converted_amount": 85}],
            "total_rows": 1,
            "enriched_rows": 1,
            "processing_time_ms": 10,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"amount": 100, "currency": "USD"}],
            "sources": ["exchange"],
            "options": {"target_currency": "EUR"},
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["enriched_rows"] == 1

    def test_enrich_multiple_sources(self, client, mock_service):
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"company_name": "Acme", "industry": "Tech", "formatted_address": "123 Main"}],
            "total_rows": 1,
            "enriched_rows": 1,
            "processing_time_ms": 55,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"company_name": "Acme", "address": "123 Main St"}],
            "sources": ["company", "address"],
        })
        assert resp.status_code == 200
        assert resp.json()["enriched_rows"] == 1

    def test_enrich_empty_data_validation(self, client):
        """Empty data list should fail validation (min_items=1)."""
        resp = client.post("/enrichment/enrich", json={
            "data": [],
            "sources": ["company"],
        })
        assert resp.status_code == 422

    def test_enrich_missing_data_field(self, client):
        resp = client.post("/enrichment/enrich", json={
            "sources": ["company"],
        })
        assert resp.status_code == 422

    def test_enrich_empty_sources_validation(self, client):
        """Empty sources list should fail validation (min_items=1)."""
        resp = client.post("/enrichment/enrich", json={
            "data": [{"company_name": "Acme"}],
            "sources": [],
        })
        assert resp.status_code == 422

    def test_enrich_missing_sources_field(self, client):
        resp = client.post("/enrichment/enrich", json={
            "data": [{"company_name": "Acme"}],
        })
        assert resp.status_code == 422

    def test_enrich_too_many_sources(self, client):
        """More than 10 sources should fail validation (max_items=10)."""
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": [f"src_{i}" for i in range(11)],
        })
        assert resp.status_code == 422

    def test_enrich_service_error(self, client, mock_service):
        """When the service raises an exception, 500 is returned."""
        mock_service.simple_enrich = AsyncMock(side_effect=RuntimeError("DB connection failed"))
        resp = client.post("/enrichment/enrich", json={
            "data": [{"company_name": "Acme"}],
            "sources": ["company"],
        })
        assert resp.status_code == 500

    def test_enrich_has_correlation_id(self, client, mock_service):
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [],
            "total_rows": 0,
            "enriched_rows": 0,
            "processing_time_ms": 0,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert "correlation_id" in resp.json()

    def test_enrich_zero_enriched_rows(self, client, mock_service):
        """When no rows are enriched, enriched_rows should be 0."""
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"x": 1}],
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 3,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert resp.status_code == 200
        assert resp.json()["enriched_rows"] == 0

    def test_enrich_default_options_empty(self, client, mock_service):
        """Omitting options should default to empty dict."""
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"x": 1}],
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 1,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert resp.status_code == 200
        # Verify options kwarg was passed as empty dict
        call_kwargs = mock_service.simple_enrich.call_args
        assert call_kwargs.kwargs.get("options") == {} or call_kwargs[1].get("options") == {}


# ===================================================================
# 4. Preview Enrichment  (POST /enrichment/preview)
# ===================================================================

class TestPreviewEnrichment:
    """POST /enrichment/preview"""

    def test_preview_success(self, client, mock_service):
        data = _sample_data(5)
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": data[:3],
            "total_rows": 5,
            "enriched_rows": 3,
            "processing_time_ms": 20,
        })
        resp = client.post("/enrichment/preview", json={
            "data": data,
            "sources": ["company"],
            "sample_size": 3,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert len(body["preview"]) == 3
        assert body["total_rows"] == 5
        assert body["enriched_rows"] == 3
        assert body["processing_time_ms"] == 20

    def test_preview_default_sample_size(self, client, mock_service):
        """When sample_size is omitted, default is 5."""
        data = _sample_data(10)
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": data[:5],
            "total_rows": 10,
            "enriched_rows": 5,
            "processing_time_ms": 15,
        })
        resp = client.post("/enrichment/preview", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 200
        call_kwargs = mock_service.simple_preview.call_args
        assert call_kwargs.kwargs.get("sample_size") == 5 or call_kwargs[1].get("sample_size") == 5

    def test_preview_sample_size_min_boundary(self, client, mock_service):
        """sample_size=1 should succeed (ge=1)."""
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": [{"x": 1}],
            "total_rows": 1,
            "enriched_rows": 1,
            "processing_time_ms": 5,
        })
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
            "sample_size": 1,
        })
        assert resp.status_code == 200

    def test_preview_sample_size_max_boundary(self, client, mock_service):
        """sample_size=10 should succeed (le=10)."""
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": [],
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 1,
        })
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
            "sample_size": 10,
        })
        assert resp.status_code == 200

    def test_preview_sample_size_too_large(self, client):
        """sample_size=11 should fail (le=10)."""
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
            "sample_size": 11,
        })
        assert resp.status_code == 422

    def test_preview_sample_size_too_small(self, client):
        """sample_size=0 should fail (ge=1)."""
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
            "sample_size": 0,
        })
        assert resp.status_code == 422

    def test_preview_empty_data_validation(self, client):
        resp = client.post("/enrichment/preview", json={
            "data": [],
            "sources": ["company"],
        })
        assert resp.status_code == 422

    def test_preview_empty_sources_validation(self, client):
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": [],
        })
        assert resp.status_code == 422

    def test_preview_service_error(self, client, mock_service):
        mock_service.simple_preview = AsyncMock(side_effect=RuntimeError("Preview failed"))
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert resp.status_code == 500

    def test_preview_has_correlation_id(self, client, mock_service):
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": [],
            "total_rows": 0,
            "enriched_rows": 0,
            "processing_time_ms": 0,
        })
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert "correlation_id" in resp.json()


# ===================================================================
# 5. Create Source  (POST /enrichment/sources/create)
# ===================================================================

class TestCreateSource:
    """POST /enrichment/sources/create"""

    def test_create_source_company_info(self, client, mock_service):
        created = _make_custom_source_obj(id="src-1", name="My Company Source", type="company_info")
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "My Company Source",
            "type": "company_info",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["source"]["name"] == "My Company Source"

    def test_create_source_address(self, client, mock_service):
        created = _make_custom_source_obj(id="src-2", name="Addr Source", type="address")
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Addr Source",
            "type": "address",
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["type"] == "address"

    def test_create_source_exchange_rate(self, client, mock_service):
        created = _make_custom_source_obj(id="src-3", name="FX Source", type="exchange_rate")
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "FX Source",
            "type": "exchange_rate",
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["type"] == "exchange_rate"

    def test_create_source_custom_type(self, client, mock_service):
        created = _make_custom_source_obj(id="src-4", name="Custom Src", type="custom")
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Custom Src",
            "type": "custom",
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["type"] == "custom"

    def test_create_source_with_description(self, client, mock_service):
        created = _make_custom_source_obj(
            id="src-5", name="Described", description="A source with description"
        )
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Described",
            "type": "custom",
            "description": "A source with description",
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["description"] == "A source with description"

    def test_create_source_with_config(self, client, mock_service):
        created = _make_custom_source_obj(
            id="src-6", name="Configured", config={"api_key": "test123"}
        )
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Configured",
            "type": "custom",
            "config": {"api_key": "test123"},
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["config"]["api_key"] == "test123"

    def test_create_source_with_cache_ttl(self, client, mock_service):
        created = _make_custom_source_obj(id="src-7", name="Cached", cache_ttl_hours=48)
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Cached",
            "type": "custom",
            "cache_ttl_hours": 48,
        })
        assert resp.status_code == 200
        assert resp.json()["source"]["cache_ttl_hours"] == 48

    def test_create_source_name_empty(self, client):
        """Empty name should fail (min_length=1)."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "",
            "type": "custom",
        })
        assert resp.status_code == 422

    def test_create_source_name_too_long(self, client):
        """Name exceeding 100 chars should fail (max_length=100)."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "x" * 101,
            "type": "custom",
        })
        assert resp.status_code == 422

    def test_create_source_name_max_boundary(self, client, mock_service):
        """Name of exactly 100 chars should succeed."""
        name = "A" * 100
        created = _make_custom_source_obj(id="src-b", name=name)
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": name,
            "type": "custom",
        })
        assert resp.status_code == 200

    def test_create_source_invalid_type(self, client):
        """Invalid type should fail validation."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "Bad Type",
            "type": "nonexistent_type",
        })
        assert resp.status_code == 422

    def test_create_source_missing_type(self, client):
        resp = client.post("/enrichment/sources/create", json={
            "name": "No Type",
        })
        assert resp.status_code == 422

    def test_create_source_cache_ttl_too_low(self, client):
        """cache_ttl_hours=0 should fail (ge=1)."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "Bad TTL",
            "type": "custom",
            "cache_ttl_hours": 0,
        })
        assert resp.status_code == 422

    def test_create_source_cache_ttl_too_high(self, client):
        """cache_ttl_hours=721 should fail (le=720)."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "Bad TTL High",
            "type": "custom",
            "cache_ttl_hours": 721,
        })
        assert resp.status_code == 422

    def test_create_source_cache_ttl_min_boundary(self, client, mock_service):
        """cache_ttl_hours=1 should succeed (ge=1)."""
        created = _make_custom_source_obj(cache_ttl_hours=1)
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Min TTL",
            "type": "custom",
            "cache_ttl_hours": 1,
        })
        assert resp.status_code == 200

    def test_create_source_cache_ttl_max_boundary(self, client, mock_service):
        """cache_ttl_hours=720 should succeed (le=720)."""
        created = _make_custom_source_obj(cache_ttl_hours=720)
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Max TTL",
            "type": "custom",
            "cache_ttl_hours": 720,
        })
        assert resp.status_code == 200

    def test_create_source_description_too_long(self, client):
        """Description exceeding 500 chars should fail (max_length=500)."""
        resp = client.post("/enrichment/sources/create", json={
            "name": "Long Desc",
            "type": "custom",
            "description": "D" * 501,
        })
        assert resp.status_code == 422

    def test_create_source_has_correlation_id(self, client, mock_service):
        created = _make_custom_source_obj()
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "With Corr ID",
            "type": "custom",
        })
        assert "correlation_id" in resp.json()


# ===================================================================
# 6. Get Source  (GET /enrichment/sources/{source_id})
# ===================================================================

class TestGetSource:
    """GET /enrichment/sources/{source_id}"""

    def test_get_builtin_company(self, client, mock_service):
        resp = client.get("/enrichment/sources/company")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["source"]["id"] == "company"
        assert body["source"]["type"] == "company_info"

    def test_get_builtin_address(self, client, mock_service):
        resp = client.get("/enrichment/sources/address")
        assert resp.status_code == 200
        assert resp.json()["source"]["id"] == "address"
        assert resp.json()["source"]["type"] == "address"

    def test_get_builtin_exchange(self, client, mock_service):
        resp = client.get("/enrichment/sources/exchange")
        assert resp.status_code == 200
        assert resp.json()["source"]["id"] == "exchange"
        assert resp.json()["source"]["type"] == "exchange_rate"

    def test_get_builtin_source_structure(self, client, mock_service):
        """Built-in sources should have all expected fields."""
        resp = client.get("/enrichment/sources/company")
        source = resp.json()["source"]
        assert "name" in source
        assert "description" in source
        assert "required_fields" in source
        assert "output_fields" in source

    def test_get_custom_source(self, client, mock_service):
        custom = _make_custom_source_obj(id="custom-99", name="My Custom")
        mock_service.get_source.return_value = custom
        resp = client.get("/enrichment/sources/custom-99")
        assert resp.status_code == 200
        body = resp.json()
        assert body["source"]["id"] == "custom-99"
        assert body["source"]["name"] == "My Custom"

    def test_get_source_not_found(self, client, mock_service):
        mock_service.get_source.return_value = None
        resp = client.get("/enrichment/sources/nonexistent-id")
        assert resp.status_code == 404
        detail = resp.json()["detail"]
        assert detail["code"] == "not_found"
        assert "not found" in detail["message"].lower()

    def test_get_source_builtin_takes_priority(self, client, mock_service):
        """If the ID matches a built-in, the service is NOT called."""
        resp = client.get("/enrichment/sources/company")
        assert resp.status_code == 200
        # Service get_source should not have been called for a built-in id
        mock_service.get_source.assert_not_called()

    def test_get_source_has_correlation_id(self, client, mock_service):
        resp = client.get("/enrichment/sources/company")
        assert "correlation_id" in resp.json()

    def test_get_source_custom_not_found_returns_404(self, client, mock_service):
        """When neither built-in nor custom matches, return 404."""
        mock_service.get_source.return_value = None
        resp = client.get("/enrichment/sources/does-not-exist")
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "not_found"


# ===================================================================
# 7. Delete Source  (DELETE /enrichment/sources/{source_id})
# ===================================================================

class TestDeleteSource:
    """DELETE /enrichment/sources/{source_id}"""

    def test_delete_source_success(self, client, mock_service):
        mock_service.delete_source.return_value = True
        resp = client.delete("/enrichment/sources/custom-1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["deleted"] is True
        assert body["source_id"] == "custom-1"

    def test_delete_source_not_found(self, client, mock_service):
        mock_service.delete_source.return_value = False
        resp = client.delete("/enrichment/sources/nonexistent")
        assert resp.status_code == 404
        detail = resp.json()["detail"]
        assert detail["code"] == "not_found"
        assert "not found" in detail["message"].lower() or "cannot be deleted" in detail["message"].lower()

    def test_delete_source_returns_source_id(self, client, mock_service):
        mock_service.delete_source.return_value = True
        resp = client.delete("/enrichment/sources/my-source")
        assert resp.json()["source_id"] == "my-source"

    def test_delete_source_has_correlation_id(self, client, mock_service):
        mock_service.delete_source.return_value = True
        resp = client.delete("/enrichment/sources/custom-1")
        assert "correlation_id" in resp.json()

    def test_delete_source_calls_service(self, client, mock_service):
        mock_service.delete_source.return_value = True
        client.delete("/enrichment/sources/target-id")
        mock_service.delete_source.assert_called_once_with("target-id")


# ===================================================================
# 8. Cache Stats  (GET /enrichment/cache/stats)
# ===================================================================

class TestCacheStats:
    """GET /enrichment/cache/stats"""

    def test_cache_stats_success(self, client, mock_service):
        mock_service.get_cache_stats.return_value = {
            "total_entries": 100,
            "hit_rate": 0.85,
            "sources": {"company": 60, "address": 40},
        }
        resp = client.get("/enrichment/cache/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["stats"]["total_entries"] == 100
        assert body["stats"]["hit_rate"] == 0.85

    def test_cache_stats_empty(self, client, mock_service):
        mock_service.get_cache_stats.return_value = {}
        resp = client.get("/enrichment/cache/stats")
        assert resp.status_code == 200
        assert resp.json()["stats"] == {}

    def test_cache_stats_has_correlation_id(self, client, mock_service):
        resp = client.get("/enrichment/cache/stats")
        assert "correlation_id" in resp.json()

    def test_cache_stats_calls_service(self, client, mock_service):
        client.get("/enrichment/cache/stats")
        mock_service.get_cache_stats.assert_called_once()


# ===================================================================
# 9. Clear Cache  (DELETE /enrichment/cache)
# ===================================================================

class TestClearCache:
    """DELETE /enrichment/cache"""

    def test_clear_cache_all(self, client, mock_service):
        mock_service.clear_cache.return_value = 42
        resp = client.delete("/enrichment/cache")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["cleared_entries"] == 42
        assert body["source_id"] is None

    def test_clear_cache_by_source_id(self, client, mock_service):
        mock_service.clear_cache.return_value = 15
        resp = client.delete("/enrichment/cache?source_id=company")
        assert resp.status_code == 200
        body = resp.json()
        assert body["cleared_entries"] == 15
        assert body["source_id"] == "company"

    def test_clear_cache_zero_entries(self, client, mock_service):
        mock_service.clear_cache.return_value = 0
        resp = client.delete("/enrichment/cache")
        assert resp.status_code == 200
        assert resp.json()["cleared_entries"] == 0

    def test_clear_cache_has_correlation_id(self, client, mock_service):
        resp = client.delete("/enrichment/cache")
        assert "correlation_id" in resp.json()

    def test_clear_cache_calls_service_with_none(self, client, mock_service):
        """When no source_id is provided, service is called with None."""
        client.delete("/enrichment/cache")
        mock_service.clear_cache.assert_called_once_with(None)

    def test_clear_cache_calls_service_with_source_id(self, client, mock_service):
        """When source_id is provided, service is called with that value."""
        client.delete("/enrichment/cache?source_id=address")
        mock_service.clear_cache.assert_called_once_with("address")


# ===================================================================
# 10. Auth / Dependency Guard
# ===================================================================

class TestAuth:
    """Verify that require_api_key is enforced when the override is removed.

    The ``require_api_key`` dependency in production raises a 401 when no
    valid API key is provided.  During pytest it auto-bypasses via an
    ``os.getenv("PYTEST_CURRENT_TEST")`` check, so we must patch that
    env var away *and* supply settings that force key validation.
    """

    def _make_no_auth_client(self, mock_service):
        """Create a client WITHOUT the require_api_key override so the
        real dependency runs -- but with the pytest bypass removed and
        settings that require a key."""
        from backend.app.services.config import get_settings

        mock_settings = MagicMock()
        mock_settings.allow_anonymous_api = False
        mock_settings.debug_mode = False
        mock_settings.api_key = "real-secret-key"

        app = FastAPI()
        app.include_router(router, prefix="/enrichment")
        # Override settings to enforce key validation, but do NOT override
        # require_api_key itself so that its logic runs.
        app.dependency_overrides[get_settings] = lambda: mock_settings
        app.dependency_overrides[get_service] = lambda: mock_service
        return TestClient(app, raise_server_exceptions=False)

    @patch.dict(os.environ, {}, clear=False)
    def test_list_sources_requires_auth(self, mock_service):
        # Remove the PYTEST_CURRENT_TEST env var so the bypass is disabled
        env = os.environ.copy()
        env.pop("PYTEST_CURRENT_TEST", None)
        with patch.dict(os.environ, env, clear=True):
            no_auth = self._make_no_auth_client(mock_service)
            resp = no_auth.get("/enrichment/sources")
            # Without a valid X-Api-Key header, should be rejected
            assert resp.status_code in (401, 403, 500)

    @patch.dict(os.environ, {}, clear=False)
    def test_enrich_requires_auth(self, mock_service):
        env = os.environ.copy()
        env.pop("PYTEST_CURRENT_TEST", None)
        with patch.dict(os.environ, env, clear=True):
            no_auth = self._make_no_auth_client(mock_service)
            resp = no_auth.post("/enrichment/enrich", json={
                "data": [{"x": 1}],
                "sources": ["company"],
            })
            assert resp.status_code in (401, 403, 500)

    @patch.dict(os.environ, {}, clear=False)
    def test_cache_stats_requires_auth(self, mock_service):
        env = os.environ.copy()
        env.pop("PYTEST_CURRENT_TEST", None)
        with patch.dict(os.environ, env, clear=True):
            no_auth = self._make_no_auth_client(mock_service)
            resp = no_auth.get("/enrichment/cache/stats")
            assert resp.status_code in (401, 403, 500)


# ===================================================================
# 11. Edge Cases
# ===================================================================

class TestEdgeCases:
    """Miscellaneous edge cases and boundary conditions."""

    def test_enrich_large_payload(self, client, mock_service):
        """Enriching the maximum allowed rows (1000) should be accepted."""
        data = [{"company_name": f"Company {i}"} for i in range(1000)]
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": data,
            "total_rows": 1000,
            "enriched_rows": 500,
            "processing_time_ms": 5000,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 200
        assert resp.json()["total_rows"] == 1000

    def test_enrich_over_max_rows(self, client):
        """Exceeding 1000 rows should fail validation (max_items=1000)."""
        data = [{"company_name": f"Company {i}"} for i in range(1001)]
        resp = client.post("/enrichment/enrich", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 422

    def test_preview_over_max_rows(self, client):
        """Preview data exceeding 100 rows should fail (max_items=100)."""
        data = [{"x": i} for i in range(101)]
        resp = client.post("/enrichment/preview", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 422

    def test_enrich_special_characters_in_data(self, client, mock_service):
        """Data with special characters should be accepted."""
        data = [{"company_name": "Acme & Co. <LLC>", "address": '123 "Main" St\nSuite #5'}]
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": data,
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 2,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 200

    def test_enrich_unicode_in_data(self, client, mock_service):
        """Data with unicode characters should be accepted."""
        data = [{"company_name": "Unternehmen GmbH", "address": "Strasse 42, Munchen"}]
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": data,
            "total_rows": 1,
            "enriched_rows": 1,
            "processing_time_ms": 3,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": data,
            "sources": ["company"],
        })
        assert resp.status_code == 200

    def test_create_source_special_chars_in_description(self, client, mock_service):
        """Description with special characters should work."""
        created = _make_custom_source_obj(
            description="Source for <companies> & 'entities' \"worldwide\""
        )
        mock_service.create_source.return_value = created
        resp = client.post("/enrichment/sources/create", json={
            "name": "Special Desc",
            "type": "custom",
            "description": "Source for <companies> & 'entities' \"worldwide\"",
        })
        assert resp.status_code == 200

    def test_get_source_with_special_id(self, client, mock_service):
        """Source IDs with hyphens and digits should be routed correctly."""
        mock_service.get_source.return_value = None
        resp = client.get("/enrichment/sources/abc-123-def")
        assert resp.status_code == 404

    def test_delete_source_with_special_id(self, client, mock_service):
        mock_service.delete_source.return_value = True
        resp = client.delete("/enrichment/sources/abc-123-def")
        assert resp.status_code == 200
        assert resp.json()["source_id"] == "abc-123-def"

    def test_enrich_single_row(self, client, mock_service):
        """Minimum valid request with 1 row and 1 source."""
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"x": 1, "industry": "Tech"}],
            "total_rows": 1,
            "enriched_rows": 1,
            "processing_time_ms": 1,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": ["company"],
        })
        assert resp.status_code == 200
        assert resp.json()["total_rows"] == 1

    def test_preview_single_row(self, client, mock_service):
        """Minimum valid preview with 1 row."""
        mock_service.simple_preview = AsyncMock(return_value={
            "preview": [{"x": 1}],
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 1,
        })
        resp = client.post("/enrichment/preview", json={
            "data": [{"x": 1}],
            "sources": ["company"],
            "sample_size": 1,
        })
        assert resp.status_code == 200

    def test_enrich_max_sources_boundary(self, client, mock_service):
        """Exactly 10 sources should be accepted (max_items=10)."""
        mock_service.simple_enrich = AsyncMock(return_value={
            "enriched_data": [{"x": 1}],
            "total_rows": 1,
            "enriched_rows": 0,
            "processing_time_ms": 1,
        })
        resp = client.post("/enrichment/enrich", json={
            "data": [{"x": 1}],
            "sources": [f"src_{i}" for i in range(10)],
        })
        assert resp.status_code == 200

    def test_builtin_sources_match_expected_constant(self, client):
        """Verify get_builtin_sources() returns exactly 3 entries."""
        builtin = EnrichmentService.get_builtin_sources()
        assert len(builtin) == 3
        ids = [s["id"] for s in builtin]
        assert ids == ["company", "address", "exchange"]

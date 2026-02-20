"""Knowledge API route contract tests."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.app.api.routes import knowledge as knowledge_routes
from backend.app.services.knowledge.service import KnowledgeService
from backend.app.services.security import require_api_key


@pytest.fixture
def client(monkeypatch, tmp_path):
    uploads_root = tmp_path / "uploads"
    monkeypatch.setenv("UPLOAD_ROOT", str(uploads_root))
    monkeypatch.setenv("NEURA_UPLOAD_ROOT", str(uploads_root))

    from backend.app.services.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setattr(knowledge_routes, "knowledge_service", KnowledgeService())

    app = FastAPI()
    app.include_router(knowledge_routes.router, prefix="/knowledge")
    app.dependency_overrides[require_api_key] = lambda: None

    try:
        yield TestClient(app)
    finally:
        get_settings.cache_clear()


def test_add_document_accepts_json_body(client: TestClient):
    response = client.post(
        "/knowledge/documents",
        json={"title": "JSON document", "document_type": "txt"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "JSON document"
    assert payload["document_type"] == "txt"


def test_add_document_accepts_multipart_upload(client: TestClient):
    response = client.post(
        "/knowledge/documents",
        files={"file": ("notes.md", b"# hello", "text/markdown")},
        data={"title": "Upload document", "tags": "alpha,beta"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Upload document"
    assert payload["document_type"] == "md"
    assert payload["file_path"]
    assert payload["file_url"].startswith("/uploads/knowledge/")
    assert payload["tags"] == ["alpha", "beta"]


def test_get_library_stats_has_fallback_when_service_missing_get_stats(client: TestClient, monkeypatch):
    class StubService:
        async def list_documents(self, **kwargs):
            return [], 0

        async def list_collections(self):
            return []

        async def list_tags(self):
            return []

    monkeypatch.setattr(knowledge_routes, "knowledge_service", StubService())

    response = client.get("/knowledge/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_documents": 0,
        "total_collections": 0,
        "total_tags": 0,
        "total_favorites": 0,
        "storage_used_bytes": 0,
        "document_types": {},
    }

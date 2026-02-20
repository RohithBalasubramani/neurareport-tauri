from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


from backend import api  # noqa: E402
from backend.app.repositories.state import StateStore  # noqa: E402
import backend.legacy.services.template_service as template_service  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Clear NEURA_STATE_DIR to prevent .env override
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    store = StateStore(base_dir=state_dir)
    monkeypatch.setattr(api, "state_store", store, raising=False)
    monkeypatch.setattr("backend.app.repositories.state.state_store", store)
    monkeypatch.setattr("backend.app.repositories.state.store.state_store", store)
    return TestClient(api.app)


def test_templates_recommend_threads_hints_into_prompt(client: TestClient, monkeypatch):
    catalog = [
        {
            "id": "tpl-1",
            "name": "Starter",
            "kind": "pdf",
            "domain": "finance",
            "tags": ["kpi"],
            "useCases": ["dashboard"],
            "primaryMetrics": ["revenue"],
            "source": "starter",
        }
    ]
    monkeypatch.setattr(template_service, "build_unified_template_catalog", lambda: catalog)

    captured: dict = {}

    def fake_recommend(catalog_arg, *, requirement, hints, max_results):
        captured["catalog"] = catalog_arg
        captured["requirement"] = requirement
        captured["hints"] = hints
        captured["max_results"] = max_results
        return [{"id": "tpl-1", "explanation": "match", "score": 0.9}]

    monkeypatch.setattr(template_service, "recommend_templates_from_catalog", fake_recommend)

    payload = {
        "requirement": "Revenue dashboard",
        "kind": "pdf",
        "kinds": ["excel", "pdf"],
        "domain": "growth",
        "domains": ["finance", "growth"],
        "schema_snapshot": {"tables": ["revenues"]},
        "tables": ["revenues", "users", "revenues"],
    }
    resp = client.post("/templates/recommend", json=payload)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["recommendations"][0]["template"]["id"] == "tpl-1"
    assert body["recommendations"][0]["score"] == pytest.approx(0.9)
    assert body["recommendations"][0]["explanation"]

    assert captured["catalog"] == catalog
    assert captured["requirement"] == "Revenue dashboard"
    hints = captured["hints"]
    assert hints["kind"] == "pdf"
    assert hints["kinds"] == ["pdf", "excel"]
    assert hints["domain"] == "growth"
    assert hints["domains"] == ["growth", "finance"]
    assert hints["schema_snapshot"] == {"tables": ["revenues"]}
    assert hints["tables"] == ["revenues", "users"]
    assert captured["max_results"] == 6


def test_templates_recommend_empty_catalog_returns_empty_list(client: TestClient, monkeypatch):
    monkeypatch.setattr(template_service, "build_unified_template_catalog", lambda: [])

    called = {}

    def fake_recommend(catalog_arg, *, requirement, hints, max_results):
        called["called"] = True
        assert catalog_arg == []
        assert hints == {}
        return []

    monkeypatch.setattr(template_service, "recommend_templates_from_catalog", fake_recommend)

    resp = client.post("/templates/recommend", json={"requirement": "Anything goes"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["recommendations"] == []
    assert called.get("called") is True

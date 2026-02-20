"""Service for template recommendations using AI."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.services.llm.client import get_llm_client
from backend.app.repositories.state import store as state_store_module
from backend.app.repositories.connections.schema import get_connection_schema

logger = logging.getLogger("neura.domain.recommendations")


def _state_store():
    return state_store_module.state_store


class RecommendationService:
    """Service for template recommendations."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def recommend_templates(
        self,
        connection_id: Optional[str] = None,
        schema_info: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None,
        limit: int = 5,
        correlation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recommend templates based on connection schema and context.

        Args:
            connection_id: Optional connection to base recommendations on
            schema_info: Optional schema information
            context: Optional user context/requirements
            limit: Maximum number of recommendations
            correlation_id: Request correlation ID

        Returns:
            List of template recommendations with scores
        """
        logger.info("Generating template recommendations", extra={"correlation_id": correlation_id})

        # Get all approved templates
        store = _state_store()
        with store.transaction() as state:
            templates = state.get("templates", {})
        approved = [t for t in templates.values() if t.get("status") == "approved"]

        if not approved:
            return []

        # Get schema if connection provided
        if connection_id and not schema_info:
            try:
                schema_info = get_connection_schema(connection_id, include_row_counts=False)
            except Exception as e:
                logger.warning("Failed to get schema for connection %s: %s", connection_id, e)

        # Build recommendation prompt
        template_catalog = []
        for t in approved:
            template_catalog.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "kind": t.get("kind"),
                "tags": t.get("tags", []),
            })

        prompt = f"""Recommend templates from this catalog based on the user's needs.

TEMPLATE CATALOG:
{template_catalog}

"""
        if schema_info:
            tables = [t["name"] for t in schema_info.get("tables", [])]
            prompt += f"DATABASE TABLES: {', '.join(tables)}\n\n"

        if context:
            prompt += f"USER CONTEXT: {context}\n\n"

        prompt += f"""Return a JSON array of the top {limit} recommended templates:
[
  {{
    "template_id": "id",
    "score": 0.95,
    "reason": "Why this template matches"
  }}
]

Return ONLY the JSON array."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="template_recommendations",
                temperature=0.3,
            )

            import json
            import re
            content = response["choices"][0]["message"]["content"]
            json_match = re.search(r"\[[\s\S]*\]", content)
            if json_match:
                recommendations = json.loads(json_match.group())
                # Enrich with template details
                for rec in recommendations:
                    tid = rec.get("template_id")
                    if tid in templates:
                        rec["template"] = templates[tid]
                return recommendations[:limit]

        except Exception as exc:
            logger.error(f"Recommendation generation failed: {exc}")

        # Fallback: return most recent templates
        sorted_templates = sorted(approved, key=lambda t: t.get("created_at", ""), reverse=True)
        return [{"template_id": t["id"], "template": t, "score": 0.5, "reason": "Recently created"} for t in sorted_templates[:limit]]

    def get_similar_templates(self, template_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get templates similar to a given template."""
        store = _state_store()
        with store.transaction() as state:
            templates = state.get("templates", {})
        target = templates.get(template_id)

        if not target:
            return []

        # Simple similarity based on tags
        target_tags = set(target.get("tags", []))
        similar = []

        for tid, t in templates.items():
            if tid == template_id or t.get("status") != "approved":
                continue
            t_tags = set(t.get("tags", []))
            overlap = len(target_tags & t_tags)
            if overlap > 0:
                similar.append({"template": t, "score": overlap / max(len(target_tags), 1)})

        similar.sort(key=lambda x: x["score"], reverse=True)
        return similar[:limit]

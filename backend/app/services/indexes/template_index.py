"""Template and mapping-history knowledge base for RAG.

Indexes report templates and records past mapping outcomes so the
system can suggest field-to-column mappings for new connections.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("neura.indexes.template")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TemplateDocument:
    """Represents a report template and its historical mapping data."""

    template_id: str
    template_name: str
    fields: list[dict] = field(default_factory=list)
    mapping_history: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _template_to_text(template: TemplateDocument) -> str:
    """Convert a template into indexable prose."""
    lines: list[str] = [
        f"Template: {template.template_name}",
    ]

    if template.metadata.get("description"):
        lines.append(f"Description: {template.metadata['description']}")

    if template.metadata.get("category"):
        lines.append(f"Category: {template.metadata['category']}")

    if template.fields:
        lines.append("Fields:")
        for fld in template.fields:
            name = fld.get("name", fld.get("field_name", "?"))
            ftype = fld.get("type", fld.get("field_type", ""))
            required = " (required)" if fld.get("required") else ""
            desc = f" - {fld['description']}" if fld.get("description") else ""
            lines.append(f"  - {name} [{ftype}]{required}{desc}")

    return "\n".join(lines)


def _mapping_to_text(
    template_id: str,
    connection_id: str,
    mappings: dict,
    success: bool,
) -> str:
    """Convert a mapping result into indexable text."""
    status = "SUCCESSFUL" if success else "FAILED"
    lines = [
        f"Mapping result ({status})",
        f"Template: {template_id}",
        f"Connection: {connection_id}",
        "Mappings:",
    ]
    for field_name, column_name in mappings.items():
        lines.append(f"  {field_name} -> {column_name}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# TemplateIndex
# ---------------------------------------------------------------------------

class TemplateIndex:
    """Indexes templates and mapping history for semantic retrieval.

    Parameters
    ----------
    embedding_pipeline:
        Object exposing ``generate_embeddings(texts)`` and
        ``chunk_text(text, chunk_size, overlap)``.
    vector_store:
        Object exposing ``add(embeddings, texts, metadata_list)`` and
        ``search(embedding, top_k)``.
    """

    def __init__(self, embedding_pipeline, vector_store) -> None:
        self._embedder = embedding_pipeline
        self._store = vector_store

    # -- template indexing --------------------------------------------------

    def index_template(self, template: TemplateDocument) -> int:
        """Index *template* description and fields. Returns chunk count."""
        text = _template_to_text(template)
        chunks = self._embedder.chunk_text(text, chunk_size=512, overlap=50)
        if not chunks:
            logger.debug(
                "No chunks produced for template %s", template.template_id,
            )
            return 0

        embeddings = self._embedder.generate_embeddings(chunks)
        metadata_list = [
            {
                "source": f"template:{template.template_id}",
                "template_name": template.template_name,
                "template_id": template.template_id,
            }
            for _ in chunks
        ]

        self._store.add(embeddings, chunks, metadata_list)
        logger.info(
            "Indexed template %s (%d chunks)",
            template.template_name, len(chunks),
        )
        return len(chunks)

    # -- mapping history ----------------------------------------------------

    def index_mapping_result(
        self,
        template_id: str,
        connection_id: str,
        mappings: dict,
        success: bool,
    ) -> None:
        """Record a mapping outcome so future suggestions can learn from it."""
        text = _mapping_to_text(template_id, connection_id, mappings, success)
        chunks = self._embedder.chunk_text(text, chunk_size=512, overlap=50)
        if not chunks:
            return

        embeddings = self._embedder.generate_embeddings(chunks)
        metadata_list = [
            {
                "source": f"mapping:{template_id}:{connection_id}",
                "template_id": template_id,
                "connection_id": connection_id,
                "success": success,
                "mappings_json": json.dumps(mappings),
            }
            for _ in chunks
        ]

        self._store.add(embeddings, chunks, metadata_list)
        logger.info(
            "Indexed mapping result for template=%s connection=%s success=%s",
            template_id, connection_id, success,
        )

    # -- querying -----------------------------------------------------------

    def find_similar_templates(
        self,
        description: str,
        top_k: int = 3,
    ) -> list[dict]:
        """Semantic search for templates matching *description*."""
        query_embedding = self._embedder.generate_embeddings([description])[0]
        results = self._store.search(query_embedding, top_k=top_k)

        # Filter to only template sources (exclude mapping records).
        template_results = [
            r for r in results
            if r.get("metadata", {}).get("source", "").startswith("template:")
        ]
        logger.debug(
            "Template search returned %d results for: %s",
            len(template_results), description[:80],
        )
        return template_results

    def get_mapping_suggestions(
        self,
        template_id: str,
        source_columns: list[str],
    ) -> list[dict]:
        """Suggest field-to-column mappings based on historical records.

        Searches past successful mappings for the given *template_id* and
        ranks column matches by frequency and semantic similarity.
        """
        # Build a query that combines the template id with available columns
        # so the vector search can find relevant historical mappings.
        query_text = (
            f"mapping for template {template_id} "
            f"columns: {', '.join(source_columns[:30])}"
        )
        query_embedding = self._embedder.generate_embeddings([query_text])[0]
        results = self._store.search(query_embedding, top_k=20)

        # Collect suggestions from successful mapping records.
        suggestions: dict[str, list[dict]] = {}

        for result in results:
            meta = result.get("metadata", {})
            source = meta.get("source", "")

            # Only consider mapping records for this template that succeeded.
            if not source.startswith(f"mapping:{template_id}:"):
                continue
            if not meta.get("success", False):
                continue

            mappings_json = meta.get("mappings_json", "{}")
            try:
                mappings = json.loads(mappings_json)
            except (json.JSONDecodeError, TypeError):
                continue

            score = result.get("score", 0.0)
            for field_name, column_name in mappings.items():
                if column_name in source_columns:
                    suggestions.setdefault(field_name, []).append({
                        "column": column_name,
                        "score": score,
                        "connection_id": meta.get("connection_id", ""),
                    })

        # Flatten into a ranked list of suggestions per field.
        ranked: list[dict] = []
        for field_name, candidates in suggestions.items():
            # Sort by score descending and pick the best.
            candidates.sort(key=lambda c: c["score"], reverse=True)
            ranked.append({
                "field": field_name,
                "suggested_column": candidates[0]["column"],
                "confidence": candidates[0]["score"],
                "alternatives": [
                    c["column"] for c in candidates[1:4]
                ],
            })

        logger.debug(
            "Generated %d mapping suggestions for template %s",
            len(ranked), template_id,
        )
        return ranked

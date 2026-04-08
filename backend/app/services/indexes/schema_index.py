"""Database schema knowledge base for RAG-powered SQL generation.

Indexes table schemas with embeddings so the LLM can retrieve only
the relevant subset of a (potentially large) database when building
queries.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("neura.indexes.schema")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SchemaDocument:
    """Represents a single database table's schema information."""

    table_name: str
    columns: list[dict] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    description: str = ""


def format_schema_for_llm(tables: list[SchemaDocument]) -> str:
    """Format a list of *SchemaDocument* objects into a compact text block
    suitable for injecting into an LLM prompt.

    Example output::

        TABLE: customers
        Description: Main customer records
        Columns:
          - id (INTEGER, PK)
          - name (VARCHAR)
        Relationships:
          - customers.id -> orders.customer_id
    """
    parts: list[str] = []
    for tbl in tables:
        lines = [f"TABLE: {tbl.table_name}"]
        if tbl.description:
            lines.append(f"Description: {tbl.description}")

        lines.append("Columns:")
        for col in tbl.columns:
            col_name = col.get("name", col.get("column_name", "?"))
            col_type = col.get("type", col.get("data_type", ""))
            extras: list[str] = []
            if col.get("primary_key"):
                extras.append("PK")
            if col.get("nullable") is False:
                extras.append("NOT NULL")
            if col.get("foreign_key"):
                extras.append(f"FK -> {col['foreign_key']}")
            suffix = f" ({col_type})" if col_type else ""
            if extras:
                suffix += f" [{', '.join(extras)}]"
            lines.append(f"  - {col_name}{suffix}")

        if tbl.relationships:
            lines.append("Relationships:")
            for rel in tbl.relationships:
                lines.append(f"  - {rel}")

        parts.append("\n".join(lines))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _table_to_text(table: SchemaDocument) -> str:
    """Convert a single table document into indexable prose."""
    return format_schema_for_llm([table])


# ---------------------------------------------------------------------------
# SchemaIndex
# ---------------------------------------------------------------------------

class SchemaIndex:
    """Indexes database schemas into a vector store for semantic retrieval.

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

    # -- indexing -----------------------------------------------------------

    def index_schema(
        self,
        connection_id: str,
        tables: list[SchemaDocument],
    ) -> int:
        """Index every table in *tables* and return the total chunk count."""
        total_chunks = 0

        for table in tables:
            text = _table_to_text(table)
            chunks = self._embedder.chunk_text(
                text, chunk_size=512, overlap=50,
            )
            if not chunks:
                logger.debug("No chunks produced for table %s", table.table_name)
                continue

            embeddings = self._embedder.generate_embeddings(chunks)
            metadata_list = [
                {
                    "source": f"schema:{connection_id}",
                    "table": table.table_name,
                }
                for _ in chunks
            ]

            self._store.add(embeddings, chunks, metadata_list)
            total_chunks += len(chunks)
            logger.debug(
                "Indexed table %s (%d chunks)", table.table_name, len(chunks),
            )

        logger.info(
            "Indexed %d tables for connection %s (%d total chunks)",
            len(tables), connection_id, total_chunks,
        )
        return total_chunks

    # -- querying -----------------------------------------------------------

    def query_relevant_tables(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Return the *top_k* most relevant schema chunks for *question*."""
        query_embedding = self._embedder.generate_embeddings([question])[0]
        results = self._store.search(query_embedding, top_k=top_k)
        logger.debug(
            "Schema query returned %d results for: %s",
            len(results), question[:80],
        )
        return results

    def get_table_context(self, table_names: list[str]) -> str:
        """Retrieve and format context for specific tables by name.

        This performs a direct metadata lookup rather than a semantic
        search, which is useful when the caller already knows which
        tables are needed.
        """
        # Build a synthetic query from the table names so we can pull
        # relevant chunks from the vector store.
        query_text = " ".join(table_names)
        query_embedding = self._embedder.generate_embeddings([query_text])[0]

        # Fetch extra results so we can filter by table name afterwards.
        results = self._store.search(query_embedding, top_k=50)

        seen_tables: set[str] = set()
        context_parts: list[str] = []
        target_set = {t.lower() for t in table_names}

        for result in results:
            tbl = result.get("metadata", {}).get("table", "")
            if tbl.lower() in target_set and tbl not in seen_tables:
                seen_tables.add(tbl)
                context_parts.append(result["text"])

        if not context_parts:
            logger.warning(
                "No context found for tables: %s", table_names,
            )

        return "\n\n".join(context_parts)

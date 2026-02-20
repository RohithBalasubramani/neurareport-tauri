"""
pgvector document store for semantic search and RAG.

Uses PostgreSQL's pgvector extension for:
- Cosine similarity search with HNSW indexing
- Hybrid search (vector + full-text via RRF)
- Source attribution for RAG outputs

Based on: pgvector/pgvector patterns + pgvector-python
"""
from __future__ import annotations
import logging
import json
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("neura.vectorstore")


@dataclass
class SearchResult:
    """A single search result with source attribution."""
    chunk_id: int
    doc_id: str
    chunk_index: int
    content: str
    source: str
    metadata: dict[str, Any]
    similarity: float

    def to_citation(self, index: int) -> dict:
        return {
            "index": index,
            "source": self.source,
            "content_preview": self.content[:200],
            "similarity": round(self.similarity, 4),
            "doc_id": self.doc_id,
        }


class PgVectorStore:
    """
    Vector store using PostgreSQL + pgvector extension.

    Schema:
    - document_chunks table with vector(dimensions) column
    - HNSW index for approximate nearest neighbor search
    - Full-text search via tsvector for hybrid retrieval
    """

    def __init__(self, connection_string: str, embedding_dim: int | None = None):
        from backend.app.services.config import get_settings

        self.connection_string = connection_string
        self.embedding_dim = int(embedding_dim or get_settings().embedding_dim)

    async def ensure_schema(self, session) -> None:
        """Create pgvector extension and document_chunks table if not exists."""
        await session.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await session.execute(f"""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id BIGSERIAL PRIMARY KEY,
                doc_id VARCHAR(255) NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding vector({self.embedding_dim}),
                source VARCHAR(500),
                metadata JSONB DEFAULT '{{}}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(doc_id, chunk_index)
            )
        """)
        await session.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks (doc_id)
        """)
        # Full-text search index
        await session.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_fts
            ON document_chunks USING gin(to_tsvector('english', content))
        """)
        await session.commit()
        logger.info("vectorstore_schema_ensured", extra={"event": "vectorstore_schema_ensured"})

    async def create_hnsw_index(self, session, m: int = 16, ef_construction: int = 64) -> None:
        """Create HNSW index. Call AFTER initial data load for best performance."""
        await session.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding_cosine
            ON document_chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = {m}, ef_construction = {ef_construction})
        """)
        await session.commit()
        logger.info("hnsw_index_created", extra={"event": "hnsw_index_created", "m": m, "ef_construction": ef_construction})

    async def upsert_chunks(self, session, chunks: list[dict[str, Any]]) -> int:
        """Upsert document chunks with embeddings."""
        count = 0
        for chunk in chunks:
            await session.execute(
                """
                INSERT INTO document_chunks (doc_id, chunk_index, content, embedding, source, metadata)
                VALUES (:doc_id, :chunk_index, :content, :embedding, :source, :metadata::jsonb)
                ON CONFLICT (doc_id, chunk_index)
                DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding,
                             source = EXCLUDED.source, metadata = EXCLUDED.metadata
                """,
                {
                    "doc_id": chunk["doc_id"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "embedding": str(chunk["embedding"]),
                    "source": chunk.get("source", ""),
                    "metadata": json.dumps(chunk.get("metadata", {})),
                },
            )
            count += 1
        await session.commit()
        return count

    async def search_similar(
        self, session, query_embedding: list[float], top_k: int = 10,
        source_filter: Optional[str] = None, ef_search: int = 100,
    ) -> list[SearchResult]:
        """Cosine similarity search with optional source filtering."""
        await session.execute(f"SET LOCAL hnsw.ef_search = {ef_search}")

        query_vec = str(query_embedding)

        if source_filter:
            rows = await session.execute(
                """
                SELECT id, doc_id, chunk_index, content, source, metadata,
                       1 - (embedding <=> :vec) AS similarity
                FROM document_chunks WHERE source = :source
                ORDER BY embedding <=> :vec LIMIT :top_k
                """,
                {"vec": query_vec, "source": source_filter, "top_k": top_k},
            )
        else:
            rows = await session.execute(
                """
                SELECT id, doc_id, chunk_index, content, source, metadata,
                       1 - (embedding <=> :vec) AS similarity
                FROM document_chunks ORDER BY embedding <=> :vec LIMIT :top_k
                """,
                {"vec": query_vec, "top_k": top_k},
            )

        return [
            SearchResult(
                chunk_id=row.id, doc_id=row.doc_id, chunk_index=row.chunk_index,
                content=row.content, source=row.source,
                metadata=row.metadata if isinstance(row.metadata, dict) else {},
                similarity=float(row.similarity),
            )
            for row in rows.fetchall()
        ]

    async def hybrid_search(
        self, session, query_embedding: list[float], query_text: str,
        top_k: int = 10, vector_weight: float = 0.7,
    ) -> list[SearchResult]:
        """Reciprocal Rank Fusion hybrid search (vector + full-text)."""
        k = 60  # RRF constant
        query_vec = str(query_embedding)

        rows = await session.execute(
            """
            WITH vector_results AS (
                SELECT id, doc_id, chunk_index, content, source, metadata,
                       ROW_NUMBER() OVER (ORDER BY embedding <=> :vec) AS vector_rank
                FROM document_chunks ORDER BY embedding <=> :vec LIMIT :limit
            ),
            text_results AS (
                SELECT id, doc_id, chunk_index, content, source, metadata,
                       ROW_NUMBER() OVER (
                           ORDER BY ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', :query)) DESC
                       ) AS text_rank
                FROM document_chunks
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
                LIMIT :limit
            )
            SELECT COALESCE(v.id, t.id) AS id,
                   COALESCE(v.doc_id, t.doc_id) AS doc_id,
                   COALESCE(v.chunk_index, t.chunk_index) AS chunk_index,
                   COALESCE(v.content, t.content) AS content,
                   COALESCE(v.source, t.source) AS source,
                   COALESCE(v.metadata, t.metadata) AS metadata,
                   COALESCE(:vw / (:k + v.vector_rank), 0) + COALESCE((1 - :vw) / (:k + t.text_rank), 0) AS similarity
            FROM vector_results v FULL OUTER JOIN text_results t ON v.id = t.id
            ORDER BY similarity DESC LIMIT :top_k
            """,
            {"vec": query_vec, "query": query_text, "limit": top_k * 2, "vw": vector_weight, "k": k, "top_k": top_k},
        )

        return [
            SearchResult(
                chunk_id=row.id, doc_id=row.doc_id, chunk_index=row.chunk_index,
                content=row.content, source=row.source,
                metadata=row.metadata if isinstance(row.metadata, dict) else {},
                similarity=float(row.similarity),
            )
            for row in rows.fetchall()
        ]

    async def delete_document(self, session, doc_id: str) -> int:
        """Delete all chunks for a document."""
        result = await session.execute(
            "DELETE FROM document_chunks WHERE doc_id = :doc_id",
            {"doc_id": doc_id},
        )
        await session.commit()
        return result.rowcount

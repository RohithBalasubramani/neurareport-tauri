"""Vector store port for RAG retrieval."""

from __future__ import annotations

from typing import Any, Protocol


class VectorSearchResult(Protocol):
    doc_id: str
    content: str
    similarity: float
    source: str
    metadata: dict[str, Any]


class VectorStore(Protocol):
    async def upsert_chunks(self, session, chunks: list[dict[str, Any]]) -> int: ...
    async def search_similar(self, session, query_embedding: list[float], top_k: int = 10) -> list[VectorSearchResult]: ...
    async def hybrid_search(self, session, query_embedding: list[float], query_text: str, top_k: int = 10) -> list[VectorSearchResult]: ...


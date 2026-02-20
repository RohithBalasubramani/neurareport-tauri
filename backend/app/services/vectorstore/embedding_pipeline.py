"""
Embedding pipeline: chunk text, generate embeddings, store in vector DB.

Uses sentence-transformers for local embedding generation (no API key needed).
Falls back to TF-IDF vector hashing when sentence-transformers is unavailable.
"""
from __future__ import annotations
import hashlib
import logging
import math
import re
from typing import Any, Optional

logger = logging.getLogger("neura.vectorstore.embedding")

# Lazy-loaded sentence-transformers model
_st_model = None
_st_model_name: str = ""


def _get_sentence_transformer(model_name: str = "all-MiniLM-L6-v2"):
    """Lazy-load a sentence-transformers model."""
    global _st_model, _st_model_name
    if _st_model is not None and _st_model_name == model_name:
        return _st_model
    try:
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer(model_name)
        _st_model_name = model_name
        logger.info("sentence_transformer_loaded", extra={"event": "sentence_transformer_loaded", "model": model_name})
        return _st_model
    except ImportError:
        logger.warning("sentence_transformers_not_installed", extra={"event": "sentence_transformers_not_installed"})
        return None


def _tfidf_hash_embedding(text: str, dim: int = 384) -> list[float]:
    """Generate a deterministic pseudo-embedding via token hashing (fallback)."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    vec = [0.0] * dim
    for token in tokens:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h // dim) % 2 == 0 else -1.0
        vec[idx] += sign
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class EmbeddingPipeline:
    """Generate embeddings using sentence-transformers (local, no API key)."""

    def __init__(self, model: str | None = None, embedding_dim: int | None = None):
        from backend.app.services.config import get_settings

        settings = get_settings()
        self.model = model or settings.embedding_model
        self.embedding_dim = int(embedding_dim or settings.embedding_dim)

    def chunk_text(self, text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - chunk_overlap
        return chunks

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using sentence-transformers or TF-IDF fallback."""
        model = _get_sentence_transformer(self.model)
        if model is not None:
            embeddings = model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]

        # Fallback: TF-IDF hash embeddings
        logger.debug("using_tfidf_fallback", extra={"event": "using_tfidf_fallback"})
        return [_tfidf_hash_embedding(t, self.embedding_dim) for t in texts]

    async def process_document(
        self, doc_id: str, content: str, source: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[dict]:
        """Full pipeline: chunk -> embed -> return records for storage."""
        chunks = self.chunk_text(content)
        if not chunks:
            return []

        embeddings = await self.generate_embeddings(chunks)

        records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            records.append({
                "doc_id": doc_id,
                "chunk_index": i,
                "content": chunk,
                "embedding": embedding,
                "source": source,
                "metadata": metadata or {},
            })

        logger.info("document_embedded", extra={
            "event": "document_embedded", "doc_id": doc_id,
            "chunks": len(records), "model": self.model,
        })
        return records

    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        embeddings = await self.generate_embeddings([query])
        return embeddings[0]

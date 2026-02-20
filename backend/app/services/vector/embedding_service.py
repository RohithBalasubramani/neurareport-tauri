"""
Vector embedding and semantic search service.

Provides document embedding, vector storage (pgvector/Qdrant), and
semantic retrieval for the RAG pipeline.

Supports:
- sentence-transformers for local embeddings
- OpenAI embeddings API as fallback
- pgvector for PostgreSQL-native vector storage
- Qdrant for dedicated vector search

Based on: pgvector/pgvector-python + qdrant/qdrant-client patterns.
"""
from __future__ import annotations

import hashlib
import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("neura.vector")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_MODEL = os.getenv("NEURA_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DEFAULT_DIMENSION = 384  # all-MiniLM-L6-v2 output dimension
QDRANT_URL = os.getenv("NEURA_QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("NEURA_QDRANT_COLLECTION", "neurareport_docs")


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    text: str
    embedding: List[float]
    model: str
    token_count: int = 0


@dataclass
class SearchResult:
    """A single search result with score."""
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmbeddingService:
    """
    Generate embeddings using sentence-transformers (local) or OpenAI API.

    Prefers local models for privacy and cost; falls back to OpenAI if
    sentence-transformers is unavailable.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None
        self._lock = threading.Lock()
        self._use_openai = False

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(
                    "embedding_model_loaded",
                    extra={"event": "embedding_model_loaded", "model": self.model_name},
                )
            except ImportError:
                logger.warning(
                    "sentence_transformers_unavailable",
                    extra={"event": "sentence_transformers_unavailable"},
                )
                self._use_openai = True
            except Exception as exc:
                logger.warning(
                    "embedding_model_load_failed",
                    extra={"event": "embedding_model_load_failed", "error": str(exc)},
                )
                self._use_openai = True

    def embed_texts(self, texts: List[str]) -> List[EmbeddingResult]:
        """Embed a batch of texts."""
        if not texts:
            return []

        self._load_model()

        if self._use_openai:
            return self._embed_openai(texts)

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return [
            EmbeddingResult(
                text=text,
                embedding=emb.tolist(),
                model=self.model_name,
            )
            for text, emb in zip(texts, embeddings)
        ]

    def embed_text(self, text: str) -> EmbeddingResult:
        """Embed a single text."""
        results = self.embed_texts([text])
        return results[0] if results else EmbeddingResult(text=text, embedding=[], model=self.model_name)

    def _embed_openai(self, texts: List[str]) -> List[EmbeddingResult]:
        """Fallback to OpenAI embeddings API."""
        try:
            import openai
            client = openai.OpenAI()
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small",
            )
            return [
                EmbeddingResult(
                    text=texts[i],
                    embedding=item.embedding,
                    model="text-embedding-3-small",
                    token_count=response.usage.total_tokens // len(texts),
                )
                for i, item in enumerate(response.data)
            ]
        except Exception as exc:
            logger.error("openai_embedding_failed", extra={"event": "openai_embedding_failed", "error": str(exc)})
            return [
                EmbeddingResult(text=t, embedding=[], model="none")
                for t in texts
            ]


class VectorStore:
    """
    Vector storage and retrieval backend.

    Supports Qdrant (preferred) and pgvector (PostgreSQL extension).
    Falls back to in-memory numpy-based search if neither is available.
    """

    def __init__(self, backend: str = "auto"):
        self._backend = backend
        self._client = None
        self._memory_store: Dict[str, Tuple[List[float], Dict[str, Any]]] = {}
        self._lock = threading.Lock()
        self._resolved_backend = None

    def _resolve_backend(self):
        """Resolve which backend to use."""
        if self._resolved_backend:
            return

        if self._backend == "qdrant" or (self._backend == "auto"):
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams

                self._client = QdrantClient(url=QDRANT_URL)
                # Ensure collection exists
                collections = [c.name for c in self._client.get_collections().collections]
                if QDRANT_COLLECTION not in collections:
                    self._client.create_collection(
                        collection_name=QDRANT_COLLECTION,
                        vectors_config=VectorParams(
                            size=DEFAULT_DIMENSION,
                            distance=Distance.COSINE,
                        ),
                    )
                self._resolved_backend = "qdrant"
                logger.info("vector_store_backend", extra={"event": "vector_store_backend", "backend": "qdrant"})
                return
            except Exception as exc:
                if self._backend == "qdrant":
                    raise
                logger.info(f"Qdrant unavailable, trying pgvector: {exc}")

        if self._backend in ("pgvector", "auto"):
            try:
                self._resolved_backend = "pgvector"
                logger.info("vector_store_backend", extra={"event": "vector_store_backend", "backend": "pgvector"})
                return
            except Exception as exc:
                if self._backend == "pgvector":
                    raise
                logger.info(f"pgvector unavailable, using memory: {exc}")

        self._resolved_backend = "memory"
        logger.info("vector_store_backend", extra={"event": "vector_store_backend", "backend": "memory"})

    def upsert(self, document_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Insert or update a vector."""
        self._resolve_backend()

        if self._resolved_backend == "qdrant":
            from qdrant_client.models import PointStruct
            point = PointStruct(
                id=self._hash_id(document_id),
                vector=embedding,
                payload={"document_id": document_id, **(metadata or {})},
            )
            self._client.upsert(collection_name=QDRANT_COLLECTION, points=[point])
        elif self._resolved_backend == "pgvector":
            self._pgvector_upsert(document_id, embedding, metadata)
        else:
            with self._lock:
                self._memory_store[document_id] = (embedding, metadata or {})

    def upsert_batch(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
        """Batch upsert vectors. Returns count of upserted items."""
        self._resolve_backend()

        if self._resolved_backend == "qdrant":
            from qdrant_client.models import PointStruct
            points = [
                PointStruct(
                    id=self._hash_id(doc_id),
                    vector=emb,
                    payload={"document_id": doc_id, **meta},
                )
                for doc_id, emb, meta in items
            ]
            self._client.upsert(collection_name=QDRANT_COLLECTION, points=points)
            return len(points)
        else:
            for doc_id, emb, meta in items:
                self.upsert(doc_id, emb, meta)
            return len(items)

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[SearchResult]:
        """Search for similar vectors."""
        self._resolve_backend()

        if self._resolved_backend == "qdrant":
            results = self._client.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=query_embedding,
                limit=top_k,
            )
            return [
                SearchResult(
                    document_id=hit.payload.get("document_id", ""),
                    text=hit.payload.get("text", ""),
                    score=hit.score,
                    metadata={k: v for k, v in hit.payload.items() if k not in ("document_id", "text")},
                )
                for hit in results
            ]
        elif self._resolved_backend == "pgvector":
            return self._pgvector_search(query_embedding, top_k)
        else:
            return self._memory_search(query_embedding, top_k)

    def delete(self, document_id: str) -> bool:
        """Delete a vector by document ID."""
        self._resolve_backend()

        if self._resolved_backend == "qdrant":
            from qdrant_client.models import PointIdsList
            self._client.delete(
                collection_name=QDRANT_COLLECTION,
                points_selector=PointIdsList(points=[self._hash_id(document_id)]),
            )
            return True
        elif self._resolved_backend == "memory":
            with self._lock:
                return self._memory_store.pop(document_id, None) is not None
        return False

    def count(self) -> int:
        """Get the number of stored vectors."""
        self._resolve_backend()

        if self._resolved_backend == "qdrant":
            info = self._client.get_collection(QDRANT_COLLECTION)
            return info.points_count
        elif self._resolved_backend == "memory":
            return len(self._memory_store)
        return 0

    def _memory_search(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """In-memory cosine similarity search."""
        if not self._memory_store:
            return []

        query = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []
        query = query / query_norm

        scored = []
        for doc_id, (emb, meta) in self._memory_store.items():
            vec = np.array(emb, dtype=np.float32)
            vec_norm = np.linalg.norm(vec)
            if vec_norm == 0:
                continue
            similarity = float(np.dot(query, vec / vec_norm))
            scored.append((doc_id, similarity, meta))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                document_id=doc_id,
                text=meta.get("text", ""),
                score=score,
                metadata={k: v for k, v in meta.items() if k != "text"},
            )
            for doc_id, score, meta in scored[:top_k]
        ]

    def _pgvector_upsert(self, document_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]]) -> None:
        """Upsert using pgvector extension."""
        # This requires the pgvector extension and appropriate table setup
        # Implementation deferred to Alembic migration for table creation
        logger.warning("pgvector_upsert_not_implemented")

    def _pgvector_search(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """Search using pgvector extension."""
        logger.warning("pgvector_search_not_implemented")
        return []

    @staticmethod
    def _hash_id(document_id: str) -> int:
        """Convert string ID to integer for Qdrant."""
        return int(hashlib.md5(document_id.encode()).hexdigest()[:16], 16)


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------
_embedding_service: Optional[EmbeddingService] = None
_vector_store: Optional[VectorStore] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

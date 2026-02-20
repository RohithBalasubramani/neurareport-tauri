# mypy: ignore-errors
"""
Lightweight RAG (Retrieval-Augmented Generation) Module.

Provides document retrieval and context augmentation:
- Simple vector-based retrieval (optional embeddings)
- BM25 keyword search
- Hybrid retrieval combining both
- Context window management
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .client import LLMClient, get_llm_client

logger = logging.getLogger("neura.llm.rag")


@dataclass
class Document:
    """A document chunk for retrieval."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result of document retrieval."""
    documents: List[Document]
    scores: List[float]
    query: str
    method: str


class BM25Index:
    """
    BM25 keyword-based retrieval index.

    Efficient for exact and fuzzy keyword matching.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._documents: List[Document] = []
        self._doc_freqs: Dict[str, int] = Counter()
        self._doc_lens: List[int] = []
        self._avg_doc_len: float = 0.0
        self._inverted_index: Dict[str, List[Tuple[int, int]]] = {}  # term -> [(doc_idx, term_freq)]

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the index."""
        for doc in documents:
            self._add_document(doc)
        self._avg_doc_len = sum(self._doc_lens) / len(self._doc_lens) if self._doc_lens else 0

    def _add_document(self, doc: Document) -> None:
        """Add a single document to the index."""
        doc_idx = len(self._documents)
        self._documents.append(doc)

        # Tokenize
        tokens = self._tokenize(doc.content)
        self._doc_lens.append(len(tokens))

        # Count term frequencies
        term_freqs = Counter(tokens)

        # Update inverted index and document frequencies
        for term, freq in term_freqs.items():
            if term not in self._inverted_index:
                self._inverted_index[term] = []
            self._inverted_index[term].append((doc_idx, freq))
            self._doc_freqs[term] += 1

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search the index and return top-k documents with scores."""
        if not self._documents:
            return []

        query_tokens = self._tokenize(query)
        scores: Dict[int, float] = {}
        n_docs = len(self._documents)

        for term in query_tokens:
            if term not in self._inverted_index:
                continue

            # Calculate IDF
            df = self._doc_freqs[term]
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

            # Score each document containing the term
            for doc_idx, tf in self._inverted_index[term]:
                doc_len = self._doc_lens[doc_idx]
                # BM25 scoring formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self._avg_doc_len)
                score = idf * numerator / denominator

                scores[doc_idx] = scores.get(doc_idx, 0) + score

        # Sort by score and return top-k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self._documents[idx], score) for idx, score in sorted_results]

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Remove very short tokens and stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'can',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
                     'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose',
                     'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
                     'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                     'just', 'and', 'but', 'or', 'if', 'because', 'as', 'until',
                     'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
                     'between', 'into', 'through', 'during', 'before', 'after',
                     'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
                     'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        return [t for t in tokens if len(t) > 2 and t not in stopwords]


class SimpleVectorStore:
    """
    Simple in-memory vector store using cosine similarity.

    For production, consider using a proper vector database like
    Chroma, Weaviate, or Pinecone.
    """

    def __init__(self):
        self._documents: List[Document] = []

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents with embeddings to the store."""
        for doc in documents:
            if doc.embedding is not None:
                self._documents.append(doc)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents using cosine similarity."""
        if not self._documents or not query_embedding:
            return []

        scores = []
        for doc in self._documents:
            if doc.embedding:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                scores.append((doc, similarity))

        # Sort by similarity and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class RAGRetriever:
    """
    RAG Retriever combining keyword and semantic search.

    Features:
    - BM25 keyword search
    - Optional vector similarity search
    - Hybrid retrieval with score fusion
    - Context window management
    """

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        use_embeddings: bool = False,
        max_context_tokens: int = 4000,
    ):
        self.client = client or get_llm_client()
        self.use_embeddings = use_embeddings
        self.max_context_tokens = max_context_tokens

        self._bm25_index = BM25Index()
        self._vector_store = SimpleVectorStore() if use_embeddings else None
        self._documents: Dict[str, Document] = {}

    def add_document(
        self,
        content: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> List[str]:
        """
        Add a document to the retriever.

        Args:
            content: Document content
            doc_id: Optional document ID
            metadata: Optional metadata
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of chunk IDs created
        """
        if not doc_id:
            doc_id = hashlib.md5(content.encode()).hexdigest()[:12]

        # Chunk the document
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        chunk_ids = []

        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_metadata = {
                **(metadata or {}),
                "parent_doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }

            doc = Document(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata,
            )

            # Generate embedding if enabled
            if self.use_embeddings:
                doc.embedding = self._get_embedding(chunk_content)

            self._documents[chunk_id] = doc
            chunk_ids.append(chunk_id)

        # Rebuild indices
        self._rebuild_indices()

        return chunk_ids

    def add_documents_bulk(
        self,
        documents: List[Dict[str, Any]],
        chunk_size: int = 500,
    ) -> None:
        """
        Add multiple documents in bulk.

        Args:
            documents: List of dicts with 'content' and optional 'id', 'metadata'
            chunk_size: Size of chunks
        """
        for doc in documents:
            self.add_document(
                content=doc["content"],
                doc_id=doc.get("id"),
                metadata=doc.get("metadata"),
                chunk_size=chunk_size,
            )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        method: str = "hybrid",
    ) -> RetrievalResult:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            method: Search method (bm25, vector, hybrid)

        Returns:
            RetrievalResult with matching documents
        """
        if method == "bm25" or not self.use_embeddings:
            results = self._bm25_index.search(query, top_k)
            return RetrievalResult(
                documents=[doc for doc, _ in results],
                scores=[score for _, score in results],
                query=query,
                method="bm25",
            )

        if method == "vector" and self._vector_store:
            query_embedding = self._get_embedding(query)
            results = self._vector_store.search(query_embedding, top_k)
            return RetrievalResult(
                documents=[doc for doc, _ in results],
                scores=[score for _, score in results],
                query=query,
                method="vector",
            )

        # Hybrid: combine BM25 and vector scores
        if method == "hybrid" and self._vector_store:
            bm25_results = self._bm25_index.search(query, top_k * 2)
            query_embedding = self._get_embedding(query)
            vector_results = self._vector_store.search(query_embedding, top_k * 2)

            # Reciprocal Rank Fusion
            fused_scores = self._reciprocal_rank_fusion(
                [r[0].id for r in bm25_results],
                [r[0].id for r in vector_results],
            )

            # Get top-k documents
            sorted_ids = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            documents = [self._documents[doc_id] for doc_id, _ in sorted_ids if doc_id in self._documents]
            scores = [score for _, score in sorted_ids[:len(documents)]]

            return RetrievalResult(
                documents=documents,
                scores=scores,
                query=query,
                method="hybrid",
            )

        # Fallback to BM25
        results = self._bm25_index.search(query, top_k)
        return RetrievalResult(
            documents=[doc for doc, _ in results],
            scores=[score for _, score in results],
            query=query,
            method="bm25",
        )

    def query_with_context(
        self,
        question: str,
        top_k: int = 5,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question using retrieved context.

        Args:
            question: The question to answer
            top_k: Number of context documents
            include_sources: Whether to include source references

        Returns:
            Dict with answer and sources
        """
        # Retrieve relevant documents
        retrieval = self.retrieve(question, top_k, method="hybrid")

        if not retrieval.documents:
            return {
                "answer": "I couldn't find relevant information to answer this question.",
                "sources": [],
                "context_used": False,
            }

        # Build context
        context = self._build_context(retrieval.documents)

        # Generate answer with context
        prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the information provided in the context
- If the context doesn't contain enough information, say so
- Be concise but complete
- Cite specific parts of the context when relevant

Answer:"""

        response = self.client.complete(
            messages=[{"role": "user", "content": prompt}],
            description="rag_query",
            temperature=0.3,
        )

        answer = response["choices"][0]["message"]["content"]

        sources = []
        if include_sources:
            for doc in retrieval.documents:
                sources.append({
                    "id": doc.id,
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "metadata": doc.metadata,
                })

        return {
            "answer": answer,
            "sources": sources,
            "context_used": True,
            "documents_retrieved": len(retrieval.documents),
        }

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end near the boundary
                for punct in ['. ', '! ', '? ', '\n\n', '\n']:
                    boundary = text.rfind(punct, start + chunk_size // 2, end)
                    if boundary != -1:
                        end = boundary + len(punct)
                        break

            chunks.append(text[start:end].strip())
            start = end - chunk_overlap

        return [c for c in chunks if c]  # Filter empty chunks

    def _build_context(self, documents: List[Document]) -> str:
        """Build context string from documents, respecting token limit."""
        context_parts = []
        estimated_tokens = 0

        for i, doc in enumerate(documents):
            # Rough token estimation (4 chars per token)
            doc_tokens = len(doc.content) // 4

            if estimated_tokens + doc_tokens > self.max_context_tokens:
                # Truncate if needed
                remaining_tokens = self.max_context_tokens - estimated_tokens
                truncated_content = doc.content[:remaining_tokens * 4]
                context_parts.append(f"[Document {i + 1}]\n{truncated_content}...")
                break

            context_parts.append(f"[Document {i + 1}]\n{doc.content}")
            estimated_tokens += doc_tokens

        return "\n\n".join(context_parts)

    def _rebuild_indices(self) -> None:
        """Rebuild search indices."""
        documents = list(self._documents.values())
        self._bm25_index = BM25Index()
        self._bm25_index.add_documents(documents)

        if self._vector_store:
            self._vector_store = SimpleVectorStore()
            self._vector_store.add_documents(documents)

    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text.

        Uses LLM to generate a simple embedding (not ideal but works without
        external embedding service).
        """
        # For production, use a proper embedding model like:
        # - OpenAI text-embedding-ada-002
        # - Sentence transformers
        # - Ollama embeddings

        # Simple hash-based embedding as fallback
        words = re.findall(r'\b\w+\b', text.lower())
        word_hashes = [hash(word) % 1000 / 1000.0 for word in words[:256]]

        # Pad or truncate to fixed size
        embedding_size = 256
        if len(word_hashes) < embedding_size:
            word_hashes.extend([0.0] * (embedding_size - len(word_hashes)))

        return word_hashes[:embedding_size]

    def _reciprocal_rank_fusion(
        self,
        ranking1: List[str],
        ranking2: List[str],
        k: int = 60,
    ) -> Dict[str, float]:
        """Combine two rankings using Reciprocal Rank Fusion."""
        fused_scores: Dict[str, float] = {}

        for rank, doc_id in enumerate(ranking1):
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        for rank, doc_id in enumerate(ranking2):
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        return fused_scores


# Convenience functions

def create_retriever(use_embeddings: bool = False) -> RAGRetriever:
    """Create a RAG retriever instance."""
    return RAGRetriever(use_embeddings=use_embeddings)


def quick_rag_query(
    question: str,
    documents: List[str],
    top_k: int = 3,
) -> str:
    """
    Quick RAG query over a list of documents.

    Args:
        question: The question to answer
        documents: List of document strings
        top_k: Number of documents to use as context

    Returns:
        Generated answer
    """
    retriever = RAGRetriever(use_embeddings=False)

    for i, doc in enumerate(documents):
        retriever.add_document(doc, doc_id=f"doc_{i}")

    result = retriever.query_with_context(question, top_k=top_k)
    return result["answer"]

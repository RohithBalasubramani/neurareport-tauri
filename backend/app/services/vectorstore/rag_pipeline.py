"""
RAG pipeline: retrieve relevant chunks, generate answer with source citations.

Based on: Haystack PromptBuilder + AnswerBuilder + source attribution patterns.
"""
from __future__ import annotations
import re
import logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("neura.vectorstore.rag")

RAG_PROMPT_TEMPLATE = """You are a helpful research assistant. Answer the question using ONLY the
provided context documents. For every claim, cite the source using [N] where N is the document index.

If the context does not contain enough information, say "I don't have enough information" and explain what is missing.

Context documents:
{context}

Question: {query}

Answer (with citations):"""


@dataclass
class RAGResponse:
    """RAG response with source attribution."""
    answer: str
    sources: list[dict[str, Any]]
    referenced_sources: list[dict[str, Any]]
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "referenced_sources": self.referenced_sources,
            "confidence": self.confidence,
        }


class RAGPipeline:
    """End-to-end RAG: embed query -> retrieve -> generate with citations."""

    def __init__(self, vector_store, embedding_pipeline, llm_model: str = "sonnet"):
        self.vector_store = vector_store
        self.embedding_pipeline = embedding_pipeline
        self.llm_model = llm_model

    async def query(
        self, session, question: str, top_k: int = 5,
        source_filter: Optional[str] = None, use_hybrid: bool = True,
    ) -> RAGResponse:
        """Run a RAG query with source attribution."""
        # 1. Embed query
        query_embedding = await self.embedding_pipeline.embed_query(question)

        # 2. Retrieve relevant chunks
        if use_hybrid:
            results = await self.vector_store.hybrid_search(session, query_embedding, question, top_k=top_k)
        else:
            results = await self.vector_store.search_similar(session, query_embedding, top_k=top_k, source_filter=source_filter)

        if not results:
            return RAGResponse(answer="No relevant documents found.", sources=[], referenced_sources=[])

        # 3. Build context with numbered sources
        context_parts = []
        sources = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] (Source: {result.source})\n{result.content}\n")
            sources.append(result.to_citation(i))

        context = "\n".join(context_parts)
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=question)

        # 4. Generate answer using centralized LLM client
        from backend.app.services.llm.client import get_llm_client
        client = get_llm_client()

        response = client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.llm_model,
            description="rag_generate_answer",
            temperature=0.1,
            max_tokens=1024,
        )
        answer = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        # 5. Extract referenced sources from [N] patterns
        referenced_indices = set(int(m) for m in re.findall(r"\[(\d+)\]", answer))
        referenced_sources = [s for s in sources if s["index"] in referenced_indices]

        # 6. Compute confidence (average similarity of referenced sources)
        if referenced_sources:
            confidence = sum(s["similarity"] for s in referenced_sources) / len(referenced_sources)
        else:
            confidence = sum(s["similarity"] for s in sources) / len(sources) if sources else 0.0

        return RAGResponse(
            answer=answer,
            sources=sources,
            referenced_sources=referenced_sources,
            confidence=round(confidence, 4),
        )

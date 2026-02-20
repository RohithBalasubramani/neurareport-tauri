"""
Hallucination detection and fact-checking pipeline.

3-stage verification:
1. Claim decomposition: break LLM output into individual claims
2. Evidence retrieval: search document store for supporting evidence
3. Claim verification: score each claim against evidence

Based on: OpenFactCheck + Exa hallucination detector patterns.
"""
from __future__ import annotations
import asyncio
import re
import logging
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Optional

logger = logging.getLogger("neura.validation.factcheck")


@dataclass
class Claim:
    """A single factual claim extracted from text."""
    text: str
    source_sentence: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    verdict: str = "unverified"  # verified, refuted, unverified, unsupported
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class FactCheckResult:
    """Result of fact-checking an LLM output."""
    original_text: str
    claims: list[Claim]
    overall_score: float = 0.0  # 0.0 = all hallucinated, 1.0 = all verified
    passed: bool = True
    pass_threshold: float = 0.6

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "overall_score": round(self.overall_score, 3),
            "total_claims": len(self.claims),
            "verified_claims": sum(1 for c in self.claims if c.verdict == "verified"),
            "refuted_claims": sum(1 for c in self.claims if c.verdict == "refuted"),
            "unsupported_claims": sum(1 for c in self.claims if c.verdict == "unsupported"),
            "claims": [
                {
                    "text": c.text,
                    "verdict": c.verdict,
                    "confidence": round(c.confidence, 3),
                    "reasoning": c.reasoning,
                    "evidence_count": len(c.evidence),
                }
                for c in self.claims
            ],
        }


class FactChecker:
    """
    Fact-checking pipeline for LLM outputs.

    Usage:
        checker = FactChecker()
        result = await checker.check(llm_output, context_docs=[...])
        if not result.passed:
            # Flag response as potentially unreliable
    """

    def __init__(self, pass_threshold: float = 0.6):
        self.pass_threshold = pass_threshold

    async def decompose_claims(self, text: str) -> list[Claim]:
        """Extract individual factual claims from text using LLM."""
        try:
            from backend.app.services.llm.client import get_llm_client
            client = get_llm_client()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    client.complete,
                    messages=[{
                        "role": "user",
                        "content": f"""Extract all factual claims from this text. Return each claim on a new line, prefixed with "- ".
Only include verifiable factual statements, not opinions or qualifiers.

Text:
{text[:3000]}

Claims:"""
                    }],
                    description="fact_check_decompose_claims",
                    temperature=0.0,
                    max_tokens=1024,
                ),
            )

            raw = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            claims = []
            for line in raw.strip().split("\n"):
                line = line.strip().lstrip("- ").strip()
                if line and len(line) > 10:
                    claims.append(Claim(text=line, source_sentence=line))

            return claims[:20]  # Cap at 20 claims

        except Exception:
            # Fallback: split by sentences
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.strip()) > 15]
            return [Claim(text=s, source_sentence=s) for s in sentences[:20]]

    async def retrieve_evidence(self, claim: Claim, context_docs: list[str]) -> list[dict[str, Any]]:
        """Search context documents for evidence. Uses vector search when available, falls back to keyword overlap."""
        # Try vector-based evidence retrieval
        try:
            from backend.app.services.vectorstore.embedding_pipeline import EmbeddingPipeline
            from backend.app.services.vectorstore.pgvector_store import PgVectorStore
            from backend.app.services.config import get_settings
            settings = get_settings()
            if "postgresql" in settings.database_url:
                pipeline = EmbeddingPipeline()
                query_embedding = await pipeline.embed_query(claim.text)
                # Use pgvector similarity search
                store = PgVectorStore(settings.database_url)
                from backend.app.services.db.engine import get_session_factory
                async with get_session_factory()() as session:
                    results = await store.search_similar(session, query_embedding, top_k=3)
                    if results:
                        return [
                            {
                                "doc_index": r.chunk_index,
                                "relevant_text": r.content[:300],
                                "overlap_score": round(r.similarity, 3),
                                "source": r.source,
                            }
                            for r in results
                        ]
        except Exception as exc:
            logger.debug("vector_evidence_fallback", extra={"event": "vector_evidence_fallback", "error": str(exc)})

        # Fallback: keyword overlap scoring
        evidence = []
        claim_lower = claim.text.lower()

        for i, doc in enumerate(context_docs):
            # Simple keyword overlap scoring
            doc_lower = doc.lower()
            claim_words = set(claim_lower.split())
            doc_words = set(doc_lower.split())
            overlap = len(claim_words & doc_words) / max(len(claim_words), 1)

            if overlap > 0.3:
                # Find the most relevant sentence
                sentences = [s.strip() for s in doc.split('.') if s.strip()]
                best_sentence = max(
                    sentences,
                    key=lambda s: len(set(s.lower().split()) & claim_words),
                    default=doc[:200],
                )
                evidence.append({
                    "doc_index": i,
                    "relevant_text": best_sentence[:300],
                    "overlap_score": round(overlap, 3),
                })

        return sorted(evidence, key=lambda e: e["overlap_score"], reverse=True)[:3]

    async def verify_claim(self, claim: Claim, context_docs: list[str]) -> Claim:
        """Verify a single claim against context documents."""
        evidence = await self.retrieve_evidence(claim, context_docs)
        claim.evidence = evidence

        if not evidence:
            claim.verdict = "unsupported"
            claim.confidence = 0.2
            claim.reasoning = "No supporting evidence found in context documents"
            return claim

        # Use best evidence overlap as confidence proxy
        best_score = max(e["overlap_score"] for e in evidence)

        if best_score > 0.6:
            claim.verdict = "verified"
            claim.confidence = min(best_score * 1.2, 1.0)
            claim.reasoning = f"Strong evidence found (overlap: {best_score:.2f})"
        elif best_score > 0.4:
            claim.verdict = "verified"
            claim.confidence = best_score
            claim.reasoning = f"Moderate evidence found (overlap: {best_score:.2f})"
        else:
            claim.verdict = "unverified"
            claim.confidence = best_score
            claim.reasoning = f"Weak evidence (overlap: {best_score:.2f})"

        return claim

    async def check(
        self,
        text: str,
        context_docs: Optional[list[str]] = None,
        context_doc_ids: Optional[list[str]] = None,
    ) -> FactCheckResult:
        """
        Full fact-checking pipeline.

        Args:
            text: LLM-generated text to verify
            context_docs: List of context document texts to check against
            context_doc_ids: IDs to look up documents (if context_docs not provided)
        """
        if context_docs is None:
            context_docs = []

        # 1. Decompose into claims
        claims = await self.decompose_claims(text)

        if not claims:
            return FactCheckResult(
                original_text=text, claims=[], overall_score=1.0, passed=True,
                pass_threshold=self.pass_threshold,
            )

        # 2 & 3. Retrieve evidence and verify each claim
        verified_claims = []
        for claim in claims:
            verified = await self.verify_claim(claim, context_docs)
            verified_claims.append(verified)

        # 4. Compute overall score
        if verified_claims:
            score_map = {"verified": 1.0, "unverified": 0.5, "unsupported": 0.2, "refuted": 0.0}
            total = sum(score_map.get(c.verdict, 0.5) for c in verified_claims)
            overall_score = total / len(verified_claims)
        else:
            overall_score = 1.0

        passed = overall_score >= self.pass_threshold

        result = FactCheckResult(
            original_text=text,
            claims=verified_claims,
            overall_score=overall_score,
            passed=passed,
            pass_threshold=self.pass_threshold,
        )

        logger.info("fact_check_completed", extra={
            "event": "fact_check_completed",
            "total_claims": len(verified_claims),
            "overall_score": round(overall_score, 3),
            "passed": passed,
        })

        return result

"""
ColBERT-based semantic embedder for widget variant scoring.

Uses token-level late interaction (MaxSim) for sharp discrimination
between widget variant descriptions. Unlike sentence-level cosine
similarity (BGE), ColBERT preserves token-level alignment — so
"3-phase voltage" correctly maps to trend-rgb-phase even though the
sentence embedding of that variant is close to generic trend-line.

Hierarchy of embedding strategies:
1. RAGatouille ColBERT v2 — best: token-level late interaction
2. sentence-transformers BGE — good: sentence-level cosine
3. TF-IDF fallback — baseline: keyword overlap with IDF weighting

All strategies are lazy-loaded and cached. If no ML library is
available, the fallback uses pure-Python TF-IDF.
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any

logger = logging.getLogger(__name__)

# ── Variant description corpus ──────────────────────────────────────────────
# Built once from widget_catalog.py, cached for the process lifetime.

_variant_corpus: dict[str, str] | None = None
_scenario_for_variant: dict[str, str] | None = None
_embedding_client_cache: dict[str, list[float]] | None = None
_embedding_client_model_name: str | None = None


def _build_corpus() -> dict[str, str]:
    """Build variant → description mapping from the widget catalog."""
    global _variant_corpus, _scenario_for_variant
    if _variant_corpus is not None:
        return _variant_corpus

    from backend.app.services.widget_intelligence.widget_catalog import WIDGET_CATALOG

    corpus: dict[str, str] = {}
    scenario_map: dict[str, str] = {}

    for entry in WIDGET_CATALOG:
        scenario = entry["scenario"]
        base_desc = entry["description"]
        good_for = " ".join(entry.get("good_for", []))

        variants = entry.get("variants", {})
        if variants:
            for vname, vdesc in variants.items():
                corpus[vname] = f"{vdesc} {base_desc} {good_for}"
                scenario_map[vname] = scenario
        else:
            # Single-variant scenario
            corpus[scenario] = f"{base_desc} {good_for}"
            scenario_map[scenario] = scenario

    _variant_corpus = corpus
    _scenario_for_variant = scenario_map
    logger.info(f"[SemanticEmbedder] Built corpus: {len(corpus)} variants")
    return corpus


def get_scenario_for_variant(variant: str) -> str:
    """Return the scenario for a variant key."""
    _build_corpus()
    return (_scenario_for_variant or {}).get(variant, variant)


# ── Strategy 1: RAGatouille ColBERT v2 ─────────────────────────────────────

_colbert_model = None
_colbert_available: bool | None = None


def _load_colbert():
    """Lazy-load ColBERT v2 via RAGatouille."""
    global _colbert_model, _colbert_available
    if _colbert_available is not None:
        return _colbert_model

    try:
        from ragatouille import RAGPretrainedModel
        _colbert_model = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        _colbert_available = True
        logger.info("[SemanticEmbedder] ColBERT v2 loaded via RAGatouille")
    except (ImportError, Exception) as e:
        _colbert_available = False
        logger.info(f"[SemanticEmbedder] ColBERT not available: {e}")
    return _colbert_model


def _score_colbert(query: str, candidates: dict[str, str]) -> dict[str, float]:
    """Score candidates using ColBERT v2 late interaction.

    Uses RAGatouille's rerank API for efficient scoring of
    query against multiple candidate descriptions.
    """
    model = _load_colbert()
    if model is None:
        return {}

    try:
        variant_names = list(candidates.keys())
        docs = list(candidates.values())

        # RAGatouille rerank: scores each doc against the query
        results = model.rerank(query=query, documents=docs, k=len(docs))

        scores: dict[str, float] = {}
        for r in results:
            idx = r.get("result_index", -1)
            score = r.get("score", 0.0)
            if 0 <= idx < len(variant_names):
                # Normalize ColBERT scores to [0, 1]
                scores[variant_names[idx]] = _sigmoid(score / 20.0)

        return scores
    except Exception as e:
        logger.warning(f"[SemanticEmbedder] ColBERT scoring failed: {e}")
        return {}


# ── Strategy 2: Sentence-transformers BGE ──────────────────────────────────

_bge_model = None
_bge_available: bool | None = None
_bge_embeddings: dict[str, Any] | None = None


def _load_bge():
    """Lazy-load BGE embedding model."""
    global _bge_model, _bge_available
    if _bge_available is not None:
        return _bge_model

    try:
        from sentence_transformers import SentenceTransformer
        _bge_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        _bge_available = True
        logger.info("[SemanticEmbedder] BGE model loaded")
    except (ImportError, Exception) as e:
        _bge_available = False
        logger.info(f"[SemanticEmbedder] BGE not available: {e}")
    return _bge_model


def _get_bge_embeddings(corpus: dict[str, str]) -> dict[str, Any]:
    """Pre-compute and cache BGE embeddings for all variants."""
    global _bge_embeddings
    if _bge_embeddings is not None:
        return _bge_embeddings

    model = _load_bge()
    if model is None:
        return {}

    import numpy as np
    names = list(corpus.keys())
    texts = list(corpus.values())
    embeddings = model.encode(texts, normalize_embeddings=True)

    _bge_embeddings = {name: emb for name, emb in zip(names, embeddings)}
    logger.info(f"[SemanticEmbedder] Cached BGE embeddings for {len(names)} variants")
    return _bge_embeddings


def _score_bge(query: str, candidates: dict[str, str]) -> dict[str, float]:
    """Score candidates using BGE sentence-level cosine similarity."""
    model = _load_bge()
    if model is None:
        return {}

    try:
        import numpy as np
        corpus = _build_corpus()
        cached = _get_bge_embeddings(corpus)

        query_emb = model.encode([query], normalize_embeddings=True)[0]

        scores: dict[str, float] = {}
        for variant in candidates:
            emb = cached.get(variant)
            if emb is not None:
                sim = float(np.dot(query_emb, emb))
                scores[variant] = max(0.0, sim)  # Clamp negatives
            else:
                scores[variant] = 0.0
        return scores
    except Exception as e:
        logger.warning(f"[SemanticEmbedder] BGE scoring failed: {e}")
        return {}


# ── Strategy 2b: Reuse Pipeline EmbeddingClient (no duplicate model load) ───

def _get_embedding_client_embeddings(
    corpus: dict[str, str],
    embedding_client: Any,
) -> dict[str, list[float]]:
    """Compute and cache embeddings for the variant corpus using EmbeddingClient."""
    global _embedding_client_cache, _embedding_client_model_name

    model_name = getattr(embedding_client, "_model_name", None)
    if _embedding_client_cache is not None and _embedding_client_model_name == model_name:
        return _embedding_client_cache

    try:
        names = list(corpus.keys())
        texts = [corpus[n] for n in names]
        vecs = embedding_client.embed_batch(texts)
        cache = {
            name: vec
            for name, vec in zip(names, vecs)
            if isinstance(vec, list) and len(vec) > 0
        }
        _embedding_client_cache = cache
        _embedding_client_model_name = model_name
        logger.info(f"[SemanticEmbedder] Cached EmbeddingClient vectors for {len(cache)} variants")
        return cache
    except Exception as e:
        logger.warning(f"[SemanticEmbedder] EmbeddingClient caching failed: {e}")
        _embedding_client_cache = {}
        _embedding_client_model_name = model_name
        return {}


def _score_embedding_client(
    query: str,
    candidates: dict[str, str],
    embedding_client: Any,
    query_embedding: list[float] | None = None,
) -> dict[str, float]:
    """Score candidates using the pipeline EmbeddingClient cosine similarity."""
    try:
        if embedding_client is None or not getattr(embedding_client, "available", False):
            return {}

        corpus = _build_corpus()
        cached = _get_embedding_client_embeddings(corpus, embedding_client)
        if not cached:
            return {}

        q_emb = query_embedding or embedding_client.embed(query)
        if not q_emb:
            return {}

        from backend.app.services.widget_intelligence.embedding import EmbeddingClient

        scores: dict[str, float] = {}
        for variant in candidates:
            emb = cached.get(variant)
            if emb is None:
                scores[variant] = 0.0
                continue
            sim = EmbeddingClient.cosine_similarity(q_emb, emb)
            scores[variant] = max(0.0, float(sim))
        return scores
    except Exception as e:
        logger.warning(f"[SemanticEmbedder] EmbeddingClient scoring failed: {e}")
        return {}


# ── Strategy 3: TF-IDF fallback (pure Python) ─────────────────────────────

_idf_cache: dict[str, float] | None = None


def _compute_idf(corpus: dict[str, str]) -> dict[str, float]:
    """Compute IDF weights from the variant corpus."""
    global _idf_cache
    if _idf_cache is not None:
        return _idf_cache

    doc_count = len(corpus)
    term_doc_freq: dict[str, int] = {}

    for text in corpus.values():
        tokens = set(_tokenize(text))
        for token in tokens:
            term_doc_freq[token] = term_doc_freq.get(token, 0) + 1

    _idf_cache = {
        term: math.log((doc_count + 1) / (df + 1)) + 1
        for term, df in term_doc_freq.items()
    }
    return _idf_cache


def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric."""
    return re.findall(r'[a-z0-9]+', text.lower())


def _score_tfidf(query: str, candidates: dict[str, str]) -> dict[str, float]:
    """Score candidates using TF-IDF cosine similarity (pure Python)."""
    corpus = _build_corpus()
    idf = _compute_idf(corpus)

    query_tokens = _tokenize(query)
    if not query_tokens:
        return {v: 0.0 for v in candidates}

    # Query TF-IDF vector
    query_tf: dict[str, float] = {}
    for t in query_tokens:
        query_tf[t] = query_tf.get(t, 0) + 1
    query_vec = {t: tf * idf.get(t, 1.0) for t, tf in query_tf.items()}
    query_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

    scores: dict[str, float] = {}
    for variant, text in candidates.items():
        doc_tokens = _tokenize(text)
        doc_tf: dict[str, float] = {}
        for t in doc_tokens:
            doc_tf[t] = doc_tf.get(t, 0) + 1
        doc_vec = {t: tf * idf.get(t, 1.0) for t, tf in doc_tf.items()}
        doc_norm = math.sqrt(sum(v * v for v in doc_vec.values())) or 1.0

        dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0)
                  for t in set(query_vec) | set(doc_vec))
        scores[variant] = dot / (query_norm * doc_norm)

    return scores


# ── Public API ──────────────────────────────────────────────────────────────

def _sigmoid(x: float) -> float:
    """Sigmoid normalization."""
    return 1.0 / (1.0 + math.exp(-x))


def score_variants_semantic(
    query: str,
    scenario: str | None = None,
    candidates: list[str] | None = None,
    embedding_client: Any | None = None,
    query_embedding: list[float] | None = None,
    strategy: str = "auto",
) -> dict[str, float]:
    """Score widget variants against a user query using the best available
    semantic embedding strategy.

    Args:
        query: User's natural language query.
        scenario: If provided, only score variants for this scenario.
        candidates: If provided, only score these specific variants.
        embedding_client: Optional pipeline EmbeddingClient to avoid duplicate model load.
        query_embedding: Optional pre-computed query embedding for the embedding_client path.
        strategy: One of "auto", "embedding_client", "colbert_v2", "bge", "tfidf".

    Returns:
        Dict mapping variant names to semantic scores in [0, 1].
    """
    corpus = _build_corpus()
    strat = (strategy or "auto").strip().lower()

    # Filter corpus to requested scope
    if candidates:
        filtered = {v: corpus[v] for v in candidates if v in corpus}
    elif scenario:
        filtered = {
            v: desc for v, desc in corpus.items()
            if (_scenario_for_variant or {}).get(v) == scenario
        }
    else:
        filtered = corpus

    if not filtered:
        return {}

    # Strategy selection: callers can force lightweight scoring (e.g., "tfidf")
    # to avoid cold-starting large models during latency-sensitive paths.
    if strat in ("tfidf",):
        scores = _score_tfidf(query, filtered)
        logger.debug(f"[SemanticEmbedder] Used TF-IDF for {len(scores)} variants")
        return scores

    if strat in ("embedding_client", "embedding", "auto") and embedding_client is not None:
        scores = _score_embedding_client(
            query, filtered, embedding_client=embedding_client, query_embedding=query_embedding,
        )
        if scores or strat != "auto":
            logger.debug(f"[SemanticEmbedder] Used EmbeddingClient for {len(scores)} variants")
            return scores

    if strat in ("colbert_v2", "colbert", "auto"):
        scores = _score_colbert(query, filtered)
        if scores or strat != "auto":
            logger.debug(f"[SemanticEmbedder] Used ColBERT for {len(scores)} variants")
            return scores

    if strat in ("bge", "auto"):
        scores = _score_bge(query, filtered)
        if scores or strat != "auto":
            logger.debug(f"[SemanticEmbedder] Used BGE for {len(scores)} variants")
            return scores

    scores = _score_tfidf(query, filtered)
    logger.debug(f"[SemanticEmbedder] Used TF-IDF fallback for {len(scores)} variants")
    return scores


def get_embedding_strategy() -> str:
    """Return which embedding strategy is active."""
    _load_colbert()
    if _colbert_available:
        return "colbert_v2"
    _load_bge()
    if _bge_available:
        return "bge"
    return "tfidf"

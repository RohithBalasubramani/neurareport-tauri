"""Embedding client stub for the widget intelligence pipeline."""
from __future__ import annotations

import math
from typing import Optional


class EmbeddingClient:
    """Minimal embedding client. Provides cosine similarity for semantic scoring."""

    def __init__(self, model_name: Optional[str] = None):
        self._model_name = model_name

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def embed(self, text: str) -> list[float]:
        """Stub: return empty embedding. Override with real implementation."""
        return []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Stub: return empty embeddings. Override with real implementation."""
        return [[] for _ in texts]

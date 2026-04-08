from __future__ import annotations

from .signatures import is_dspy_available, get_signature, available_signatures, StubPrediction
from .modules import get_module, CachedModule
from .claude_adapter import ClaudeCodeLM, configure_dspy_with_claude
from .optimizer import DSPyOptimizer, OptimizationConfig

__all__ = [
    "is_dspy_available",
    "get_signature",
    "available_signatures",
    "StubPrediction",
    "get_module",
    "CachedModule",
    "ClaudeCodeLM",
    "configure_dspy_with_claude",
    "DSPyOptimizer",
    "OptimizationConfig",
]

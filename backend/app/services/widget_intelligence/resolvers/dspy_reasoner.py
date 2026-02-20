"""
DSPy-based reasoning for widget variant selection (Layer 3).

Uses DSPy ChainOfThought to reason about which variant best fits
the DATA SHAPE PROPERTIES — not keywords or text descriptions.

DSPy is invoked only when the LangGraph constraint graph (Layer 2)
produces ambiguous results (confidence gap < 0.10 or top score < 0.45).

Input: structured data shape properties + pre-scored candidates.
Output: reasoned selection based on data properties.

Falls back to pure constraint-based selection if DSPy/LLM is unavailable.
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)

# ── Try to import DSPy ──────────────────────────────────────────────────────

_dspy_available = False
_dspy_configured = False
_dspy_last_attempt_ts = 0.0

try:
    import dspy
    _dspy_available = True
    logger.debug("[DSPyReasoner] DSPy library available")
except ImportError:
    logger.debug("[DSPyReasoner] DSPy not available, using constraint-based fallback")


# ── DSPy Signatures ─────────────────────────────────────────────────────────

if _dspy_available:
    class VariantSelection(dspy.Signature):
        """Select the best data visualization variant based on data properties.

        Given structured data shape properties and pre-scored candidates,
        reason about which variant produces the most informative visualization.
        Do NOT rely on keywords in the query — focus on data properties.
        """
        query: str = dspy.InputField(desc="User's data query")
        query_type: str = dspy.InputField(
            desc="status/analysis/comparison/trend/diagnostic/overview/alert/forecast"
        )
        question_intent: str = dspy.InputField(
            desc="baseline/trend/anomaly/comparison/correlation/health"
        )
        data_shape: str = dspy.InputField(desc=(
            "Measured data properties: entity_count, metric_count, variance(spread), "
            "temporal_density, dominant_metric_type, has_phase_data, has_cumulative, "
            "has_binary, has_hierarchy, data_richness, flags"
        ))
        candidates: str = dspy.InputField(
            desc="Surviving variants with composite scores and descriptions, one per line"
        )
        selected_variant: str = dspy.OutputField(
            desc="Single best variant name from candidates list"
        )
        reasoning: str = dspy.OutputField(
            desc="Brief explanation citing specific data properties that make this variant best"
        )

    class VariantValidator(dspy.Signature):
        """Validate that a selected variant can meaningfully render this data shape."""
        variant: str = dspy.InputField(desc="Selected variant name")
        data_shape: str = dspy.InputField(desc="Data shape properties")
        is_valid: str = dspy.OutputField(desc="'yes' if variant fits the data shape, 'no' otherwise")
        concern: str = dspy.OutputField(
            desc="Specific data property that makes this variant poor, or 'none'"
        )


# ── DSPy Module ─────────────────────────────────────────────────────────────

if _dspy_available:
    class VariantPlanner(dspy.Module):
        """DSPy module: ChainOfThought selection + Predict validation."""

        def __init__(self):
            super().__init__()
            self.select = dspy.ChainOfThought(VariantSelection)
            self.validate = dspy.Predict(VariantValidator)

        def forward(
            self,
            query: str,
            query_type: str,
            question_intent: str,
            data_shape: str,
            candidates: str,
        ) -> dspy.Prediction:
            selection = self.select(
                query=query,
                query_type=query_type,
                question_intent=question_intent,
                data_shape=data_shape,
                candidates=candidates,
            )
            validation = self.validate(
                variant=selection.selected_variant,
                data_shape=data_shape,
            )
            return dspy.Prediction(
                selected_variant=selection.selected_variant,
                reasoning=selection.reasoning,
                is_valid=validation.is_valid,
                concern=validation.concern,
            )


# ── LLM Configuration ──────────────────────────────────────────────────────

_DSPY_CONFIG_RETRY_SECONDS = 60.0


def _detect_vllm_model_id(vllm_base_url: str) -> str | None:
    """Detect a usable model id from a vLLM OpenAI-compatible `/models` endpoint."""
    try:
        import httpx
        base = vllm_base_url.rstrip("/")
        r = httpx.get(f"{base}/models", timeout=0.6)
        if r.status_code != 200:
            return None
        data = r.json()
        ids = [m.get("id") for m in (data.get("data") or []) if isinstance(m, dict) and m.get("id")]
        if not ids:
            return None

        # Prefer the widget-selection LoRA if present, otherwise fall back to the first id.
        for preferred in ("cc-widgets", "cc-data-query"):
            if preferred in ids:
                return preferred
        return ids[0]
    except Exception:
        return None


def _configure_dspy() -> bool:
    """Configure DSPy with available LLM backend.

    Tries in order:
    1. Local vLLM endpoint (VLLM_URL or VLLM_BASE_URL)
    2. OpenAI API (OPENAI_API_KEY)
    3. Anthropic API (ANTHROPIC_API_KEY)
    """
    global _dspy_configured, _dspy_last_attempt_ts
    if _dspy_configured or not _dspy_available:
        return _dspy_configured

    # Avoid repeated network attempts when the backend is down (e.g., tests).
    now = time.monotonic()
    if _dspy_last_attempt_ts and (now - _dspy_last_attempt_ts) < _DSPY_CONFIG_RETRY_SECONDS:
        return False
    _dspy_last_attempt_ts = now

    import os

    # Explicit kill switch (useful for deterministic / low-latency deployments).
    disable = os.environ.get("PIPELINE_DSPY_DISABLE") or os.environ.get("DSPY_DISABLE")
    if disable and str(disable).strip().lower() in ("1", "true", "yes", "on"):
        return False

    # Try local vLLM first (fastest, no API cost).
    vllm_url = os.environ.get("VLLM_URL") or os.environ.get("VLLM_BASE_URL")
    if not vllm_url:
        # Fall back to pipeline config default even when env vars aren't exported.
        try:
            from backend.app.services.widget_intelligence.config import VLLM_BASE_URL as _CFG_VLLM_BASE_URL
            vllm_url = _CFG_VLLM_BASE_URL
        except Exception:
            vllm_url = None

    if vllm_url:
        try:
            model_id = (
                os.environ.get("DSPY_VLLM_MODEL")
                or os.environ.get("VLLM_MODEL")
                or _detect_vllm_model_id(vllm_url)
            )
            if not model_id:
                raise RuntimeError("Could not detect vLLM model id from /models (set DSPY_VLLM_MODEL)")

            lm = dspy.LM(
                model=f"openai/{model_id}",
                api_base=vllm_url,
                api_key="dummy",
                max_tokens=200,
                temperature=0.1,
            )
            dspy.configure(lm=lm)
            _dspy_configured = True
            logger.info(f"[DSPyReasoner] Configured with vLLM at {vllm_url} (model={model_id})")
            return True
        except Exception as e:
            logger.debug(f"[DSPyReasoner] vLLM config failed: {e}")

    # Try OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            lm = dspy.LM(
                model="openai/gpt-4o-mini",
                api_key=openai_key,
                max_tokens=200,
                temperature=0.1,
            )
            dspy.configure(lm=lm)
            _dspy_configured = True
            logger.info("[DSPyReasoner] Configured with OpenAI gpt-4o-mini")
            return True
        except Exception as e:
            logger.debug(f"[DSPyReasoner] OpenAI config failed: {e}")

    # Try Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            lm = dspy.LM(
                model="anthropic/claude-haiku-4-5-20251001",
                api_key=anthropic_key,
                max_tokens=200,
                temperature=0.1,
            )
            dspy.configure(lm=lm)
            _dspy_configured = True
            logger.info("[DSPyReasoner] Configured with Anthropic Claude Haiku")
            return True
        except Exception as e:
            logger.debug(f"[DSPyReasoner] Anthropic config failed: {e}")

    logger.info("[DSPyReasoner] No LLM backend available, DSPy reasoning disabled")
    return False


# ── Constraint-based fallback (no LLM) ─────────────────────────────────────

def _constraint_fallback(
    candidates: list[str],
    composite_scores: dict[str, float],
) -> tuple[str, str]:
    """Pure constraint-based selection without LLM.

    Simply picks the highest-scoring candidate from composite scores.
    """
    if not candidates:
        return "", "no candidates"

    best = candidates[0]
    best_score = composite_scores.get(best, 0.0)
    for v in candidates[1:]:
        s = composite_scores.get(v, 0.0)
        if s > best_score:
            best_score = s
            best = v

    return best, f"Top composite score ({best_score:.3f}), no DSPy available"


# ── Public API ──────────────────────────────────────────────────────────────

_planner_module = None


def reason_variant_selection(
    query: str,
    candidates: list[str],
    composite_scores: dict[str, float],
    data_shape_text: str,
    query_type: str = "overview",
    question_intent: str = "",
    candidate_descriptions: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Use DSPy to reason about which variant best fits the data shape.

    Args:
        query: User's natural language query.
        candidates: List of candidate variant names.
        composite_scores: Pre-computed composite scores from Layer 2.
        data_shape_text: Formatted DataShapeProfile text.
        query_type: ParsedIntent query type.
        question_intent: Question dict intent.
        candidate_descriptions: Optional {variant: description} for context.

    Returns:
        (selected_variant, reasoning) tuple.
    """
    global _planner_module

    if not candidates:
        return "", "no candidates"

    descs = candidate_descriptions or {}

    # Try DSPy first
    if _dspy_available and _configure_dspy():
        try:
            if _planner_module is None:
                _planner_module = VariantPlanner()

            # Format candidates with scores and descriptions
            candidates_text = "\n".join(
                f"- {v} (composite={composite_scores.get(v, 0.0):.3f}): "
                f"{descs.get(v, 'visualization variant')}"
                for v in candidates
            )

            result = _planner_module(
                query=query,
                query_type=query_type,
                question_intent=question_intent,
                data_shape=data_shape_text,
                candidates=candidates_text,
            )

            selected = result.selected_variant.strip()
            reasoning = result.reasoning.strip()

            # Validate the LLM picked a real candidate
            if selected in candidates:
                if hasattr(result, "is_valid") and "no" in str(result.is_valid).lower():
                    logger.info(
                        f"[DSPyReasoner] LLM pick {selected} failed validation: "
                        f"{result.concern}. Falling back."
                    )
                else:
                    logger.debug(f"[DSPyReasoner] LLM selected: {selected}")
                    return selected, f"[DSPy] {reasoning}"
            else:
                logger.warning(
                    f"[DSPyReasoner] LLM returned invalid variant '{selected}', "
                    f"candidates: {candidates}"
                )

        except Exception as e:
            logger.warning(f"[DSPyReasoner] DSPy call failed: {e}")

    # Fallback: pick highest composite score
    return _constraint_fallback(candidates, composite_scores)


def is_dspy_available() -> bool:
    """Check if DSPy is installed and an LLM backend is configured."""
    if not _dspy_available:
        return False
    return _configure_dspy()

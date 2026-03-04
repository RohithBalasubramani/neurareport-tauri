from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("neura.quality.evaluator")


@dataclass
class QualityScore:
    """Result of a quality evaluation."""

    overall: float  # 0.0 - 1.0
    criteria: Dict[str, float]
    feedback: str
    heuristic_flags: List[str] = field(default_factory=list)


class QualityEvaluator:
    """Multi-criteria LLM + heuristic quality scoring.

    Evaluates generated output using a combination of fast heuristic
    checks and optional LLM-based criterion scoring.  Heuristic flags
    surface common problems (empty output, repetition, error markers)
    while the LLM provides nuanced per-criterion ratings.
    """

    DEFAULT_CRITERIA: List[str] = [
        "completeness",
        "accuracy",
        "clarity",
        "relevance",
        "formatting",
    ]
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "completeness": 0.25,
        "accuracy": 0.30,
        "clarity": 0.20,
        "relevance": 0.15,
        "formatting": 0.10,
    }

    def __init__(
        self,
        criteria: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
        client: Any = None,
        use_llm: bool = True,
    ) -> None:
        self.criteria = criteria or list(self.DEFAULT_CRITERIA)
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)
        self._client = client
        self.use_llm = use_llm

    # ------------------------------------------------------------------
    # Lazy LLM client accessor
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from backend.app.services.llm.client import get_llm_client

                self._client = get_llm_client()
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    "llm_client_unavailable",
                    extra={"event": "llm_client_unavailable", "error": str(exc)},
                )
        return self._client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, output: str, context: Dict[str, Any]) -> QualityScore:
        """Evaluate *output* and return a :class:`QualityScore`.

        Parameters
        ----------
        output:
            The generated text to evaluate.
        context:
            Auxiliary information (e.g. the original prompt, expected
            topics) available to the evaluator.
        """

        # 1. Heuristic pass (always runs)
        heuristic_scores, flags = self._heuristic_evaluate(output)

        # 2. LLM pass (optional, skipped for trivial output)
        llm_scores: Dict[str, float] = {}
        if self.use_llm and len(output.strip()) >= 50:
            llm_scores = self._llm_evaluate(output, context)

        # 3. Merge: LLM scores take precedence where available,
        #    heuristic scores fill the gaps.
        merged: Dict[str, float] = {}
        for criterion in self.criteria:
            if criterion in llm_scores:
                merged[criterion] = llm_scores[criterion]
            elif criterion in heuristic_scores:
                merged[criterion] = heuristic_scores[criterion]
            else:
                # Default to a neutral 0.5 for un-scored criteria
                merged[criterion] = 0.5

        # 4. Weighted average for overall score
        total_weight = sum(self.weights.get(c, 0.0) for c in self.criteria)
        if total_weight > 0:
            overall = sum(
                merged[c] * self.weights.get(c, 0.0) for c in self.criteria
            ) / total_weight
        else:
            overall = sum(merged.values()) / max(len(merged), 1)

        overall = max(0.0, min(1.0, overall))

        # 5. Build human-readable feedback
        feedback = self._build_feedback(merged, flags, overall)

        return QualityScore(
            overall=round(overall, 3),
            criteria={k: round(v, 3) for k, v in merged.items()},
            feedback=feedback,
            heuristic_flags=flags,
        )

    # ------------------------------------------------------------------
    # LLM evaluation
    # ------------------------------------------------------------------

    def _llm_evaluate(
        self, output: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Ask the LLM to rate each criterion 0.0-1.0."""
        client = self._get_client()
        if client is None:
            return {}

        criteria_list = "\n".join(
            f"- {c}" for c in self.criteria
        )
        prompt_text = context.get("prompt", "(no prompt provided)")

        system_msg = (
            "You are a strict quality evaluator. Given the ORIGINAL PROMPT "
            "and the GENERATED OUTPUT, rate the output on each of the "
            "following criteria from 0.0 (worst) to 1.0 (best).\n\n"
            f"Criteria:\n{criteria_list}\n\n"
            "Return ONLY a JSON object mapping each criterion name to a "
            "float score.  Example: {\"completeness\": 0.8, \"accuracy\": 0.9, ...}"
        )

        user_msg = (
            f"ORIGINAL PROMPT:\n{str(prompt_text)[:2000]}\n\n"
            f"GENERATED OUTPUT:\n{output[:4000]}"
        )

        try:
            response = client.complete(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                description="quality_evaluation",
                temperature=0.1,
            )

            content = response["choices"][0]["message"]["content"]
            return self._parse_llm_scores(content)
        except Exception as exc:
            logger.warning(
                "llm_evaluate_failed",
                extra={"event": "llm_evaluate_failed", "error": str(exc)},
            )
            return {}

    def _parse_llm_scores(self, raw: str) -> Dict[str, float]:
        """Extract criterion scores from an LLM response string."""
        import json as _json

        # Try to extract JSON from the response (may have markdown fences)
        text = raw.strip()
        json_match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
        if not json_match:
            return {}

        try:
            data = _json.loads(json_match.group())
        except _json.JSONDecodeError:
            return {}

        scores: Dict[str, float] = {}
        for criterion in self.criteria:
            if criterion in data:
                try:
                    val = float(data[criterion])
                    scores[criterion] = max(0.0, min(1.0, val))
                except (ValueError, TypeError):
                    pass
        return scores

    # ------------------------------------------------------------------
    # Heuristic evaluation
    # ------------------------------------------------------------------

    def _heuristic_evaluate(
        self, output: str,
    ) -> Tuple[Dict[str, float], List[str]]:
        """Run fast rule-based checks and return (scores, flags)."""
        scores: Dict[str, float] = {}
        flags: List[str] = []
        stripped = output.strip()

        # Empty output
        if not stripped:
            scores["completeness"] = 0.0
            flags.append("empty_output")
            return scores, flags

        # Very short output
        if len(stripped) < 50:
            scores["completeness"] = 0.3
            flags.append("very_short")

        # No structure (no newlines, no headers like # or **)
        has_newlines = "\n" in stripped
        has_headers = bool(re.search(r"(^|\n)(#{1,6}\s|[*]{2})", stripped))
        if not has_newlines and not has_headers:
            scores["formatting"] = 0.4
            flags.append("no_structure")

        # Repetitive text (same sentence repeated 3+ times)
        sentences = re.split(r"[.!?]+", stripped)
        sentences = [s.strip().lower() for s in sentences if s.strip()]
        if sentences:
            from collections import Counter

            counts = Counter(sentences)
            most_common_count = counts.most_common(1)[0][1] if counts else 0
            if most_common_count >= 3:
                scores["clarity"] = 0.3
                flags.append("repetitive")

        # Contains error markers
        error_pattern = re.compile(
            r"\b(Error:|Failed|Traceback|Exception:|FATAL)\b", re.IGNORECASE
        )
        if error_pattern.search(stripped):
            scores["accuracy"] = 0.2
            flags.append("error_markers")

        return scores, flags

    # ------------------------------------------------------------------
    # Feedback builder
    # ------------------------------------------------------------------

    def _build_feedback(
        self,
        scores: Dict[str, float],
        flags: List[str],
        overall: float,
    ) -> str:
        """Build a human-readable summary of the evaluation."""
        parts: List[str] = []

        if overall >= 0.8:
            parts.append("Overall quality is good.")
        elif overall >= 0.5:
            parts.append("Overall quality is acceptable but could improve.")
        else:
            parts.append("Overall quality is below acceptable thresholds.")

        # Mention low-scoring criteria
        weak = [c for c, v in scores.items() if v < 0.5]
        if weak:
            parts.append(f"Weak criteria: {', '.join(weak)}.")

        if flags:
            parts.append(f"Issues detected: {', '.join(flags)}.")

        return " ".join(parts)

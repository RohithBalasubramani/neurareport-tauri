from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("neura.optimization.optimizer")

# ---------------------------------------------------------------------------
# Optional dependency: DSPy
# ---------------------------------------------------------------------------
_dspy_available = False
try:
    import dspy

    _dspy_available = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
from .claude_adapter import configure_dspy_with_claude
from .modules import get_module


# =========================================================================== #
#  Configuration                                                              #
# =========================================================================== #


@dataclass
class OptimizationConfig:
    """Configuration for DSPy optimization runs.

    Attributes:
        max_bootstrapped_demos: Maximum number of bootstrapped
            demonstrations to generate during optimization.
        max_labeled_demos: Maximum number of labeled demonstrations
            to include in prompts.
        num_candidate_programs: Number of candidate prompt programs
            to evaluate during optimization.
        metric_threshold: Minimum metric score to consider a candidate
            successful during bootstrapping.
        save_dir: Directory to save/load optimized module checkpoints.
            If ``None``, checkpoints are not persisted.
    """

    max_bootstrapped_demos: int = 3
    max_labeled_demos: int = 5
    num_candidate_programs: int = 10
    metric_threshold: float = 0.7
    save_dir: Optional[Path] = None


# =========================================================================== #
#  Default quality metric                                                     #
# =========================================================================== #


def default_quality_metric(
    example: Any,
    prediction: Any,
    trace: Any = None,
) -> float:
    """Simple quality metric for report quality assessment.

    Checks whether the prediction contains a non-empty ``quality_score``
    field and attempts to parse it as a float.  Returns the parsed score
    if valid, ``0.5`` as a neutral default if parsing fails, or ``0.0``
    if the field is entirely absent.

    Args:
        example: The DSPy ``Example`` (unused in this basic metric).
        prediction: The prediction object returned by the module.
        trace: Optional trace information (unused).

    Returns:
        A float score in the range ``[0.0, 1.0]``.
    """
    score_str = getattr(prediction, "quality_score", "")
    if not score_str:
        return 0.0

    try:
        score = float(score_str)
        return max(0.0, min(1.0, score))
    except (ValueError, TypeError):
        return 0.5


# =========================================================================== #
#  DSPyOptimizer                                                              #
# =========================================================================== #


class DSPyOptimizer:
    """BootstrapFewShot optimization runner for DSPy modules.

    Wraps the DSPy ``BootstrapFewShot`` teleprompter to compile optimized
    prompt programs, evaluate them, and persist checkpoints.

    Args:
        config: Optimization configuration.  If ``None``, default values
            are used.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None) -> None:
        self.config = config or OptimizationConfig()

    # ------------------------------------------------------------------ #
    #  Optimize                                                           #
    # ------------------------------------------------------------------ #

    def optimize_module(
        self,
        module: Any,
        trainset: List[Any],
        metric: Callable[..., float] = default_quality_metric,
        save_name: Optional[str] = None,
    ) -> Any:
        """Optimize a DSPy module using BootstrapFewShot.

        Args:
            module: The DSPy module to optimize.
            trainset: List of ``dspy.Example`` training examples.
            metric: Callable ``(example, prediction, trace?) -> float``.
            save_name: If provided (and ``save_dir`` is set), save the
                compiled module under this name.

        Returns:
            The compiled (optimized) module, or the original module
            unchanged if DSPy is unavailable.
        """
        if not _dspy_available:
            logger.warning(
                "optimize_skip",
                extra={
                    "event": "optimize_skip",
                    "reason": "dspy_unavailable",
                },
            )
            return module

        # Ensure DSPy is configured with our Claude adapter
        configure_dspy_with_claude()

        logger.info(
            "optimization_start",
            extra={
                "event": "optimization_start",
                "trainset_size": len(trainset),
                "max_bootstrapped": self.config.max_bootstrapped_demos,
                "max_labeled": self.config.max_labeled_demos,
            },
        )

        try:
            optimizer = dspy.BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=self.config.max_bootstrapped_demos,
                max_labeled_demos=self.config.max_labeled_demos,
            )

            compiled = optimizer.compile(module, trainset=trainset)

            logger.info(
                "optimization_complete",
                extra={"event": "optimization_complete"},
            )

            # Persist checkpoint if configured
            if save_name and self.config.save_dir:
                self._save_checkpoint(compiled, save_name)

            return compiled

        except Exception:
            logger.error(
                "optimization_failed",
                exc_info=True,
                extra={"event": "optimization_failed"},
            )
            return module

    # ------------------------------------------------------------------ #
    #  Load                                                               #
    # ------------------------------------------------------------------ #

    def load_optimized(self, save_name: str) -> Optional[Any]:
        """Load a previously optimized module checkpoint.

        Args:
            save_name: The name used when saving the checkpoint.

        Returns:
            The loaded module, or ``None`` if DSPy is unavailable or the
            checkpoint does not exist.
        """
        if not _dspy_available:
            logger.info(
                "load_skip",
                extra={"event": "load_skip", "reason": "dspy_unavailable"},
            )
            return None

        if not self.config.save_dir:
            logger.warning(
                "load_skip",
                extra={"event": "load_skip", "reason": "no_save_dir"},
            )
            return None

        path = self.config.save_dir / f"{save_name}.json"
        if not path.exists():
            logger.warning(
                "checkpoint_not_found",
                extra={"event": "checkpoint_not_found", "path": str(path)},
            )
            return None

        try:
            module = dspy.Module()
            module.load(path)
            logger.info(
                "checkpoint_loaded",
                extra={"event": "checkpoint_loaded", "path": str(path)},
            )
            return module
        except Exception:
            logger.error(
                "checkpoint_load_failed",
                exc_info=True,
                extra={"event": "checkpoint_load_failed", "path": str(path)},
            )
            return None

    # ------------------------------------------------------------------ #
    #  Evaluate                                                           #
    # ------------------------------------------------------------------ #

    def evaluate(
        self,
        module: Any,
        testset: List[Any],
        metric: Callable[..., float] = default_quality_metric,
    ) -> Dict[str, Any]:
        """Evaluate a module against a test set.

        Runs the module on each example in *testset*, computes the metric,
        and returns aggregate and per-example scores.

        Args:
            module: The DSPy module (or fallback) to evaluate.
            testset: List of ``dspy.Example`` test examples.
            metric: Callable ``(example, prediction, trace?) -> float``.

        Returns:
            A dict with ``score`` (average), ``num_examples``,
            ``per_example`` scores, and a ``note`` if DSPy is unavailable.
        """
        if not _dspy_available:
            return {
                "score": 0.0,
                "num_examples": len(testset),
                "per_example": [],
                "note": "DSPy unavailable; evaluation skipped",
            }

        if not testset:
            return {
                "score": 0.0,
                "num_examples": 0,
                "per_example": [],
                "note": "Empty test set",
            }

        per_example: List[Dict[str, Any]] = []
        total_score = 0.0

        for i, example in enumerate(testset):
            try:
                # Extract input fields from example
                inputs = {
                    k: v
                    for k, v in example.items()
                    if k not in ("dspy_uuid", "dspy_split")
                }
                prediction = module(**inputs)
                score = metric(example, prediction)
            except Exception as exc:
                logger.warning(
                    "eval_example_failed",
                    exc_info=True,
                    extra={"event": "eval_example_failed", "index": i},
                )
                score = 0.0
                prediction = None

            total_score += score
            per_example.append({
                "index": i,
                "score": score,
                "prediction": str(prediction)[:200] if prediction else None,
            })

        avg_score = total_score / len(testset)

        logger.info(
            "evaluation_complete",
            extra={
                "event": "evaluation_complete",
                "avg_score": round(avg_score, 4),
                "num_examples": len(testset),
            },
        )

        return {
            "score": round(avg_score, 4),
            "num_examples": len(testset),
            "per_example": per_example,
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _save_checkpoint(self, module: Any, save_name: str) -> None:
        """Persist an optimized module to disk."""
        if not self.config.save_dir:
            return

        self.config.save_dir.mkdir(parents=True, exist_ok=True)
        path = self.config.save_dir / f"{save_name}.json"

        try:
            module.save(path)
            logger.info(
                "checkpoint_saved",
                extra={"event": "checkpoint_saved", "path": str(path)},
            )
        except Exception:
            logger.error(
                "checkpoint_save_failed",
                exc_info=True,
                extra={"event": "checkpoint_save_failed", "path": str(path)},
            )

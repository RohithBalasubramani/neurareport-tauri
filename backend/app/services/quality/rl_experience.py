from __future__ import annotations

import logging
import random
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neura.quality.rl_experience")


# ---------------------------------------------------------------------------
# Beta-distribution arm (generalised from widget_selector.BetaParams)
# ---------------------------------------------------------------------------


@dataclass
class BetaArm:
    """A single arm in a Thompson Sampling bandit.

    Maintains Beta distribution parameters that are updated with
    observed rewards.  Positive rewards grow *alpha* (success count);
    negative rewards grow *beta* (failure count).
    """

    alpha: float = 1.0
    beta: float = 1.0
    pulls: int = 0
    total_reward: float = 0.0

    def sample(self) -> float:
        """Draw a single sample from the Beta(alpha, beta) distribution."""
        return random.betavariate(
            max(self.alpha, 0.01), max(self.beta, 0.01)
        )

    def update(self, reward: float) -> None:
        """Update distribution parameters with an observed *reward*.

        Positive rewards increase *alpha*; negative rewards increase
        *beta*.
        """
        self.pulls += 1
        self.total_reward += reward
        self.alpha += max(reward, 0.0)
        self.beta += max(-reward, 0.0)

    @property
    def mean(self) -> float:
        """Expected value of the Beta distribution."""
        return self.alpha / (self.alpha + self.beta)


# ---------------------------------------------------------------------------
# Thompson Sampler
# ---------------------------------------------------------------------------


class ThompsonSampler:
    """Domain-aware Thompson Sampling bandit.

    Arms are organised by *domain* (e.g. ``"widget_type"``,
    ``"prompt_template"``) so a single sampler instance can serve
    multiple independent decision problems.
    """

    def __init__(self) -> None:
        self._arms: Dict[str, Dict[str, BetaArm]] = defaultdict(dict)
        self._lock = threading.Lock()

    def select(self, domain: str, arms: list[str]) -> str:
        """Sample each arm and return the one with the highest draw.

        Any arm names not yet seen are initialised with a uniform
        ``BetaArm(1, 1)`` prior.
        """
        with self._lock:
            domain_arms = self._arms[domain]
            best_arm: Optional[str] = None
            best_sample = -1.0
            for arm_name in arms:
                if arm_name not in domain_arms:
                    domain_arms[arm_name] = BetaArm()
                sample = domain_arms[arm_name].sample()
                if sample > best_sample:
                    best_sample = sample
                    best_arm = arm_name
        # Fallback: if arms was empty, return the first element of the
        # original list (caller should guarantee non-empty).
        if best_arm is None and arms:
            return arms[0]
        return best_arm  # type: ignore[return-value]

    def update(self, domain: str, arm: str, reward: float) -> None:
        """Record an observed *reward* for the given arm."""
        with self._lock:
            if arm not in self._arms[domain]:
                self._arms[domain][arm] = BetaArm()
            self._arms[domain][arm].update(reward)

    def get_stats(self, domain: str) -> Dict[str, Dict[str, Any]]:
        """Return summary statistics for every arm in *domain*."""
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            for arm_name, arm in self._arms.get(domain, {}).items():
                result[arm_name] = {
                    "alpha": arm.alpha,
                    "beta": arm.beta,
                    "mean": round(arm.mean, 4),
                    "pulls": arm.pulls,
                    "total_reward": round(arm.total_reward, 4),
                }
            return result

    def reset(self, domain: str) -> None:
        """Clear all arms for *domain*."""
        with self._lock:
            self._arms.pop(domain, None)


# ---------------------------------------------------------------------------
# Experience Store
# ---------------------------------------------------------------------------


class RLExperienceStore:
    """Append-only store of (state, action, reward) experience tuples.

    Experiences are bucketed by *domain* and persisted to the
    state store so they survive process restarts.
    """

    def __init__(self) -> None:
        self._experiences: Dict[str, List[dict]] = defaultdict(list)
        self._lock = threading.Lock()
        self._max_per_domain: int = 1000
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(
        self,
        domain: str,
        state: dict,
        action: str,
        reward: float,
        metadata: Optional[dict] = None,
    ) -> None:
        """Append an experience tuple and persist."""
        entry = {
            "state": state,
            "action": action,
            "reward": reward,
            "metadata": metadata or {},
        }
        with self._lock:
            bucket = self._experiences[domain]
            bucket.append(entry)
            # Trim oldest entries when over capacity
            if len(bucket) > self._max_per_domain:
                self._experiences[domain] = bucket[-self._max_per_domain :]
            self._persist()

    def get_experiences(
        self, domain: str, limit: int = 100
    ) -> List[dict]:
        """Return the most recent experiences for *domain*."""
        with self._lock:
            bucket = self._experiences.get(domain, [])
            return list(bucket[-limit:])

    def get_best_action(self, domain: str) -> Optional[str]:
        """Return the action with the highest average reward in *domain*.

        Returns ``None`` if no experiences have been recorded.
        """
        with self._lock:
            bucket = self._experiences.get(domain, [])
            if not bucket:
                return None

        # Group by action, compute average reward
        totals: Dict[str, float] = defaultdict(float)
        counts: Dict[str, int] = defaultdict(int)
        for exp in bucket:
            action = exp.get("action", "")
            totals[action] += exp.get("reward", 0.0)
            counts[action] += 1

        best_action: Optional[str] = None
        best_avg = float("-inf")
        for action, total in totals.items():
            avg = total / counts[action]
            if avg > best_avg:
                best_avg = avg
                best_action = action

        return best_action

    # ------------------------------------------------------------------
    # Persistence (follows docqa/service.py state-store pattern)
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write experiences to the state store."""
        try:
            from backend.app.repositories.state import store as state_store_module

            store = state_store_module.state_store
            with store._lock:
                state = store._read_state() or {}
                if not isinstance(state, dict):
                    state = {}
                state["rl_experiences"] = dict(self._experiences)
                store._write_state(state)
        except Exception as exc:
            logger.warning(
                "rl_persist_failed",
                extra={"event": "rl_persist_failed", "error": str(exc)},
            )

    def _load(self) -> None:
        """Restore experiences from the state store on startup."""
        try:
            from backend.app.repositories.state import store as state_store_module

            store = state_store_module.state_store
            with store._lock:
                state = store._read_state() or {}
            if not isinstance(state, dict):
                return
            raw = state.get("rl_experiences", {})
            if not isinstance(raw, dict):
                return
            for domain, entries in raw.items():
                if isinstance(entries, list):
                    self._experiences[domain] = entries
        except Exception as exc:
            logger.warning(
                "rl_load_failed",
                extra={"event": "rl_load_failed", "error": str(exc)},
            )


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------

_sampler: Optional[ThompsonSampler] = None
_sampler_lock = threading.Lock()


def get_thompson_sampler() -> ThompsonSampler:
    """Return the process-wide :class:`ThompsonSampler` singleton."""
    global _sampler
    if _sampler is None:
        with _sampler_lock:
            if _sampler is None:
                _sampler = ThompsonSampler()
    return _sampler


_experience_store: Optional[RLExperienceStore] = None
_experience_store_lock = threading.Lock()


def get_experience_store() -> RLExperienceStore:
    """Return the process-wide :class:`RLExperienceStore` singleton."""
    global _experience_store
    if _experience_store is None:
        with _experience_store_lock:
            if _experience_store is None:
                _experience_store = RLExperienceStore()
    return _experience_store

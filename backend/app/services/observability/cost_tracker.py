from __future__ import annotations

"""
Per-operation token and cost accounting with daily rollups.

Tracks LLM token usage per operation, estimates costs, enforces budgets,
and persists daily rollups to disk for historical analysis.
"""

import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.services.llm.client import estimate_cost, TOKEN_COSTS
from backend.app.services.observability.metrics import LLM_TOKEN_USAGE

logger = logging.getLogger("neura.observability.cost_tracker")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class OperationRecord:
    """Single token-usage record for one LLM call."""

    operation: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class CostBudget:
    """Budget limits for LLM spend."""

    daily_limit_usd: float = 50.0
    monthly_limit_usd: float = 1000.0
    alert_threshold_pct: float = 0.8


# ---------------------------------------------------------------------------
# CostTracker
# ---------------------------------------------------------------------------

class CostTracker:
    """
    Thread-safe, per-operation token and cost tracker with daily rollups.

    Records every LLM call, aggregates by operation and calendar day,
    checks spend against a configurable budget, and optionally persists
    rollups as JSON files for later analysis.
    """

    def __init__(
        self,
        budget: Optional[CostBudget] = None,
        persist_dir: Optional[str] = None,
    ) -> None:
        self._budget = budget or CostBudget()
        self._persist_dir: Optional[Path] = Path(persist_dir) if persist_dir else None
        self._lock = threading.Lock()

        # operation -> list[OperationRecord]
        self._history: Dict[str, List[OperationRecord]] = defaultdict(list)

        # date_str -> { "total_input_tokens": int, "total_output_tokens": int,
        #               "total_cost": float, "request_count": int,
        #               "by_operation": { op: {...} } }
        self._daily_rollups: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "request_count": 0,
                "by_operation": defaultdict(
                    lambda: {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                        "count": 0,
                    }
                ),
            }
        )

        if self._persist_dir:
            self._persist_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "cost_tracker_initialized",
            extra={
                "event": "cost_tracker_initialized",
                "daily_limit_usd": self._budget.daily_limit_usd,
                "monthly_limit_usd": self._budget.monthly_limit_usd,
                "persist_dir": str(self._persist_dir) if self._persist_dir else None,
            },
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(
        self,
        operation: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> OperationRecord:
        """Record token usage for a single LLM call (thread-safe)."""
        cost = estimate_cost(model, input_tokens, output_tokens)
        rec = OperationRecord(
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        with self._lock:
            self._history[operation].append(rec)

            rollup = self._daily_rollups[today]
            rollup["total_input_tokens"] += input_tokens
            rollup["total_output_tokens"] += output_tokens
            rollup["total_cost"] += cost
            rollup["request_count"] += 1

            op_rollup = rollup["by_operation"][operation]
            op_rollup["input_tokens"] += input_tokens
            op_rollup["output_tokens"] += output_tokens
            op_rollup["cost"] += cost
            op_rollup["count"] += 1

        # Persist outside the lock to reduce contention
        self._persist_daily(today)

        logger.debug(
            "cost_record",
            extra={
                "event": "cost_record",
                "operation": operation,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost, 6),
            },
        )
        return rec

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Return aggregate stats for a single operation."""
        with self._lock:
            records = self._history.get(operation, [])
            if not records:
                return {
                    "operation": operation,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_cost": 0.0,
                    "request_count": 0,
                }
            return {
                "operation": operation,
                "total_input_tokens": sum(r.input_tokens for r in records),
                "total_output_tokens": sum(r.output_tokens for r in records),
                "total_cost": round(sum(r.cost for r in records), 6),
                "request_count": len(records),
            }

    def get_daily_rollup(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Return aggregated stats for a calendar day (default: today UTC)."""
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()
        date_str = target_date.strftime("%Y-%m-%d")

        with self._lock:
            if date_str in self._daily_rollups:
                rollup = self._daily_rollups[date_str]
                # Convert nested defaultdicts to plain dicts for serialisation
                return {
                    "date": date_str,
                    "total_input_tokens": rollup["total_input_tokens"],
                    "total_output_tokens": rollup["total_output_tokens"],
                    "total_cost": round(rollup["total_cost"], 6),
                    "request_count": rollup["request_count"],
                    "by_operation": dict(rollup["by_operation"]),
                }

        # Try loading from disk if not in memory
        persisted = self._load_daily(date_str)
        if persisted:
            return persisted

        return {
            "date": date_str,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "request_count": 0,
            "by_operation": {},
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Return a global summary across all operations and days."""
        with self._lock:
            total_input = 0
            total_output = 0
            total_cost = 0.0
            total_requests = 0
            operations: Dict[str, Dict[str, Any]] = {}

            for op, records in self._history.items():
                op_input = sum(r.input_tokens for r in records)
                op_output = sum(r.output_tokens for r in records)
                op_cost = sum(r.cost for r in records)
                total_input += op_input
                total_output += op_output
                total_cost += op_cost
                total_requests += len(records)
                operations[op] = {
                    "input_tokens": op_input,
                    "output_tokens": op_output,
                    "cost": round(op_cost, 6),
                    "count": len(records),
                }

            return {
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_cost": round(total_cost, 6),
                "total_requests": total_requests,
                "operations": operations,
                "days_tracked": len(self._daily_rollups),
            }

    def check_budget(self) -> Dict[str, Any]:
        """Check current spend against the configured budget."""
        today_rollup = self.get_daily_rollup()
        daily_used = today_rollup["total_cost"]
        daily_limit = self._budget.daily_limit_usd
        within_budget = daily_used < daily_limit
        alert = daily_used >= (daily_limit * self._budget.alert_threshold_pct)

        if alert and within_budget:
            logger.warning(
                "cost_budget_alert",
                extra={
                    "event": "cost_budget_alert",
                    "daily_used": round(daily_used, 4),
                    "daily_limit": daily_limit,
                    "pct_used": round(daily_used / daily_limit * 100, 1) if daily_limit else 0,
                },
            )

        if not within_budget:
            logger.error(
                "cost_budget_exceeded",
                extra={
                    "event": "cost_budget_exceeded",
                    "daily_used": round(daily_used, 4),
                    "daily_limit": daily_limit,
                },
            )

        return {
            "within_budget": within_budget,
            "daily_used": round(daily_used, 6),
            "daily_limit": daily_limit,
            "monthly_limit": self._budget.monthly_limit_usd,
            "alert": alert,
        }

    def export_to_prometheus(self) -> None:
        """Push accumulated token counts to the Prometheus LLM_TOKEN_USAGE counter."""
        with self._lock:
            for op, records in self._history.items():
                for rec in records:
                    LLM_TOKEN_USAGE.labels(model=rec.model, token_type="input").inc(
                        rec.input_tokens
                    )
                    LLM_TOKEN_USAGE.labels(model=rec.model, token_type="output").inc(
                        rec.output_tokens
                    )

        logger.debug("cost_tracker_exported_prometheus", extra={"event": "cost_tracker_exported_prometheus"})

    def reset(self) -> None:
        """Clear all in-memory records and rollups."""
        with self._lock:
            self._history.clear()
            self._daily_rollups.clear()
        logger.info("cost_tracker_reset", extra={"event": "cost_tracker_reset"})

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_daily(self, date_str: str) -> None:
        """Write the rollup for *date_str* to a JSON file in persist_dir."""
        if not self._persist_dir:
            return
        try:
            with self._lock:
                rollup = self._daily_rollups.get(date_str)
                if not rollup:
                    return
                data = {
                    "date": date_str,
                    "total_input_tokens": rollup["total_input_tokens"],
                    "total_output_tokens": rollup["total_output_tokens"],
                    "total_cost": round(rollup["total_cost"], 6),
                    "request_count": rollup["request_count"],
                    "by_operation": {k: dict(v) for k, v in rollup["by_operation"].items()},
                }
            out_path = self._persist_dir / f"rollup_{date_str}.json"
            out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning(
                "cost_persist_failed",
                extra={"event": "cost_persist_failed", "date": date_str, "error": str(exc)},
            )

    def _load_daily(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Read a persisted daily rollup from disk."""
        if not self._persist_dir:
            return None
        try:
            path = self._persist_dir / f"rollup_{date_str}.json"
            if not path.exists():
                return None
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(
                "cost_load_failed",
                extra={"event": "cost_load_failed", "date": date_str, "error": str(exc)},
            )
            return None


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_instance: Optional[CostTracker] = None
_lock = threading.Lock()


def get_cost_tracker(
    budget: Optional[CostBudget] = None,
    persist_dir: Optional[str] = None,
) -> CostTracker:
    """Return the module-level CostTracker singleton (lazy-init, thread-safe)."""
    global _instance
    with _lock:
        if _instance is None:
            _instance = CostTracker(budget=budget, persist_dir=persist_dir)
    return _instance

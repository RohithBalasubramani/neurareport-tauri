from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("neura.graph.fallback")


def run_report_pipeline_sequential(state: Dict[str, Any]) -> Dict[str, Any]:
    """Sequential fallback for the report pipeline."""
    from .graph_report import (
        node_extract_data,
        node_generate_sql,
        node_execute_queries,
        node_map_fields,
        node_generate_sections,
        node_review,
        node_finalize,
    )

    logger.info(
        "report_pipeline_sequential_start",
        extra={"event": "report_pipeline_sequential_start"},
    )

    # Execute nodes sequentially
    state.update(node_extract_data(state))
    state.update(node_generate_sql(state))
    state.update(node_execute_queries(state))
    state.update(node_map_fields(state))

    max_revisions = state.get("max_revisions", 2)
    while True:
        state.update(node_generate_sections(state))
        state.update(node_review(state))
        if state.get("review_score", 1.0) >= 0.7 or state.get("revision_count", 0) >= max_revisions:
            break

    state.update(node_finalize(state))
    state["method"] = "sequential"

    logger.info(
        "report_pipeline_sequential_complete",
        extra={
            "event": "report_pipeline_sequential_complete",
            "confidence": state.get("confidence"),
            "revision_count": state.get("revision_count"),
        },
    )
    return state


def run_agent_workflow_sequential(state: Dict[str, Any]) -> Dict[str, Any]:
    """Sequential fallback for the agent workflow."""
    from .graph_agent_workflow import (
        node_plan,
        node_search,
        node_analyze,
        node_draft,
        node_evaluate,
        node_finalize,
    )

    logger.info(
        "agent_workflow_sequential_start",
        extra={"event": "agent_workflow_sequential_start"},
    )

    state.update(node_plan(state))
    state.update(node_search(state))
    state.update(node_analyze(state))

    max_revisions = state.get("max_revisions", 2)
    while True:
        state.update(node_draft(state))
        state.update(node_evaluate(state))
        if state.get("quality_score", 1.0) >= 0.7 or state.get("revision_count", 0) >= max_revisions:
            break

    state.update(node_finalize(state))
    state["method"] = "sequential"

    logger.info(
        "agent_workflow_sequential_complete",
        extra={
            "event": "agent_workflow_sequential_complete",
            "quality_score": state.get("quality_score"),
            "revision_count": state.get("revision_count"),
        },
    )
    return state

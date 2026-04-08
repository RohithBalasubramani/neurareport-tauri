from __future__ import annotations

import concurrent.futures
import json
import logging
import threading
from typing import Any, Dict, List

try:
    from langgraph.graph import StateGraph, START, END

    _langgraph_available = True
except ImportError:
    _langgraph_available = False

from .state import AgentWorkflowState
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.graph.agent_workflow")

# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


def node_plan(state: Dict[str, Any]) -> Dict[str, Any]:
    """Break task into prioritized sub-tasks."""
    logger.info(
        "node_plan_start",
        extra={
            "event": "node_plan_start",
            "agent_type": state.get("agent_type"),
        },
    )
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a task planner. Break the given task into sub-tasks. "
                        "Return a JSON array of objects with keys: task, priority (1-5), "
                        "estimated_effort (low/medium/high)."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Task: {state.get('task_description', '')}\n"
                        f"Agent type: {state.get('agent_type', 'research')}\n"
                        f"Context: {json.dumps(state.get('context', {}))}\n\n"
                        "Return a JSON array of sub-task objects."
                    ),
                },
            ],
            description="graph:node_plan",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            plan = json.loads(text)
            if not isinstance(plan, list):
                plan = [{"task": str(plan), "priority": 1, "estimated_effort": "medium"}]
        except (json.JSONDecodeError, TypeError):
            plan = [{"task": text, "priority": 1, "estimated_effort": "medium"}]
        logger.info("node_plan_complete", extra={"subtask_count": len(plan)})
        return {"plan": plan}
    except Exception as exc:
        logger.error("node_plan_error", extra={"error": str(exc)})
        return {
            "plan": [{"task": state.get("task_description", ""), "priority": 1}],
            "errors": state.get("errors", []) + [f"plan: {exc}"],
        }


def _search_subtask(subtask: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single search sub-task (used in parallel)."""
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant. Search and gather information for the given sub-task. Return a JSON object with keys: findings, sources, relevance_score.",
                },
                {
                    "role": "user",
                    "content": f"Sub-task: {json.dumps(subtask)}\n\nReturn JSON with findings.",
                },
            ],
            description="graph:node_search_subtask",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            result = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            result = {"findings": text, "sources": [], "relevance_score": 0.5}
        result["subtask"] = subtask.get("task", "")
        return result
    except Exception as exc:
        return {
            "subtask": subtask.get("task", ""),
            "findings": "",
            "error": str(exc),
        }


def node_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run parallel searches for each planned sub-task."""
    logger.info(
        "node_search_start",
        extra={
            "event": "node_search_start",
            "subtask_count": len(state.get("plan", [])),
        },
    )
    plan = state.get("plan", [])
    if not plan:
        return {"search_results": []}

    results: List[Dict[str, Any]] = []
    max_workers = min(len(plan), 4)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_search_subtask, task): task for task in plan}
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    task = futures[future]
                    results.append(
                        {
                            "subtask": task.get("task", ""),
                            "findings": "",
                            "error": str(exc),
                        }
                    )
    except Exception as exc:
        logger.error("node_search_parallel_error", extra={"error": str(exc)})
        # Fallback: sequential execution
        for task in plan:
            results.append(_search_subtask(task))

    logger.info("node_search_complete", extra={"result_count": len(results)})
    return {"search_results": results}


def node_analyze(state: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize search results into a coherent analysis."""
    logger.info("node_analyze_start", extra={"event": "node_analyze_start"})
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an analyst. Synthesize the search results into a "
                        "coherent analysis. Return a JSON object with keys: summary, "
                        "key_findings, gaps, recommendations."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Task: {state.get('task_description', '')}\n"
                        f"Search results: {json.dumps(state.get('search_results', []))}\n\n"
                        "Return JSON analysis."
                    ),
                },
            ],
            description="graph:node_analyze",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            analysis = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            analysis = {"summary": text, "key_findings": [], "gaps": [], "recommendations": []}
        return {"analysis_results": analysis}
    except Exception as exc:
        logger.error("node_analyze_error", extra={"error": str(exc)})
        return {
            "analysis_results": {"summary": "", "error": str(exc)},
            "errors": state.get("errors", []) + [f"analyze: {exc}"],
        }


def node_draft(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a draft based on analysis results."""
    logger.info(
        "node_draft_start",
        extra={
            "event": "node_draft_start",
            "revision_count": state.get("revision_count", 0),
        },
    )
    try:
        client = get_llm_client()
        feedback_ctx = ""
        if state.get("evaluation_feedback"):
            feedback_ctx = (
                f"\n\nPrevious evaluation feedback (incorporate improvements):\n"
                f"{state['evaluation_feedback']}"
            )
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a content writer. Generate a comprehensive draft "
                        "based on the analysis. The output should be well-structured "
                        "and address the original task."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Task: {state.get('task_description', '')}\n"
                        f"Analysis: {json.dumps(state.get('analysis_results', {}))}"
                        f"{feedback_ctx}\n\n"
                        "Write the draft content."
                    ),
                },
            ],
            description="graph:node_draft",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        return {"draft_content": text}
    except Exception as exc:
        logger.error("node_draft_error", extra={"error": str(exc)})
        return {
            "draft_content": "",
            "errors": state.get("errors", []) + [f"draft: {exc}"],
        }


def node_evaluate(state: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate draft quality and provide feedback."""
    logger.info(
        "node_evaluate_start",
        extra={
            "event": "node_evaluate_start",
            "revision_count": state.get("revision_count", 0),
        },
    )
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a quality evaluator. Score the draft on completeness, "
                        "accuracy, and clarity. Return a JSON object with keys: "
                        "score (0.0-1.0), feedback (string)."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Task: {state.get('task_description', '')}\n"
                        f"Draft: {state.get('draft_content', '')}\n\n"
                        "Return JSON with score and feedback."
                    ),
                },
            ],
            description="graph:node_evaluate",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            evaluation = json.loads(text)
            score = float(evaluation.get("score", 0.5))
            feedback = str(evaluation.get("feedback", ""))
        except (json.JSONDecodeError, TypeError, ValueError):
            score = 0.5
            feedback = text
        revision_count = state.get("revision_count", 0) + 1
        logger.info(
            "node_evaluate_complete",
            extra={"quality_score": score, "revision_count": revision_count},
        )
        return {
            "quality_score": score,
            "evaluation_feedback": feedback,
            "revision_count": revision_count,
        }
    except Exception as exc:
        logger.error("node_evaluate_error", extra={"error": str(exc)})
        return {
            "quality_score": 1.0,  # Skip revision on error
            "evaluation_feedback": f"Evaluation failed: {exc}",
            "revision_count": state.get("revision_count", 0) + 1,
            "errors": state.get("errors", []) + [f"evaluate: {exc}"],
        }


def node_finalize(state: Dict[str, Any]) -> Dict[str, Any]:
    """Produce final output from the draft."""
    logger.info("node_finalize_start", extra={"event": "node_finalize_start"})
    method = "langgraph" if _langgraph_available else "sequential"
    final_output = {
        "content": state.get("draft_content", ""),
        "analysis": state.get("analysis_results", {}),
        "quality_score": state.get("quality_score", 0.0),
        "revision_count": state.get("revision_count", 0),
        "plan": state.get("plan", []),
    }
    logger.info(
        "node_finalize_complete",
        extra={
            "method": method,
            "quality_score": state.get("quality_score", 0.0),
        },
    )
    return {
        "final_output": final_output,
        "method": method,
    }


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def route_after_evaluate(state: Dict[str, Any]) -> str:
    """Route to revision or finalization based on quality score."""
    score = state.get("quality_score", 1.0)
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)
    if score < 0.7 and revision_count < max_revisions:
        logger.info(
            "route_revision",
            extra={"score": score, "revision_count": revision_count},
        )
        return "node_draft"
    logger.info(
        "route_finalize",
        extra={"score": score, "revision_count": revision_count},
    )
    return "node_finalize"


# ---------------------------------------------------------------------------
# Graph construction (thread-safe singleton)
# ---------------------------------------------------------------------------

_compiled_graph = None
_graph_lock = threading.Lock()


def _build_agent_graph():
    """Build and compile the agent workflow StateGraph."""
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph

    with _graph_lock:
        # Double-check after acquiring lock
        if _compiled_graph is not None:
            return _compiled_graph

        if not _langgraph_available:
            raise ImportError("langgraph is not installed")

        graph = StateGraph(AgentWorkflowState)

        # Add nodes
        graph.add_node("node_plan", node_plan)
        graph.add_node("node_search", node_search)
        graph.add_node("node_analyze", node_analyze)
        graph.add_node("node_draft", node_draft)
        graph.add_node("node_evaluate", node_evaluate)
        graph.add_node("node_finalize", node_finalize)

        # Add edges: linear pipeline up to evaluate
        graph.add_edge(START, "node_plan")
        graph.add_edge("node_plan", "node_search")
        graph.add_edge("node_search", "node_analyze")
        graph.add_edge("node_analyze", "node_draft")
        graph.add_edge("node_draft", "node_evaluate")

        # Conditional: evaluate -> revise or finalize
        graph.add_conditional_edges(
            "node_evaluate",
            route_after_evaluate,
            {
                "node_draft": "node_draft",
                "node_finalize": "node_finalize",
            },
        )
        graph.add_edge("node_finalize", END)

        _compiled_graph = graph.compile()
        logger.info(
            "agent_workflow_graph_compiled",
            extra={"event": "agent_workflow_graph_compiled"},
        )
        return _compiled_graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_agent_workflow(
    task_description: str,
    agent_type: str = "research",
    context: Dict[str, Any] | None = None,
    max_revisions: int = 2,
) -> dict:
    """
    Run the agent workflow pipeline.

    Attempts LangGraph execution first; falls back to sequential execution
    if LangGraph is unavailable or encounters an error.

    Returns the final state dict.
    """
    initial_state: Dict[str, Any] = {
        "task_description": task_description,
        "agent_type": agent_type,
        "context": context or {},
        "max_revisions": max_revisions,
        "revision_count": 0,
        "errors": [],
    }

    # Try LangGraph first
    if _langgraph_available:
        try:
            logger.info(
                "agent_workflow_langgraph_start",
                extra={
                    "event": "agent_workflow_langgraph_start",
                    "agent_type": agent_type,
                },
            )
            compiled = _build_agent_graph()
            result = compiled.invoke(initial_state)
            logger.info(
                "agent_workflow_langgraph_complete",
                extra={
                    "event": "agent_workflow_langgraph_complete",
                    "quality_score": result.get("quality_score"),
                },
            )
            return dict(result)
        except Exception as exc:
            logger.warning(
                "agent_workflow_langgraph_failed",
                extra={"error": str(exc), "agent_type": agent_type},
            )

    # Fallback to sequential
    logger.info(
        "agent_workflow_sequential_fallback",
        extra={
            "event": "agent_workflow_sequential_fallback",
            "agent_type": agent_type,
        },
    )
    from .fallback import run_agent_workflow_sequential

    return run_agent_workflow_sequential(initial_state)

from __future__ import annotations

import json
import logging
import threading
from typing import Any, Dict

try:
    from langgraph.graph import StateGraph, START, END

    _langgraph_available = True
except ImportError:
    _langgraph_available = False

from .state import ReportPipelineState
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.graph.report")

# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


def node_extract_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured data requirements from user query and template."""
    logger.info(
        "node_extract_data_start",
        extra={
            "event": "node_extract_data_start",
            "report_id": state.get("report_id"),
        },
    )
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a data-requirements analyst. Given a user query and "
                        "template context, extract structured data requirements as JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"User query: {state.get('user_query', '')}\n"
                        f"Template ID: {state.get('template_id', '')}\n"
                        f"Parameters: {json.dumps(state.get('parameters', {}))}\n\n"
                        "Return a JSON object with keys: tables, columns, filters, "
                        "aggregations, relationships."
                    ),
                },
            ],
            description="graph:node_extract_data",
        )
        # Attempt to parse structured output from LLM response
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            extracted = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            extracted = {
                "raw_response": text,
                "tables": [],
                "columns": [],
                "filters": [],
            }
        return {"extracted_data": extracted}
    except Exception as exc:
        logger.error("node_extract_data_error", extra={"error": str(exc)})
        return {
            "extracted_data": {},
            "errors": state.get("errors", []) + [f"extract_data: {exc}"],
        }


def node_generate_sql(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SQL queries from extracted data requirements."""
    logger.info(
        "node_generate_sql_start",
        extra={
            "event": "node_generate_sql_start",
            "report_id": state.get("report_id"),
        },
    )
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a SQL expert. Generate SQL queries based on data "
                        "requirements. Return a JSON array of SQL query strings."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Data requirements: {json.dumps(state.get('extracted_data', {}))}\n"
                        f"Connection ID: {state.get('connection_id', '')}\n\n"
                        "Return a JSON array of SQL query strings."
                    ),
                },
            ],
            description="graph:node_generate_sql",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            queries = json.loads(text)
            if not isinstance(queries, list):
                queries = [str(queries)]
        except (json.JSONDecodeError, TypeError):
            queries = [text] if text.strip() else []
        return {"sql_queries": queries}
    except Exception as exc:
        logger.error("node_generate_sql_error", extra={"error": str(exc)})
        return {
            "sql_queries": [],
            "errors": state.get("errors", []) + [f"generate_sql: {exc}"],
        }


def node_execute_queries(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute SQL queries against the connection (stub: returns mock results)."""
    logger.info(
        "node_execute_queries_start",
        extra={
            "event": "node_execute_queries_start",
            "report_id": state.get("report_id"),
            "query_count": len(state.get("sql_queries", [])),
        },
    )
    # Stub implementation -- real version will use the connections service
    results = []
    for idx, query in enumerate(state.get("sql_queries", [])):
        logger.debug(
            "executing_query_stub",
            extra={"query_index": idx, "query_preview": query[:200]},
        )
        results.append(
            {
                "query_index": idx,
                "query": query,
                "rows": [],
                "row_count": 0,
                "status": "stub",
            }
        )
    return {"query_results": results}


def node_map_fields(state: Dict[str, Any]) -> Dict[str, Any]:
    """Map query results to template fields."""
    logger.info(
        "node_map_fields_start",
        extra={
            "event": "node_map_fields_start",
            "report_id": state.get("report_id"),
        },
    )
    try:
        client = get_llm_client()
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a data mapping specialist. Map query results to "
                        "report template fields. Return a JSON mapping object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Query results: {json.dumps(state.get('query_results', []))}\n"
                        f"Template ID: {state.get('template_id', '')}\n"
                        f"Extracted data requirements: {json.dumps(state.get('extracted_data', {}))}\n\n"
                        "Return a JSON object mapping template field names to values."
                    ),
                },
            ],
            description="graph:node_map_fields",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            mapped = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            mapped = {"raw_mapping": text}
        return {"mapped_fields": mapped}
    except Exception as exc:
        logger.error("node_map_fields_error", extra={"error": str(exc)})
        return {
            "mapped_fields": {},
            "errors": state.get("errors", []) + [f"map_fields: {exc}"],
        }


def node_generate_sections(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate report sections using LLM and mapped fields."""
    logger.info(
        "node_generate_sections_start",
        extra={
            "event": "node_generate_sections_start",
            "report_id": state.get("report_id"),
            "revision_count": state.get("revision_count", 0),
        },
    )
    try:
        client = get_llm_client()
        feedback_ctx = ""
        if state.get("review_feedback"):
            feedback_ctx = (
                f"\n\nPrevious review feedback (incorporate improvements):\n"
                f"{state['review_feedback']}"
            )
        response = client.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a report writer. Generate report sections based on "
                        "the mapped data fields. Return a JSON array of section objects "
                        "with keys: title, content, order."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Mapped fields: {json.dumps(state.get('mapped_fields', {}))}\n"
                        f"User query: {state.get('user_query', '')}"
                        f"{feedback_ctx}\n\n"
                        "Return a JSON array of section objects."
                    ),
                },
            ],
            description="graph:node_generate_sections",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            sections = json.loads(text)
            if not isinstance(sections, list):
                sections = [{"title": "Report", "content": str(sections), "order": 0}]
        except (json.JSONDecodeError, TypeError):
            sections = [{"title": "Report", "content": text, "order": 0}]
        return {"generated_sections": sections}
    except Exception as exc:
        logger.error("node_generate_sections_error", extra={"error": str(exc)})
        return {
            "generated_sections": [],
            "errors": state.get("errors", []) + [f"generate_sections: {exc}"],
        }


def node_review(state: Dict[str, Any]) -> Dict[str, Any]:
    """Review report quality and provide feedback."""
    logger.info(
        "node_review_start",
        extra={
            "event": "node_review_start",
            "report_id": state.get("report_id"),
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
                        "You are a report quality reviewer. Evaluate the report sections "
                        "for completeness, accuracy, and clarity. Return a JSON object "
                        "with keys: score (0.0-1.0), feedback (string)."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Sections: {json.dumps(state.get('generated_sections', []))}\n"
                        f"User query: {state.get('user_query', '')}\n"
                        f"Mapped fields: {json.dumps(state.get('mapped_fields', {}))}\n\n"
                        "Return JSON with score and feedback."
                    ),
                },
            ],
            description="graph:node_review",
        )
        text = response.get("content", "") if isinstance(response, dict) else str(response)
        try:
            review = json.loads(text)
            score = float(review.get("score", 0.5))
            feedback = str(review.get("feedback", ""))
        except (json.JSONDecodeError, TypeError, ValueError):
            score = 0.5
            feedback = text
        revision_count = state.get("revision_count", 0) + 1
        logger.info(
            "node_review_complete",
            extra={
                "review_score": score,
                "revision_count": revision_count,
            },
        )
        return {
            "review_score": score,
            "review_feedback": feedback,
            "revision_count": revision_count,
        }
    except Exception as exc:
        logger.error("node_review_error", extra={"error": str(exc)})
        return {
            "review_score": 1.0,  # Skip revision on error
            "review_feedback": f"Review failed: {exc}",
            "revision_count": state.get("revision_count", 0) + 1,
            "errors": state.get("errors", []) + [f"review: {exc}"],
        }


def node_finalize(state: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble final report from generated sections."""
    logger.info(
        "node_finalize_start",
        extra={
            "event": "node_finalize_start",
            "report_id": state.get("report_id"),
        },
    )
    sections = state.get("generated_sections", [])
    final_report = {
        "report_id": state.get("report_id", ""),
        "template_id": state.get("template_id", ""),
        "sections": sections,
        "review_score": state.get("review_score", 0.0),
        "revision_count": state.get("revision_count", 0),
        "metadata": {
            "user_query": state.get("user_query", ""),
            "sql_queries": state.get("sql_queries", []),
            "query_result_count": len(state.get("query_results", [])),
        },
    }
    confidence = state.get("review_score", 0.5)
    method = "langgraph" if _langgraph_available else "sequential"
    logger.info(
        "node_finalize_complete",
        extra={
            "confidence": confidence,
            "method": method,
            "section_count": len(sections),
        },
    )
    return {
        "final_report": final_report,
        "confidence": confidence,
        "method": method,
    }


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def route_after_review(state: Dict[str, Any]) -> str:
    """Route to revision or finalization based on review score."""
    score = state.get("review_score", 1.0)
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)
    if score < 0.7 and revision_count < max_revisions:
        logger.info(
            "route_revision",
            extra={"score": score, "revision_count": revision_count},
        )
        return "node_generate_sections"
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


def _build_report_graph():
    """Build and compile the report pipeline StateGraph."""
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph

    with _graph_lock:
        # Double-check after acquiring lock
        if _compiled_graph is not None:
            return _compiled_graph

        if not _langgraph_available:
            raise ImportError("langgraph is not installed")

        graph = StateGraph(ReportPipelineState)

        # Add nodes
        graph.add_node("node_extract_data", node_extract_data)
        graph.add_node("node_generate_sql", node_generate_sql)
        graph.add_node("node_execute_queries", node_execute_queries)
        graph.add_node("node_map_fields", node_map_fields)
        graph.add_node("node_generate_sections", node_generate_sections)
        graph.add_node("node_review", node_review)
        graph.add_node("node_finalize", node_finalize)

        # Add edges: linear pipeline up to review
        graph.add_edge(START, "node_extract_data")
        graph.add_edge("node_extract_data", "node_generate_sql")
        graph.add_edge("node_generate_sql", "node_execute_queries")
        graph.add_edge("node_execute_queries", "node_map_fields")
        graph.add_edge("node_map_fields", "node_generate_sections")
        graph.add_edge("node_generate_sections", "node_review")

        # Conditional: review -> revise or finalize
        graph.add_conditional_edges(
            "node_review",
            route_after_review,
            {
                "node_generate_sections": "node_generate_sections",
                "node_finalize": "node_finalize",
            },
        )
        graph.add_edge("node_finalize", END)

        _compiled_graph = graph.compile()
        logger.info("report_graph_compiled", extra={"event": "report_graph_compiled"})
        return _compiled_graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_report_pipeline(
    report_id: str,
    template_id: str,
    connection_id: str,
    user_query: str = "",
    max_revisions: int = 2,
    **kwargs: Any,
) -> dict:
    """
    Run the report generation pipeline.

    Attempts LangGraph execution first; falls back to sequential execution
    if LangGraph is unavailable or encounters an error.

    Returns the final state dict.
    """
    initial_state: Dict[str, Any] = {
        "report_id": report_id,
        "template_id": template_id,
        "connection_id": connection_id,
        "user_query": user_query,
        "max_revisions": max_revisions,
        "revision_count": 0,
        "errors": [],
        **kwargs,
    }

    # Try LangGraph first
    if _langgraph_available:
        try:
            logger.info(
                "report_pipeline_langgraph_start",
                extra={
                    "event": "report_pipeline_langgraph_start",
                    "report_id": report_id,
                },
            )
            compiled = _build_report_graph()
            result = compiled.invoke(initial_state)
            logger.info(
                "report_pipeline_langgraph_complete",
                extra={
                    "event": "report_pipeline_langgraph_complete",
                    "report_id": report_id,
                    "confidence": result.get("confidence"),
                },
            )
            return dict(result)
        except Exception as exc:
            logger.warning(
                "report_pipeline_langgraph_failed",
                extra={"error": str(exc), "report_id": report_id},
            )

    # Fallback to sequential
    logger.info(
        "report_pipeline_sequential_fallback",
        extra={
            "event": "report_pipeline_sequential_fallback",
            "report_id": report_id,
        },
    )
    from .fallback import run_report_pipeline_sequential

    return run_report_pipeline_sequential(initial_state)

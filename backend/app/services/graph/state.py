from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class ReportPipelineState(TypedDict, total=False):
    """State for the report generation pipeline."""

    # Input
    report_id: str
    template_id: str
    connection_id: str
    user_query: str
    parameters: Dict[str, Any]

    # Pipeline state
    extracted_data: Dict[str, Any]
    sql_queries: List[str]
    query_results: List[Dict[str, Any]]
    mapped_fields: Dict[str, Any]
    generated_sections: List[Dict[str, Any]]
    review_feedback: str
    review_score: float
    revision_count: int
    max_revisions: int

    # Output
    final_report: Dict[str, Any]
    confidence: float
    method: str
    errors: List[str]


class AgentWorkflowState(TypedDict, total=False):
    """State for the agent workflow pipeline."""

    # Input
    task_description: str
    agent_type: str
    context: Dict[str, Any]

    # Pipeline state
    plan: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    draft_content: str
    revision_count: int
    max_revisions: int
    evaluation_feedback: str

    # Output
    final_output: Any
    quality_score: float
    method: str
    errors: List[str]

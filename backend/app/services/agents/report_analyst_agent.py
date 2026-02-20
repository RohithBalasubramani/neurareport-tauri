# mypy: ignore-errors
"""
Report Analyst Agent — analyzes, summarizes, compares, and answers
questions about generated reports.

Follows the exact pattern of research_agent.py.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from backend.app.services.agents.base_agent import (
    AgentError,
    LLMContentFilterError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
    ProgressCallback,
    ProgressUpdate,
    ValidationError,
)
from backend.app.services.agents.agent_registry import register_agent
from backend.app.services.reports.report_context import ReportContext, ReportContextProvider

logger = logging.getLogger("neura.agents.report_analyst")


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class KeyFinding(BaseModel):
    """A key insight extracted from a report."""
    finding: str = Field(..., min_length=1)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    source_section: Optional[str] = None


class DataHighlight(BaseModel):
    """A notable data point from report tables."""
    metric: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    context: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable", "new"


class ReportAnalysis(BaseModel):
    """Complete analysis output from the Report Analyst Agent."""
    run_id: str
    analysis_type: str
    summary: str = Field(default="", min_length=0)
    key_findings: List[KeyFinding] = Field(default_factory=list)
    data_highlights: List[DataHighlight] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    comparison: Optional[Dict[str, Any]] = None  # For "compare" mode
    answer: Optional[str] = None  # For "qa" mode
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# AGENT
# =============================================================================

@register_agent(
    "report_analyst",
    version="1.0",
    capabilities=["report_analysis", "report_comparison", "insight_extraction", "report_qa"],
    timeout_seconds=300,
)
class ReportAnalystAgent:
    """
    Analyzes generated reports to extract insights, summarize findings,
    compare reports, and answer questions about report content.
    """

    INPUT_COST_PER_1K = 0.003
    OUTPUT_COST_PER_1K = 0.015
    DEFAULT_TIMEOUT_SECONDS = 120
    MAX_TIMEOUT_SECONDS = 300

    def __init__(self):
        self._client = None
        self._model = None
        self._context_provider = ReportContextProvider()

    def _get_client(self):
        if self._client is None:
            from backend.app.services.llm.client import get_llm_client
            self._client = get_llm_client()
        return self._client

    def _get_model(self) -> str:
        if self._model is None:
            from backend.app.services.llm.config import get_llm_config
            self._model = get_llm_config().model
        return self._model

    async def execute(
        self,
        run_id: str,
        analysis_type: str = "summarize",
        question: Optional[str] = None,
        compare_run_id: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> tuple[ReportAnalysis, Dict[str, Any]]:
        """
        Execute report analysis.

        Args:
            run_id: Report run to analyze
            analysis_type: "summarize" | "insights" | "compare" | "qa"
            question: Question text (required for "qa" type)
            compare_run_id: Second run_id (required for "compare" type)
            focus_areas: Optional areas to focus analysis on
            progress_callback: Optional callback for progress updates
            timeout_seconds: Timeout for LLM calls

        Returns:
            Tuple of (ReportAnalysis, metadata dict)
        """
        # Validate
        valid_types = {"summarize", "insights", "compare", "qa"}
        if analysis_type not in valid_types:
            raise ValidationError(
                f"analysis_type must be one of {valid_types}, got '{analysis_type}'",
                field="analysis_type",
            )
        if analysis_type == "qa" and not question:
            raise ValidationError("question is required for 'qa' analysis_type", field="question")
        if analysis_type == "compare" and not compare_run_id:
            raise ValidationError(
                "compare_run_id is required for 'compare' analysis_type",
                field="compare_run_id",
            )

        total_steps = 3
        current_step = 0

        def report_progress(percent: int, message: str, step: str):
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percent=percent,
                    message=message,
                    current_step=step,
                    total_steps=total_steps,
                    current_step_num=current_step,
                ))

        total_input_tokens = 0
        total_output_tokens = 0

        try:
            # Step 1: Load report context
            current_step = 1
            report_progress(5, "Loading report data...", "load")

            context = self._context_provider.get_report_context(run_id)
            if not context:
                raise AgentError(
                    f"Report run '{run_id}' not found",
                    code="REPORT_NOT_FOUND",
                    retryable=False,
                )
            if not context.text_content and not context.tables:
                html_url = (context.artifact_urls or {}).get("html_url")
                hint = f" html_url={html_url!r}" if html_url else " (no html_url recorded)"
                raise AgentError(
                    f"Report run '{run_id}' has no readable content.{hint} — "
                    f"the HTML file may have been deleted or the report generation may not have produced one",
                    code="REPORT_EMPTY",
                    retryable=False,
                )

            compare_context = None
            if analysis_type == "compare" and compare_run_id:
                compare_context = self._context_provider.get_report_context(compare_run_id)
                if not compare_context:
                    raise AgentError(
                        f"Comparison report run '{compare_run_id}' not found",
                        code="REPORT_NOT_FOUND",
                        retryable=False,
                    )

            report_progress(10, "Report data loaded", "load")

            # Step 2: LLM analysis
            current_step = 2
            report_progress(15, f"Analyzing report ({analysis_type})...", "analyze")

            if analysis_type == "summarize":
                result, tokens = await self._analyze_summarize(
                    context, focus_areas, timeout_seconds
                )
            elif analysis_type == "insights":
                result, tokens = await self._analyze_insights(
                    context, focus_areas, timeout_seconds
                )
            elif analysis_type == "compare":
                result, tokens = await self._analyze_compare(
                    context, compare_context, focus_areas, timeout_seconds
                )
            elif analysis_type == "qa":
                result, tokens = await self._analyze_qa(
                    context, question, timeout_seconds
                )
            else:
                result, tokens = await self._analyze_summarize(
                    context, focus_areas, timeout_seconds
                )

            total_input_tokens += tokens["input"]
            total_output_tokens += tokens["output"]
            report_progress(80, "Analysis complete", "analyze")

            # Step 3: Structure results
            current_step = 3
            report_progress(85, "Structuring results...", "finalize")

            analysis = ReportAnalysis(
                run_id=run_id,
                analysis_type=analysis_type,
                summary=result.get("summary", ""),
                key_findings=[
                    KeyFinding(
                        finding=f.get("finding", f) if isinstance(f, dict) else str(f),
                        confidence=f.get("confidence", 0.8) if isinstance(f, dict) else 0.8,
                        source_section=f.get("source_section") if isinstance(f, dict) else None,
                    )
                    for f in result.get("key_findings", [])
                ],
                data_highlights=[
                    DataHighlight(
                        metric=d.get("metric", ""),
                        value=str(d.get("value", "")),
                        context=d.get("context"),
                        trend=d.get("trend"),
                    )
                    for d in result.get("data_highlights", [])
                    if isinstance(d, dict)
                ],
                recommendations=result.get("recommendations", []),
                comparison=result.get("comparison"),
                answer=result.get("answer"),
            )

            cost_cents = int(
                (total_input_tokens / 1000 * self.INPUT_COST_PER_1K * 100)
                + (total_output_tokens / 1000 * self.OUTPUT_COST_PER_1K * 100)
            )

            metadata = {
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Report analysis complete", "done")
            return analysis, metadata

        except asyncio.TimeoutError:
            raise LLMTimeoutError(timeout_seconds)
        except (ValidationError, AgentError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "rate_limit" in error_str:
                raise LLMRateLimitError()
            elif "timeout" in error_str:
                raise LLMTimeoutError(timeout_seconds)
            elif "content filter" in error_str or "content_filter" in error_str:
                raise LLMContentFilterError(str(e))
            else:
                raise AgentError(
                    str(e),
                    code="REPORT_ANALYSIS_FAILED",
                    retryable=True,
                )

    # ------------------------------------------------------------------
    # Analysis methods (one per analysis_type)
    # ------------------------------------------------------------------

    def _build_report_prompt_section(self, ctx: ReportContext) -> str:
        """Build the report content section for LLM prompts."""
        parts = [
            f"Report: {ctx.template_name}",
            f"Kind: {ctx.template_kind}",
            f"Period: {ctx.start_date} to {ctx.end_date}",
            f"Status: {ctx.status}",
            f"Generated: {ctx.created_at}",
        ]
        if ctx.key_values:
            parts.append(f"Parameters: {json.dumps(ctx.key_values, default=str)}")
        parts.append("")
        parts.append("--- REPORT CONTENT ---")
        parts.append(ctx.text_content or "(no text content)")

        if ctx.tables:
            parts.append("")
            parts.append("--- DATA TABLES ---")
            for i, table in enumerate(ctx.tables, 1):
                headers = table.get("headers", [])
                rows = table.get("rows", [])
                parts.append(f"\nTable {i}:")
                if headers:
                    parts.append(" | ".join(headers))
                    parts.append("-" * 40)
                for row in rows[:50]:  # Limit rows to prevent context overflow
                    parts.append(" | ".join(str(c) for c in row))
                if len(rows) > 50:
                    parts.append(f"... ({len(rows) - 50} more rows)")

        return "\n".join(parts)

    async def _analyze_summarize(
        self,
        ctx: ReportContext,
        focus_areas: Optional[List[str]],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        focus_prompt = ""
        if focus_areas:
            focus_prompt = f"\nFocus especially on: {', '.join(focus_areas)}"

        system_prompt = f"""You are an expert report analyst. Summarize the following report, extracting key findings and actionable recommendations.
{focus_prompt}

Return JSON only:
{{
    "summary": "Executive summary (2-4 paragraphs)",
    "key_findings": [
        {{"finding": "...", "confidence": 0.9, "source_section": "..."}},
        ...
    ],
    "data_highlights": [
        {{"metric": "...", "value": "...", "context": "...", "trend": "up|down|stable|new"}},
        ...
    ],
    "recommendations": ["actionable recommendation 1", ...]
}}"""

        report_content = self._build_report_prompt_section(ctx)

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Analyze and summarize this report:\n\n{report_content}",
            max_tokens=3000,
            timeout_seconds=timeout_seconds,
        )
        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

    async def _analyze_insights(
        self,
        ctx: ReportContext,
        focus_areas: Optional[List[str]],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        focus_prompt = ""
        if focus_areas:
            focus_prompt = f"\nFocus especially on: {', '.join(focus_areas)}"

        system_prompt = f"""You are a data analyst expert. Extract deep insights from this report. Look for:
- Trends and patterns in the data
- Anomalies and outliers
- Correlations between metrics
- Areas of concern or opportunity
{focus_prompt}

Return JSON only:
{{
    "summary": "Brief overview of key insights",
    "key_findings": [
        {{"finding": "detailed insight", "confidence": 0.85, "source_section": "where in report"}},
        ...
    ],
    "data_highlights": [
        {{"metric": "metric name", "value": "value", "context": "why notable", "trend": "up|down|stable|new"}},
        ...
    ],
    "recommendations": ["data-driven recommendation 1", ...]
}}"""

        report_content = self._build_report_prompt_section(ctx)

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Extract deep insights from this report:\n\n{report_content}",
            max_tokens=3000,
            timeout_seconds=timeout_seconds,
        )
        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

    async def _analyze_compare(
        self,
        ctx: ReportContext,
        compare_ctx: Optional[ReportContext],
        focus_areas: Optional[List[str]],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        focus_prompt = ""
        if focus_areas:
            focus_prompt = f"\nFocus comparison on: {', '.join(focus_areas)}"

        report_a = self._build_report_prompt_section(ctx)
        report_b = self._build_report_prompt_section(compare_ctx) if compare_ctx else "(no comparison report)"

        system_prompt = f"""You are an expert report analyst. Compare these two reports and identify differences, trends, and changes.
{focus_prompt}

Return JSON only:
{{
    "summary": "Comparison overview",
    "key_findings": [
        {{"finding": "key difference or similarity", "confidence": 0.85, "source_section": "..."}},
        ...
    ],
    "data_highlights": [
        {{"metric": "metric name", "value": "current vs previous", "context": "change explanation", "trend": "up|down|stable"}},
        ...
    ],
    "comparison": {{
        "report_a_period": "date range",
        "report_b_period": "date range",
        "improvements": ["improvement 1", ...],
        "regressions": ["regression 1", ...],
        "unchanged": ["unchanged area 1", ...]
    }},
    "recommendations": ["recommendation based on comparison", ...]
}}"""

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Compare these two reports:\n\n=== REPORT A ===\n{report_a}\n\n=== REPORT B ===\n{report_b}",
            max_tokens=4000,
            timeout_seconds=timeout_seconds,
        )
        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

    async def _analyze_qa(
        self,
        ctx: ReportContext,
        question: Optional[str],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        system_prompt = """You are an expert report analyst. Answer the user's question about the report accurately, citing specific data from the report when possible.

Return JSON only:
{
    "answer": "Direct, detailed answer to the question",
    "summary": "Brief context about the report relevant to the question",
    "key_findings": [
        {"finding": "supporting evidence from the report", "confidence": 0.9, "source_section": "..."},
        ...
    ],
    "data_highlights": [
        {"metric": "relevant metric", "value": "value", "context": "relevance to question"},
        ...
    ],
    "recommendations": []
}"""

        report_content = self._build_report_prompt_section(ctx)

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Based on this report:\n\n{report_content}\n\nQuestion: {question}",
            max_tokens=2000,
            timeout_seconds=timeout_seconds,
        )
        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

    # ------------------------------------------------------------------
    # LLM call helper (same pattern as research_agent)
    # ------------------------------------------------------------------

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        timeout_seconds: int,
    ) -> Dict[str, Any]:
        """Make an LLM call using Claude Code CLI with proper error handling."""
        client = self._get_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        loop = asyncio.get_running_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.complete(
                    messages=messages,
                    description="report_analyst",
                    max_tokens=max_tokens,
                    temperature=0.5,
                ),
            ),
            timeout=timeout_seconds,
        )

        content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ) or ""

        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        parsed = self._parse_json_response(content)

        return {
            "raw": content,
            "parsed": parsed,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        if not content or not content.strip():
            return {}

        cleaned = content.strip()

        json_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL)
        if json_block_match:
            cleaned = json_block_match.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Find outermost balanced braces
        start_idx = cleaned.find("{")
        if start_idx != -1:
            depth = 0
            in_string = False
            escape_next = False
            for i, char in enumerate(cleaned[start_idx:], start_idx):
                if escape_next:
                    escape_next = False
                    continue
                if char == "\\":
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(cleaned[start_idx : i + 1])
                        except json.JSONDecodeError:
                            break

        logger.warning("Failed to parse JSON from LLM response: %s...", content[:200])
        return {}

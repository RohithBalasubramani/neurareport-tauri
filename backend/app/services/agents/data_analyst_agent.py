"""
Data Analyst Agent - Production-grade implementation.

Answers questions about data, generates insights, suggests charts, and
produces SQL query recommendations.  Operates over in-memory tabular data
(list of dicts), computes real statistics from the full dataset, and feeds
a stratified sample + stats to the LLM for accurate analysis.

Design Principles:
- Full-dataset statistics computed locally (not LLM-guessed)
- Stratified sampling for LLM context window efficiency
- Structured output with confidence score
- Progress callbacks for real-time updates
- Proper error categorization and cost tracking
"""
from __future__ import annotations

import asyncio
import json
import logging
import statistics
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.services.agents.base_agent import (
    AgentError,
    BaseAgentV2,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMContentFilterError,
    ProgressCallback,
    ProgressUpdate,
    ValidationError,
)

logger = logging.getLogger("neura.agents.data_analyst")


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class DataAnalystInput(BaseModel):
    """Validated input for data analyst agent."""
    question: str = Field(..., min_length=5, max_length=1000)
    data: List[Dict[str, Any]] = Field(..., min_length=1)
    data_description: Optional[str] = Field(default=None, max_length=2000)
    generate_charts: bool = Field(default=True)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty or whitespace")
        if len(v.split()) < 2:
            raise ValueError("Question must contain at least 2 words")
        return v

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not v:
            raise ValueError("Data must contain at least one row")
        if len(v) > 100_000:
            raise ValueError("Data cannot exceed 100,000 rows")
        # Ensure all rows have consistent keys
        first_keys = set(v[0].keys())
        for i, row in enumerate(v[:10]):  # Check first 10 for speed
            if set(row.keys()) != first_keys:
                raise ValueError(
                    f"Row {i} has inconsistent columns. "
                    f"Expected {sorted(first_keys)}, got {sorted(row.keys())}"
                )
        return v


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class ChartSuggestion(BaseModel):
    """A suggested chart for visualising the data."""
    chart_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    x_column: Optional[str] = None
    y_columns: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None, max_length=500)


class DataAnalysisReport(BaseModel):
    """Complete data analysis output."""
    question: str
    answer: str = Field(..., min_length=1)
    data_summary: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    charts: List[ChartSuggestion] = Field(default_factory=list)
    sql_queries: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    row_count: int = Field(default=0, ge=0)
    column_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# =============================================================================
# DATA ANALYST AGENT
# =============================================================================
from backend.app.services.agents.agent_registry import register_agent


@register_agent(
    "data_analyst",
    version="2.0",
    capabilities=["data_analysis", "chart_suggestion", "sql_generation", "statistics"],
    timeout_seconds=180,
)
class DataAnalystAgent(BaseAgentV2):
    """
    Production-grade data analyst agent.

    Features:
    - Local column-level statistics from FULL dataset
    - Stratified sampling for LLM context efficiency
    - Chart generation suggestions with column mappings
    - SQL query recommendations
    - Confidence scoring
    """

    async def execute(
        self,
        question: str,
        data: List[Dict[str, Any]],
        data_description: Optional[str] = None,
        generate_charts: bool = True,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = 120,
    ) -> tuple[DataAnalysisReport, Dict[str, Any]]:
        """Execute data analysis.

        Returns:
            Tuple of (DataAnalysisReport, metadata dict).
        """
        # Validate input
        try:
            validated = DataAnalystInput(
                question=question,
                data=data,
                data_description=data_description,
                generate_charts=generate_charts,
            )
        except Exception as e:
            raise ValidationError(str(e), field="input")

        total_steps = 2
        total_input_tokens = 0
        total_output_tokens = 0

        def report_progress(percent: int, message: str, step: str, step_num: int):
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percent=percent,
                    message=message,
                    current_step=step,
                    total_steps=total_steps,
                    current_step_num=step_num,
                ))

        try:
            # Step 1: Compute local statistics
            report_progress(10, "Computing dataset statistics...", "statistics", 1)

            columns = list(validated.data[0].keys())
            full_stats = self._compute_column_stats(validated.data, columns)
            sample = self._stratified_sample(validated.data, sample_size=30)
            stats_summary = json.dumps(full_stats, indent=2, default=str)
            data_sample = json.dumps(sample, indent=2, default=str)

            report_progress(30, "Statistics computed, analysing data...", "analysis", 2)

            # Step 2: LLM analysis
            system_prompt = f"""You are an expert data analyst. Analyse the provided data and answer the question.

Data Description: {validated.data_description or 'Not provided'}
Columns: {', '.join(columns)}
Total rows: {len(validated.data)}

IMPORTANT: The statistics below are computed from the FULL dataset, not just the sample.
Column Statistics (full dataset):
{stats_summary}

Provide your response as JSON:
{{
    "answer": "<direct answer to the question>",
    "data_summary": {{"key metrics": "..."}},
    "insights": ["<insight 1>", "<insight 2>"],
    "charts": [{{"chart_type": "<bar|line|scatter|pie|histogram>", "title": "<title>", "x_column": "<col>", "y_columns": ["<col>"], "description": "<why this chart>"}}],
    "sql_queries": ["<SQL query that would answer this>"],
    "confidence": <0.0-1.0>
}}"""

            result = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Data sample (stratified from full dataset):\n{data_sample}\n\nQuestion: {validated.question}",
                max_tokens=2000,
                timeout_seconds=timeout_seconds,
                temperature=0.3,
            )

            total_input_tokens += result["input_tokens"]
            total_output_tokens += result["output_tokens"]
            parsed = result["parsed"]

            report_progress(90, "Compiling report...", "analysis", 2)

            charts = []
            if validated.generate_charts:
                for c in parsed.get("charts", []):
                    try:
                        charts.append(ChartSuggestion(
                            chart_type=c.get("chart_type", "bar"),
                            title=c.get("title", "Chart"),
                            x_column=c.get("x_column"),
                            y_columns=c.get("y_columns", []),
                            description=c.get("description"),
                        ))
                    except Exception:
                        pass  # Skip malformed chart suggestions

            report = DataAnalysisReport(
                question=validated.question,
                answer=parsed.get("answer", "Unable to analyse data"),
                data_summary=parsed.get("data_summary", {}),
                insights=parsed.get("insights", []),
                charts=charts,
                sql_queries=parsed.get("sql_queries", []),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.5))),
                row_count=len(validated.data),
                column_count=len(columns),
            )

            cost_cents = self._estimate_cost_cents(total_input_tokens, total_output_tokens)
            metadata = {
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Analysis complete", "done", 2)
            return report, metadata

        except (ValidationError, AgentError):
            raise
        except asyncio.TimeoutError:
            raise LLMTimeoutError(timeout_seconds)
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "rate_limit" in error_str:
                raise LLMRateLimitError()
            elif "timeout" in error_str:
                raise LLMTimeoutError(timeout_seconds)
            elif "content filter" in error_str:
                raise LLMContentFilterError(str(e))
            raise AgentError(str(e), code="DATA_ANALYSIS_FAILED", retryable=True)

    # ----- local statistics helpers (never sent to LLM, computed locally) -----

    def _compute_column_stats(
        self, data: List[Dict[str, Any]], columns: List[str]
    ) -> Dict[str, Any]:
        """Compute summary statistics for all columns in the dataset."""
        stats: Dict[str, Any] = {}
        for col in columns:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if not values:
                stats[col] = {"type": "empty", "count": 0}
                continue

            numeric_values: List[float] = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass

            if len(numeric_values) > len(values) * 0.5:
                stats[col] = {
                    "type": "numeric",
                    "count": len(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": round(statistics.mean(numeric_values), 2),
                    "median": round(statistics.median(numeric_values), 2),
                    "std": round(statistics.stdev(numeric_values), 2) if len(numeric_values) > 1 else 0,
                }
            else:
                value_counts = Counter(str(v) for v in values)
                top_values = value_counts.most_common(5)
                stats[col] = {
                    "type": "categorical",
                    "count": len(values),
                    "unique": len(value_counts),
                    "top_values": [{"value": v, "count": c} for v, c in top_values],
                }
        return stats

    def _stratified_sample(
        self, data: List[Dict[str, Any]], sample_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Get a stratified sample from beginning, middle, and end."""
        if len(data) <= sample_size:
            return data

        n = len(data)
        indices: set[int] = set()
        indices.update(range(min(10, n)))
        indices.update(range(max(0, n - 10), n))

        remaining = sample_size - len(indices)
        if remaining > 0:
            step = max(1, n // remaining)
            for i in range(0, n, step):
                indices.add(i)
                if len(indices) >= sample_size:
                    break

        return [data[i] for i in sorted(indices)][:sample_size]

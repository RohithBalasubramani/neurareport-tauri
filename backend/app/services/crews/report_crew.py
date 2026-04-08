"""
Report generation crew.

Pipeline::

    Template Analyst  ->  Data Engineer  ->  Report Writer  ->  QA Reviewer
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from ..llm.agents import Agent, AgentConfig, Crew, Task
from ..llm.client import LLMClient, get_llm_client

logger = logging.getLogger("neura.crews.report")


class ReportCrew:
    """Four-agent crew for end-to-end report generation.

    Agents
    ------
    * **Template Analyst** (temp 0.2) -- dissects the template structure.
    * **Data Engineer** (temp 0.1) -- prepares and validates data for the report.
    * **Report Writer** (temp 0.6) -- drafts the report narrative.
    * **QA Reviewer** (temp 0.3) -- reviews the final output for quality.
    """

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        verbose: bool = False,
    ) -> None:
        self._client = client
        self.verbose = verbose

    @property
    def client(self) -> LLMClient:
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    # ------------------------------------------------------------------
    # Agent definitions
    # ------------------------------------------------------------------

    def _build_agents(self) -> List[Agent]:
        configs = [
            AgentConfig(
                role="template_analyst",
                goal=(
                    "Analyse the report template to identify required sections, "
                    "placeholders, formatting rules, and data requirements."
                ),
                backstory=(
                    "You are a template-design expert who has built hundreds of "
                    "report templates.  You understand placeholder syntax, conditional "
                    "sections, and data-binding conventions deeply."
                ),
                temperature=0.2,
            ),
            AgentConfig(
                role="data_engineer",
                goal=(
                    "Prepare, validate, and transform raw data so it is ready to "
                    "populate the report template accurately."
                ),
                backstory=(
                    "You are a senior data engineer specialising in ETL pipelines. "
                    "You clean, reshape, and validate datasets to match target schemas "
                    "with meticulous attention to edge cases and nulls."
                ),
                temperature=0.1,
            ),
            AgentConfig(
                role="report_writer",
                goal=(
                    "Draft a complete, well-written report that fills every template "
                    "section using the prepared data."
                ),
                backstory=(
                    "You are a professional report writer who turns structured data "
                    "into compelling business narratives.  You follow templates "
                    "precisely while making the prose clear and engaging."
                ),
                temperature=0.6,
            ),
            AgentConfig(
                role="qa_reviewer",
                goal=(
                    "Review the generated report for completeness, accuracy, "
                    "formatting compliance, and overall quality."
                ),
                backstory=(
                    "You are a relentless quality-assurance reviewer.  You check "
                    "every placeholder is filled, every number is correct, the tone "
                    "is consistent, and the report meets all template requirements."
                ),
                temperature=0.3,
            ),
        ]
        return [Agent(cfg, self.client) for cfg in configs]

    # ------------------------------------------------------------------
    # Task definitions
    # ------------------------------------------------------------------

    def _build_tasks(
        self,
        template_context: Dict[str, Any],
        data_context: Dict[str, Any],
    ) -> List[Task]:
        template_repr = json.dumps(template_context, indent=2, default=str)
        data_repr = json.dumps(data_context, indent=2, default=str)

        analyse_desc = (
            "Analyse the report template and identify all required sections, "
            "placeholders, and data requirements.\n\n"
            f"TEMPLATE CONTEXT:\n{template_repr}"
        )

        prepare_desc = (
            "Using the template analysis, prepare and validate the raw data. "
            "Map data fields to template requirements, handle missing values, "
            "and transform data types as needed.\n\n"
            f"DATA CONTEXT:\n{data_repr}"
        )

        write_desc = (
            "Using the template analysis and prepared data, draft the complete "
            "report.  Fill every section and placeholder.  Write clear, "
            "professional prose."
        )

        review_desc = (
            "Review the drafted report for:\n"
            "- Completeness (all sections filled)\n"
            "- Accuracy (data matches source)\n"
            "- Formatting compliance\n"
            "- Grammar and readability\n"
            "Provide a quality score (0-100) and list of issues."
        )

        return [
            Task(
                description=analyse_desc,
                agent_role="template_analyst",
                expected_output=(
                    "Structured template analysis: sections, placeholders, "
                    "data requirements, and formatting rules."
                ),
            ),
            Task(
                description=prepare_desc,
                agent_role="data_engineer",
                expected_output=(
                    "Prepared dataset mapped to template fields with "
                    "validation status per field."
                ),
                dependencies=[analyse_desc[:50]],
            ),
            Task(
                description=write_desc,
                agent_role="report_writer",
                expected_output="Complete draft report with all sections populated.",
                dependencies=[analyse_desc[:50], prepare_desc[:50]],
            ),
            Task(
                description=review_desc,
                agent_role="qa_reviewer",
                expected_output=(
                    "Quality review with score, issue list, and pass/fail verdict."
                ),
                dependencies=[write_desc[:50]],
            ),
        ]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        template_context: Dict[str, Any],
        data_context: Dict[str, Any],
        on_progress: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """Run the full report-generation pipeline.

        Args:
            template_context: Template metadata (structure, placeholders, etc.).
            data_context: Raw data to populate the report with.
            on_progress: Optional callback ``(agent_role, status)`` invoked
                between task executions.

        Returns:
            Dict with ``results``, ``errors``, and ``execution_summary`` keys.
        """
        start = time.time()
        logger.info(
            "report_crew_start",
            extra={"event": "report_crew_start"},
        )

        agents = self._build_agents()
        tasks = self._build_tasks(template_context, data_context)

        # Optionally wrap Crew.kickoff to inject progress callbacks
        crew = Crew(agents, tasks, verbose=self.verbose)

        if on_progress:
            # Notify before kickoff with each role
            for task in tasks:
                on_progress(task.agent_role, "pending")

        result = crew.kickoff({
            "template_context": template_context,
            "data_context": data_context,
        })

        if on_progress:
            for task in tasks:
                status = "completed" if task.description[:50] in result.get("results", {}) else "failed"
                on_progress(task.agent_role, status)

        elapsed = time.time() - start
        result.setdefault("execution_summary", {})["total_wall_time"] = round(elapsed, 2)

        logger.info(
            "report_crew_complete",
            extra={
                "event": "report_crew_complete",
                "elapsed_s": round(elapsed, 2),
            },
        )
        return result

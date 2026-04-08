"""
Report review team: ContentReviewer + FactChecker + Editor.

Uses AutoGen RoundRobinGroupChat when available, otherwise falls back to the
internal Crew orchestrator.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..llm.agents import AgentConfig, Task
from ..llm.client import LLMClient, get_llm_client
from .base_team import BaseTeam, TeamConfig

logger = logging.getLogger("neura.teams.report_review")


class ReportReviewTeam(BaseTeam):
    """Three-agent team for reviewing and refining report content.

    Pipeline::

        ContentReviewer  ->  FactChecker  ->  Editor
        (review)             (fact-check)      (edit & polish)
    """

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        *,
        max_rounds: int = 10,
        timeout: float = 90.0,
        use_autogen: bool = True,
        verbose: bool = False,
    ) -> None:
        config = TeamConfig(
            name="report_review",
            max_rounds=max_rounds,
            timeout=timeout,
            use_autogen=use_autogen,
            verbose=verbose,
        )
        super().__init__(config, client)

    # ------------------------------------------------------------------
    # Agent definitions
    # ------------------------------------------------------------------

    def _define_agents(self) -> List[AgentConfig]:
        return [
            AgentConfig(
                role="content_reviewer",
                goal=(
                    "Review report content for clarity, structure, completeness, "
                    "and adherence to the template requirements."
                ),
                backstory=(
                    "You are a senior technical editor with decades of experience "
                    "reviewing business reports, financial documents, and analytical "
                    "narratives.  You focus on logical flow, readability, and whether "
                    "all required sections are present and well-developed."
                ),
                temperature=0.3,
            ),
            AgentConfig(
                role="fact_checker",
                goal=(
                    "Verify factual claims, numerical data, and cross-references "
                    "within the report for accuracy and consistency."
                ),
                backstory=(
                    "You are a meticulous fact-checker who has worked at major "
                    "publications.  You verify numbers, check that cited data matches "
                    "source tables, flag unsupported claims, and ensure internal "
                    "consistency across sections."
                ),
                temperature=0.1,
            ),
            AgentConfig(
                role="editor",
                goal=(
                    "Produce the final polished version of the report by incorporating "
                    "review feedback and fact-check corrections."
                ),
                backstory=(
                    "You are a professional copy-editor who transforms rough drafts "
                    "into publication-ready documents.  You fix grammar, improve "
                    "transitions, ensure consistent terminology, and produce a "
                    "cohesive final output."
                ),
                temperature=0.4,
            ),
        ]

    # ------------------------------------------------------------------
    # Task definitions
    # ------------------------------------------------------------------

    def _define_tasks(self, inputs: Dict[str, Any]) -> List[Task]:
        report_content = inputs.get("report_content", "")
        template_name = inputs.get("template_name", "general")

        review_desc = (
            f"Review the following report (template: {template_name}) for "
            "clarity, structure, completeness, and adherence to requirements. "
            "Provide a structured list of issues with severity (critical / major / minor) "
            "and specific suggestions for improvement.\n\n"
            f"REPORT CONTENT:\n{report_content}"
        )

        fact_check_desc = (
            "Using the content review results, fact-check the report. "
            "Verify all numerical claims, cross-references, and data consistency. "
            "Produce a list of verified facts and any corrections needed."
        )

        edit_desc = (
            "Incorporate the content review feedback and fact-check corrections "
            "to produce the final polished version of the report. "
            "Fix grammar, improve transitions, ensure consistent terminology, "
            "and output the complete revised report."
        )

        return [
            Task(
                description=review_desc,
                agent_role="content_reviewer",
                expected_output=(
                    "Structured review with issues categorised as critical / major / minor "
                    "and actionable suggestions."
                ),
                context={"template_name": template_name},
            ),
            Task(
                description=fact_check_desc,
                agent_role="fact_checker",
                expected_output=(
                    "Fact-check report listing verified facts, corrections needed, "
                    "and confidence levels."
                ),
                dependencies=[review_desc[:50]],
            ),
            Task(
                description=edit_desc,
                agent_role="editor",
                expected_output="Final polished report incorporating all feedback.",
                dependencies=[fact_check_desc[:50]],
            ),
        ]


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------


def review_report(
    report_content: str,
    template_name: str = "",
    client: Optional[LLMClient] = None,
) -> dict:
    """Review a report using the three-agent review pipeline.

    Args:
        report_content: The raw report text to review.
        template_name: Optional template name for context.
        client: Optional pre-configured LLM client.

    Returns:
        Dict with ``results``, ``errors``, and ``execution_summary`` keys.
    """
    team = ReportReviewTeam(client=client)
    return team.run({
        "report_content": report_content,
        "template_name": template_name or "general",
    })

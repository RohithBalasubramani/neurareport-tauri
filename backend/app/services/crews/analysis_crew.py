"""
Data analysis crew.

Pipeline::

    Data Explorer  ->  Statistician  ->  Narrator
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from ..llm.agents import Agent, AgentConfig, Crew, Task
from ..llm.client import LLMClient, get_llm_client

logger = logging.getLogger("neura.crews.analysis")


class AnalysisCrew:
    """Three-agent crew for data analysis and narrative generation.

    Agents
    ------
    * **Data Explorer** (temp 0.4) -- profiles the data and surfaces patterns.
    * **Statistician** (temp 0.1) -- runs rigorous statistical analysis.
    * **Narrator** (temp 0.7) -- translates findings into a readable narrative.
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
                role="data_explorer",
                goal=(
                    "Profile the dataset, identify distributions, outliers, "
                    "missing values, and surface initial patterns worth "
                    "investigating."
                ),
                backstory=(
                    "You are a data scientist who loves the exploratory phase. "
                    "You build quick profiles, generate summary statistics, "
                    "spot anomalies, and form hypotheses that guide deeper "
                    "analysis."
                ),
                temperature=0.4,
            ),
            AgentConfig(
                role="statistician",
                goal=(
                    "Perform rigorous statistical analysis on the data, "
                    "testing hypotheses, computing confidence intervals, and "
                    "identifying significant relationships."
                ),
                backstory=(
                    "You are a PhD statistician who insists on methodological "
                    "correctness.  You select appropriate tests, verify "
                    "assumptions, report effect sizes and p-values, and never "
                    "over-claim from the data."
                ),
                temperature=0.1,
            ),
            AgentConfig(
                role="narrator",
                goal=(
                    "Transform the statistical findings into a clear, "
                    "compelling narrative accessible to a business audience."
                ),
                backstory=(
                    "You are a data storyteller who bridges the gap between "
                    "analysts and decision-makers.  You translate complex "
                    "statistics into plain language, use analogies, and always "
                    "tie findings back to actionable business implications."
                ),
                temperature=0.7,
            ),
        ]
        return [Agent(cfg, self.client) for cfg in configs]

    # ------------------------------------------------------------------
    # Task definitions
    # ------------------------------------------------------------------

    def _build_tasks(
        self,
        data_context: Dict[str, Any],
        analysis_question: str,
        data_profile: Optional[Dict[str, Any]],
    ) -> List[Task]:
        data_repr = json.dumps(data_context, indent=2, default=str)
        profile_section = ""
        if data_profile:
            profile_section = (
                f"\n\nEXISTING DATA PROFILE:\n"
                f"{json.dumps(data_profile, indent=2, default=str)}"
            )

        explore_desc = (
            "Explore the following dataset and answer the analysis question. "
            "Profile the data: distributions, missing values, outliers, "
            "correlations, and initial patterns.\n\n"
            f"ANALYSIS QUESTION: {analysis_question}\n\n"
            f"DATA CONTEXT:\n{data_repr}"
            f"{profile_section}"
        )

        stats_desc = (
            "Using the exploratory findings, perform rigorous statistical "
            "analysis relevant to the analysis question.  Include:\n"
            "- Appropriate statistical tests with justification\n"
            "- Confidence intervals and effect sizes\n"
            "- Assessment of statistical significance\n"
            "- Caveats and limitations"
        )

        narrate_desc = (
            "Synthesise the exploration and statistical analysis into a "
            "business-friendly narrative that directly answers the analysis "
            "question.  Include:\n"
            "- Key finding (one sentence)\n"
            "- Supporting evidence\n"
            "- Confidence level\n"
            "- Limitations and caveats\n"
            "- Recommended next steps"
        )

        return [
            Task(
                description=explore_desc,
                agent_role="data_explorer",
                expected_output=(
                    "Data profile with distributions, outliers, patterns, "
                    "and initial hypotheses."
                ),
                context={"analysis_question": analysis_question},
            ),
            Task(
                description=stats_desc,
                agent_role="statistician",
                expected_output=(
                    "Statistical analysis report with tests, results, "
                    "confidence intervals, and significance assessments."
                ),
                dependencies=[explore_desc[:50]],
            ),
            Task(
                description=narrate_desc,
                agent_role="narrator",
                expected_output=(
                    "Business-friendly narrative answering the analysis "
                    "question with evidence and recommendations."
                ),
                dependencies=[stats_desc[:50]],
            ),
        ]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        data_context: Dict[str, Any],
        analysis_question: str,
        data_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the data-analysis pipeline.

        Args:
            data_context: The dataset or data summary to analyse.
            analysis_question: The business question to answer.
            data_profile: Optional pre-computed data profile to speed up
                exploration.

        Returns:
            Dict with ``results``, ``errors``, and ``execution_summary`` keys.
        """
        start = time.time()
        logger.info(
            "analysis_crew_start",
            extra={
                "event": "analysis_crew_start",
                "question": analysis_question[:100],
            },
        )

        agents = self._build_agents()
        tasks = self._build_tasks(data_context, analysis_question, data_profile)

        crew = Crew(agents, tasks, verbose=self.verbose)
        result = crew.kickoff({
            "data_context": data_context,
            "analysis_question": analysis_question,
            "data_profile": data_profile or {},
        })

        elapsed = time.time() - start
        result.setdefault("execution_summary", {})["total_wall_time"] = round(elapsed, 2)

        logger.info(
            "analysis_crew_complete",
            extra={
                "event": "analysis_crew_complete",
                "elapsed_s": round(elapsed, 2),
            },
        )
        return result

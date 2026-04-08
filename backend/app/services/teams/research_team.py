"""
Research team: Researcher + Analyst + Writer.

Gathers information on a topic, performs structured analysis, and produces
a well-written research summary.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..llm.agents import AgentConfig, Task
from ..llm.client import LLMClient, get_llm_client
from .base_team import BaseTeam, TeamConfig

logger = logging.getLogger("neura.teams.research")


class ResearchTeam(BaseTeam):
    """Three-agent team for topic research and write-up.

    Pipeline::

        Researcher  ->  Analyst  ->  Writer
        (gather)        (analyse)    (write)
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
            name="research",
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
                role="researcher",
                goal=(
                    "Gather comprehensive information on the given topic, "
                    "identifying key facts, trends, and relevant data points."
                ),
                backstory=(
                    "You are a seasoned research analyst who has worked across "
                    "consulting, academia, and journalism.  You know how to "
                    "identify credible sources, distil complex topics into "
                    "structured findings, and flag knowledge gaps."
                ),
                temperature=0.7,
            ),
            AgentConfig(
                role="analyst",
                goal=(
                    "Perform structured analysis of the research findings, "
                    "identifying patterns, drawing conclusions, and assessing "
                    "confidence levels."
                ),
                backstory=(
                    "You are a quantitative analyst with a background in "
                    "statistics and strategic consulting.  You excel at turning "
                    "raw research into actionable insights, building frameworks, "
                    "and highlighting risks and opportunities."
                ),
                temperature=0.3,
            ),
            AgentConfig(
                role="writer",
                goal=(
                    "Produce a clear, well-structured research summary that "
                    "synthesises the analysis into a compelling narrative."
                ),
                backstory=(
                    "You are an award-winning business writer who transforms "
                    "dense analytical material into readable, engaging reports. "
                    "You balance rigour with accessibility and always include "
                    "an executive summary and clear recommendations."
                ),
                temperature=0.5,
            ),
        ]

    # ------------------------------------------------------------------
    # Task definitions
    # ------------------------------------------------------------------

    def _define_tasks(self, inputs: Dict[str, Any]) -> List[Task]:
        topic = inputs.get("topic", "")
        depth = inputs.get("depth", "standard")
        extra_context = inputs.get("context", "")

        depth_instruction = {
            "brief": "Provide a high-level overview with 3-5 key points.",
            "standard": "Provide a thorough overview covering background, current state, and outlook.",
            "deep": (
                "Provide an exhaustive deep-dive with historical context, "
                "quantitative data, competing viewpoints, and detailed outlook."
            ),
        }.get(depth, "Provide a thorough overview.")

        research_desc = (
            f"Research the following topic: {topic}\n\n"
            f"DEPTH: {depth_instruction}\n"
            + (f"\nADDITIONAL CONTEXT:\n{extra_context}" if extra_context else "")
            + "\n\nGather key facts, trends, data points, and relevant background. "
            "Organise findings into clear categories."
        )

        analyse_desc = (
            "Analyse the research findings.  Identify:\n"
            "- Key patterns and trends\n"
            "- Strengths and weaknesses\n"
            "- Risks and opportunities\n"
            "- Confidence level for each conclusion\n"
            "Produce a structured analytical framework."
        )

        write_desc = (
            "Synthesise the research and analysis into a polished summary. "
            "Include:\n"
            "- Executive summary (2-3 sentences)\n"
            "- Detailed findings\n"
            "- Analysis and conclusions\n"
            "- Recommendations (if applicable)\n"
            "Write for a business audience."
        )

        return [
            Task(
                description=research_desc,
                agent_role="researcher",
                expected_output=(
                    "Structured research findings organised by category with "
                    "sources and confidence indicators."
                ),
                context={"topic": topic, "depth": depth},
            ),
            Task(
                description=analyse_desc,
                agent_role="analyst",
                expected_output=(
                    "Analytical framework with patterns, conclusions, and "
                    "confidence levels."
                ),
                dependencies=[research_desc[:50]],
            ),
            Task(
                description=write_desc,
                agent_role="writer",
                expected_output=(
                    "Polished research summary with executive summary, findings, "
                    "analysis, and recommendations."
                ),
                dependencies=[analyse_desc[:50]],
            ),
        ]


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------


def research_topic(
    topic: str,
    depth: str = "standard",
    context: Optional[str] = None,
    client: Optional[LLMClient] = None,
) -> dict:
    """Research a topic using the three-agent research pipeline.

    Args:
        topic: The topic to research.
        depth: Research depth — ``"brief"``, ``"standard"``, or ``"deep"``.
        context: Optional additional context or constraints.
        client: Optional pre-configured LLM client.

    Returns:
        Dict with ``results``, ``errors``, and ``execution_summary`` keys.
    """
    team = ResearchTeam(client=client)
    return team.run({
        "topic": topic,
        "depth": depth,
        "context": context or "",
    })

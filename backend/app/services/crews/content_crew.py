"""
Content adaptation crew.

Pipeline::

    Content Strategist  ->  Platform Specialist  ->  Editor
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from ..llm.agents import Agent, AgentConfig, Crew, Task
from ..llm.client import LLMClient, get_llm_client

logger = logging.getLogger("neura.crews.content")


class ContentCrew:
    """Three-agent crew for adapting content across formats and platforms.

    Agents
    ------
    * **Content Strategist** (temp 0.5) -- plans the adaptation approach.
    * **Platform Specialist** (temp 0.4) -- adapts content for each target format.
    * **Editor** (temp 0.3) -- polishes and ensures consistency.
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
                role="content_strategist",
                goal=(
                    "Analyse the source content and develop an adaptation "
                    "strategy for each target format, identifying what to "
                    "keep, condense, expand, or restructure."
                ),
                backstory=(
                    "You are a content strategy director who has led "
                    "multi-channel campaigns.  You understand how message, "
                    "tone, and structure must change across reports, slide "
                    "decks, executive summaries, and web content."
                ),
                temperature=0.5,
            ),
            AgentConfig(
                role="platform_specialist",
                goal=(
                    "Transform the source content into each requested target "
                    "format following the adaptation strategy and any style "
                    "guide constraints."
                ),
                backstory=(
                    "You are a versatile content producer who has written "
                    "everything from white papers to social posts.  You adapt "
                    "language, structure, and detail level to fit the medium "
                    "while preserving the core message."
                ),
                temperature=0.4,
            ),
            AgentConfig(
                role="content_editor",
                goal=(
                    "Review all adapted versions for consistency, accuracy, "
                    "style-guide compliance, and overall quality."
                ),
                backstory=(
                    "You are a managing editor with an eye for brand "
                    "consistency.  You ensure every piece — regardless of "
                    "format — maintains the same facts, tone, and voice "
                    "while being optimised for its medium."
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
        source_content: Dict[str, Any],
        target_formats: List[str],
        style_guide: Optional[str],
    ) -> List[Task]:
        source_repr = json.dumps(source_content, indent=2, default=str)
        formats_repr = ", ".join(target_formats) if target_formats else "general"
        style_section = f"\n\nSTYLE GUIDE:\n{style_guide}" if style_guide else ""

        strategy_desc = (
            "Analyse the source content and develop an adaptation strategy "
            f"for the following target formats: {formats_repr}.\n\n"
            f"SOURCE CONTENT:\n{source_repr}"
            f"{style_section}\n\n"
            "For each format, outline what to keep, condense, expand, or "
            "restructure.  Note any format-specific constraints."
        )

        adapt_desc = (
            "Following the adaptation strategy, produce the content in each "
            f"target format ({formats_repr}).  Ensure each version stands on "
            "its own while being faithful to the source material."
        )

        edit_desc = (
            "Review all adapted content versions for:\n"
            "- Factual consistency with the source\n"
            "- Style-guide compliance\n"
            "- Format-appropriate structure and tone\n"
            "- Grammar and readability\n"
            "Produce the final polished versions."
        )

        return [
            Task(
                description=strategy_desc,
                agent_role="content_strategist",
                expected_output=(
                    "Adaptation strategy per format with keep/condense/expand "
                    "decisions and format-specific notes."
                ),
            ),
            Task(
                description=adapt_desc,
                agent_role="platform_specialist",
                expected_output=(
                    "Adapted content for each target format, clearly separated."
                ),
                dependencies=[strategy_desc[:50]],
            ),
            Task(
                description=edit_desc,
                agent_role="content_editor",
                expected_output=(
                    "Final polished versions of all adapted content with "
                    "consistency notes."
                ),
                dependencies=[adapt_desc[:50]],
            ),
        ]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        source_content: Dict[str, Any],
        target_formats: List[str],
        style_guide: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the content adaptation pipeline.

        Args:
            source_content: Original content to adapt.
            target_formats: List of target format names
                (e.g. ``["executive_summary", "slide_deck", "blog_post"]``).
            style_guide: Optional style-guide text or reference.

        Returns:
            Dict with ``results``, ``errors``, and ``execution_summary`` keys.
        """
        start = time.time()
        logger.info(
            "content_crew_start",
            extra={
                "event": "content_crew_start",
                "target_formats": target_formats,
            },
        )

        agents = self._build_agents()
        tasks = self._build_tasks(source_content, target_formats, style_guide)

        crew = Crew(agents, tasks, verbose=self.verbose)
        result = crew.kickoff({
            "source_content": source_content,
            "target_formats": target_formats,
            "style_guide": style_guide or "",
        })

        elapsed = time.time() - start
        result.setdefault("execution_summary", {})["total_wall_time"] = round(elapsed, 2)

        logger.info(
            "content_crew_complete",
            extra={
                "event": "content_crew_complete",
                "elapsed_s": round(elapsed, 2),
            },
        )
        return result

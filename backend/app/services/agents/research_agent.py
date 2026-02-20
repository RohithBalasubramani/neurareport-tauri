"""
Research Agent - Production-grade implementation.

Design Principles:
- Explicit progress tracking
- Structured output with validation
- Proper error categorization
- Cost tracking for LLM usage
- Timeout handling
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("neura.agents.research")


# =============================================================================
# ERROR TYPES — unified from base_agent.py
# =============================================================================

from backend.app.services.agents.base_agent import (  # noqa: E402
    AgentError,
    LLMContentFilterError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
    ValidationError,
)


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class ResearchSection(BaseModel):
    """A section in the research report."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    word_count: int = Field(default=0, ge=0)

    def model_post_init(self, __context):
        if not self.word_count:
            self.word_count = len(self.content.split())


class ResearchSource(BaseModel):
    """A source referenced in the research."""
    title: str = Field(..., min_length=1, max_length=300)
    url: Optional[str] = Field(default=None, max_length=2000)
    relevance: Optional[str] = Field(default=None, max_length=500)


class ResearchReport(BaseModel):
    """Complete research report output."""
    topic: str
    depth: str
    summary: str = Field(..., min_length=10)
    sections: List[ResearchSection] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    sources: List[ResearchSource] = Field(default_factory=list)
    word_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context):
        if not self.word_count:
            total = len(self.summary.split())
            for section in self.sections:
                total += section.word_count
            self.word_count = total


# =============================================================================
# PROGRESS CALLBACK
# =============================================================================

from backend.app.services.agents.base_agent import ProgressUpdate, ProgressCallback


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class ResearchInput(BaseModel):
    """Validated input for research agent."""
    topic: str = Field(..., max_length=500)
    depth: Literal["quick", "moderate", "comprehensive"] = "comprehensive"
    focus_areas: List[str] = Field(default_factory=list)
    max_sections: int = Field(default=5, ge=1, le=20)

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty or whitespace")
        # Must contain at least 2 words for meaningful research
        words = v.split()
        if len(words) < 2:
            raise ValueError("Topic must contain at least 2 words for meaningful research")
        # Basic content validation - reject obviously invalid topics
        if all(c in '0123456789!@#$%^&*()' for c in v.replace(' ', '')):
            raise ValueError("Topic must contain meaningful text")
        return v

    @field_validator('focus_areas')
    @classmethod
    def validate_focus_areas(cls, v: List[str]) -> List[str]:
        if not v:
            return v
        # Clean and deduplicate
        cleaned = []
        seen = set()
        for area in v:
            area = area.strip()
            if area and area.lower() not in seen:
                seen.add(area.lower())
                cleaned.append(area)
        return cleaned[:10]  # Max 10 focus areas


# =============================================================================
# RESEARCH AGENT
# =============================================================================
from backend.app.services.agents.agent_registry import register_agent


@register_agent(
    "research",
    version="2.0",
    capabilities=["research", "report_generation", "topic_analysis"],
    timeout_seconds=300,
)
class ResearchAgent:
    """
    Production-grade research agent.

    Features:
    - Input validation with semantic checks
    - Structured output with schema validation
    - Progress callbacks for real-time updates
    - Proper error categorization
    - Token/cost tracking
    - Timeout handling

    Usage:
        agent = ResearchAgent()
        result = await agent.execute(
            topic="AI trends in healthcare 2025",
            depth="comprehensive",
            progress_callback=lambda p: print(f"{p.percent}% - {p.message}")
        )
    """

    # Token cost estimates (per 1K tokens)
    INPUT_COST_PER_1K = 0.003  # $0.003 per 1K input tokens
    OUTPUT_COST_PER_1K = 0.015  # $0.015 per 1K output tokens

    # Timeout settings
    DEFAULT_TIMEOUT_SECONDS = 120
    MAX_TIMEOUT_SECONDS = 300

    def __init__(self):
        self._client = None
        self._model = None

    def _get_client(self):
        """Get unified LLM client (Claude Code CLI) lazily."""
        if self._client is None:
            from backend.app.services.llm.client import get_llm_client
            self._client = get_llm_client()
        return self._client

    def _get_model(self) -> str:
        """Get model name from LLM config."""
        if self._model is None:
            from backend.app.services.llm.config import get_llm_config
            self._model = get_llm_config().model
        return self._model

    async def execute(
        self,
        topic: str,
        depth: str = "comprehensive",
        focus_areas: Optional[List[str]] = None,
        max_sections: int = 5,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> tuple[ResearchReport, Dict[str, Any]]:
        """
        Execute research on a topic.

        Args:
            topic: Topic to research
            depth: Research depth (quick, moderate, comprehensive)
            focus_areas: Optional areas to focus on
            max_sections: Maximum number of sections
            progress_callback: Optional callback for progress updates
            timeout_seconds: Timeout for LLM calls

        Returns:
            Tuple of (ResearchReport, metadata dict with token counts and cost)

        Raises:
            ValidationError: If input validation fails
            LLMTimeoutError: If LLM request times out
            LLMRateLimitError: If rate limited
            LLMResponseError: If LLM returns invalid response
            AgentError: For other errors
        """
        # Validate input
        try:
            validated_input = ResearchInput(
                topic=topic,
                depth=depth,
                focus_areas=focus_areas or [],
                max_sections=max_sections,
            )
        except Exception as e:
            raise ValidationError(str(e), field="input")

        # Setup progress tracking
        total_steps = 3  # outline, sections, synthesis
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

        # Track tokens and cost
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            # Step 1: Generate research outline
            current_step = 1
            report_progress(10, "Generating research outline...", "outline")

            outline_result, tokens = await self._generate_outline(
                validated_input,
                timeout_seconds=timeout_seconds,
            )
            total_input_tokens += tokens["input"]
            total_output_tokens += tokens["output"]

            report_progress(25, "Outline generated", "outline")

            # Step 2: Generate sections
            current_step = 2
            sections_result, tokens = await self._generate_sections(
                validated_input,
                outline_result,
                progress_callback=lambda pct, msg: report_progress(
                    25 + int(pct * 0.5),  # 25% to 75%
                    msg,
                    "sections"
                ),
                timeout_seconds=timeout_seconds,
            )
            total_input_tokens += tokens["input"]
            total_output_tokens += tokens["output"]

            report_progress(75, "Sections generated", "sections")

            # Step 3: Synthesize and finalize
            current_step = 3
            report_progress(80, "Synthesizing findings...", "synthesis")

            final_result, tokens = await self._synthesize_report(
                validated_input,
                outline_result,
                sections_result,
                timeout_seconds=timeout_seconds,
            )
            total_input_tokens += tokens["input"]
            total_output_tokens += tokens["output"]

            report_progress(95, "Finalizing report...", "synthesis")

            # Build final report
            report = ResearchReport(
                topic=validated_input.topic,
                depth=validated_input.depth,
                summary=final_result.get("summary", ""),
                sections=[
                    ResearchSection(
                        title=s.get("title", "Untitled"),
                        content=s.get("content", ""),
                    )
                    for s in sections_result.get("sections", [])
                ],
                key_findings=final_result.get("key_findings", []),
                recommendations=final_result.get("recommendations", []),
                sources=[
                    ResearchSource(
                        title=src.get("title", "Unknown"),
                        url=src.get("url"),
                        relevance=src.get("relevance"),
                    )
                    for src in final_result.get("sources", [])
                ],
            )

            # Calculate cost
            cost_cents = int(
                (total_input_tokens / 1000 * self.INPUT_COST_PER_1K * 100) +
                (total_output_tokens / 1000 * self.OUTPUT_COST_PER_1K * 100)
            )

            metadata = {
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Research complete", "done")

            return report, metadata

        except asyncio.TimeoutError:
            raise LLMTimeoutError(timeout_seconds)
        except Exception as e:
            # Categorize the error
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
                    code="RESEARCH_FAILED",
                    retryable=True,
                )

    async def _generate_outline(
        self,
        input: ResearchInput,
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        """Generate research outline."""
        focus_prompt = ""
        if input.focus_areas:
            focus_prompt = f"\nFocus on these areas: {', '.join(input.focus_areas)}"

        depth_instructions = {
            "quick": "Create a brief outline with 2-3 main topics.",
            "moderate": "Create a balanced outline with 4-5 main topics and subtopics.",
            "comprehensive": "Create a detailed outline with all major aspects, subtopics, and related concepts.",
        }

        system_prompt = f"""You are a research planning expert. Create a structured outline for researching the given topic.

{depth_instructions.get(input.depth, depth_instructions['moderate'])}
{focus_prompt}

Return JSON only:
{{
    "main_topics": ["topic1", "topic2", ...],
    "subtopics": {{"topic1": ["subtopic1", ...], ...}},
    "key_questions": ["question1", ...]
}}

Maximum {input.max_sections} main topics."""

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Create a research outline for: {input.topic}",
            max_tokens=1000,
            timeout_seconds=timeout_seconds,
        )

        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

    async def _generate_sections(
        self,
        input: ResearchInput,
        outline: Dict[str, Any],
        progress_callback: Callable[[float, str], None],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        """Generate research sections based on outline."""
        main_topics = outline.get("main_topics", [])[:input.max_sections]
        subtopics = outline.get("subtopics", {})

        total_input_tokens = 0
        total_output_tokens = 0
        sections = []

        for i, topic in enumerate(main_topics):
            progress = i / len(main_topics)
            progress_callback(progress, f"Researching: {topic}")

            topic_subtopics = subtopics.get(topic, [])

            system_prompt = f"""You are an expert research writer. Write a detailed section about the given topic.

Topic Context: Part of a larger report on "{input.topic}"
Section Topic: {topic}
Subtopics to cover: {', '.join(topic_subtopics) if topic_subtopics else 'General overview'}

Depth: {input.depth}
- quick: 100-200 words, key points only
- moderate: 300-500 words, balanced coverage
- comprehensive: 500-800 words, detailed analysis

Return JSON only:
{{
    "title": "Section Title",
    "content": "Full section content with paragraphs...",
    "key_points": ["point1", ...]
}}"""

            result = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Write the section about: {topic}",
                max_tokens=2000,
                timeout_seconds=timeout_seconds,
            )

            total_input_tokens += result["input_tokens"]
            total_output_tokens += result["output_tokens"]

            sections.append(result["parsed"])

        return {"sections": sections}, {"input": total_input_tokens, "output": total_output_tokens}

    async def _synthesize_report(
        self,
        input: ResearchInput,
        outline: Dict[str, Any],
        sections: Dict[str, Any],
        timeout_seconds: int,
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        """Synthesize final report with summary, findings, and recommendations."""
        section_summaries = []
        for s in sections.get("sections", []):
            title = s.get("title", "")
            points = s.get("key_points", [])
            section_summaries.append(f"- {title}: {', '.join(points[:3])}")

        system_prompt = f"""You are a research analyst. Synthesize the research sections into a final report.

Topic: {input.topic}
Research Depth: {input.depth}

Section Summaries:
{chr(10).join(section_summaries)}

Create a synthesis with:
1. Executive summary (2-3 paragraphs)
2. Key findings (5-10 bullet points)
3. Recommendations (3-5 actionable items)
4. Sources/references (if applicable)

Return JSON only:
{{
    "summary": "Executive summary...",
    "key_findings": ["finding1", ...],
    "recommendations": ["recommendation1", ...],
    "sources": [{{"title": "Source", "url": "optional url", "relevance": "why relevant"}}]
}}"""

        result = await self._call_llm(
            system_prompt=system_prompt,
            user_prompt="Synthesize the research into a final report.",
            max_tokens=2000,
            timeout_seconds=timeout_seconds,
        )

        return result["parsed"], {"input": result["input_tokens"], "output": result["output_tokens"]}

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
            {"role": "user", "content": user_prompt}
        ]

        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_running_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.complete(
                    messages=messages,
                    description="research_agent",
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
            ),
            timeout=timeout_seconds,
        )

        # Extract content from OpenAI-compatible response format
        content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ) or ""

        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # Parse JSON from response
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

        # Handle ```json ... ``` blocks
        json_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL)
        if json_block_match:
            cleaned = json_block_match.group(1).strip()
        elif cleaned.startswith("```"):
            parts = cleaned.split("```", 2)
            if len(parts) >= 2:
                cleaned = parts[1].strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in content
        for pattern in [r"\{.*\}", r"\[.*\]"]:
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from LLM output: {content[:200]}...")
        raise LLMResponseError("Failed to parse JSON from LLM response")

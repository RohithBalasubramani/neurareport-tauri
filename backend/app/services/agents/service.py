"""
AI Agents Service
Specialized AI agents for research, analysis, email drafting, and more.
"""
from __future__ import annotations

import asyncio
import logging
import hashlib
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of AI agents."""
    RESEARCH = "research"
    DATA_ANALYST = "data_analyst"
    EMAIL_DRAFT = "email_draft"
    CONTENT_REPURPOSE = "content_repurpose"
    PROOFREADING = "proofreading"


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def _utc_now() -> datetime:
    """Return current UTC time (avoids deprecated utcnow)."""
    return datetime.now(timezone.utc)


class AgentTask(BaseModel):
    """Task assigned to an agent."""
    task_id: str
    agent_type: AgentType
    input: Dict[str, Any]
    status: AgentStatus = AgentStatus.IDLE
    progress: float = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=_utc_now)
    completed_at: Optional[datetime] = None


class ResearchReport(BaseModel):
    """Result from research agent."""
    topic: str
    summary: str
    sections: List[Dict[str, str]] = Field(default_factory=list)  # {title, content}
    sources: List[Dict[str, Any]] = Field(default_factory=list)  # {title, url} - url may be None/null
    key_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    word_count: int = 0


class DataAnalysisResult(BaseModel):
    """Result from data analyst agent."""
    query: str
    answer: str
    data_summary: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    sql_queries: List[str] = Field(default_factory=list)
    confidence: float = 0


class EmailDraft(BaseModel):
    """Result from email draft agent."""
    subject: str
    body: str
    tone: str
    suggested_recipients: List[str] = Field(default_factory=list)
    attachments_suggested: List[str] = Field(default_factory=list)
    follow_up_actions: List[str] = Field(default_factory=list)


class RepurposedContent(BaseModel):
    """Result from content repurposing agent."""
    original_format: str
    outputs: List[Dict[str, Any]] = Field(default_factory=list)  # {format, content, metadata}
    adaptations_made: List[str] = Field(default_factory=list)


class ProofreadingResult(BaseModel):
    """Result from proofreading agent."""
    original_text: str
    corrected_text: str
    issues_found: List[Dict[str, Any]] = Field(default_factory=list)
    style_suggestions: List[str] = Field(default_factory=list)
    readability_score: float = 0
    word_count: int = 0
    reading_level: str = ""


class BaseAgent(ABC):
    """Base class for AI agents."""

    def __init__(self):
        self._llm_client = None

    # Backwards compatibility alias
    @property
    def _client(self):
        """Backwards compatibility alias for _llm_client."""
        return self._llm_client

    @_client.setter
    def _client(self, value):
        """Backwards compatibility setter for _llm_client."""
        self._llm_client = value

    def _get_client(self):
        """Backwards compatibility alias for _get_llm_client."""
        return self._get_llm_client()

    def _get_llm_client(self):
        """Get OpenAI client (legacy service expectation).

        Note: This is the legacy in-memory agent service used by a subset of
        API/tests that patch `openai.OpenAI`. The production agent service uses
        the unified LLM client.
        """
        if self._llm_client is None:
            import openai
            self._llm_client = openai.OpenAI()
        return self._llm_client

    def _get_model(self) -> str:
        """Get model name from LLM config."""
        from backend.app.services.llm.config import get_llm_config
        return get_llm_config().model

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Make an OpenAI chat-completions call (legacy).

        The v2 agent service owns the unified LLM abstraction; this legacy
        implementation keeps a minimal OpenAI-compatible call path for tests
        and backward compatibility.
        """
        client = self._get_llm_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        model = self._get_model()
        # Some OpenAI models (e.g. gpt-5) use max_completion_tokens instead of max_tokens.
        # Keep this logic local to the legacy agent service to satisfy compatibility tests.
        create_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if str(model).startswith("gpt-5"):
            create_kwargs["max_completion_tokens"] = max_tokens
        else:
            create_kwargs["max_tokens"] = max_tokens

        response = client.chat.completions.create(**create_kwargs)

        # Support both SDK object responses and dict-like responses.
        try:
            return response.choices[0].message.content or ""
        except Exception:
            pass

        try:
            return (
                (response or {}).get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                or ""
            )
        except Exception:
            return ""

    # Backwards compatibility alias
    def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Backwards compatible alias for _call_llm."""
        return self._call_llm(system_prompt, user_prompt, max_tokens, temperature)

    def _safe_parse_json(self, content: str, default: dict | None = None) -> dict:
        """Safely parse JSON from LLM output, handling code blocks and malformed JSON.

        Args:
            content: Raw LLM output that may contain JSON
            default: Default value if parsing fails

        Returns:
            Parsed JSON dict or default value
        """
        import json
        import re

        if default is None:
            default = {}

        if not content or not content.strip():
            return default

        # Try to extract JSON from markdown code blocks
        cleaned = content.strip()

        # Handle ```json ... ``` blocks
        json_block_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL)
        if json_block_match:
            cleaned = json_block_match.group(1).strip()
        elif cleaned.startswith("```"):
            # Handle case where ``` is at start but no closing
            parts = cleaned.split("```", 2)
            if len(parts) >= 2:
                cleaned = parts[1].strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object or array in the content
        for pattern in [r"\{.*\}", r"\[.*\]"]:
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from LLM output: {content[:200]}...")
        return default

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the agent's task."""
        pass


class ResearchAgent(BaseAgent):
    """
    Research Agent
    Deep-dives into any topic and compiles comprehensive reports.
    """

    async def execute(
        self,
        topic: str,
        depth: str = "comprehensive",  # quick, moderate, comprehensive
        focus_areas: Optional[List[str]] = None,
        max_sections: int = 5,
    ) -> ResearchReport:
        """
        Research a topic and compile a report.

        Args:
            topic: Topic to research
            depth: Research depth level
            focus_areas: Specific areas to focus on
            max_sections: Maximum number of sections

        Returns:
            ResearchReport with findings
        """
        focus_prompt = ""
        if focus_areas:
            focus_prompt = f"\nFocus on these areas: {', '.join(focus_areas)}"

        depth_instructions = {
            "quick": "Provide a brief overview with key points only.",
            "moderate": "Provide a balanced report with main points and some detail.",
            "comprehensive": "Provide an in-depth analysis with detailed sections, examples, and recommendations.",
        }

        system_prompt = f"""You are an expert research analyst. Your task is to research the given topic and compile a comprehensive report.

{depth_instructions.get(depth, depth_instructions['moderate'])}
{focus_prompt}

Structure your response as JSON:
{{
    "summary": "<executive summary>",
    "sections": [
        {{"title": "<section title>", "content": "<detailed content>"}},
        ...
    ],
    "key_findings": ["<finding 1>", "<finding 2>", ...],
    "recommendations": ["<recommendation 1>", ...],
    "sources": [{{"title": "<source title>", "url": "<url if applicable>"}}]
}}

Limit to {max_sections} main sections."""

        try:
            content = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Research topic: {topic}",
                max_tokens=4000,
                temperature=0.7,
            )

            # Safely parse JSON from LLM output
            result = self._safe_parse_json(content, default={
                "summary": "Unable to parse research results",
                "sections": [],
                "sources": [],
                "key_findings": [],
                "recommendations": [],
            })

            return ResearchReport(
                topic=topic,
                summary=result.get("summary", ""),
                sections=result.get("sections", []),
                sources=result.get("sources", []),
                key_findings=result.get("key_findings", []),
                recommendations=result.get("recommendations", []),
                word_count=len(content.split()),
            )

        except Exception as e:
            logger.exception("agent_task_failed")
            return ResearchReport(
                topic=topic,
                summary="Research failed due to an internal error",
            )


class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent
    Answers questions about data and generates insights.
    """

    def _compute_column_stats(self, data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
        """Compute summary statistics for all columns in the dataset."""
        stats = {}
        for col in columns:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if not values:
                stats[col] = {"type": "empty", "count": 0}
                continue

            # Determine column type and compute appropriate stats
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass

            if len(numeric_values) > len(values) * 0.5:  # More than 50% numeric
                import statistics
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
                # Categorical column
                from collections import Counter
                value_counts = Counter(str(v) for v in values)
                top_values = value_counts.most_common(5)
                stats[col] = {
                    "type": "categorical",
                    "count": len(values),
                    "unique": len(value_counts),
                    "top_values": [{"value": v, "count": c} for v, c in top_values],
                }
        return stats

    def _stratified_sample(self, data: List[Dict[str, Any]], sample_size: int = 50) -> List[Dict[str, Any]]:
        """Get a stratified sample from the data to ensure representation."""
        if len(data) <= sample_size:
            return data

        # Take samples from beginning, middle, and end to capture distribution
        n = len(data)
        indices = set()

        # First 10 rows
        indices.update(range(min(10, n)))
        # Last 10 rows
        indices.update(range(max(0, n - 10), n))
        # Evenly spaced samples from the middle
        remaining = sample_size - len(indices)
        if remaining > 0:
            step = max(1, n // remaining)
            for i in range(0, n, step):
                indices.add(i)
                if len(indices) >= sample_size:
                    break

        return [data[i] for i in sorted(indices)][:sample_size]

    async def execute(
        self,
        question: str,
        data: List[Dict[str, Any]],
        data_description: Optional[str] = None,
        generate_charts: bool = True,
    ) -> DataAnalysisResult:
        """
        Analyze data and answer questions.

        Args:
            question: Question about the data
            data: Data to analyze
            data_description: Description of the data
            generate_charts: Whether to suggest charts

        Returns:
            DataAnalysisResult with analysis
        """
        import json

        # Get column info and compute full dataset statistics
        if data:
            columns = list(data[0].keys())
            column_info = f"Columns: {', '.join(columns)}"

            # Compute statistics from FULL dataset (not just sample)
            full_stats = self._compute_column_stats(data, columns)
            stats_summary = json.dumps(full_stats, indent=2, default=str)

            # Get stratified sample for detailed inspection
            sample = self._stratified_sample(data, sample_size=30)
            data_sample = json.dumps(sample, indent=2, default=str)
        else:
            column_info = "No data provided"
            stats_summary = "{}"
            data_sample = "[]"

        system_prompt = f"""You are an expert data analyst. Analyze the provided data and answer the question.

Data Description: {data_description or 'Not provided'}
{column_info}
Total rows: {len(data)}

IMPORTANT: The statistics below are computed from the FULL dataset, not just the sample.
Column Statistics (full dataset):
{stats_summary}

Provide your response as JSON:
{{
    "answer": "<direct answer to the question>",
    "data_summary": {{"key metrics": "..."}},
    "insights": ["<insight 1>", "<insight 2>", ...],
    "charts": [{{"type": "<chart type>", "title": "<title>", "x_column": "<col>", "y_columns": ["<col>"]}}],
    "sql_queries": ["<SQL query that would answer this>"],
    "confidence": <0.0-1.0>
}}"""

        try:
            content = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Data sample (stratified from full dataset):\n{data_sample}\n\nQuestion: {question}",
                max_tokens=2000,
                temperature=0.3,
            )

            # Safely parse JSON from LLM output
            result = self._safe_parse_json(content, default={
                "answer": "Unable to parse analysis results",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0.0,
            })

            return DataAnalysisResult(
                query=question,
                answer=result.get("answer", ""),
                data_summary=result.get("data_summary", {}),
                insights=result.get("insights", []),
                charts=result.get("charts", []) if generate_charts else [],
                sql_queries=result.get("sql_queries", []),
                confidence=result.get("confidence", 0.5),
            )

        except Exception as e:
            logger.exception("agent_task_failed")
            return DataAnalysisResult(
                query=question,
                answer="Analysis failed due to an internal error",
            )


class EmailDraftAgent(BaseAgent):
    """
    Email Draft Agent
    Composes email responses based on context and previous emails.
    """

    async def execute(
        self,
        context: str,
        purpose: str,
        tone: str = "professional",
        recipient_info: Optional[str] = None,
        previous_emails: Optional[List[str]] = None,
        include_subject: bool = True,
    ) -> EmailDraft:
        """
        Draft an email response.

        Args:
            context: Context for the email
            purpose: Purpose of the email
            tone: Desired tone (professional, friendly, formal, casual)
            recipient_info: Information about the recipient
            previous_emails: Previous emails in the thread
            include_subject: Whether to suggest a subject line

        Returns:
            EmailDraft with the composed email
        """
        previous_context = ""
        if previous_emails:
            previous_context = "\n\nPrevious emails in thread:\n" + "\n---\n".join(previous_emails[-3:])

        recipient_context = ""
        if recipient_info:
            recipient_context = f"\n\nRecipient information: {recipient_info}"

        system_prompt = f"""You are an expert email writer. Draft an email based on the context and purpose provided.

Tone: {tone}
{recipient_context}
{previous_context}

Provide your response as JSON:
{{
    "subject": "<email subject line>",
    "body": "<full email body>",
    "tone": "{tone}",
    "suggested_recipients": ["<email if mentioned>"],
    "attachments_suggested": ["<suggested attachment if relevant>"],
    "follow_up_actions": ["<action items from this email>"]
}}"""

        try:
            content = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Context: {context}\n\nPurpose: {purpose}",
                max_tokens=1500,
                temperature=0.7,
            )

            # Safely parse JSON from LLM output
            result = self._safe_parse_json(content, default={
                "subject": "",
                "body": "Unable to generate email draft",
                "tone": tone,
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            return EmailDraft(
                subject=result.get("subject", ""),
                body=result.get("body", ""),
                tone=result.get("tone", tone),
                suggested_recipients=result.get("suggested_recipients", []),
                attachments_suggested=result.get("attachments_suggested", []),
                follow_up_actions=result.get("follow_up_actions", []),
            )

        except Exception as e:
            logger.exception("agent_task_failed")
            return EmailDraft(
                subject="",
                body="Draft failed due to an internal error",
                tone=tone,
            )


class ContentRepurposingAgent(BaseAgent):
    """
    Content Repurposing Agent
    Transforms content from one format to multiple other formats.
    """

    async def execute(
        self,
        content: str,
        source_format: str,
        target_formats: List[str],
        preserve_key_points: bool = True,
        adapt_length: bool = True,
    ) -> RepurposedContent:
        """
        Repurpose content into multiple formats.

        Args:
            content: Original content
            source_format: Original format (article, report, transcript, etc.)
            target_formats: Target formats (tweet_thread, linkedin_post, blog_summary, slides, etc.)
            preserve_key_points: Ensure key points are preserved
            adapt_length: Adapt length for each format

        Returns:
            RepurposedContent with all versions
        """
        format_guidelines = {
            "tweet_thread": "Create a Twitter thread (max 280 chars per tweet, 5-10 tweets)",
            "linkedin_post": "Create a LinkedIn post (professional tone, 1300 chars max)",
            "blog_summary": "Create a blog-style summary (300-500 words)",
            "slides": "Create slide content (title + 3-5 bullet points per slide, max 10 slides)",
            "email_newsletter": "Create newsletter content (catchy subject, scannable body)",
            "video_script": "Create a video script (conversational, 2-3 minutes)",
            "infographic": "Create infographic copy (headline, key stats, takeaways)",
            "podcast_notes": "Create podcast show notes (summary, timestamps, links)",
            "press_release": "Create press release format (headline, lead, quotes)",
            "executive_summary": "Create executive summary (1 page, key decisions)",
        }

        outputs = []
        adaptations = []

        for target_format in target_formats:
            guidelines = format_guidelines.get(target_format, f"Create {target_format} format content")

            system_prompt = f"""You are a content repurposing expert. Transform the following {source_format} into {target_format} format.

Guidelines: {guidelines}
{'Preserve all key points and main ideas.' if preserve_key_points else ''}
{'Adapt the length appropriately for the format.' if adapt_length else ''}

Return ONLY the transformed content, no explanations."""

            try:
                transformed = self._call_llm(
                    system_prompt=system_prompt,
                    user_prompt=content,
                    max_tokens=2000,
                    temperature=0.7,
                )

                outputs.append({
                    "format": target_format,
                    "content": transformed,
                    "metadata": {
                        "word_count": len(transformed.split()),
                        "char_count": len(transformed),
                    }
                })

                adaptations.append(f"Converted to {target_format}")

            except Exception as e:
                logger.exception("agent_task_failed")
                outputs.append({
                    "format": target_format,
                    "content": "Conversion failed due to an internal error",
                    "metadata": {"error": True}
                })

        return RepurposedContent(
            original_format=source_format,
            outputs=outputs,
            adaptations_made=adaptations,
        )


class ProofreadingAgent(BaseAgent):
    """
    Proofreading Agent
    Comprehensive style and grammar checking.
    """

    async def execute(
        self,
        text: str,
        style_guide: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        preserve_voice: bool = True,
    ) -> ProofreadingResult:
        """
        Proofread and improve text.

        Args:
            text: Text to proofread
            style_guide: Style guide to follow (AP, Chicago, etc.)
            focus_areas: Specific areas to focus on
            preserve_voice: Preserve author's voice

        Returns:
            ProofreadingResult with corrections
        """
        style_context = f"\nFollow {style_guide} style guide." if style_guide else ""
        focus_context = f"\nFocus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        voice_context = "\nPreserve the author's unique voice while making corrections." if preserve_voice else ""

        system_prompt = f"""You are an expert editor and proofreader. Review the text for:
1. Grammar and spelling errors
2. Punctuation issues
3. Style and clarity improvements
4. Consistency issues
5. Readability enhancements
{style_context}{focus_context}{voice_context}

Provide your response as JSON:
{{
    "corrected_text": "<the improved text>",
    "issues_found": [
        {{"type": "<error type>", "original": "<original text>", "correction": "<corrected>", "explanation": "<why>"}}
    ],
    "style_suggestions": ["<suggestion 1>", ...],
    "readability_score": <0-100>,
    "reading_level": "<grade level>"
}}"""

        try:
            content = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=text,
                max_tokens=4000,
                temperature=0.3,
            )

            # Safely parse JSON from LLM output
            result = self._safe_parse_json(content, default={
                "corrected_text": text,
                "issues_found": [],
                "style_suggestions": [],
                "readability_score": 0,
                "reading_level": "",
            })

            return ProofreadingResult(
                original_text=text,
                corrected_text=result.get("corrected_text", text),
                issues_found=result.get("issues_found", []),
                style_suggestions=result.get("style_suggestions", []),
                readability_score=result.get("readability_score", 0),
                word_count=len(text.split()),
                reading_level=result.get("reading_level", ""),
            )

        except Exception as e:
            logger.exception("agent_task_failed")
            return ProofreadingResult(
                original_text=text,
                corrected_text=text,
                issues_found=[{"type": "error", "original": "", "correction": "", "explanation": "Review failed due to an internal error"}],
            )


class AgentService:
    """
    Central service for managing AI agents.
    """

    # Maximum number of completed tasks to keep in memory
    MAX_COMPLETED_TASKS = 100
    # Maximum age of completed tasks in seconds (1 hour)
    MAX_TASK_AGE_SECONDS = 3600

    def __init__(self):
        self._agents = {
            AgentType.RESEARCH: ResearchAgent(),
            AgentType.DATA_ANALYST: DataAnalystAgent(),
            AgentType.EMAIL_DRAFT: EmailDraftAgent(),
            AgentType.CONTENT_REPURPOSE: ContentRepurposingAgent(),
            AgentType.PROOFREADING: ProofreadingAgent(),
        }
        self._tasks: Dict[str, AgentTask] = {}
        # Legacy service is in-memory and used in both sync and async contexts.
        # Use a threading lock so callers can list tasks without having to await.
        self._tasks_lock = threading.RLock()

    def _cleanup_old_tasks(self) -> None:
        """Remove old completed tasks to prevent memory leaks.

        Must be called while holding self._tasks_lock.
        """
        now = datetime.now(timezone.utc)
        completed_tasks = [
            (task_id, task) for task_id, task in self._tasks.items()
            if task.status in (AgentStatus.COMPLETED, AgentStatus.FAILED)
        ]

        # Remove tasks older than MAX_TASK_AGE_SECONDS
        for task_id, task in completed_tasks:
            if task.completed_at:
                age_seconds = (now - task.completed_at).total_seconds()
                if age_seconds > self.MAX_TASK_AGE_SECONDS:
                    del self._tasks[task_id]

        # If still too many tasks, remove oldest completed ones
        completed_tasks = [
            (task_id, task) for task_id, task in self._tasks.items()
            if task.status in (AgentStatus.COMPLETED, AgentStatus.FAILED)
        ]
        if len(completed_tasks) > self.MAX_COMPLETED_TASKS:
            # Sort by completion time, oldest first
            sorted_tasks = sorted(
                completed_tasks,
                key=lambda x: x[1].completed_at or datetime.min.replace(tzinfo=timezone.utc)
            )
            # Remove oldest tasks until we're under the limit
            for task_id, _ in sorted_tasks[:len(completed_tasks) - self.MAX_COMPLETED_TASKS]:
                del self._tasks[task_id]

    async def run_agent(
        self,
        agent_type: AgentType,
        **kwargs,
    ) -> AgentTask:
        """
        Run an agent with the given parameters.

        Args:
            agent_type: Type of agent to run
            **kwargs: Agent-specific parameters

        Returns:
            AgentTask with results
        """
        with self._tasks_lock:
            # Clean up old tasks before adding new ones
            self._cleanup_old_tasks()

            task_id = hashlib.sha256(f"{agent_type}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

            task = AgentTask(
                task_id=task_id,
                agent_type=agent_type,
                input=kwargs,
                status=AgentStatus.RUNNING,
            )
            self._tasks[task_id] = task

        try:
            agent = self._agents.get(agent_type)
            if not agent:
                raise ValueError(f"Unknown agent type: {agent_type}")

            result = await agent.execute(**kwargs)
            with self._tasks_lock:
                task.result = result.model_dump() if hasattr(result, "model_dump") else result
                task.status = AgentStatus.COMPLETED

        except Exception as e:
            logger.exception("agent_task_failed")
            with self._tasks_lock:
                task.status = AgentStatus.FAILED
                task.error = "Task failed due to an internal error"

        task.completed_at = datetime.now(timezone.utc)
        return task

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    class _AwaitableList(list):
        """List that can also be awaited (returns itself).

        This preserves compatibility with older call sites that did `await service.list_tasks()`
        while allowing sync callers (including FastAPI route handlers) to use it directly.
        """

        def __await__(self):
            if False:  # pragma: no cover - makes this a generator
                yield None
            return self

    def list_tasks(self, agent_type: Optional[AgentType] = None, limit: int = 50) -> List[AgentTask]:
        """List recent tasks, optionally filtered by agent type."""
        with self._tasks_lock:
            tasks = list(self._tasks.values())
        if agent_type:
            tasks = [t for t in tasks if t.agent_type == agent_type]
        sorted_tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)[:limit]
        return self._AwaitableList(sorted_tasks)

    async def clear_completed_tasks(self) -> int:
        """Clear all completed and failed tasks. Returns count of cleared tasks."""
        with self._tasks_lock:
            to_remove = [
                task_id for task_id, task in self._tasks.items()
                if task.status in (AgentStatus.COMPLETED, AgentStatus.FAILED)
            ]
            for task_id in to_remove:
                del self._tasks[task_id]
        return len(to_remove)


# Singleton instances
agent_service = AgentService()

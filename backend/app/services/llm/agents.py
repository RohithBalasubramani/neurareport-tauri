# mypy: ignore-errors
"""
Multi-Agent Orchestration System.

Inspired by CrewAI, this module provides:
- Specialized agents for different tasks
- Agent coordination and task delegation
- Pipeline execution with state management
- Tool integration for agents
"""
from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from .client import LLMClient, get_llm_client
from .config import LLMConfig

logger = logging.getLogger("neura.llm.agents")


class AgentRole(str, Enum):
    """Predefined agent roles."""
    DOCUMENT_ANALYZER = "document_analyzer"
    DATA_EXTRACTOR = "data_extractor"
    SQL_GENERATOR = "sql_generator"
    CHART_SUGGESTER = "chart_suggester"
    TEMPLATE_MAPPER = "template_mapper"
    REPORT_GENERATOR = "report_generator"
    QUALITY_REVIEWER = "quality_reviewer"
    COORDINATOR = "coordinator"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    role: str
    goal: str
    backstory: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[str] = field(default_factory=list)
    allow_delegation: bool = False
    verbose: bool = False


@dataclass
class Task:
    """A task to be executed by an agent."""
    description: str
    agent_role: str
    expected_output: str
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    agent_role: str
    output: Any
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)


class Tool(ABC):
    """Base class for agent tools."""
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given arguments."""
        pass


class Agent:
    """
    An AI agent with a specific role and capabilities.

    Agents can:
    - Execute tasks based on their role
    - Use tools to accomplish tasks
    - Delegate to other agents (if allowed)
    """

    def __init__(
        self,
        config: AgentConfig,
        client: Optional[LLMClient] = None,
        tools: Optional[Dict[str, Tool]] = None,
    ):
        self.config = config
        self.client = client or get_llm_client()
        self.tools = tools or {}
        self._conversation_history: List[Dict[str, Any]] = []

    @property
    def role(self) -> str:
        return self.config.role

    def execute_task(
        self,
        task: Task,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """
        Execute a task and return the result.

        Args:
            task: The task to execute
            context: Additional context from previous tasks

        Returns:
            TaskResult with the execution outcome
        """
        start_time = time.time()
        task_id = f"{self.role}_{int(start_time)}"

        try:
            # Build the prompt
            prompt = self._build_task_prompt(task, context)

            # Execute the task
            response = self.client.complete(
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                model=self.config.model,
                description=f"agent_{self.role}_{task_id}",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            output = response["choices"][0]["message"]["content"]
            token_usage = response.get("usage", {})

            # Check if tool use is requested
            output = self._process_tool_calls(output, task)

            # Store in conversation history
            self._conversation_history.append({
                "task": task.description,
                "output": output,
            })

            execution_time = time.time() - start_time

            logger.info(
                "agent_task_complete",
                extra={
                    "event": "agent_task_complete",
                    "agent_role": self.role,
                    "task_id": task_id,
                    "execution_time": execution_time,
                }
            )

            return TaskResult(
                task_id=task_id,
                agent_role=self.role,
                output=output,
                success=True,
                execution_time=execution_time,
                token_usage=token_usage,
            )

        except Exception as e:
            logger.error(
                "agent_task_failed",
                extra={
                    "event": "agent_task_failed",
                    "agent_role": self.role,
                    "task_id": task_id,
                    "error": str(e),
                }
            )
            return TaskResult(
                task_id=task_id,
                agent_role=self.role,
                output=None,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        prompt = f"""You are a {self.config.role} agent.

GOAL: {self.config.goal}

BACKSTORY: {self.config.backstory}

GUIDELINES:
- Focus on your specific role and expertise
- Provide clear, structured outputs
- If you need to use a tool, indicate it clearly
- Be thorough but concise
"""

        if self.tools:
            prompt += "\n\nAVAILABLE TOOLS:\n"
            for name, tool in self.tools.items():
                prompt += f"- {name}: {tool.description}\n"
            prompt += "\nTo use a tool, respond with: TOOL_CALL: tool_name(arg1=value1, arg2=value2)"

        return prompt

    def _build_task_prompt(
        self,
        task: Task,
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build the task prompt."""
        prompt = f"""TASK: {task.description}

EXPECTED OUTPUT: {task.expected_output}
"""

        if task.context:
            prompt += f"\nTASK CONTEXT:\n{json.dumps(task.context, indent=2)}\n"

        if context:
            prompt += f"\nPREVIOUS RESULTS:\n{json.dumps(context, indent=2)}\n"

        return prompt

    def _process_tool_calls(self, output: str, task: Task) -> str:
        """Process any tool calls in the output."""
        import re

        tool_pattern = r"TOOL_CALL:\s*(\w+)\((.*?)\)"
        matches = re.findall(tool_pattern, output)

        for tool_name, args_str in matches:
            if tool_name in self.tools:
                try:
                    # Parse arguments
                    args = {}
                    if args_str:
                        for arg in args_str.split(","):
                            if "=" in arg:
                                key, value = arg.split("=", 1)
                                args[key.strip()] = value.strip().strip("'\"")

                    # Execute tool
                    result = self.tools[tool_name].execute(**args)

                    # Replace tool call with result
                    tool_call = f"TOOL_CALL: {tool_name}({args_str})"
                    output = output.replace(tool_call, f"TOOL_RESULT ({tool_name}): {result}")

                except Exception as e:
                    logger.warning(
                        "agent_tool_call_failed",
                        extra={
                            "tool": tool_name,
                            "error": str(e),
                        }
                    )

        return output


class Crew:
    """
    A crew of agents working together on tasks.

    Manages agent coordination and task execution flow.
    """

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        verbose: bool = False,
    ):
        self.agents = {agent.role: agent for agent in agents}
        self.tasks = tasks
        self.verbose = verbose
        self._results: Dict[str, TaskResult] = {}

    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start the crew's work on all tasks.

        Args:
            inputs: Initial inputs for the tasks

        Returns:
            Dict with all task results
        """
        context = inputs or {}

        logger.info(
            "crew_kickoff",
            extra={
                "event": "crew_kickoff",
                "num_agents": len(self.agents),
                "num_tasks": len(self.tasks),
            }
        )

        for task in self.tasks:
            # Check dependencies
            for dep in task.dependencies:
                if dep not in self._results or not self._results[dep].success:
                    logger.warning(
                        "crew_task_dependency_not_met",
                        extra={
                            "task": task.description[:50],
                            "dependency": dep,
                        }
                    )
                    continue

            # Get the agent for this task
            agent = self.agents.get(task.agent_role)
            if not agent:
                logger.error(
                    "crew_agent_not_found",
                    extra={
                        "agent_role": task.agent_role,
                        "available_agents": list(self.agents.keys()),
                    }
                )
                continue

            # Build context from previous results
            task_context = {**context}
            for dep in task.dependencies:
                if dep in self._results:
                    task_context[dep] = self._results[dep].output

            # Execute the task
            result = agent.execute_task(task, task_context)
            self._results[task.description[:50]] = result

            if result.success:
                context[task.description[:50]] = result.output

            if self.verbose:
                print(f"[{task.agent_role}] {task.description[:50]}: {'SUCCESS' if result.success else 'FAILED'}")

        return {
            "results": {k: v.output for k, v in self._results.items() if v.success},
            "errors": {k: v.error for k, v in self._results.items() if not v.success},
            "execution_summary": self._get_execution_summary(),
        }

    def _get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution."""
        total_time = sum(r.execution_time for r in self._results.values())
        total_tokens = sum(
            r.token_usage.get("total_tokens", 0)
            for r in self._results.values()
        )

        return {
            "total_tasks": len(self.tasks),
            "successful_tasks": sum(1 for r in self._results.values() if r.success),
            "failed_tasks": sum(1 for r in self._results.values() if not r.success),
            "total_execution_time": total_time,
            "total_tokens_used": total_tokens,
        }


# Predefined agents for NeuraReport

def create_document_analyzer_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a document analysis agent."""
    config = AgentConfig(
        role=AgentRole.DOCUMENT_ANALYZER.value,
        goal="Analyze documents to extract structure, content, and metadata",
        backstory="""You are an expert document analyst with years of experience
        analyzing various document types including PDFs, spreadsheets, and reports.
        You excel at understanding document structure, identifying key sections,
        and extracting meaningful information.""",
        temperature=0.3,
    )
    return Agent(config, client)


def create_data_extractor_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a data extraction agent."""
    config = AgentConfig(
        role=AgentRole.DATA_EXTRACTOR.value,
        goal="Extract structured data from documents accurately",
        backstory="""You are a meticulous data extraction specialist.
        You can identify tables, lists, and structured data in any format
        and convert them into clean, well-organized data structures.
        Accuracy is your top priority.""",
        temperature=0.2,
    )
    return Agent(config, client)


def create_sql_generator_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a SQL generation agent."""
    config = AgentConfig(
        role=AgentRole.SQL_GENERATOR.value,
        goal="Generate accurate and efficient SQL queries",
        backstory="""You are a database expert specializing in SQL query generation.
        You understand complex data relationships and can translate natural language
        requirements into precise SQL queries. You're proficient in DuckDB, SQLite,
        and standard SQL.""",
        temperature=0.1,
    )
    return Agent(config, client)


def create_chart_suggester_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a chart suggestion agent."""
    config = AgentConfig(
        role=AgentRole.CHART_SUGGESTER.value,
        goal="Suggest optimal visualizations for data",
        backstory="""You are a data visualization expert who understands
        how to present data effectively. You know when to use bar charts,
        line graphs, pie charts, and other visualizations based on the
        data characteristics and the story to be told.""",
        temperature=0.5,
    )
    return Agent(config, client)


def create_template_mapper_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a template mapping agent."""
    config = AgentConfig(
        role=AgentRole.TEMPLATE_MAPPER.value,
        goal="Map data fields to template placeholders accurately",
        backstory="""You are an expert at understanding document templates
        and mapping data fields to placeholders. You can identify patterns,
        handle edge cases, and ensure data is correctly positioned in reports.""",
        temperature=0.2,
    )
    return Agent(config, client)


def create_quality_reviewer_agent(client: Optional[LLMClient] = None) -> Agent:
    """Create a quality review agent."""
    config = AgentConfig(
        role=AgentRole.QUALITY_REVIEWER.value,
        goal="Review outputs for accuracy and quality",
        backstory="""You are a meticulous quality assurance specialist.
        You review work products for accuracy, completeness, and adherence
        to requirements. You catch errors others might miss.""",
        temperature=0.3,
    )
    return Agent(config, client)


# Pre-built crews for common workflows

def create_document_processing_crew(
    client: Optional[LLMClient] = None,
    verbose: bool = False,
) -> Crew:
    """Create a crew for document processing workflow."""
    agents = [
        create_document_analyzer_agent(client),
        create_data_extractor_agent(client),
        create_quality_reviewer_agent(client),
    ]

    tasks = [
        Task(
            description="Analyze the document structure and identify key sections",
            agent_role=AgentRole.DOCUMENT_ANALYZER.value,
            expected_output="JSON with document structure, sections, and content overview",
        ),
        Task(
            description="Extract all tables and structured data from the document",
            agent_role=AgentRole.DATA_EXTRACTOR.value,
            expected_output="JSON with extracted tables, their headers, and row data",
            dependencies=["Analyze the document structure and identify key sections"[:50]],
        ),
        Task(
            description="Review extracted data for accuracy and completeness",
            agent_role=AgentRole.QUALITY_REVIEWER.value,
            expected_output="Quality report with any issues found and suggestions",
            dependencies=["Extract all tables and structured data from the document"[:50]],
        ),
    ]

    return Crew(agents, tasks, verbose)


def create_report_generation_crew(
    client: Optional[LLMClient] = None,
    verbose: bool = False,
) -> Crew:
    """Create a crew for report generation workflow."""
    agents = [
        create_data_extractor_agent(client),
        create_sql_generator_agent(client),
        create_template_mapper_agent(client),
        create_chart_suggester_agent(client),
    ]

    tasks = [
        Task(
            description="Extract and prepare data for the report",
            agent_role=AgentRole.DATA_EXTRACTOR.value,
            expected_output="Clean, structured data ready for report generation",
        ),
        Task(
            description="Generate SQL queries for data retrieval",
            agent_role=AgentRole.SQL_GENERATOR.value,
            expected_output="DuckDB-compatible SQL queries for report data",
            dependencies=["Extract and prepare data for the report"[:50]],
        ),
        Task(
            description="Map data fields to template placeholders",
            agent_role=AgentRole.TEMPLATE_MAPPER.value,
            expected_output="Field mapping configuration JSON",
            dependencies=["Extract and prepare data for the report"[:50]],
        ),
        Task(
            description="Suggest visualizations for the report data",
            agent_role=AgentRole.CHART_SUGGESTER.value,
            expected_output="Chart recommendations with configurations",
            dependencies=["Extract and prepare data for the report"[:50]],
        ),
    ]

    return Crew(agents, tasks, verbose)

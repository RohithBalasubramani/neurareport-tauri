"""
Base team abstraction with AutoGen RoundRobinGroupChat and Crew fallback.

Supports AutoGen 0.4 (autogen-agentchat), AutoGen 0.2/AG2, and a pure-Python
fallback using the internal Crew orchestrator.
"""
from __future__ import annotations

import asyncio
import logging
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..llm.agents import Agent, AgentConfig, Crew, Task, TaskResult
from ..llm.client import LLMClient, get_llm_client

logger = logging.getLogger("neura.teams.base")

# ---------------------------------------------------------------------------
# AutoGen optional import (0.4 -> 0.2 -> unavailable)
# ---------------------------------------------------------------------------

_autogen_available = False
_autogen_version = "none"  # "0.4" | "0.2" | "none"

try:
    from autogen_agentchat.agents import BaseChatAgent  # type: ignore
    from autogen_agentchat.base import Response as AgentResponse  # type: ignore
    from autogen_agentchat.messages import TextMessage  # type: ignore
    from autogen_agentchat.conditions import MaxMessageTermination  # type: ignore
    from autogen_agentchat.teams import RoundRobinGroupChat  # type: ignore
    from autogen_core import CancellationToken  # type: ignore

    _autogen_available = True
    _autogen_version = "0.4"
    logger.debug("AutoGen 0.4 (autogen-agentchat) available for teams")
except ImportError:
    try:
        import autogen  # type: ignore  # noqa: F811

        _autogen_available = True
        _autogen_version = "0.2"
        logger.debug("AutoGen 0.2 available for teams")
    except ImportError:
        try:
            import pyautogen as autogen  # type: ignore  # noqa: F811

            _autogen_available = True
            _autogen_version = "0.2"
            logger.debug("pyautogen available for teams")
        except ImportError:
            logger.debug("AutoGen not available; teams will use Crew fallback")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class TeamConfig:
    """Configuration for a multi-agent team."""

    name: str
    max_rounds: int = 10
    timeout: float = 60.0
    use_autogen: bool = True
    verbose: bool = False

# ---------------------------------------------------------------------------
# Base Team
# ---------------------------------------------------------------------------


class BaseTeam(ABC):
    """Abstract base class for multi-agent teams.

    Concrete subclasses define agents and tasks; execution is handled
    automatically via AutoGen (if available) or the internal Crew fallback.
    """

    def __init__(
        self,
        config: TeamConfig,
        client: Optional[LLMClient] = None,
    ) -> None:
        self.config = config
        self._client = client  # lazily resolved via property

    # -- lazy LLM client ---------------------------------------------------

    @property
    def client(self) -> LLMClient:
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    # -- abstract hooks ----------------------------------------------------

    @abstractmethod
    def _define_agents(self) -> List[AgentConfig]:
        """Return the list of agent configurations for this team."""
        ...

    @abstractmethod
    def _define_tasks(self, inputs: Dict[str, Any]) -> List[Task]:
        """Return ordered tasks given the run inputs."""
        ...

    # -- public entry point ------------------------------------------------

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the team workflow.

        Tries AutoGen first (when ``config.use_autogen`` is *True* and the
        library is installed), otherwise falls back to the internal ``Crew``
        orchestrator.
        """
        start = time.time()
        logger.info(
            "team_run_start",
            extra={
                "event": "team_run_start",
                "team": self.config.name,
                "use_autogen": self.config.use_autogen,
                "autogen_available": _autogen_available,
            },
        )

        try:
            if self.config.use_autogen and _autogen_available:
                result = self._run_with_autogen(inputs)
            else:
                result = self._run_with_crew(inputs)
        except Exception as exc:
            logger.error(
                "team_run_failed",
                extra={
                    "event": "team_run_failed",
                    "team": self.config.name,
                    "error": str(exc),
                },
            )
            raise

        elapsed = time.time() - start
        logger.info(
            "team_run_complete",
            extra={
                "event": "team_run_complete",
                "team": self.config.name,
                "elapsed_s": round(elapsed, 2),
            },
        )
        result.setdefault("execution_summary", {})["total_wall_time"] = round(elapsed, 2)
        return result

    # -- AutoGen execution -------------------------------------------------

    def _run_with_autogen(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute via AutoGen group-chat."""
        agent_configs = self._define_agents()
        tasks = self._define_tasks(inputs)

        if _autogen_version == "0.4":
            return self._run_autogen_04(agent_configs, tasks, inputs)
        return self._run_autogen_02(agent_configs, tasks, inputs)

    # -- AutoGen 0.4 -------------------------------------------------------

    def _run_autogen_04(
        self,
        agent_configs: List[AgentConfig],
        tasks: List[Task],
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """AutoGen 0.4 execution using RoundRobinGroupChat."""

        # Build internal Agent objects keyed by role
        agents_by_role: Dict[str, Agent] = {
            cfg.role: Agent(cfg, self.client)
            for cfg in agent_configs
        }

        # -- nested wrapper class ------------------------------------------

        class _WrappedAgent(BaseChatAgent):  # type: ignore[misc]
            """Thin AutoGen 0.4 wrapper around our Agent."""

            def __init__(self, inner: Agent, task: Task) -> None:
                super().__init__(inner.role, description=inner.config.goal)
                self._inner = inner
                self._task = task

            @property
            def produced_message_types(self) -> List[type]:
                return [TextMessage]

            async def on_messages(
                self,
                messages: Sequence[Any],
                cancellation_token: Any,
            ) -> Any:
                # Build context from prior messages
                context: Dict[str, Any] = dict(inputs)
                for msg in messages:
                    text = getattr(msg, "content", str(msg))
                    source = getattr(msg, "source", "unknown")
                    context[source] = text

                result: TaskResult = self._inner.execute_task(self._task, context)
                output_text = str(result.output) if result.success else f"ERROR: {result.error}"
                return AgentResponse(
                    chat_message=TextMessage(
                        content=output_text,
                        source=self._inner.role,
                    )
                )

            async def on_reset(self, cancellation_token: Any) -> None:
                pass

        # Build wrapped agents in task order
        wrapped: List[_WrappedAgent] = []
        for task in tasks:
            inner = agents_by_role.get(task.agent_role)
            if inner is None:
                logger.warning(
                    "team_agent_missing",
                    extra={"event": "team_agent_missing", "role": task.agent_role},
                )
                continue
            wrapped.append(_WrappedAgent(inner, task))

        termination = MaxMessageTermination(max_messages=self.config.max_rounds)
        team = RoundRobinGroupChat(wrapped, termination_condition=termination)

        # Run the async group-chat in a sync context
        initial_message = TextMessage(
            content=str(inputs),
            source="user",
        )

        loop = _get_or_create_event_loop()
        token = CancellationToken()
        chat_result = loop.run_until_complete(
            team.run(task=initial_message, cancellation_token=token)
        )

        # Collect results
        results: Dict[str, Any] = {}
        errors: Dict[str, Any] = {}
        for msg in getattr(chat_result, "messages", []):
            source = getattr(msg, "source", "unknown")
            content = getattr(msg, "content", "")
            if source != "user":
                if content.startswith("ERROR:"):
                    errors[source] = content
                else:
                    results[source] = content

        return {
            "results": results,
            "errors": errors,
            "execution_summary": {
                "backend": "autogen_0.4",
                "rounds": len(getattr(chat_result, "messages", [])),
            },
        }

    # -- AutoGen 0.2 -------------------------------------------------------

    def _run_autogen_02(
        self,
        agent_configs: List[AgentConfig],
        tasks: List[Task],
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """AutoGen 0.2 / AG2 execution using ConversableAgent + GroupChat."""

        agents_by_role: Dict[str, Agent] = {
            cfg.role: Agent(cfg, self.client)
            for cfg in agent_configs
        }

        ag2_agents = []
        task_map: Dict[str, Task] = {}

        for task in tasks:
            inner = agents_by_role.get(task.agent_role)
            if inner is None:
                continue
            task_map[inner.role] = task

            def _make_reply_func(agent_inner: Agent, agent_task: Task):
                def _reply(recipient: Any, messages: Any, sender: Any, config: Any) -> tuple:
                    context: Dict[str, Any] = dict(inputs)
                    if isinstance(messages, list) and messages:
                        last = messages[-1]
                        if isinstance(last, dict):
                            context["last_message"] = last.get("content", "")
                    result = agent_inner.execute_task(agent_task, context)
                    output = str(result.output) if result.success else f"ERROR: {result.error}"
                    return True, output
                return _reply

            conv_agent = autogen.ConversableAgent(  # type: ignore[attr-defined]
                name=inner.role,
                llm_config=False,
                human_input_mode="NEVER",
            )
            conv_agent.register_reply([autogen.Agent], _make_reply_func(inner, task))  # type: ignore[attr-defined]
            ag2_agents.append(conv_agent)

        group_chat = autogen.GroupChat(  # type: ignore[attr-defined]
            agents=ag2_agents,
            messages=[],
            max_round=self.config.max_rounds,
        )
        manager = autogen.GroupChatManager(  # type: ignore[attr-defined]
            groupchat=group_chat,
            llm_config=False,
        )

        # Initiate chat from the first agent
        if ag2_agents:
            ag2_agents[0].initiate_chat(manager, message=str(inputs))

        results: Dict[str, Any] = {}
        errors: Dict[str, Any] = {}
        for msg in group_chat.messages:
            name = msg.get("name", msg.get("role", "unknown"))
            content = msg.get("content", "")
            if name != "user":
                if isinstance(content, str) and content.startswith("ERROR:"):
                    errors[name] = content
                else:
                    results[name] = content

        return {
            "results": results,
            "errors": errors,
            "execution_summary": {
                "backend": "autogen_0.2",
                "rounds": len(group_chat.messages),
            },
        }

    # -- Crew fallback -----------------------------------------------------

    def _run_with_crew(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute via the internal Crew orchestrator (pure-Python)."""
        agent_configs = self._define_agents()
        tasks = self._define_tasks(inputs)

        agents = [Agent(cfg, self.client) for cfg in agent_configs]
        crew = Crew(agents, tasks, verbose=self.config.verbose)

        result = crew.kickoff(inputs)
        result.setdefault("execution_summary", {})["backend"] = "crew_fallback"
        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Return the running event loop or create a new one."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We are already inside an async context; create a new loop in a
        # background thread so we can call run_until_complete.
        result_holder: Dict[str, Any] = {}
        exc_holder: Dict[str, BaseException] = {}

        def _run_in_thread() -> None:
            new_loop = asyncio.new_event_loop()
            result_holder["loop"] = new_loop

        t = threading.Thread(target=_run_in_thread, daemon=True)
        t.start()
        t.join(timeout=1.0)
        return result_holder.get("loop", asyncio.new_event_loop())

    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

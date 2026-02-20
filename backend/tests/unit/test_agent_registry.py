"""Tests for the agent registry with dynamic discovery."""
import pytest
from backend.app.services.agents.agent_registry import (
    AgentRegistry,
    register_agent,
    get_agent_registry,
)


class DummyAgent:
    """A test agent for registration."""
    def execute(self, task):
        return {"result": "done"}


class TestAgentRegistry:
    """Test agent registration and discovery."""

    def setup_method(self):
        self.registry = AgentRegistry()

    def test_register_and_get(self):
        self.registry.register("test_agent", DummyAgent)
        agent = self.registry.get("test_agent")
        assert agent is not None
        assert isinstance(agent, DummyAgent)

    def test_get_nonexistent(self):
        agent = self.registry.get("nonexistent")
        assert agent is None

    def test_get_descriptor(self):
        self.registry.register("test_agent", DummyAgent, version="2.0", capabilities=["research"])
        desc = self.registry.get_descriptor("test_agent")
        assert desc is not None
        assert desc.version == "2.0"
        assert "research" in desc.capabilities

    def test_find_by_capability(self):
        self.registry.register("agent_a", DummyAgent, capabilities=["research", "analysis"])
        self.registry.register("agent_b", DummyAgent, capabilities=["writing"])
        found = self.registry.find_by_capability("research")
        assert len(found) == 1
        assert found[0].name == "agent_a"

    def test_list_agents(self):
        self.registry.register("agent_a", DummyAgent)
        self.registry.register("agent_b", DummyAgent)
        agents = self.registry.list_agents()
        assert len(agents) == 2
        names = [a["name"] for a in agents]
        assert "agent_a" in names
        assert "agent_b" in names

    def test_singleton_instance_caching(self):
        self.registry.register("cached", DummyAgent)
        instance1 = self.registry.get("cached")
        instance2 = self.registry.get("cached")
        assert instance1 is instance2

    def test_thread_safety(self):
        import threading

        errors = []

        def register_agents(start):
            try:
                for i in range(10):
                    self.registry.register(f"agent_{start}_{i}", DummyAgent)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_agents, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(self.registry.list_agents()) == 50


class TestRegisterDecorator:
    """Test the @register_agent decorator."""

    def test_decorator_registers_class(self):
        @register_agent(name="decorated_agent", version="1.0", capabilities=["test"])
        class DecoratedAgent:
            def execute(self):
                return "decorated"

        registry = get_agent_registry()
        desc = registry.get_descriptor("decorated_agent")
        assert desc is not None
        assert desc.version == "1.0"

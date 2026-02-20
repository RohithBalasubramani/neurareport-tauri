"""Tests for the prompt registry and versioning system."""
import pytest
from backend.app.services.prompts.prompt_registry import (
    PromptRegistry,
    PromptEntry,
    PromptVersion,
)


class TestPromptRegistry:
    """Test prompt registration and rendering."""

    def setup_method(self):
        self.registry = PromptRegistry(prompts_dir="/nonexistent")

    def test_register_and_get(self):
        self.registry.register(
            "test_prompt",
            "Hello {{ name }}!",
            version="v1",
            category="test",
        )
        entry = self.registry.get("test_prompt")
        assert entry is not None
        assert entry.name == "test_prompt"
        assert entry.active_version == "v1"

    def test_render_template(self):
        self.registry.register("greet", "Hello {{ name }}!", version="v1")
        result = self.registry.render("greet", name="World")
        assert result == "Hello World!"

    def test_multiple_versions(self):
        self.registry.register("prompt", "V1: {{ text }}", version="v1")
        self.registry.register("prompt", "V2: {{ text }}", version="v2")
        entry = self.registry.get("prompt")
        assert "v1" in entry.versions
        assert "v2" in entry.versions

    def test_render_specific_version(self):
        self.registry.register("prompt", "V1: {{ x }}", version="v1")
        self.registry.register("prompt", "V2: {{ x }}", version="v2")
        result = self.registry.render("prompt", version="v2", x="test")
        assert result == "V2: test"

    def test_render_nonexistent_raises(self):
        with pytest.raises(KeyError):
            self.registry.render("nonexistent")

    def test_list_prompts(self):
        self.registry.register("a_prompt", "template a", category="cat_a")
        self.registry.register("b_prompt", "template b", category="cat_b")
        prompts = self.registry.list_prompts()
        assert len(prompts) == 2
        assert prompts[0]["name"] == "a_prompt"
        assert prompts[1]["name"] == "b_prompt"

    def test_load_from_nonexistent_directory(self):
        count = self.registry.load_from_directory("/definitely/not/a/path")
        assert count == 0


class TestPromptVersion:
    """Test individual prompt version rendering."""

    def test_render_simple(self):
        pv = PromptVersion(version="v1", template="Hello {{ who }}!")
        assert pv.render(who="World") == "Hello World!"

    def test_render_with_metadata(self):
        pv = PromptVersion(
            version="v1",
            template="Use model {{ model }}",
            model="gpt-4o",
            temperature=0.5,
        )
        assert pv.model == "gpt-4o"
        assert pv.temperature == 0.5

"""
Prompt versioning and registry service.

Stores prompts as YAML templates with:
- Version tracking and rollback
- Jinja2 template rendering
- A/B testing support via variant weights
- Runtime prompt serving to agents

Based on: bigscience-workshop/promptsource + promptslab/Promptify patterns.
"""
from __future__ import annotations
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml
from jinja2 import Template

logger = logging.getLogger("neura.prompts.registry")


@dataclass
class PromptVersion:
    """A single version of a prompt template."""
    version: str
    template: str
    description: str = ""
    model: str = "sonnet"
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """Render the prompt template with variables."""
        return Template(self.template).render(**kwargs)


@dataclass
class PromptEntry:
    """A prompt with multiple versions."""
    name: str
    category: str
    description: str = ""
    versions: dict[str, PromptVersion] = field(default_factory=dict)
    active_version: str = "v1"

    @property
    def active(self) -> Optional[PromptVersion]:
        return self.versions.get(self.active_version)

    def render(self, version: Optional[str] = None, **kwargs) -> str:
        """Render the active (or specified) version of the prompt."""
        v = self.versions.get(version or self.active_version)
        if v is None:
            raise ValueError(f"Prompt version '{version or self.active_version}' not found for '{self.name}'")
        return v.render(**kwargs)


class PromptRegistry:
    """
    Central registry for versioned prompt templates.

    Loads prompts from YAML files in a directory structure:
        prompts/
            analysis/
                document_analysis.yaml
                chart_suggestion.yaml
            generation/
                report_generation.yaml
            agents/
                research.yaml
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        self._prompts: dict[str, PromptEntry] = {}
        self._prompts_dir = prompts_dir or str(
            Path(__file__).parent / "registry"
        )

    def load_from_directory(self, directory: Optional[str] = None) -> int:
        """Load all prompt YAML files from the directory tree."""
        base = Path(directory or self._prompts_dir)
        if not base.exists():
            logger.warning("prompts_dir_missing", extra={"event": "prompts_dir_missing", "path": str(base)})
            return 0

        count = 0
        for yaml_file in base.rglob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    continue

                name = data.get("name", yaml_file.stem)
                category = data.get("category", yaml_file.parent.name)

                entry = PromptEntry(
                    name=name,
                    category=category,
                    description=data.get("description", ""),
                    active_version=data.get("active_version", "v1"),
                )

                for ver_key, ver_data in data.get("versions", {}).items():
                    entry.versions[ver_key] = PromptVersion(
                        version=ver_key,
                        template=ver_data.get("template", ""),
                        description=ver_data.get("description", ""),
                        model=ver_data.get("model", "sonnet"),
                        temperature=ver_data.get("temperature", 0.7),
                        max_tokens=ver_data.get("max_tokens", 1024),
                        metadata=ver_data.get("metadata", {}),
                    )

                self._prompts[name] = entry
                count += 1
            except Exception as exc:
                logger.warning("prompt_load_failed", extra={"event": "prompt_load_failed", "file": str(yaml_file), "error": str(exc)})

        logger.info("prompts_loaded", extra={"event": "prompts_loaded", "count": count})
        return count

    def register(self, name: str, template: str, version: str = "v1", **kwargs) -> None:
        """Register a prompt programmatically."""
        if name not in self._prompts:
            self._prompts[name] = PromptEntry(name=name, category=kwargs.get("category", "default"))
        self._prompts[name].versions[version] = PromptVersion(
            version=version, template=template, **{k: v for k, v in kwargs.items() if k != "category"},
        )
        if len(self._prompts[name].versions) == 1:
            self._prompts[name].active_version = version

    def get(self, name: str) -> Optional[PromptEntry]:
        return self._prompts.get(name)

    def render(self, name: str, version: Optional[str] = None, **kwargs) -> str:
        """Render a prompt by name."""
        entry = self._prompts.get(name)
        if entry is None:
            raise KeyError(f"Prompt '{name}' not found in registry")
        return entry.render(version=version, **kwargs)

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all registered prompts."""
        return [
            {
                "name": e.name,
                "category": e.category,
                "description": e.description,
                "active_version": e.active_version,
                "versions": list(e.versions.keys()),
            }
            for e in sorted(self._prompts.values(), key=lambda e: e.name)
        ]


_registry: Optional[PromptRegistry] = None


def get_prompt_registry() -> PromptRegistry:
    """Get or create the singleton prompt registry."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
        _registry.load_from_directory()
    return _registry

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from backend.app.utils.strategies import StrategyRegistry


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "template"


@dataclass
class TemplateKindStrategy:
    kind: str
    base_dir: Path

    def generate_id(self, hint: str | None) -> str:
        name = _slugify(hint or "template")
        return f"{name}-{uuid.uuid4().hex[:6]}-{self.kind}"

    def target_dir(self, template_id: str) -> Path:
        return (self.base_dir / template_id).resolve()

    def ensure_target_dir(self, template_id: str) -> Path:
        tdir = self.target_dir(template_id)
        tdir.mkdir(parents=True, exist_ok=True)
        return tdir


def build_template_kind_registry(pdf_root: Path, excel_root: Path) -> StrategyRegistry[TemplateKindStrategy]:
    registry: StrategyRegistry[TemplateKindStrategy] = StrategyRegistry(
        default_factory=lambda: TemplateKindStrategy(kind="pdf", base_dir=pdf_root)
    )
    registry.register("pdf", TemplateKindStrategy(kind="pdf", base_dir=pdf_root))
    registry.register("excel", TemplateKindStrategy(kind="excel", base_dir=excel_root))
    return registry

from __future__ import annotations

import logging
from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Optional

from backend.app.utils.strategies import StrategyRegistry
from backend.app.services.reports.docx_export import html_file_to_docx, pdf_file_to_docx
from backend.app.services.reports.xlsx_export import html_file_to_xlsx
from backend.app.services.utils.mailer import send_report_email

logger = logging.getLogger("neura.reports.strategies")


@dataclass
class RenderArtifacts:
    docx_path: Optional[Path]
    xlsx_path: Optional[Path]


class RenderStrategy:
    def render_docx(self, html_path: Path, pdf_path: Optional[Path], dest_tmp: Path, *, landscape: bool, font_scale: Optional[float]) -> Optional[Path]:
        if pdf_path and pdf_path.exists():
            try:
                pdf_result = pdf_file_to_docx(pdf_path, dest_tmp)
            except Exception:
                logger.exception("docx_pdf_convert_failed")
            else:
                if pdf_result:
                    return pdf_result
        try:
            api_mod = importlib.import_module("backend.api")
            html_to_docx = getattr(api_mod, "html_file_to_docx", html_file_to_docx)
        except Exception:
            html_to_docx = html_file_to_docx
        return html_to_docx(html_path, dest_tmp, landscape=landscape, body_font_scale=font_scale)

    def render_xlsx(self, html_path: Path, dest_tmp: Path) -> Optional[Path]:
        try:
            api_mod = importlib.import_module("backend.api")
            html_to_xlsx = getattr(api_mod, "html_file_to_xlsx", html_file_to_xlsx)
        except Exception:
            html_to_xlsx = html_file_to_xlsx
        return html_to_xlsx(html_path, dest_tmp)


class NotificationStrategy:
    def send(self, *, recipients: list[str], subject: str, body: str, attachments: list[Path]) -> bool:
        return send_report_email(
            to_addresses=recipients,
            subject=subject,
            body=body,
            attachments=attachments,
        )


def build_render_strategy_registry() -> StrategyRegistry[RenderStrategy]:
    registry: StrategyRegistry[RenderStrategy] = StrategyRegistry(default_factory=RenderStrategy)
    registry.register("pdf", RenderStrategy())
    registry.register("excel", RenderStrategy())
    return registry


def build_notification_strategy_registry() -> StrategyRegistry[NotificationStrategy]:
    registry: StrategyRegistry[NotificationStrategy] = StrategyRegistry(default_factory=NotificationStrategy)
    registry.register("email", NotificationStrategy())
    return registry

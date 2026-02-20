from __future__ import annotations

import logging
import os

from fastapi import HTTPException

from backend.app.api.generate.chart_suggest_routes import build_chart_suggest_router  # ARCH-EXC-003
from backend.app.api.generate.discover_routes import build_discover_router  # ARCH-EXC-003
from backend.app.api.generate.saved_charts_routes import build_saved_charts_router  # ARCH-EXC-003
from backend.app.schemas.generate.reports import DiscoverPayload
from backend.app.services.generate.chart_suggestions_service import suggest_charts as suggest_charts_service
from backend.app.services.generate.discovery_service import discover_reports as discover_reports_service
from backend.app.services.prompts.llm_prompts_charts import (
    CHART_SUGGEST_PROMPT_VERSION,
    build_chart_suggestions_prompt,
)
from backend.app.services.prompts.llm_prompts import PROMPT_VERSION, PROMPT_VERSION_3_5, PROMPT_VERSION_4
from backend.app.services.contract.ContractBuilderV2 import load_contract_v2
from backend.app.repositories.state import store as state_store_module
from backend.app.services.utils import call_chat_completion, get_correlation_id, strip_code_fences
from backend.app.services.utils.artifacts import load_manifest
from backend.app.services.reports.discovery import discover_batches_and_counts
from backend.app.services.reports.discovery_excel import discover_batches_and_counts as discover_batches_and_counts_excel
from backend.app.services.reports.discovery_metrics import build_batch_field_catalog_and_stats, build_batch_metrics
from backend.app.services.templates.TemplateVerify import get_openai_client
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.schedule_utils import clean_key_values
from backend.legacy.utils.template_utils import manifest_endpoint, normalize_template_id, template_dir

_build_sample_data_rows = lambda batches, metadata=None, limit=100: build_batch_metrics(  # noqa: E731
    batches,
    metadata or {},
    limit=limit,
)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


def _state_store():
    return state_store_module.state_store


def _ensure_template_exists(template_id: str) -> tuple[str, dict]:
    normalized = normalize_template_id(template_id)
    record = _state_store().get_template_record(normalized)
    if not record:
        raise HTTPException(status_code=404, detail="template_not_found")
    return normalized, record


def build_feature_routers():
    logger = logging.getLogger("neura.api")
    saved_charts_router = build_saved_charts_router(_ensure_template_exists, normalize_template_id)

    chart_suggest_router = build_chart_suggest_router(
        template_dir_fn=template_dir,
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_pdf_fn=discover_batches_and_counts,
        discover_excel_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_metrics_fn=build_batch_metrics,
        build_prompt_fn=build_chart_suggestions_prompt,
        call_chat_completion_fn=lambda **kwargs: call_chat_completion(
            get_openai_client(), **kwargs, description=CHART_SUGGEST_PROMPT_VERSION
        ),
        model=DEFAULT_MODEL,
        strip_code_fences_fn=strip_code_fences,
        get_correlation_id_fn=get_correlation_id,
        logger=logger,
    )

    discover_router = build_discover_router(
        template_dir_fn=template_dir,
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_pdf_fn=discover_batches_and_counts,
        discover_excel_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_batch_metrics_fn=build_batch_metrics,
        load_manifest_fn=load_manifest,
        manifest_endpoint_fn_pdf=lambda tpl_id, kind="pdf": manifest_endpoint(tpl_id, kind=kind),
        manifest_endpoint_fn_excel=lambda tpl_id, kind="excel": manifest_endpoint(tpl_id, kind=kind),
        logger=logger,
    )

    return saved_charts_router, chart_suggest_router, discover_router


__all__ = [
    "build_feature_routers",
    "DiscoverPayload",
    "discover_reports_service",
    "PROMPT_VERSION",
    "PROMPT_VERSION_3_5",
    "PROMPT_VERSION_4",
    "suggest_charts_service",
]

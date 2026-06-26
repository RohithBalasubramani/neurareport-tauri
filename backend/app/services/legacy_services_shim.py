"""
Compatibility shim: maps V2's legacy_services imports to prodo's actual locations.
"""
# Template functions
from backend.legacy.services.template_service import verify_template, verify_excel
from backend.legacy.services.file_service.edit import (
    chat_template_edit, chat_template_create,
    apply_chat_template_edit, create_template_from_chat,
    _run_template_chat_llm,
)
from backend.legacy.services.file_service.generator import generator_assets
from backend.legacy.services.mapping.preview import run_mapping_preview
from backend.legacy.services.mapping.approve import run_mapping_approve
from backend.legacy.services.mapping.corrections import run_corrections_preview
from backend.legacy.schemas.template_schema import (
    TemplateChatPayload, TemplateChatMessage,
    MappingPayload, CorrectionsPreviewPayload,
    GeneratorAssetsPayload, RunPayload,
)
from backend.legacy.services.file_service.verify import template_dir
from backend.app.services.utils import get_correlation_id

# DB path helper
import os
from pathlib import Path

def db_path_from_payload_or_default(connection_id=None):
    """Resolve DB path from connection or env."""
    from backend.app.repositories import resolve_db_path
    if connection_id:
        return resolve_db_path(connection_id)
    env_db = os.getenv("NR_DEFAULT_DB") or os.getenv("DB_PATH")
    if env_db:
        return Path(env_db)
    return None

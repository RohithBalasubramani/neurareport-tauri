from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class TemplateManualEditPayload(BaseModel):
    html: str


class TemplateAiEditPayload(BaseModel):
    instructions: str
    html: Optional[str] = None


class MappingPayload(BaseModel):
    mapping: dict[str, str]
    connection_id: Optional[str] = None
    user_values_text: Optional[str] = None
    user_instructions: Optional[str] = None
    dialect_hint: Optional[str] = None
    catalog_allowlist: Optional[list[str]] = None
    params_spec: Optional[list[str]] = None
    sample_params: Optional[dict[str, Any]] = None
    generator_dialect: Optional[str] = None
    force_generator_rebuild: bool = False
    keys: Optional[list[str]] = None

    model_config = ConfigDict(extra="allow")


class GeneratorAssetsPayload(BaseModel):
    step4_output: Optional[dict[str, Any]] = None
    contract: Optional[dict[str, Any]] = None
    overview_md: Optional[str] = None
    final_template_html: Optional[str] = None
    reference_pdf_image: Optional[str] = None
    catalog: Optional[list[str]] = None
    dialect: Optional[str] = "duckdb"
    params: Optional[list[str]] = None
    sample_params: Optional[dict[str, Any]] = None
    force_rebuild: bool = False
    key_tokens: Optional[list[str]] = None

    model_config = ConfigDict(extra="allow")


class CorrectionsPreviewPayload(BaseModel):
    user_input: Optional[str] = ""
    page: int = 1
    mapping_override: Optional[dict[str, Any]] = None
    sample_tokens: Optional[list[str]] = None
    model_selector: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class TemplateRecommendPayload(BaseModel):
    requirement: str
    kind: Optional[str] = None
    domain: Optional[str] = None
    kinds: Optional[list[str]] = None
    domains: Optional[list[str]] = None
    schema_snapshot: Optional[dict[str, Any]] = None
    tables: Optional[list[str]] = None

    model_config = ConfigDict(extra="allow")


class TemplateRecommendation(BaseModel):
    template: dict[str, Any]
    explanation: str
    score: float


class TemplateRecommendResponse(BaseModel):
    recommendations: list[TemplateRecommendation]


class LastUsedPayload(BaseModel):
    connection_id: Optional[str] = None
    template_id: Optional[str] = None


class TemplateUpdatePayload(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class TemplateChatMessage(BaseModel):
    """A single message in the template editing chat conversation."""
    role: str  # 'user' | 'assistant'
    content: str


class TemplateChatPayload(BaseModel):
    """Payload for conversational template editing."""
    messages: list[TemplateChatMessage]
    html: Optional[str] = None  # Current HTML state (optional, uses saved if not provided)

    model_config = ConfigDict(extra="allow")


class TemplateChatResponse(BaseModel):
    """Response from conversational template editing."""
    message: str  # Assistant's response message
    ready_to_apply: bool  # Whether LLM has gathered enough info to apply changes
    proposed_changes: Optional[list[str]] = None  # List of proposed changes when ready
    updated_html: Optional[str] = None  # The updated HTML if ready_to_apply is True
    follow_up_questions: Optional[list[str]] = None  # Questions to ask user if not ready


class TemplateCreateFromChatPayload(BaseModel):
    """Payload for creating a template from a chat conversation."""
    name: str
    html: str
    kind: str = "pdf"

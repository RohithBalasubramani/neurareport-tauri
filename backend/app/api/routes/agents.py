"""
AI Agents API Routes
Endpoints for specialized AI agents.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.services.agents import agent_service
from backend.app.services.agents import AgentType
from backend.app.services.security import require_api_key

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Topic to research")
    depth: str = Field(default="comprehensive", description="Research depth")
    focus_areas: Optional[List[str]] = Field(default=None, description="Focus areas")
    max_sections: int = Field(default=5, ge=1, le=10, description="Max sections")


class DataAnalysisRequest(BaseModel):
    question: str = Field(..., description="Question about the data")
    data: List[Dict[str, Any]] = Field(..., description="Data to analyze")
    data_description: Optional[str] = Field(default=None, description="Data description")
    generate_charts: bool = Field(default=True, description="Generate chart suggestions")


class EmailDraftRequest(BaseModel):
    context: str = Field(..., description="Email context")
    purpose: str = Field(..., description="Email purpose")
    tone: str = Field(default="professional", description="Email tone")
    recipient_info: Optional[str] = Field(default=None, description="Recipient info")
    previous_emails: Optional[List[str]] = Field(default=None, description="Previous emails")


class ContentRepurposeRequest(BaseModel):
    content: str = Field(..., description="Original content")
    source_format: str = Field(..., description="Source format")
    target_formats: List[str] = Field(..., description="Target formats")
    preserve_key_points: bool = Field(default=True, description="Preserve key points")
    adapt_length: bool = Field(default=True, description="Adapt length")


class ProofreadingRequest(BaseModel):
    text: str = Field(..., description="Text to proofread")
    style_guide: Optional[str] = Field(default=None, description="Style guide")
    focus_areas: Optional[List[str]] = Field(default=None, description="Focus areas")
    preserve_voice: bool = Field(default=True, description="Preserve voice")


# =============================================================================
# AGENT ENDPOINTS
# =============================================================================

@router.get("")
async def list_agents():
    """List available agent types with their capabilities."""
    agent_types = []
    for at in AgentType:
        agent_types.append({
            "id": at.value,
            "name": at.value.replace("_", " ").title(),
            "type": at.value,
            "status": "available",
        })
    return {"agents": agent_types, "total": len(agent_types)}


@router.post("/research")
async def run_research_agent(request: ResearchRequest):
    """
    Run the research agent to compile a report on a topic.

    Returns:
        ResearchReport with findings
    """
    try:
        task = await agent_service.run_research(
            topic=request.topic,
            depth=request.depth,
            focus_areas=request.focus_areas,
            max_sections=request.max_sections,
        )
        return task.model_dump()
    except Exception as e:
        logger.exception("Research agent failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/data-analysis")
async def run_data_analyst_agent(request: DataAnalysisRequest):
    """
    Run the data analyst agent to answer questions about data.

    Returns:
        DataAnalysisResult with insights
    """
    try:
        task = await agent_service.run_data_analyst(
            question=request.question,
            data=request.data,
            data_description=request.data_description,
            generate_charts=request.generate_charts,
        )
        return task.model_dump()
    except Exception as e:
        logger.exception("Data analyst agent failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/email-draft")
async def run_email_draft_agent(request: EmailDraftRequest):
    """
    Run the email draft agent to compose an email.

    Returns:
        EmailDraft with composed email
    """
    try:
        task = await agent_service.run_email_draft(
            context=request.context,
            purpose=request.purpose,
            tone=request.tone,
            recipient_info=request.recipient_info,
            previous_emails=request.previous_emails,
        )
        return task.model_dump()
    except Exception as e:
        logger.exception("Email draft agent failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/content-repurpose")
async def run_content_repurposing_agent(request: ContentRepurposeRequest):
    """
    Run the content repurposing agent to transform content.

    Returns:
        RepurposedContent with all versions
    """
    try:
        task = await agent_service.run_content_repurpose(
            content=request.content,
            source_format=request.source_format,
            target_formats=request.target_formats,
            preserve_key_points=request.preserve_key_points,
            adapt_length=request.adapt_length,
        )
        return task.model_dump()
    except Exception as e:
        logger.exception("Content repurposing agent failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/proofread")
async def run_proofreading_agent(request: ProofreadingRequest):
    """
    Run the proofreading agent for comprehensive style and grammar check.

    Returns:
        ProofreadingResult with corrections
    """
    try:
        task = await agent_service.run_proofreading(
            text=request.text,
            style_guide=request.style_guide,
            focus_areas=request.focus_areas,
            preserve_voice=request.preserve_voice,
        )
        return task.model_dump()
    except Exception as e:
        logger.exception("Proofreading agent failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# =============================================================================
# TASK MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task by ID."""
    task = agent_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.model_dump()


@router.get("/tasks")
async def list_tasks(agent_type: Optional[str] = None):
    """List all tasks, optionally filtered by agent type."""
    tasks = agent_service.list_tasks(agent_type=agent_type)
    return [t.model_dump() for t in tasks]


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/types")
async def list_agent_types():
    """List available agent types."""
    return {
        "types": [
            {
                "id": t.value,
                "name": t.value.replace("_", " ").title(),
                "description": {
                    "research": "Deep-dive research and report compilation",
                    "data_analyst": "Data analysis and question answering",
                    "email_draft": "Email composition based on context",
                    "content_repurpose": "Content transformation to multiple formats",
                    "proofreading": "Comprehensive style and grammar checking",
                }.get(t.value, "")
            }
            for t in AgentType
        ]
    }


@router.get("/formats/repurpose")
async def list_repurpose_formats():
    """List available content repurposing formats."""
    return {
        "formats": [
            {"id": "tweet_thread", "name": "Twitter Thread", "description": "5-10 tweets, 280 chars each"},
            {"id": "linkedin_post", "name": "LinkedIn Post", "description": "Professional, 1300 chars max"},
            {"id": "blog_summary", "name": "Blog Summary", "description": "300-500 words"},
            {"id": "slides", "name": "Presentation Slides", "description": "Title + bullet points per slide"},
            {"id": "email_newsletter", "name": "Email Newsletter", "description": "Catchy subject, scannable body"},
            {"id": "video_script", "name": "Video Script", "description": "Conversational, 2-3 minutes"},
            {"id": "infographic", "name": "Infographic Copy", "description": "Headlines, stats, takeaways"},
            {"id": "podcast_notes", "name": "Podcast Show Notes", "description": "Summary, timestamps, links"},
            {"id": "press_release", "name": "Press Release", "description": "Headline, lead, quotes"},
            {"id": "executive_summary", "name": "Executive Summary", "description": "1 page, key decisions"},
        ]
    }

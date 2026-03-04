"""API routes for quality feedback collection and RL stats."""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from backend.app.services.quality.feedback import (
    FeedbackEntry,
    FeedbackType,
    get_feedback_collector,
)
from backend.app.services.quality.rl_experience import get_thompson_sampler

logger = logging.getLogger("neura.api.feedback")

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class SubmitFeedbackRequest(BaseModel):
    """Payload for submitting a feedback signal."""

    source: str
    entity_id: str
    feedback_type: str
    rating: Optional[float] = None
    correction_text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# POST /  — submit feedback
# ---------------------------------------------------------------------------


@router.post("/")
async def submit_feedback(
    body: SubmitFeedbackRequest,
    request: Request,
):
    """Submit a feedback entry and propagate as a reward signal."""
    correlation_id = getattr(request.state, "correlation_id", None)

    # Validate feedback_type against the enum
    try:
        fb_type = FeedbackType(body.feedback_type)
    except ValueError:
        valid = [t.value for t in FeedbackType]
        raise HTTPException(
            status_code=422,
            detail=f"Invalid feedback_type '{body.feedback_type}'. "
            f"Must be one of: {valid}",
        )

    entry = FeedbackEntry(
        source=body.source,
        entity_id=body.entity_id,
        feedback_type=fb_type,
        rating=body.rating,
        correction_text=body.correction_text,
        tags=body.tags,
    )

    collector = get_feedback_collector()
    saved = collector.submit(entry)

    # Convert to scalar reward and update the Thompson Sampler
    reward = collector.to_reward(saved)
    sampler = get_thompson_sampler()
    sampler.update(body.source, body.entity_id, reward)

    logger.info(
        "feedback_api_submitted",
        extra={
            "event": "feedback_api_submitted",
            "feedback_id": saved.id,
            "source": body.source,
            "entity_id": body.entity_id,
            "reward": reward,
            "correlation_id": correlation_id,
        },
    )

    return {
        "status": "ok",
        "feedback_id": saved.id,
        "reward": reward,
        "correlation_id": correlation_id,
    }


# ---------------------------------------------------------------------------
# GET /  — list feedback
# ---------------------------------------------------------------------------


@router.get("/")
async def list_feedback(
    request: Request,
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(100, ge=1, le=1000, description="Max entries to return"),
):
    """List recent feedback entries, optionally filtered by source."""
    correlation_id = getattr(request.state, "correlation_id", None)
    collector = get_feedback_collector()
    entries = collector.list_feedback(source=source, limit=limit)

    return {
        "status": "ok",
        "count": len(entries),
        "entries": [e.model_dump(mode="json") for e in entries],
        "correlation_id": correlation_id,
    }


# ---------------------------------------------------------------------------
# GET /stats  — aggregated stats
# ---------------------------------------------------------------------------


@router.get("/stats")
async def get_feedback_stats(
    request: Request,
    source: str = Query(..., description="Source domain"),
    entity_id: str = Query(..., description="Entity identifier"),
):
    """Return aggregated reward and Thompson Sampler statistics."""
    correlation_id = getattr(request.state, "correlation_id", None)
    collector = get_feedback_collector()
    sampler = get_thompson_sampler()

    aggregate_reward = collector.aggregate_rewards(source, entity_id)
    sampler_stats = sampler.get_stats(source)

    return {
        "status": "ok",
        "source": source,
        "entity_id": entity_id,
        "aggregate_reward": round(aggregate_reward, 4),
        "sampler_stats": sampler_stats,
        "correlation_id": correlation_id,
    }

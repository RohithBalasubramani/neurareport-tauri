# mypy: ignore-errors
"""
User Experience Features - Analysis customization, collaboration, and real-time features.

Features:
9.1 Analysis Customization (preferences, focus areas, output formats)
9.2 Collaboration Features (sharing, comments, version history)
9.3 Real-Time Features (streaming, incremental results, progress tracking)
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from backend.app.schemas.analyze.enhanced_analysis import (
    AnalysisDepth,
    AnalysisPreferences,
    EnhancedAnalysisResult,
    SummaryMode,
)
from backend.app.services.analyze.enhanced_analysis_store import get_analysis_store

logger = logging.getLogger("neura.analyze.ux")


# =============================================================================
# 9.1 ANALYSIS CUSTOMIZATION
# =============================================================================

# Industry-specific configurations
INDUSTRY_CONFIGS = {
    "finance": {
        "focus_areas": ["financial", "risk", "compliance"],
        "key_metrics": ["revenue", "margin", "roi", "debt", "equity"],
        "terminology": ["EBITDA", "P/E ratio", "liquidity", "leverage"],
        "analysis_prompts": {
            "summary": "Focus on financial performance, risk indicators, and compliance matters.",
            "insights": "Identify financial risks, opportunities, and key performance drivers.",
        },
    },
    "healthcare": {
        "focus_areas": ["operational", "compliance", "patient"],
        "key_metrics": ["patient_volume", "readmission_rate", "cost_per_case"],
        "terminology": ["HIPAA", "CMS", "quality metrics", "patient outcomes"],
        "analysis_prompts": {
            "summary": "Focus on patient care metrics, compliance, and operational efficiency.",
            "insights": "Identify quality improvement opportunities and compliance risks.",
        },
    },
    "technology": {
        "focus_areas": ["growth", "innovation", "technical"],
        "key_metrics": ["mrr", "arr", "churn", "cac", "ltv"],
        "terminology": ["SaaS", "API", "scalability", "uptime"],
        "analysis_prompts": {
            "summary": "Focus on growth metrics, product performance, and technical capabilities.",
            "insights": "Identify growth opportunities, technical risks, and market trends.",
        },
    },
    "retail": {
        "focus_areas": ["sales", "inventory", "customer"],
        "key_metrics": ["same_store_sales", "inventory_turnover", "customer_acquisition"],
        "terminology": ["SKU", "foot traffic", "conversion rate", "basket size"],
        "analysis_prompts": {
            "summary": "Focus on sales performance, inventory management, and customer behavior.",
            "insights": "Identify sales trends, inventory optimization, and customer insights.",
        },
    },
    "manufacturing": {
        "focus_areas": ["operational", "quality", "supply_chain"],
        "key_metrics": ["oee", "defect_rate", "cycle_time", "inventory_days"],
        "terminology": ["lean", "six sigma", "yield", "throughput"],
        "analysis_prompts": {
            "summary": "Focus on production efficiency, quality metrics, and supply chain.",
            "insights": "Identify operational improvements, quality issues, and supply risks.",
        },
    },
}

# Output format configurations
OUTPUT_FORMATS = {
    "executive": {
        "max_summary_words": 150,
        "max_insights": 5,
        "include_technical_details": False,
        "visualization_style": "simple",
        "language_style": "concise",
    },
    "technical": {
        "max_summary_words": 500,
        "max_insights": 15,
        "include_technical_details": True,
        "visualization_style": "detailed",
        "language_style": "technical",
    },
    "visual": {
        "max_summary_words": 100,
        "max_insights": 8,
        "include_technical_details": False,
        "visualization_style": "rich",
        "chart_priority": True,
        "language_style": "brief",
    },
}


@dataclass
class AnalysisConfiguration:
    """Complete analysis configuration based on preferences."""
    preferences: AnalysisPreferences
    industry_config: Dict[str, Any] = field(default_factory=dict)
    output_config: Dict[str, Any] = field(default_factory=dict)
    custom_prompts: Dict[str, str] = field(default_factory=dict)


def build_analysis_configuration(
    preferences: AnalysisPreferences,
) -> AnalysisConfiguration:
    """Build complete analysis configuration from preferences."""
    # Get industry config
    industry_config = INDUSTRY_CONFIGS.get(preferences.industry, {})

    # Get output format config
    output_config = OUTPUT_FORMATS.get(preferences.output_format, OUTPUT_FORMATS["executive"])

    # Build custom prompts based on configuration
    custom_prompts = {}

    focus_str = ", ".join(preferences.focus_areas) if preferences.focus_areas else "general"
    depth_modifier = {
        AnalysisDepth.QUICK: "Be brief and highlight only the most critical points.",
        AnalysisDepth.STANDARD: "Provide a balanced analysis with key details.",
        AnalysisDepth.COMPREHENSIVE: "Provide thorough analysis with supporting details.",
        AnalysisDepth.DEEP: "Provide exhaustive analysis with all available details and nuances.",
    }

    base_prompt = f"Focus areas: {focus_str}. {depth_modifier.get(preferences.analysis_depth, '')}"

    if industry_config:
        base_prompt += f" Industry context: {preferences.industry}. "
        base_prompt += industry_config.get("analysis_prompts", {}).get("summary", "")

    custom_prompts["base"] = base_prompt
    custom_prompts["summary"] = industry_config.get("analysis_prompts", {}).get("summary", "")
    custom_prompts["insights"] = industry_config.get("analysis_prompts", {}).get("insights", "")

    return AnalysisConfiguration(
        preferences=preferences,
        industry_config=industry_config,
        output_config=output_config,
        custom_prompts=custom_prompts,
    )


def get_default_preferences() -> AnalysisPreferences:
    """Get default analysis preferences."""
    return AnalysisPreferences(
        analysis_depth=AnalysisDepth.STANDARD,
        focus_areas=["financial", "operational"],
        output_format="executive",
        language="en",
        currency_preference="USD",
        enable_predictions=True,
        enable_recommendations=True,
        auto_chart_generation=True,
        max_charts=10,
        summary_mode=SummaryMode.EXECUTIVE,
    )


# =============================================================================
# 9.2 COLLABORATION FEATURES
# =============================================================================

@dataclass
class AnalysisComment:
    """A comment on an analysis or specific element."""
    id: str
    analysis_id: str
    user_id: str
    user_name: str
    content: str
    element_type: Optional[str] = None  # table, chart, insight, metric
    element_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    replies: List['AnalysisComment'] = field(default_factory=list)
    resolved: bool = False


@dataclass
class AnalysisShare:
    """Sharing configuration for an analysis."""
    id: str
    analysis_id: str
    share_type: str  # link, email, embed
    access_level: str  # view, comment, edit
    created_by: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    password_protected: bool = False
    access_count: int = 0
    allowed_emails: List[str] = field(default_factory=list)


@dataclass
class AnalysisVersion:
    """A version of an analysis."""
    version_id: str
    analysis_id: str
    version_number: int
    created_at: datetime
    created_by: str
    description: str
    changes: List[str]
    snapshot: Dict[str, Any]  # Serialized analysis state


class CollaborationService:
    """Manages collaboration features."""

    def __init__(self):
        self._comments: Dict[str, List[AnalysisComment]] = {}
        self._shares: Dict[str, List[AnalysisShare]] = {}
        self._versions: Dict[str, List[AnalysisVersion]] = {}
        self._store = get_analysis_store()

    def _parse_dt(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except Exception:
            return None

    def _comment_to_dict(self, comment: AnalysisComment) -> Dict[str, Any]:
        return {
            "id": comment.id,
            "analysis_id": comment.analysis_id,
            "user_id": comment.user_id,
            "user_name": comment.user_name,
            "content": comment.content,
            "element_type": comment.element_type,
            "element_id": comment.element_id,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
            "replies": [self._comment_to_dict(r) for r in comment.replies],
            "resolved": comment.resolved,
        }

    def _comment_from_dict(self, data: Dict[str, Any]) -> AnalysisComment:
        replies = [self._comment_from_dict(r) for r in data.get("replies", [])]
        return AnalysisComment(
            id=data.get("id", f"comment_{uuid.uuid4().hex[:12]}"),
            analysis_id=data.get("analysis_id", ""),
            user_id=data.get("user_id", "anonymous"),
            user_name=data.get("user_name", "Anonymous"),
            content=data.get("content", ""),
            element_type=data.get("element_type"),
            element_id=data.get("element_id"),
            created_at=self._parse_dt(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=self._parse_dt(data.get("updated_at")) or datetime.now(timezone.utc),
            replies=replies,
            resolved=bool(data.get("resolved", False)),
        )

    def _share_to_dict(self, share: AnalysisShare) -> Dict[str, Any]:
        return {
            "id": share.id,
            "analysis_id": share.analysis_id,
            "share_type": share.share_type,
            "access_level": share.access_level,
            "created_by": share.created_by,
            "created_at": share.created_at.isoformat() if share.created_at else None,
            "expires_at": share.expires_at.isoformat() if share.expires_at else None,
            "password_protected": share.password_protected,
            "access_count": share.access_count,
            "allowed_emails": list(share.allowed_emails or []),
        }

    def _share_from_dict(self, data: Dict[str, Any]) -> AnalysisShare:
        return AnalysisShare(
            id=data.get("id", f"share_{uuid.uuid4().hex[:12]}"),
            analysis_id=data.get("analysis_id", ""),
            share_type=data.get("share_type", "link"),
            access_level=data.get("access_level", "view"),
            created_by=data.get("created_by", "api"),
            created_at=self._parse_dt(data.get("created_at")) or datetime.now(timezone.utc),
            expires_at=self._parse_dt(data.get("expires_at")),
            password_protected=bool(data.get("password_protected", False)),
            access_count=int(data.get("access_count", 0) or 0),
            allowed_emails=list(data.get("allowed_emails") or []),
        )

    def _version_to_dict(self, version: AnalysisVersion) -> Dict[str, Any]:
        return {
            "version_id": version.version_id,
            "analysis_id": version.analysis_id,
            "version_number": version.version_number,
            "created_at": version.created_at.isoformat() if version.created_at else None,
            "created_by": version.created_by,
            "description": version.description,
            "changes": list(version.changes or []),
            "snapshot": version.snapshot,
        }

    def _version_from_dict(self, data: Dict[str, Any]) -> AnalysisVersion:
        return AnalysisVersion(
            version_id=data.get("version_id", f"v_{uuid.uuid4().hex[:12]}"),
            analysis_id=data.get("analysis_id", ""),
            version_number=int(data.get("version_number", 1) or 1),
            created_at=self._parse_dt(data.get("created_at")) or datetime.now(timezone.utc),
            created_by=data.get("created_by", "api"),
            description=data.get("description", ""),
            changes=list(data.get("changes") or []),
            snapshot=data.get("snapshot") or {},
        )

    def _ensure_comments_loaded(self, analysis_id: str) -> None:
        if analysis_id not in self._comments:
            payload = self._store.load_comments(analysis_id)
            self._comments[analysis_id] = [self._comment_from_dict(p) for p in payload]

    def _ensure_shares_loaded(self, analysis_id: str) -> None:
        if analysis_id not in self._shares:
            payload = self._store.list_shares_for_analysis(analysis_id)
            self._shares[analysis_id] = [self._share_from_dict(p) for p in payload]

    def _ensure_versions_loaded(self, analysis_id: str) -> None:
        if analysis_id not in self._versions:
            payload = self._store.load_versions(analysis_id)
            self._versions[analysis_id] = [self._version_from_dict(p) for p in payload]

    def _persist_comments(self, analysis_id: str) -> None:
        payload = [self._comment_to_dict(c) for c in self._comments.get(analysis_id, [])]
        self._store.save_comments(analysis_id, payload)

    def _persist_versions(self, analysis_id: str) -> None:
        payload = [self._version_to_dict(v) for v in self._versions.get(analysis_id, [])]
        self._store.save_versions(analysis_id, payload)

    def add_comment(
        self,
        analysis_id: str,
        user_id: str,
        user_name: str,
        content: str,
        element_type: Optional[str] = None,
        element_id: Optional[str] = None,
        parent_comment_id: Optional[str] = None,
    ) -> AnalysisComment:
        """Add a comment to an analysis."""
        comment = AnalysisComment(
            id=f"comment_{uuid.uuid4().hex[:12]}",
            analysis_id=analysis_id,
            user_id=user_id,
            user_name=user_name,
            content=content,
            element_type=element_type,
            element_id=element_id,
        )

        self._ensure_comments_loaded(analysis_id)

        if parent_comment_id:
            # Find parent and add as reply
            for existing in self._comments[analysis_id]:
                if existing.id == parent_comment_id:
                    existing.replies.append(comment)
                    break
        else:
            self._comments[analysis_id].append(comment)

        self._persist_comments(analysis_id)
        return comment

    def get_comments(self, analysis_id: str) -> List[AnalysisComment]:
        """Get all comments for an analysis."""
        self._ensure_comments_loaded(analysis_id)
        return self._comments.get(analysis_id, [])

    def create_share_link(
        self,
        analysis_id: str,
        created_by: str,
        access_level: str = "view",
        expires_hours: Optional[int] = None,
        password_protected: bool = False,
        allowed_emails: List[str] = None,
    ) -> AnalysisShare:
        """Create a shareable link for an analysis."""
        share = AnalysisShare(
            id=f"share_{uuid.uuid4().hex[:12]}",
            analysis_id=analysis_id,
            share_type="link",
            access_level=access_level,
            created_by=created_by,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours) if expires_hours else None,
            password_protected=password_protected,
            allowed_emails=allowed_emails or [],
        )

        self._ensure_shares_loaded(analysis_id)
        self._shares[analysis_id].append(share)
        self._store.save_share(self._share_to_dict(share))

        return share

    def get_shares(self, analysis_id: str) -> List[AnalysisShare]:
        """List shares for an analysis."""
        self._ensure_shares_loaded(analysis_id)
        return self._shares.get(analysis_id, [])

    def get_share(self, share_id: str) -> Optional[AnalysisShare]:
        """Get a share by ID."""
        payload = self._store.load_share(share_id)
        if not payload:
            return None
        return self._share_from_dict(payload)

    def record_share_access(self, share_id: str) -> None:
        """Increment access count for a share."""
        share = self.get_share(share_id)
        if not share:
            return
        share.access_count += 1
        # Update in-memory list if loaded
        if share.analysis_id in self._shares:
            for idx, existing in enumerate(self._shares[share.analysis_id]):
                if existing.id == share.id:
                    self._shares[share.analysis_id][idx] = share
                    break
        self._store.save_share(self._share_to_dict(share))

    def save_version(
        self,
        analysis_id: str,
        created_by: str,
        description: str,
        analysis_snapshot: Dict[str, Any],
    ) -> AnalysisVersion:
        """Save a version of the analysis."""
        if analysis_id not in self._versions:
            self._ensure_versions_loaded(analysis_id)

        version_number = len(self._versions[analysis_id]) + 1

        # Detect changes from previous version
        changes = []
        if self._versions[analysis_id]:
            prev = self._versions[analysis_id][-1].snapshot
            # Compare key metrics
            prev_metrics = len(prev.get("metrics", []))
            curr_metrics = len(analysis_snapshot.get("metrics", []))
            if curr_metrics != prev_metrics:
                changes.append(f"Metrics: {prev_metrics} -> {curr_metrics}")

        version = AnalysisVersion(
            version_id=f"v_{uuid.uuid4().hex[:12]}",
            analysis_id=analysis_id,
            version_number=version_number,
            created_at=datetime.now(timezone.utc),
            created_by=created_by,
            description=description,
            changes=changes,
            snapshot=analysis_snapshot,
        )

        self._versions[analysis_id].append(version)
        self._persist_versions(analysis_id)
        return version

    def get_version_history(self, analysis_id: str) -> List[AnalysisVersion]:
        """Get version history for an analysis."""
        self._ensure_versions_loaded(analysis_id)
        return self._versions.get(analysis_id, [])


# Need to import timedelta
from datetime import timedelta


# =============================================================================
# 9.3 REAL-TIME FEATURES
# =============================================================================

@dataclass
class ProgressUpdate:
    """A progress update for streaming."""
    stage: str
    progress: float  # 0-100
    detail: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[Dict[str, Any]] = None


@dataclass
class IncrementalResult:
    """An incremental result during analysis."""
    result_type: str  # table, entity, metric, chart, insight
    data: Any
    is_final: bool = False


class StreamingAnalysisSession:
    """Manages a streaming analysis session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.started_at = datetime.now(timezone.utc)
        self.progress = 0.0
        self.current_stage = "initializing"
        self.is_cancelled = False
        self.is_complete = False
        self._progress_callbacks: List[Callable[[ProgressUpdate], None]] = []
        self._result_callbacks: List[Callable[[IncrementalResult], None]] = []
        self._incremental_results: List[IncrementalResult] = []

    def add_progress_callback(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Add a callback for progress updates."""
        self._progress_callbacks.append(callback)

    def add_result_callback(self, callback: Callable[[IncrementalResult], None]) -> None:
        """Add a callback for incremental results."""
        self._result_callbacks.append(callback)

    def update_progress(self, stage: str, progress: float, detail: str, data: Optional[Dict] = None) -> None:
        """Update progress and notify callbacks."""
        if self.is_cancelled:
            raise asyncio.CancelledError("Analysis was cancelled")

        self.current_stage = stage
        self.progress = progress

        update = ProgressUpdate(
            stage=stage,
            progress=progress,
            detail=detail,
            data=data,
        )

        for callback in self._progress_callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def emit_result(self, result_type: str, data: Any, is_final: bool = False) -> None:
        """Emit an incremental result."""
        result = IncrementalResult(
            result_type=result_type,
            data=data,
            is_final=is_final,
        )
        self._incremental_results.append(result)

        for callback in self._result_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.warning(f"Result callback error: {e}")

    def cancel(self) -> None:
        """Cancel the analysis session."""
        self.is_cancelled = True

    def complete(self) -> None:
        """Mark the session as complete."""
        self.is_complete = True
        self.progress = 100.0


async def stream_analysis_progress(
    session: StreamingAnalysisSession,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream analysis progress as server-sent events."""
    last_progress = -1

    while not session.is_complete and not session.is_cancelled:
        if session.progress != last_progress:
            last_progress = session.progress
            yield {
                "event": "progress",
                "stage": session.current_stage,
                "progress": session.progress,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Check for new incremental results
        pending = list(session._incremental_results)
        session._incremental_results.clear()
        for result in pending:
            yield {
                "event": "result",
                "type": result.result_type,
                "data": result.data if isinstance(result.data, dict) else str(result.data),
                "is_final": result.is_final,
            }

        await asyncio.sleep(0.1)

    if session.is_cancelled:
        yield {"event": "cancelled", "timestamp": datetime.now(timezone.utc).isoformat()}
    else:
        yield {"event": "complete", "progress": 100, "timestamp": datetime.now(timezone.utc).isoformat()}


# =============================================================================
# SUGGESTED QUESTIONS
# =============================================================================

def generate_suggested_questions(
    tables: List[Any],
    metrics: List[Any],
    entities: List[Any],
) -> List[str]:
    """Generate suggested questions based on extracted data."""
    questions = []

    # Questions based on metrics
    if metrics:
        metric_names = [m.name for m in metrics[:5]]
        for name in metric_names:
            questions.append(f"What factors contributed to the {name}?")
            questions.append(f"How does the {name} compare to previous periods?")

        if len(metrics) >= 2:
            questions.append(f"What's the relationship between {metric_names[0]} and {metric_names[1]}?")

    # Questions based on tables
    if tables:
        for table in tables[:3]:
            if hasattr(table, 'title') and table.title:
                questions.append(f"What are the key insights from the {table.title} data?")
            if hasattr(table, 'headers'):
                numeric_cols = [h for h, d in zip(table.headers, getattr(table, 'data_types', [])) if d == 'numeric']
                if numeric_cols:
                    questions.append(f"What's the trend for {numeric_cols[0]}?")

    # Questions based on entities
    if entities:
        org_entities = [e for e in entities if hasattr(e, 'type') and e.type.value == 'organization']
        if org_entities:
            questions.append(f"What is the role of {org_entities[0].value} in this document?")

    # Generic insightful questions
    questions.extend([
        "What are the main risks identified in this document?",
        "What opportunities are suggested by the data?",
        "What actions should be taken based on these findings?",
        "Are there any anomalies or unusual patterns?",
        "How does this compare to industry benchmarks?",
    ])

    return questions[:10]  # Return top 10


# =============================================================================
# USER EXPERIENCE SERVICE ORCHESTRATOR
# =============================================================================

class UserExperienceService:
    """Orchestrates user experience features."""

    def __init__(self):
        self.collaboration = CollaborationService()
        self._active_sessions: Dict[str, StreamingAnalysisSession] = {}

    def build_configuration(self, preferences: AnalysisPreferences) -> AnalysisConfiguration:
        """Build analysis configuration from preferences."""
        return build_analysis_configuration(preferences)

    def get_industry_options(self) -> List[Dict[str, str]]:
        """Get available industry options."""
        return [
            {"value": key, "label": key.replace("_", " ").title(), "description": config.get("focus_areas", [])}
            for key, config in INDUSTRY_CONFIGS.items()
        ]

    def get_output_format_options(self) -> List[Dict[str, Any]]:
        """Get available output format options."""
        return [
            {"value": key, "label": key.title(), "config": config}
            for key, config in OUTPUT_FORMATS.items()
        ]

    def create_streaming_session(self) -> StreamingAnalysisSession:
        """Create a new streaming analysis session."""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        session = StreamingAnalysisSession(session_id)
        self._active_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[StreamingAnalysisSession]:
        """Get an active session."""
        return self._active_sessions.get(session_id)

    def cancel_session(self, session_id: str) -> bool:
        """Cancel an active session."""
        session = self._active_sessions.get(session_id)
        if session:
            session.cancel()
            return True
        return False

    def generate_suggested_questions(
        self,
        tables: List[Any],
        metrics: List[Any],
        entities: List[Any],
    ) -> List[str]:
        """Generate suggested questions."""
        return generate_suggested_questions(tables, metrics, entities)

    # Collaboration methods
    def add_comment(self, *args, **kwargs) -> AnalysisComment:
        return self.collaboration.add_comment(*args, **kwargs)

    def get_comments(self, analysis_id: str) -> List[AnalysisComment]:
        return self.collaboration.get_comments(analysis_id)

    def create_share_link(self, *args, **kwargs) -> AnalysisShare:
        return self.collaboration.create_share_link(*args, **kwargs)

    def get_share(self, share_id: str) -> Optional[AnalysisShare]:
        return self.collaboration.get_share(share_id)

    def record_share_access(self, share_id: str) -> None:
        self.collaboration.record_share_access(share_id)

    def save_version(self, *args, **kwargs) -> AnalysisVersion:
        return self.collaboration.save_version(*args, **kwargs)

    def get_version_history(self, analysis_id: str) -> List[AnalysisVersion]:
        return self.collaboration.get_version_history(analysis_id)

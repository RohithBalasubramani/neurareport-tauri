"""
AI Agents Service Module
Provides specialized AI agents for various tasks.

This module provides two implementations:
1. Legacy in-memory implementation (service.py) - for backward compatibility
2. Production-grade persistent implementation (agent_service.py) - recommended

Use agent_service_v2 for new code:
    from backend.app.services.agents import agent_service_v2
    task = await agent_service_v2.run_research(topic="AI trends")
"""
# Legacy imports for backward compatibility
from .service import (
    AgentService as LegacyAgentService,
    agent_service as legacy_agent_service,
    AgentType,
    AgentStatus,
    AgentTask,
    ResearchReport,
    DataAnalysisResult,
    EmailDraft,
    RepurposedContent,
    ProofreadingResult,
    ResearchAgent as LegacyResearchAgent,
    DataAnalystAgent,
    EmailDraftAgent,
    ContentRepurposingAgent,
    ProofreadingAgent,
)

# New production-grade implementation
from .agent_service import (
    AgentService,
    AgentTaskWorker,
    agent_service,
    agent_task_worker,
)
# Repository types re-exported for api layer access
from backend.app.repositories.agent_tasks import AgentTaskStatus
from backend.app.repositories.agent_tasks.repository import (
    TaskConflictError,
    TaskNotFoundError,
)
from .base_agent import BaseAgentV2
from .research_agent import (
    ResearchAgent,
    ResearchReport as ResearchReportV2,
    ResearchInput,
    AgentError,
    ValidationError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMResponseError,
)
from .data_analyst_agent import (
    DataAnalystAgent as DataAnalystAgentV2,
    DataAnalystInput,
    DataAnalysisReport as DataAnalysisReportV2,
)
from .email_draft_agent import (
    EmailDraftAgentV2,
    EmailDraftInput,
    EmailDraftResult as EmailDraftResultV2,
)
from .content_repurpose_agent import (
    ContentRepurposeAgentV2,
    ContentRepurposeInput,
    ContentRepurposeReport as ContentRepurposeReportV2,
)
from .proofreading_agent import (
    ProofreadingAgentV2,
    ProofreadingInput,
    ProofreadingReport as ProofreadingReportV2,
)

# Alias for clarity
agent_service_v2 = agent_service

__all__ = [
    # New implementation (recommended)
    "AgentService",
    "AgentTaskWorker",
    "agent_service",
    "agent_service_v2",
    "agent_task_worker",
    "BaseAgentV2",
    # Research
    "ResearchAgent",
    "ResearchInput",
    "ResearchReportV2",
    # Data Analyst
    "DataAnalystAgentV2",
    "DataAnalystInput",
    "DataAnalysisReportV2",
    # Email Draft
    "EmailDraftAgentV2",
    "EmailDraftInput",
    "EmailDraftResultV2",
    # Content Repurpose
    "ContentRepurposeAgentV2",
    "ContentRepurposeInput",
    "ContentRepurposeReportV2",
    # Proofreading
    "ProofreadingAgentV2",
    "ProofreadingInput",
    "ProofreadingReportV2",
    # Error types
    "AgentError",
    "ValidationError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMResponseError",
    # Legacy (for backward compatibility)
    "LegacyAgentService",
    "legacy_agent_service",
    "LegacyResearchAgent",
    "DataAnalystAgent",
    "EmailDraftAgent",
    "ContentRepurposingAgent",
    "ProofreadingAgent",
    # Repository types (re-exported for api layer)
    "AgentTaskStatus",
    "TaskConflictError",
    "TaskNotFoundError",
    # Shared types
    "AgentType",
    "AgentStatus",
    "AgentTask",
    "ResearchReport",
    "DataAnalysisResult",
    "EmailDraft",
    "RepurposedContent",
    "ProofreadingResult",
]

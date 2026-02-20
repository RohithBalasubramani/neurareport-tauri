"""Workflow Schemas.

Pydantic models for workflow automation.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of workflow nodes."""
    TRIGGER = "trigger"
    WEBHOOK = "webhook"
    ACTION = "action"
    EMAIL = "email"
    NOTIFICATION = "notification"
    CONDITION = "condition"
    LOOP = "loop"
    APPROVAL = "approval"
    DATA_TRANSFORM = "data_transform"
    DELAY = "delay"
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"


class TriggerType(str, Enum):
    """Types of workflow triggers."""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    FILE_UPLOAD = "file_upload"
    EVENT = "event"


class ExecutionStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"


class WorkflowNode(BaseModel):
    """A single node in a workflow."""
    id: str
    type: NodeType
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})


class WorkflowEdge(BaseModel):
    """Connection between workflow nodes."""
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None
    condition: Optional[str] = None


class WorkflowTrigger(BaseModel):
    """Workflow trigger configuration."""
    type: TriggerType
    config: dict[str, Any] = Field(default_factory=dict)


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow."""
    name: str
    description: Optional[str] = None
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    triggers: list[WorkflowTrigger] = Field(default_factory=list)
    is_active: bool = True


class UpdateWorkflowRequest(BaseModel):
    """Request to update a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[list[WorkflowNode]] = None
    edges: Optional[list[WorkflowEdge]] = None
    triggers: Optional[list[WorkflowTrigger]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    """Workflow response model."""
    id: str
    name: str
    description: Optional[str]
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]
    triggers: list[WorkflowTrigger]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    run_count: int = 0


class WorkflowListResponse(BaseModel):
    """List of workflows response."""
    workflows: list[WorkflowResponse]
    total: int


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow."""
    input_data: dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = True


class NodeExecutionResult(BaseModel):
    """Result of executing a single node."""
    node_id: str
    status: ExecutionStatus
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution status response."""
    id: str
    workflow_id: str
    status: ExecutionStatus
    input_data: dict[str, Any]
    output_data: Optional[dict[str, Any]] = None
    node_results: list[NodeExecutionResult] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class ApprovalRequest(BaseModel):
    """Request for workflow approval action."""
    execution_id: str
    node_id: str
    approved: bool
    comment: Optional[str] = None


class ConfigureTriggerRequest(BaseModel):
    """Request to configure a workflow trigger."""
    trigger_type: TriggerType
    config: dict[str, Any] = Field(default_factory=dict)

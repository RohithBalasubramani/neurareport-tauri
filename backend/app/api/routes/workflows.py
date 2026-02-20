"""Workflow API Routes.

REST API endpoints for workflow automation.
"""
from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from backend.app.schemas.workflows.workflow import (
    ApprovalRequest,
    ConfigureTriggerRequest,
    CreateWorkflowRequest,
    ExecuteWorkflowRequest,
    ExecutionStatus,
    NodeType,
    TriggerType,
    UpdateWorkflowRequest,
    WorkflowEdge,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowNode,
    WorkflowResponse,
    WorkflowTrigger,
)
from backend.app.services.security import require_api_key
from backend.app.services.workflow.service import workflow_service
from backend.app.api.middleware import limiter, RATE_LIMIT_STRICT

logger = logging.getLogger("neura.api.workflows")

router = APIRouter(tags=["workflows"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=WorkflowResponse)
async def create_workflow(request: CreateWorkflowRequest):
    """Create a new workflow."""
    return await workflow_service.create_workflow(request)


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    active_only: bool = Query(False, description="Only return active workflows"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all workflows."""
    workflows, total = await workflow_service.list_workflows(
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
    return WorkflowListResponse(workflows=workflows, total=total)


# --- Static-prefix routes (must be declared before /{workflow_id}) ---


@router.get("/approvals/pending")
async def get_pending_approvals(workflow_id: Optional[str] = None):
    """Get all pending approvals."""
    return await workflow_service.get_pending_approvals(workflow_id=workflow_id)


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(execution_id: str):
    """Get execution status."""
    execution = await workflow_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/executions/{execution_id}/approve")
async def approve_execution(execution_id: str, request: ApprovalRequest):
    """Approve or reject a pending approval."""
    result = await workflow_service.approve_execution(
        execution_id,
        node_id=request.node_id,
        approved=request.approved,
        comment=request.comment,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Pending approval not found")
    return result


@router.get("/node-types")
async def list_node_types():
    """List available node types."""
    node_types = [
        {"type": nt.value, "label": nt.value.replace("_", " ").title()}
        for nt in NodeType
    ]
    return {"node_types": node_types, "total": len(node_types)}


@router.get("/node-types/{node_type}/schema")
async def get_node_type_schema(node_type: str):
    """Get schema for a node type."""
    try:
        nt = NodeType(node_type)
    except ValueError:
        raise HTTPException(status_code=404, detail="Node type not found")

    # Define config schemas per node type
    schemas = {
        NodeType.TRIGGER: {"properties": {"event": {"type": "string"}}},
        NodeType.WEBHOOK: {"properties": {"url": {"type": "string"}, "method": {"type": "string"}}},
        NodeType.ACTION: {"properties": {"action_type": {"type": "string"}, "message": {"type": "string"}}},
        NodeType.EMAIL: {"properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}},
        NodeType.NOTIFICATION: {"properties": {"channel": {"type": "string"}, "message": {"type": "string"}}},
        NodeType.CONDITION: {"properties": {"condition": {"type": "string"}}},
        NodeType.LOOP: {"properties": {"items_path": {"type": "string"}, "max_iterations": {"type": "integer"}}},
        NodeType.APPROVAL: {"properties": {"approver": {"type": "string"}, "timeout_hours": {"type": "integer"}}},
        NodeType.DATA_TRANSFORM: {"properties": {"transform": {"type": "object"}}},
        NodeType.DELAY: {"properties": {"delay_ms": {"type": "integer"}}},
        NodeType.HTTP_REQUEST: {"properties": {"url": {"type": "string"}, "method": {"type": "string"}, "headers": {"type": "object"}, "body": {"type": "object"}}},
        NodeType.DATABASE_QUERY: {"properties": {"query": {"type": "string"}, "connection": {"type": "string"}}},
    }

    return {
        "node_type": nt.value,
        "label": nt.value.replace("_", " ").title(),
        "config_schema": schemas.get(nt, {"properties": {}}),
    }


@router.get("/templates")
async def list_workflow_templates():
    """List workflow templates."""
    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            templates = state.get("workflow_templates", {})
    except Exception:
        templates = {}

    template_list = list(templates.values())
    return {"templates": template_list, "total": len(template_list)}


class CreateFromTemplateRequest(BaseModel):
    name: Optional[str] = None
    input_data: dict[str, Any] = Field(default_factory=dict)


@router.post("/templates/{template_id}/create", response_model=WorkflowResponse)
async def create_workflow_from_template(
    template_id: str,
    request: CreateFromTemplateRequest,
):
    """Create workflow from template."""
    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            templates = state.get("workflow_templates", {})
            template = templates.get(template_id)
    except Exception:
        template = None

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    create_request = CreateWorkflowRequest(
        name=request.name or template.get("name", "Workflow from template"),
        description=template.get("description"),
        nodes=[WorkflowNode(**n) for n in template.get("nodes", [])],
        edges=[WorkflowEdge(**e) for e in template.get("edges", [])],
        triggers=[WorkflowTrigger(**t) for t in template.get("triggers", [])],
        is_active=True,
    )

    return await workflow_service.create_workflow(create_request)


# --- Parameterized routes ---


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get a workflow by ID."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, request: UpdateWorkflowRequest):
    """Update a workflow."""
    workflow = await workflow_service.update_workflow(workflow_id, request)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    deleted = await workflow_service.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "deleted", "id": workflow_id}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
@limiter.limit(RATE_LIMIT_STRICT)
async def execute_workflow(
    request: Request,
    workflow_id: str,
    req: ExecuteWorkflowRequest,
):
    """Execute a workflow."""
    try:
        return await workflow_service.execute_workflow(
            workflow_id,
            input_data=req.input_data,
            async_execution=req.async_execution,
        )
    except ValueError as e:
        logger.warning("Workflow not found: %s", e)
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        logger.error("Workflow execution failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Workflow execution failed due to an internal error.",
        )


@router.get("/{workflow_id}/executions", response_model=list[WorkflowExecutionResponse])
async def list_executions(
    workflow_id: str,
    status: Optional[ExecutionStatus] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """List executions for a workflow."""
    return await workflow_service.list_executions(
        workflow_id=workflow_id,
        status=status,
        limit=limit,
    )


# Required config keys per trigger type
_TRIGGER_REQUIRED_KEYS: dict[TriggerType, set[str]] = {
    TriggerType.SCHEDULE: {"cron"},
    TriggerType.WEBHOOK: {"secret"},
    TriggerType.FILE_UPLOAD: {"path"},
    TriggerType.EVENT: {"event_name"},
    TriggerType.MANUAL: set(),
}


@router.post("/{workflow_id}/trigger", response_model=WorkflowResponse)
async def configure_trigger(workflow_id: str, request: ConfigureTriggerRequest):
    """Configure a workflow trigger."""
    # Validate trigger type is recognized
    try:
        trigger_type = TriggerType(request.trigger_type)
    except ValueError:
        valid = [t.value for t in TriggerType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trigger_type '{request.trigger_type}'. Must be one of: {', '.join(valid)}",
        )

    # Validate required config keys for the trigger type
    required = _TRIGGER_REQUIRED_KEYS.get(trigger_type, set())
    missing = required - set(request.config.keys())
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Trigger type '{trigger_type.value}' requires config keys: {', '.join(sorted(missing))}",
        )

    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Add or update trigger
    new_trigger = WorkflowTrigger(type=trigger_type, config=request.config)
    triggers = list(workflow.triggers)

    # Replace existing trigger of same type or add new
    found = False
    for i, t in enumerate(triggers):
        if t.type == trigger_type:
            triggers[i] = new_trigger
            found = True
            break
    if not found:
        triggers.append(new_trigger)

    update_request = UpdateWorkflowRequest(triggers=triggers)
    return await workflow_service.update_workflow(workflow_id, update_request)


# --- Execution control ---


@router.post("/{workflow_id}/executions/{execution_id}/cancel")
async def cancel_execution(workflow_id: str, execution_id: str):
    """Cancel a running execution."""
    execution = await workflow_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="Execution not found for this workflow")

    exec_data = workflow_service._executions.get(execution_id)
    if not exec_data:
        raise HTTPException(status_code=404, detail="Execution not found")

    if exec_data["status"] in (ExecutionStatus.COMPLETED.value, ExecutionStatus.CANCELLED.value):
        raise HTTPException(status_code=400, detail="Execution is already finished")

    exec_data["status"] = ExecutionStatus.CANCELLED.value
    exec_data["finished_at"] = datetime.now(timezone.utc)
    exec_data["error"] = "Cancelled by user"

    return {"status": "cancelled", "execution_id": execution_id}


@router.post("/{workflow_id}/executions/{execution_id}/retry")
async def retry_execution(workflow_id: str, execution_id: str):
    """Retry a failed execution."""
    execution = await workflow_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="Execution not found for this workflow")
    if execution.status != ExecutionStatus.FAILED:
        raise HTTPException(status_code=400, detail="Only failed executions can be retried")

    # Re-execute the workflow with the same input data
    try:
        new_execution = await workflow_service.execute_workflow(
            workflow_id,
            input_data=execution.input_data,
            async_execution=True,
        )
        return new_execution
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        logger.error("Retry execution failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Retry failed due to an internal error.")


@router.get("/{workflow_id}/executions/{execution_id}/logs")
async def get_execution_logs(workflow_id: str, execution_id: str):
    """Get execution logs."""
    execution = await workflow_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="Execution not found for this workflow")

    logs = []
    for result in execution.node_results:
        logs.append({
            "node_id": result.node_id,
            "status": result.status.value,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "finished_at": result.finished_at.isoformat() if result.finished_at else None,
            "error": result.error,
            "output_keys": list(result.output.keys()) if result.output else [],
        })

    return {
        "execution_id": execution_id,
        "workflow_id": workflow_id,
        "status": execution.status.value,
        "logs": logs,
    }


# --- Trigger management ---


@router.put("/{workflow_id}/triggers/{trigger_id}")
async def update_trigger(
    workflow_id: str,
    trigger_id: str,
    request: ConfigureTriggerRequest,
):
    """Update a specific trigger."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        trigger_type = TriggerType(request.trigger_type)
    except ValueError:
        valid = [t.value for t in TriggerType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trigger_type. Must be one of: {', '.join(valid)}",
        )

    triggers = list(workflow.triggers)
    trigger_idx = int(trigger_id) if trigger_id.isdigit() else None

    if trigger_idx is None or trigger_idx < 0 or trigger_idx >= len(triggers):
        raise HTTPException(status_code=404, detail="Trigger not found")

    triggers[trigger_idx] = WorkflowTrigger(type=trigger_type, config=request.config)
    update_request = UpdateWorkflowRequest(triggers=triggers)
    return await workflow_service.update_workflow(workflow_id, update_request)


@router.delete("/{workflow_id}/triggers/{trigger_id}")
async def delete_trigger(workflow_id: str, trigger_id: str):
    """Delete a trigger."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    triggers = list(workflow.triggers)
    trigger_idx = int(trigger_id) if trigger_id.isdigit() else None

    if trigger_idx is None or trigger_idx < 0 or trigger_idx >= len(triggers):
        raise HTTPException(status_code=404, detail="Trigger not found")

    triggers.pop(trigger_idx)
    update_request = UpdateWorkflowRequest(triggers=triggers)
    result = await workflow_service.update_workflow(workflow_id, update_request)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "deleted", "trigger_id": trigger_id}


@router.post("/{workflow_id}/triggers/{trigger_id}/enable")
async def enable_trigger(workflow_id: str, trigger_id: str):
    """Enable a trigger."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    triggers = list(workflow.triggers)
    trigger_idx = int(trigger_id) if trigger_id.isdigit() else None

    if trigger_idx is None or trigger_idx < 0 or trigger_idx >= len(triggers):
        raise HTTPException(status_code=404, detail="Trigger not found")

    trigger = triggers[trigger_idx]
    updated_config = dict(trigger.config)
    updated_config["enabled"] = True
    triggers[trigger_idx] = WorkflowTrigger(type=trigger.type, config=updated_config)

    update_request = UpdateWorkflowRequest(triggers=triggers)
    await workflow_service.update_workflow(workflow_id, update_request)
    return {"status": "enabled", "trigger_id": trigger_id}


@router.post("/{workflow_id}/triggers/{trigger_id}/disable")
async def disable_trigger(workflow_id: str, trigger_id: str):
    """Disable a trigger."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    triggers = list(workflow.triggers)
    trigger_idx = int(trigger_id) if trigger_id.isdigit() else None

    if trigger_idx is None or trigger_idx < 0 or trigger_idx >= len(triggers):
        raise HTTPException(status_code=404, detail="Trigger not found")

    trigger = triggers[trigger_idx]
    updated_config = dict(trigger.config)
    updated_config["enabled"] = False
    triggers[trigger_idx] = WorkflowTrigger(type=trigger.type, config=updated_config)

    update_request = UpdateWorkflowRequest(triggers=triggers)
    await workflow_service.update_workflow(workflow_id, update_request)
    return {"status": "disabled", "trigger_id": trigger_id}


# --- Template management ---


@router.post("/{workflow_id}/save-as-template")
async def save_as_template(workflow_id: str):
    """Save workflow as a reusable template."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    template_id = str(uuid.uuid4())
    template = {
        "id": template_id,
        "name": workflow.name,
        "description": workflow.description,
        "nodes": [n.model_dump() for n in workflow.nodes],
        "edges": [e.model_dump() for e in workflow.edges],
        "triggers": [t.model_dump() for t in workflow.triggers],
        "source_workflow_id": workflow_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            if "workflow_templates" not in state:
                state["workflow_templates"] = {}
            state["workflow_templates"][template_id] = template
    except Exception as e:
        logger.warning("Failed to persist workflow template: %s", e)

    return template


# --- Webhook management ---


class CreateWebhookRequest(BaseModel):
    name: Optional[str] = None
    events: list[str] = Field(default_factory=lambda: ["*"])


@router.post("/{workflow_id}/webhooks")
async def create_webhook(workflow_id: str, request: CreateWebhookRequest):
    """Create a webhook for a workflow."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    webhook_id = str(uuid.uuid4())
    webhook_secret = secrets.token_urlsafe(32)

    webhook = {
        "id": webhook_id,
        "workflow_id": workflow_id,
        "name": request.name or f"webhook-{webhook_id[:8]}",
        "secret": webhook_secret,
        "events": request.events,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            key = f"workflow_webhooks:{workflow_id}"
            if key not in state:
                state[key] = {}
            state[key][webhook_id] = webhook
    except Exception as e:
        logger.warning("Failed to persist webhook: %s", e)

    return webhook


@router.get("/{workflow_id}/webhooks")
async def list_webhooks(workflow_id: str):
    """List webhooks for a workflow."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    webhooks = {}
    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            key = f"workflow_webhooks:{workflow_id}"
            webhooks = state.get(key, {})
    except Exception as e:
        logger.debug("Failed to load webhooks from state store: %s", e)

    webhook_list = list(webhooks.values())
    return {"webhooks": webhook_list, "total": len(webhook_list)}


@router.delete("/{workflow_id}/webhooks/{webhook_id}")
async def delete_webhook(workflow_id: str, webhook_id: str):
    """Delete a webhook."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            key = f"workflow_webhooks:{workflow_id}"
            webhooks = state.get(key, {})
            if webhook_id not in webhooks:
                raise HTTPException(status_code=404, detail="Webhook not found")
            del webhooks[webhook_id]
            state[key] = webhooks
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Failed to delete webhook from state store: %s", e)
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"status": "deleted", "webhook_id": webhook_id}


@router.post("/{workflow_id}/webhooks/{webhook_id}/regenerate-secret")
async def regenerate_webhook_secret(workflow_id: str, webhook_id: str):
    """Regenerate webhook secret."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    new_secret = secrets.token_urlsafe(32)

    try:
        from backend.app.repositories.state.store import state_store
        with state_store.transaction() as state:
            key = f"workflow_webhooks:{workflow_id}"
            webhooks = state.get(key, {})
            if webhook_id not in webhooks:
                raise HTTPException(status_code=404, detail="Webhook not found")
            webhooks[webhook_id]["secret"] = new_secret
            state[key] = webhooks
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Failed to regenerate webhook secret: %s", e)
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"webhook_id": webhook_id, "secret": new_secret}


# --- Debug ---


class DebugWorkflowRequest(BaseModel):
    input_data: dict[str, Any] = Field(default_factory=dict)


@router.post("/{workflow_id}/debug")
async def debug_workflow(workflow_id: str, request: DebugWorkflowRequest):
    """Debug a workflow (dry run)."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        execution = await workflow_service.execute_workflow(
            workflow_id,
            input_data=request.input_data,
            async_execution=False,
        )
        return {
            "debug": True,
            "execution_id": execution.id,
            "status": execution.status.value,
            "node_results": [
                {
                    "node_id": r.node_id,
                    "status": r.status.value,
                    "output": r.output,
                    "error": r.error,
                }
                for r in execution.node_results
            ],
            "output_data": execution.output_data,
            "error": execution.error,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        logger.error("Debug workflow failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Debug execution failed.")

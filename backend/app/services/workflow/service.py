"""Workflow Service.

Core workflow management and execution service.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from backend.app.schemas.workflows.workflow import (
    CreateWorkflowRequest,
    ExecutionStatus,
    NodeExecutionResult,
    NodeType,
    TriggerType,
    UpdateWorkflowRequest,
    WorkflowEdge,
    WorkflowExecutionResponse,
    WorkflowNode,
    WorkflowResponse,
    WorkflowTrigger,
)

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


class WorkflowService:
    """Service for managing workflows."""

    def __init__(self):
        self._workflows: dict[str, dict] = {}
        self._executions: dict[str, dict] = {}
        self._pending_approvals: dict[str, dict] = {}
        self._running_tasks: set = set()

    def _safe_eval_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Safely evaluate a condition expression without using eval().

        Supports simple comparisons like:
        - "true" / "false"
        - "input.value > 10"
        - "input.status == 'active'"
        - "input.count >= 5 and input.enabled"
        """
        import re
        import operator

        condition_raw = condition.strip()
        condition_lower = condition_raw.lower()

        # Handle simple boolean literals
        if condition_lower in ("true", "1", "yes"):
            return True
        if condition_lower in ("false", "0", "no", ""):
            return False

        condition = condition_raw

        # Safe operators mapping
        ops = {
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            "<=": operator.le,
            ">": operator.gt,
            "<": operator.lt,
        }

        def get_value(path: str, ctx: dict) -> Any:
            """Safely get a nested value from context."""
            parts = path.strip().split(".")
            value = ctx
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value

        def parse_literal(s: str) -> Any:
            """Parse a literal value (string, number, bool)."""
            s = s.strip()
            if s.startswith(("'", '"')) and s.endswith(("'", '"')):
                return s[1:-1]
            if s.lower() == "true":
                return True
            if s.lower() == "false":
                return False
            if s.lower() == "none":
                return None
            try:
                if "." in s:
                    return float(s)
                return int(s)
            except ValueError:
                # Treat as context path
                return get_value(s, context)

        # Handle compound conditions (and/or)
        if " and " in condition:
            parts = condition.split(" and ")
            return all(self._safe_eval_condition(p.strip(), context) for p in parts)
        if " or " in condition:
            parts = condition.split(" or ")
            return any(self._safe_eval_condition(p.strip(), context) for p in parts)

        # Handle negation
        if condition.startswith("not "):
            return not self._safe_eval_condition(condition[4:].strip(), context)

        # Handle comparisons
        for op_str, op_func in ops.items():
            if op_str in condition:
                left, right = condition.split(op_str, 1)
                left_val = parse_literal(left)
                right_val = parse_literal(right)
                try:
                    return op_func(left_val, right_val)
                except (TypeError, ValueError):
                    return False

        # Handle simple truthiness check (e.g., "input.enabled")
        value = parse_literal(condition)
        return bool(value)

    async def create_workflow(
        self,
        request: CreateWorkflowRequest,
    ) -> WorkflowResponse:
        """Create a new workflow."""
        workflow_id = str(uuid.uuid4())
        now = _now()

        workflow = {
            "id": workflow_id,
            "name": request.name,
            "description": request.description,
            "nodes": [n.model_dump() for n in request.nodes],
            "edges": [e.model_dump() for e in request.edges],
            "triggers": [t.model_dump() for t in request.triggers],
            "is_active": request.is_active,
            "created_at": now,
            "updated_at": now,
            "last_run_at": None,
            "run_count": 0,
        }

        self._workflows[workflow_id] = workflow

        # Persist to state store
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                state["workflows"][workflow_id] = workflow
        except Exception as e:
            logger.warning(f"Failed to persist workflow to state store: {e}")

        return self._to_response(workflow)

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowResponse]:
        """Get a workflow by ID."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            # Try loading from state store
            try:
                from backend.app.repositories.state.store import state_store
                with state_store.transaction() as state:
                    workflow = state.get("workflows", {}).get(workflow_id)
                    if workflow:
                        self._workflows[workflow_id] = workflow
            except Exception as e:
                logger.debug("Failed to load workflow from state store: %s", e)

        if not workflow:
            return None
        return self._to_response(workflow)

    async def list_workflows(
        self,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[WorkflowResponse], int]:
        """List all workflows."""
        # Load from state store
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                self._workflows.update(state.get("workflows", {}))
        except Exception as e:
            logger.debug("Failed to load workflows from state store: %s", e)

        workflows = list(self._workflows.values())

        if active_only:
            workflows = [w for w in workflows if w.get("is_active")]

        workflows.sort(key=lambda w: w.get("updated_at", ""), reverse=True)
        total = len(workflows)
        workflows = workflows[offset:offset + limit]

        return [self._to_response(w) for w in workflows], total

    async def update_workflow(
        self,
        workflow_id: str,
        request: UpdateWorkflowRequest,
    ) -> Optional[WorkflowResponse]:
        """Update a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        if request.name is not None:
            workflow["name"] = request.name
        if request.description is not None:
            workflow["description"] = request.description
        if request.nodes is not None:
            workflow["nodes"] = [n.model_dump() for n in request.nodes]
        if request.edges is not None:
            workflow["edges"] = [e.model_dump() for e in request.edges]
        if request.triggers is not None:
            workflow["triggers"] = [t.model_dump() for t in request.triggers]
        if request.is_active is not None:
            workflow["is_active"] = request.is_active

        workflow["updated_at"] = _now()

        # Persist to state store
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                state["workflows"][workflow_id] = workflow
        except Exception as e:
            logger.warning(f"Failed to persist workflow update: {e}")

        return self._to_response(workflow)

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id not in self._workflows:
            return False

        del self._workflows[workflow_id]

        # Remove from state store
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                state["workflows"].pop(workflow_id, None)
        except Exception as e:
            logger.warning(f"Failed to delete workflow from state store: {e}")

        return True

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: dict[str, Any],
        async_execution: bool = True,
    ) -> WorkflowExecutionResponse:
        """Execute a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        execution_id = str(uuid.uuid4())
        now = _now()

        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": ExecutionStatus.PENDING.value,
            "input_data": input_data,
            "output_data": None,
            "node_results": [],
            "error": None,
            "started_at": now,
            "finished_at": None,
        }

        self._executions[execution_id] = execution

        # Update workflow stats
        workflow["last_run_at"] = now
        workflow["run_count"] = workflow.get("run_count", 0) + 1

        if async_execution:
            # Schedule async execution
            task = asyncio.create_task(self._run_workflow(execution_id, workflow, input_data))
            self._running_tasks.add(task)
            task.add_done_callback(self._running_tasks.discard)
        else:
            # Run synchronously
            await self._run_workflow(execution_id, workflow, input_data)
            execution = self._executions[execution_id]

        return self._execution_to_response(execution)

    async def _run_workflow(
        self,
        execution_id: str,
        workflow: dict,
        input_data: dict[str, Any],
    ) -> None:
        """Run workflow execution."""
        execution = self._executions[execution_id]
        execution["status"] = ExecutionStatus.RUNNING.value

        try:
            nodes = workflow.get("nodes", [])
            edges = workflow.get("edges", [])

            # Build execution order (topological sort)
            node_map = {n["id"]: n for n in nodes}
            incoming = {n["id"]: [] for n in nodes}
            outgoing = {n["id"]: [] for n in nodes}

            for edge in edges:
                outgoing[edge["source"]].append(edge["target"])
                incoming[edge["target"]].append(edge["source"])

            # Find start nodes (no incoming edges)
            queue = [nid for nid, inc in incoming.items() if not inc]
            enqueued = set(queue)
            context = {"input": input_data, "outputs": {}}

            while queue:
                node_id = queue.pop(0)
                node = node_map.get(node_id)
                if not node:
                    continue

                # Execute node
                result = await self._execute_node(node, context)
                execution["node_results"].append(result)

                if result["status"] == ExecutionStatus.FAILED.value:
                    execution["status"] = ExecutionStatus.FAILED.value
                    execution["error"] = result.get("error")
                    break

                if result["status"] == ExecutionStatus.WAITING_APPROVAL.value:
                    execution["status"] = ExecutionStatus.WAITING_APPROVAL.value
                    self._pending_approvals[execution_id] = {
                        "node_id": node_id,
                        "workflow_id": workflow["id"],
                    }
                    return

                # Store output for downstream nodes
                context["outputs"][node_id] = result.get("output", {})

                # Add downstream nodes to queue
                for target in outgoing.get(node_id, []):
                    if target in enqueued:
                        continue
                    # Check if all dependencies are satisfied
                    deps = incoming.get(target, [])
                    if all(d in context["outputs"] for d in deps):
                        queue.append(target)
                        enqueued.add(target)

            if execution["status"] == ExecutionStatus.RUNNING.value:
                execution["status"] = ExecutionStatus.COMPLETED.value
                execution["output_data"] = context["outputs"]

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution["status"] = ExecutionStatus.FAILED.value
            execution["error"] = "Workflow execution failed. Check logs for details."
            logger.error("Workflow execution %s failed: %s", execution_id, e, exc_info=True)

        finally:
            execution["finished_at"] = _now()

            # Persist execution
            try:
                from backend.app.repositories.state.store import state_store
                with state_store.transaction() as state:
                    state["workflow_executions"][execution_id] = execution
            except Exception as e:
                logger.error("Failed to persist execution %s: %s", execution_id, e)

    async def _execute_node(
        self,
        node: dict,
        context: dict[str, Any],
    ) -> dict:
        """Execute a single workflow node."""
        node_id = node["id"]
        node_type = node["type"]
        config = node.get("config", {})
        now = _now()

        result = {
            "node_id": node_id,
            "status": ExecutionStatus.RUNNING.value,
            "output": None,
            "error": None,
            "started_at": now,
            "finished_at": None,
        }

        try:
            if node_type == NodeType.TRIGGER.value:
                # Trigger node - pass input through
                result["output"] = context.get("input", {})

            elif node_type == NodeType.CONDITION.value:
                # Evaluate condition safely (no eval)
                condition = config.get("condition", "true")
                passed = self._safe_eval_condition(condition, context)
                result["output"] = {"passed": passed}

            elif node_type == NodeType.ACTION.value:
                # Execute action
                action_type = config.get("action_type", "log")
                if action_type == "log":
                    logger.info(f"Workflow action: {config.get('message', '')}")
                result["output"] = {"action": action_type, "executed": True}

            elif node_type == NodeType.EMAIL.value:
                # Send email (placeholder)
                result["output"] = {
                    "sent": True,
                    "to": config.get("to"),
                    "subject": config.get("subject"),
                }

            elif node_type == NodeType.APPROVAL.value:
                # Require approval
                result["status"] = ExecutionStatus.WAITING_APPROVAL.value
                result["output"] = {"awaiting_approval": True}
                return result

            elif node_type == NodeType.DATA_TRANSFORM.value:
                # Transform data
                transform = config.get("transform", {})
                result["output"] = {"transformed": True, "data": transform}

            elif node_type == NodeType.DELAY.value:
                # Wait for specified duration
                delay_ms = config.get("delay_ms", 1000)
                await asyncio.sleep(delay_ms / 1000)
                result["output"] = {"delayed": True, "duration_ms": delay_ms}

            elif node_type == NodeType.HTTP_REQUEST.value:
                # Make HTTP request
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    method = config.get("method", "GET")
                    url = config.get("url", "")
                    async with session.request(method, url) as resp:
                        result["output"] = {
                            "status_code": resp.status,
                            "body": await resp.text(),
                        }

            else:
                result["output"] = {"node_type": node_type, "executed": True}

            result["status"] = ExecutionStatus.COMPLETED.value

        except Exception as e:
            logger.error("Workflow node execution failed: %s", e, exc_info=True)
            result["status"] = ExecutionStatus.FAILED.value
            result["error"] = "Workflow node execution failed"

        finally:
            result["finished_at"] = _now()

        return result

    async def get_execution(
        self,
        execution_id: str,
    ) -> Optional[WorkflowExecutionResponse]:
        """Get execution status."""
        execution = self._executions.get(execution_id)
        if not execution:
            # Try loading from state store
            try:
                from backend.app.repositories.state.store import state_store
                with state_store.transaction() as state:
                    execution = state.get("workflow_executions", {}).get(execution_id)
            except Exception as e:
                logger.debug("Failed to load execution from state store: %s", e)

        if not execution:
            return None
        return self._execution_to_response(execution)

    async def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 50,
    ) -> list[WorkflowExecutionResponse]:
        """List workflow executions."""
        # Load from state store
        try:
            from backend.app.repositories.state.store import state_store
            with state_store.transaction() as state:
                self._executions.update(state.get("workflow_executions", {}))
        except Exception as e:
            logger.debug("Failed to load executions from state store: %s", e)

        executions = list(self._executions.values())

        if workflow_id:
            executions = [e for e in executions if e.get("workflow_id") == workflow_id]
        if status:
            executions = [e for e in executions if e.get("status") == status.value]

        executions.sort(key=lambda e: e.get("started_at", ""), reverse=True)
        executions = executions[:limit]

        return [self._execution_to_response(e) for e in executions]

    async def approve_execution(
        self,
        execution_id: str,
        node_id: str,
        approved: bool,
        comment: Optional[str] = None,
    ) -> Optional[WorkflowExecutionResponse]:
        """Approve or reject a pending approval."""
        approval = self._pending_approvals.get(execution_id)
        if not approval or approval.get("node_id") != node_id:
            return None

        execution = self._executions.get(execution_id)
        if not execution:
            return None

        del self._pending_approvals[execution_id]

        if approved:
            # Continue execution
            workflow = self._workflows.get(execution["workflow_id"])
            if workflow:
                task = asyncio.create_task(
                    self._run_workflow(execution_id, workflow, execution["input_data"])
                )
                self._running_tasks.add(task)
                task.add_done_callback(self._running_tasks.discard)
        else:
            execution["status"] = ExecutionStatus.CANCELLED.value
            execution["error"] = f"Rejected: {comment or 'No reason provided'}"
            execution["finished_at"] = _now()

        return self._execution_to_response(execution)

    async def get_pending_approvals(
        self,
        workflow_id: Optional[str] = None,
    ) -> list[dict]:
        """Get pending approvals."""
        approvals = []
        for exec_id, approval in self._pending_approvals.items():
            if workflow_id and approval.get("workflow_id") != workflow_id:
                continue
            execution = self._executions.get(exec_id)
            if execution:
                approvals.append({
                    "execution_id": exec_id,
                    "workflow_id": approval["workflow_id"],
                    "node_id": approval["node_id"],
                    "requested_at": execution.get("started_at"),
                })
        return approvals

    def _to_response(self, workflow: dict) -> WorkflowResponse:
        """Convert workflow dict to response model."""
        return WorkflowResponse(
            id=workflow["id"],
            name=workflow["name"],
            description=workflow.get("description"),
            nodes=[WorkflowNode(**n) for n in workflow.get("nodes", [])],
            edges=[WorkflowEdge(**e) for e in workflow.get("edges", [])],
            triggers=[WorkflowTrigger(**t) for t in workflow.get("triggers", [])],
            is_active=workflow.get("is_active", True),
            created_at=workflow["created_at"],
            updated_at=workflow["updated_at"],
            last_run_at=workflow.get("last_run_at"),
            run_count=workflow.get("run_count", 0),
        )

    def _execution_to_response(self, execution: dict) -> WorkflowExecutionResponse:
        """Convert execution dict to response model."""
        return WorkflowExecutionResponse(
            id=execution["id"],
            workflow_id=execution["workflow_id"],
            status=ExecutionStatus(execution["status"]),
            input_data=execution.get("input_data", {}),
            output_data=execution.get("output_data"),
            node_results=[
                NodeExecutionResult(**r) for r in execution.get("node_results", [])
            ],
            error=execution.get("error"),
            started_at=execution["started_at"],
            finished_at=execution.get("finished_at"),
        )


# Singleton instance
workflow_service = WorkflowService()

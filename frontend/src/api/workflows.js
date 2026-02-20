/**
 * Workflows API Client
 * Handles workflow automation, triggers, and execution.
 */
import { api } from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

// ============================================
// Workflow CRUD
// ============================================

export async function createWorkflow(data) {
  const response = await api.post('/workflows', data);
  return response.data;
}

export async function getWorkflow(workflowId) {
  const response = await api.get(`/workflows/${workflowId}`);
  return response.data;
}

export async function updateWorkflow(workflowId, data) {
  const response = await api.put(`/workflows/${workflowId}`, data);
  return response.data;
}

export async function deleteWorkflow(workflowId) {
  const response = await api.delete(`/workflows/${workflowId}`);
  return response.data;
}

export async function listWorkflows(params = {}) {
  const response = await api.get('/workflows', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { workflows: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const workflows = asArray(payload, ['workflows', 'items', 'results']);
    return { ...payload, workflows, total: payload.total ?? workflows.length };
  }
  return { workflows: [], total: 0 };
}

// ============================================
// Workflow Execution
// ============================================

export async function executeWorkflow(workflowId, inputs = {}) {
  const response = await api.post(`/workflows/${workflowId}/execute`, { input_data: inputs });
  return response.data;
}

export async function getExecution(workflowId, executionId) {
  const response = await api.get(`/workflows/executions/${executionId}`);
  return response.data;
}

export async function listExecutions(workflowId, params = {}) {
  const response = await api.get(`/workflows/${workflowId}/executions`, { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { executions: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const executions = asArray(payload, ['executions', 'items', 'results']);
    return { ...payload, executions, total: payload.total ?? executions.length };
  }
  return { executions: [], total: 0 };
}

export async function cancelExecution(workflowId, executionId) {
  const response = await api.post(`/workflows/${workflowId}/executions/${executionId}/cancel`);
  return response.data;
}

export async function retryExecution(workflowId, executionId) {
  const response = await api.post(`/workflows/${workflowId}/executions/${executionId}/retry`);
  return response.data;
}

// ============================================
// Triggers
// ============================================

export async function addTrigger(workflowId, trigger) {
  const response = await api.post(`/workflows/${workflowId}/trigger`, {
    trigger_type: trigger.type || trigger.trigger_type,
    config: trigger.config || {},
  });
  return response.data;
}

export async function updateTrigger(workflowId, triggerId, data) {
  const response = await api.put(`/workflows/${workflowId}/triggers/${triggerId}`, data);
  return response.data;
}

export async function deleteTrigger(workflowId, triggerId) {
  const response = await api.delete(`/workflows/${workflowId}/triggers/${triggerId}`);
  return response.data;
}

export async function enableTrigger(workflowId, triggerId) {
  const response = await api.post(`/workflows/${workflowId}/triggers/${triggerId}/enable`);
  return response.data;
}

export async function disableTrigger(workflowId, triggerId) {
  const response = await api.post(`/workflows/${workflowId}/triggers/${triggerId}/disable`);
  return response.data;
}

// ============================================
// Node Types
// ============================================

export async function listNodeTypes() {
  const response = await api.get('/workflows/node-types');
  const payload = response.data;
  return asArray(payload, ['node_types', 'types', 'items', 'results']);
}

export async function getNodeTypeSchema(nodeType) {
  const response = await api.get(`/workflows/node-types/${nodeType}/schema`);
  return response.data;
}

// ============================================
// Templates
// ============================================

export async function listWorkflowTemplates(params = {}) {
  const response = await api.get('/workflows/templates', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { templates: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const templates = asArray(payload, ['templates', 'workflows', 'items', 'results']);
    return { ...payload, templates, total: payload.total ?? templates.length };
  }
  return { templates: [], total: 0 };
}

export async function createFromTemplate(templateId, name) {
  const response = await api.post(`/workflows/templates/${templateId}/create`, { name });
  return response.data;
}

export async function saveAsTemplate(workflowId, name, description = null) {
  const response = await api.post(`/workflows/${workflowId}/save-as-template`, { name, description });
  return response.data;
}

// ============================================
// Approval Workflows
// ============================================

export async function getPendingApprovals(params = {}) {
  const response = await api.get('/workflows/approvals/pending', { params });
  return response.data;
}

export async function approveStep(executionId, stepId, comment = null) {
  const response = await api.post(`/workflows/executions/${executionId}/approve`, {
    execution_id: executionId,
    node_id: stepId,
    approved: true,
    comment,
  });
  return response.data;
}

export async function rejectStep(executionId, stepId, reason) {
  const response = await api.post(`/workflows/executions/${executionId}/approve`, {
    execution_id: executionId,
    node_id: stepId,
    approved: false,
    comment: reason,
  });
  return response.data;
}

// ============================================
// Webhooks
// ============================================

export async function createWebhook(workflowId, config) {
  const response = await api.post(`/workflows/${workflowId}/webhooks`, config);
  return response.data;
}

export async function listWebhooks(workflowId) {
  const response = await api.get(`/workflows/${workflowId}/webhooks`);
  return asArray(response.data, ['webhooks', 'items', 'results']);
}

export async function deleteWebhook(workflowId, webhookId) {
  const response = await api.delete(`/workflows/${workflowId}/webhooks/${webhookId}`);
  return response.data;
}

export async function regenerateWebhookSecret(workflowId, webhookId) {
  const response = await api.post(`/workflows/${workflowId}/webhooks/${webhookId}/regenerate-secret`);
  return response.data;
}

// ============================================
// Logs & Debugging
// ============================================

export async function getExecutionLogs(workflowId, executionId, params = {}) {
  const response = await api.get(`/workflows/${workflowId}/executions/${executionId}/logs`, { params });
  return response.data;
}

export async function debugWorkflow(workflowId, nodeId, testData) {
  const response = await api.post(`/workflows/${workflowId}/debug`, {
    node_id: nodeId,
    test_data: testData,
  });
  return response.data;
}

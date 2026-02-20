/**
 * Workflow Store - Zustand store for workflow automation.
 */
import { create } from 'zustand';
import * as workflowsApi from '../api/workflows';

const useWorkflowStore = create((set, get) => ({
  // State
  workflows: [],
  currentWorkflow: null,
  executions: [],
  currentExecution: null,
  nodeTypes: [],
  pendingApprovals: [],
  loading: false,
  executing: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Workflow CRUD
  fetchWorkflows: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowsApi.listWorkflows(params);
      set({ workflows: response.workflows || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  createWorkflow: async (data) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowsApi.createWorkflow(data);
      set((state) => ({
        workflows: [workflow, ...state.workflows].slice(0, 200),
        currentWorkflow: workflow,
        loading: false,
      }));
      return workflow;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getWorkflow: async (workflowId) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowsApi.getWorkflow(workflowId);
      set({ currentWorkflow: workflow, loading: false });
      return workflow;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  updateWorkflow: async (workflowId, data) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowsApi.updateWorkflow(workflowId, data);
      set((state) => ({
        workflows: state.workflows.map((w) => (w.id === workflowId ? workflow : w)),
        currentWorkflow: state.currentWorkflow?.id === workflowId ? workflow : state.currentWorkflow,
        loading: false,
      }));
      return workflow;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteWorkflow: async (workflowId) => {
    set({ loading: true, error: null });
    try {
      await workflowsApi.deleteWorkflow(workflowId);
      set((state) => ({
        workflows: state.workflows.filter((w) => w.id !== workflowId),
        currentWorkflow: state.currentWorkflow?.id === workflowId ? null : state.currentWorkflow,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Execution
  executeWorkflow: async (workflowId, inputs = {}) => {
    set({ executing: true, error: null });
    try {
      const execution = await workflowsApi.executeWorkflow(workflowId, inputs);
      set((state) => ({
        executions: [execution, ...state.executions].slice(0, 200),
        currentExecution: execution,
        executing: false,
      }));
      return execution;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  fetchExecutions: async (workflowId, params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowsApi.listExecutions(workflowId, params);
      set({ executions: response.executions || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getExecution: async (workflowId, executionId) => {
    set({ loading: true, error: null });
    try {
      const execution = await workflowsApi.getExecution(workflowId, executionId);
      set({ currentExecution: execution, loading: false });
      return execution;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  cancelExecution: async (workflowId, executionId) => {
    try {
      await workflowsApi.cancelExecution(workflowId, executionId);
      set((state) => ({
        executions: state.executions.map((e) =>
          e.id === executionId ? { ...e, status: 'cancelled' } : e
        ),
        currentExecution: state.currentExecution?.id === executionId
          ? { ...state.currentExecution, status: 'cancelled' }
          : state.currentExecution,
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  retryExecution: async (workflowId, executionId) => {
    set({ executing: true, error: null });
    try {
      const execution = await workflowsApi.retryExecution(workflowId, executionId);
      set((state) => ({
        executions: state.executions.map((e) => (e.id === executionId ? execution : e)),
        currentExecution: state.currentExecution?.id === executionId ? execution : state.currentExecution,
        executing: false,
      }));
      return execution;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Triggers
  addTrigger: async (workflowId, trigger) => {
    set({ loading: true, error: null });
    try {
      const result = await workflowsApi.addTrigger(workflowId, trigger);
      await get().getWorkflow(workflowId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteTrigger: async (workflowId, triggerId) => {
    set({ loading: true, error: null });
    try {
      await workflowsApi.deleteTrigger(workflowId, triggerId);
      await get().getWorkflow(workflowId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  enableTrigger: async (workflowId, triggerId) => {
    try {
      await workflowsApi.enableTrigger(workflowId, triggerId);
      await get().getWorkflow(workflowId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  disableTrigger: async (workflowId, triggerId) => {
    try {
      await workflowsApi.disableTrigger(workflowId, triggerId);
      await get().getWorkflow(workflowId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  updateTrigger: async (workflowId, triggerId, data) => {
    set({ loading: true, error: null });
    try {
      const result = await workflowsApi.updateTrigger(workflowId, triggerId, data);
      await get().getWorkflow(workflowId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Node Types
  fetchNodeTypes: async () => {
    try {
      const types = await workflowsApi.listNodeTypes();
      set({ nodeTypes: types || [] });
      return types;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  getNodeTypeSchema: async (nodeType) => {
    try {
      const schema = await workflowsApi.getNodeTypeSchema(nodeType);
      return schema;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Approvals
  fetchPendingApprovals: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowsApi.getPendingApprovals(params);
      set({ pendingApprovals: response.approvals || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  approveStep: async (executionId, stepId, comment = null) => {
    set({ loading: true, error: null });
    try {
      const result = await workflowsApi.approveStep(executionId, stepId, comment);
      set((state) => ({
        pendingApprovals: state.pendingApprovals.filter(
          (a) => !(a.execution_id === executionId && a.step_id === stepId)
        ),
        loading: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  rejectStep: async (executionId, stepId, reason) => {
    set({ loading: true, error: null });
    try {
      const result = await workflowsApi.rejectStep(executionId, stepId, reason);
      set((state) => ({
        pendingApprovals: state.pendingApprovals.filter(
          (a) => !(a.execution_id === executionId && a.step_id === stepId)
        ),
        loading: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Templates
  createFromTemplate: async (templateId, name) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowsApi.createFromTemplate(templateId, name);
      set((state) => ({
        workflows: [workflow, ...state.workflows].slice(0, 200),
        currentWorkflow: workflow,
        loading: false,
      }));
      return workflow;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  saveAsTemplate: async (workflowId, name, description = null) => {
    try {
      const result = await workflowsApi.saveAsTemplate(workflowId, name, description);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  listWorkflowTemplates: async () => {
    set({ loading: true, error: null });
    try {
      const templates = await workflowsApi.listWorkflowTemplates();
      set({ loading: false });
      return templates;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Webhooks
  createWebhook: async (workflowId, data) => {
    set({ loading: true, error: null });
    try {
      const webhook = await workflowsApi.createWebhook(workflowId, data);
      set({ loading: false });
      return webhook;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  listWebhooks: async (workflowId) => {
    try {
      const webhooks = await workflowsApi.listWebhooks(workflowId);
      return webhooks;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  deleteWebhook: async (workflowId, webhookId) => {
    set({ loading: true, error: null });
    try {
      await workflowsApi.deleteWebhook(workflowId, webhookId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  regenerateWebhookSecret: async (workflowId, webhookId) => {
    try {
      const result = await workflowsApi.regenerateWebhookSecret(workflowId, webhookId);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Execution Logs
  getExecutionLogs: async (workflowId, executionId) => {
    try {
      const logs = await workflowsApi.getExecutionLogs(workflowId, executionId);
      return logs;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Debug
  debugWorkflow: async (workflowId, nodeId, testData) => {
    try {
      const result = await workflowsApi.debugWorkflow(workflowId, nodeId, testData);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Reset
  reset: () => set({
    currentWorkflow: null,
    executions: [],
    currentExecution: null,
    error: null,
  }),

  clearWorkflows: () => set({
    workflows: [],
    currentWorkflow: null,
    executions: [],
  }),
}));

export default useWorkflowStore;

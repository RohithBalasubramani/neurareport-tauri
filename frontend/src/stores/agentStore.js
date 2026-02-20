/**
 * Agent Store - Zustand store for AI agents.
 */
import { create } from 'zustand';
import * as agentsApi from '../api/agents';
import * as agentsV2Api from '../api/agentsV2';

const taskIdentifier = (task) => task?.id || task?.task_id || null;

const useAgentStore = create((set, get) => ({
  // State
  tasks: [],
  currentTask: null,
  agentTypes: [],
  repurposeFormats: [],
  loading: false,
  executing: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Research Agent
  runResearch: async (topic, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsApi.runResearchAgent(topic, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Data Analyst Agent
  runDataAnalysis: async (question, data, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsApi.runDataAnalystAgent(question, data, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Email Draft Agent
  runEmailDraft: async (context, purpose, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsApi.runEmailDraftAgent(context, purpose, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Content Repurpose Agent
  runContentRepurpose: async (content, sourceFormat, targetFormats, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsApi.runContentRepurposeAgent(content, sourceFormat, targetFormats, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Proofreading Agent
  runProofreading: async (text, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsApi.runProofreadingAgent(text, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Report Analyst Agent
  runReportAnalyst: async (runId, options = {}) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsV2Api.runReportAnalystAgent(runId, options);
      set((state) => ({
        tasks: [task, ...state.tasks].slice(0, 200),
        currentTask: task,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Generate Report from Agent Task
  generateReportFromTask: async (taskId, config = {}) => {
    set({ executing: true, error: null });
    try {
      const result = await agentsV2Api.generateReportFromTask(taskId, config);
      set({ executing: false });
      return result;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  // Task Management
  fetchTasks: async (agentType = null) => {
    set({ loading: true, error: null });
    try {
      const tasks = await agentsApi.listTasks(agentType);
      set({ tasks, loading: false });
      return tasks;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getTask: async (taskId) => {
    set({ loading: true, error: null });
    try {
      const task = await agentsApi.getTask(taskId);
      set({ currentTask: task, loading: false });
      return task;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Utility
  fetchAgentTypes: async () => {
    try {
      const response = await agentsApi.listAgentTypes();
      set({ agentTypes: response.types || [] });
      return response.types;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  fetchRepurposeFormats: async () => {
    try {
      const response = await agentsApi.listRepurposeFormats();
      set({ repurposeFormats: response.formats || [] });
      return response.formats;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // V2 Task Management
  cancelTask: async (taskId) => {
    try {
      await agentsV2Api.cancelTask(taskId);
      set((state) => ({
        tasks: state.tasks.map((t) =>
          taskIdentifier(t) === taskId ? { ...t, status: 'cancelled' } : t
        ),
        currentTask: taskIdentifier(state.currentTask) === taskId
          ? { ...state.currentTask, status: 'cancelled' }
          : state.currentTask,
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  retryTask: async (taskId) => {
    set({ executing: true, error: null });
    try {
      const task = await agentsV2Api.retryTask(taskId);
      set((state) => ({
        tasks: state.tasks.map((t) => (taskIdentifier(t) === taskId ? task : t)),
        currentTask: taskIdentifier(state.currentTask) === taskId ? task : state.currentTask,
        executing: false,
      }));
      return task;
    } catch (err) {
      set({ error: err.message, executing: false });
      return null;
    }
  },

  getTaskEvents: async (taskId) => {
    try {
      const events = await agentsV2Api.getTaskEvents(taskId);
      return events;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  getAgentStats: async () => {
    try {
      const stats = await agentsV2Api.getStats();
      return stats;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  streamTaskProgress: async (taskId, onEvent) => {
    try {
      return await agentsV2Api.streamTaskProgress(taskId, onEvent);
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Reset
  reset: () => set({
    currentTask: null,
    error: null,
  }),

  clearTasks: () => set({
    tasks: [],
    currentTask: null,
  }),
}));

export default useAgentStore;

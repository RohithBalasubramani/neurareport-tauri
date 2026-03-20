/**
 * Pipeline Store - Zustand store for pipeline/crew stage tracking.
 */
import { create } from 'zustand';
import * as agentsV2Api from '../api/agentsV2';

const usePipelineStore = create((set, get) => ({
  // State
  activePipelines: {},     // { pipelineId: { stages: [...], currentStage, status, result, error } }
  pipelineHistory: [],     // completed pipelines (newest first, max 200)
  loading: false,
  error: null,

  // Actions
  startPipeline: (pipelineId, stages) => {
    set((state) => ({
      activePipelines: {
        ...state.activePipelines,
        [pipelineId]: {
          stages: stages.map((s, i) => ({
            index: i,
            label: s.label || s,
            agent: s.agent || null,
            status: 'pending',
            output: null,
            startedAt: null,
            completedAt: null,
          })),
          currentStage: 0,
          status: 'running',
          result: null,
          error: null,
          startedAt: new Date().toISOString(),
        },
      },
    }));
  },

  updateStage: (pipelineId, stageIndex, status, output = null) => {
    set((state) => {
      const pipeline = state.activePipelines[pipelineId];
      if (!pipeline) return state;

      const stages = [...pipeline.stages];
      stages[stageIndex] = {
        ...stages[stageIndex],
        status,
        output,
        ...(status === 'in_progress' ? { startedAt: new Date().toISOString() } : {}),
        ...(status === 'completed' || status === 'failed' ? { completedAt: new Date().toISOString() } : {}),
      };

      return {
        activePipelines: {
          ...state.activePipelines,
          [pipelineId]: {
            ...pipeline,
            stages,
            currentStage: status === 'completed' ? stageIndex + 1 : stageIndex,
          },
        },
      };
    });
  },

  completePipeline: (pipelineId, result) => {
    set((state) => {
      const pipeline = state.activePipelines[pipelineId];
      if (!pipeline) return state;

      const completed = {
        ...pipeline,
        status: 'completed',
        result,
        completedAt: new Date().toISOString(),
      };

      const { [pipelineId]: _, ...remaining } = state.activePipelines;
      return {
        activePipelines: remaining,
        pipelineHistory: [completed, ...state.pipelineHistory].slice(0, 200),
      };
    });
  },

  failPipeline: (pipelineId, error) => {
    set((state) => {
      const pipeline = state.activePipelines[pipelineId];
      if (!pipeline) return state;

      const failed = {
        ...pipeline,
        status: 'failed',
        error,
        completedAt: new Date().toISOString(),
      };

      const { [pipelineId]: _, ...remaining } = state.activePipelines;
      return {
        activePipelines: remaining,
        pipelineHistory: [failed, ...state.pipelineHistory].slice(0, 200),
      };
    });
  },

  streamPipelineProgress: async (taskId, onEvent) => {
    try {
      return await agentsV2Api.streamTaskProgress(taskId, (event) => {
        if (event.stage_index !== undefined) {
          get().updateStage(taskId, event.stage_index, event.status, event.output);
        }
        if (event.status === 'completed') {
          get().completePipeline(taskId, event.result);
        }
        if (event.status === 'failed') {
          get().failPipeline(taskId, event.error);
        }
        if (onEvent) onEvent(event);
      });
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Reset
  clearHistory: () => set({ pipelineHistory: [] }),
  clearError: () => set({ error: null }),
}));

export default usePipelineStore;

/**
 * Chart Store - Zustand store for chart analysis and generation.
 */
import { create } from 'zustand';
import * as chartsApi from '../api/charts';

const useChartStore = create((set) => ({
  // State
  chartData: null,
  analysisResult: null,
  loading: false,
  generating: false,
  error: null,

  // Actions
  setError: (error) => set({ error }),

  // Data Analysis
  analyzeData: async (data, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await chartsApi.analyzeData(data, options);
      set({ analysisResult: result, loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  queueAnalyzeData: async (data, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await chartsApi.queueAnalyzeData(data, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Chart Generation
  generateChart: async (data, chartType, options = {}) => {
    set({ generating: true, error: null });
    try {
      const result = await chartsApi.generateChart(data, chartType, options);
      set({ chartData: result, generating: false });
      return result;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  queueGenerateChart: async (data, chartType, options = {}) => {
    set({ generating: true, error: null });
    try {
      const result = await chartsApi.queueGenerateChart(data, chartType, options);
      set({ generating: false });
      return result;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  // Reset
  clearChart: () => set({ chartData: null, analysisResult: null, error: null }),

  reset: () => set({
    chartData: null,
    analysisResult: null,
    error: null,
  }),
}));

export default useChartStore;

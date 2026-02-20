/**
 * Executive Summary Store
 */
import { create } from 'zustand';
import * as summaryApi from '../api/summary';

const useSummaryStore = create((set) => ({
  // State
  summary: null,
  loading: false,
  error: null,
  history: [], // Keep track of recent summaries

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Generate a summary from content
  generateSummary: async ({ content, tone = 'formal', maxSentences = 5, focusAreas }) => {
    set({ loading: true, error: null });
    try {
      const response = await summaryApi.generateSummary({
        content,
        tone,
        maxSentences,
        focusAreas,
      });
      const summary = response.summary;
      set((state) => ({
        summary,
        history: [
          {
            id: Date.now(),
            summary,
            tone,
            maxSentences,
            focusAreas,
            contentPreview: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
            createdAt: new Date().toISOString(),
          },
          ...state.history.slice(0, 9), // Keep last 10
        ],
        loading: false,
      }));
      return summary;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Queue a summary job in the background
  queueSummary: async ({ content, tone = 'formal', maxSentences = 5, focusAreas }) => {
    set({ error: null });
    try {
      const response = await summaryApi.queueSummary({
        content,
        tone,
        maxSentences,
        focusAreas,
      });
      return response;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Get summary for a specific report
  getReportSummary: async (reportId) => {
    set({ loading: true, error: null });
    try {
      const response = await summaryApi.getReportSummary(reportId);
      set({ summary: response.summary, loading: false });
      return response.summary;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Queue report summary generation
  queueReportSummary: async (reportId) => {
    set({ error: null });
    try {
      const response = await summaryApi.queueReportSummary(reportId);
      return response;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Clear the current summary
  clearSummary: () => set({ summary: null, error: null }),

  // Clear history
  clearHistory: () => set({ history: [] }),

  // Reset state
  reset: () => set({
    summary: null,
    error: null,
  }),
}));

export default useSummaryStore;

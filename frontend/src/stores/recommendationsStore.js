/**
 * Recommendations Store - Zustand store for content recommendations.
 */
import { create } from 'zustand';
import * as recommendationsApi from '../api/recommendations';

const useRecommendationsStore = create((set) => ({
  // State
  recommendations: [],
  loading: false,
  error: null,

  // Actions
  setError: (error) => set({ error }),

  getRecommendations: async (context = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await recommendationsApi.getRecommendations(context);
      set({ recommendations: result.recommendations || [], loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  queueRecommendations: async (context = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await recommendationsApi.queueRecommendations(context);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  reset: () => set({
    recommendations: [],
    error: null,
  }),
}));

export default useRecommendationsStore;

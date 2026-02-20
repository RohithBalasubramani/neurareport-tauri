/**
 * Data Enrichment Store
 */
import { create } from 'zustand';
import * as enrichmentApi from '../api/enrichment';

const useEnrichmentStore = create((set, get) => ({
  // State
  sources: [],
  customSources: [],
  cacheStats: null,
  previewResult: null,
  enrichmentResult: null,
  loading: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch available sources
  fetchSources: async () => {
    set({ loading: true, error: null });
    try {
      const response = await enrichmentApi.getEnrichmentSources();
      const fetchedSources = Array.isArray(response.sources) ? response.sources : [];
      const builtInSources = [];
      const customSources = [];
      fetchedSources.forEach((source) => {
        const isCustom = Boolean(
          source?.created_at ||
          source?.updated_at ||
          source?.cache_ttl_hours !== undefined ||
          source?.config
        );
        if (isCustom) {
          customSources.push(source);
        } else {
          builtInSources.push(source);
        }
      });
      set({ sources: builtInSources, customSources, loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  // Create custom source
  createSource: async ({ name, type, description, config, cacheTtlHours }) => {
    set({ loading: true, error: null });
    try {
      const response = await enrichmentApi.createSource({ name, type, description, config, cacheTtlHours });
      const newSource = response.source;
      set((state) => ({
        customSources: [
          ...state.customSources.filter((source) => source.id !== newSource.id),
          newSource,
        ].slice(0, 200),
        loading: false,
      }));
      return newSource;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Delete custom source
  deleteSource: async (sourceId) => {
    set({ loading: true, error: null });
    try {
      await enrichmentApi.deleteSource(sourceId);
      set((state) => ({
        customSources: state.customSources.filter((s) => s.id !== sourceId),
        sources: state.sources.filter((s) => s.id !== sourceId),
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Fetch cache stats
  fetchCacheStats: async () => {
    try {
      const response = await enrichmentApi.getCacheStats();
      set({ cacheStats: response.stats });
      return response.stats;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Clear cache
  clearCache: async (sourceId = null) => {
    set({ loading: true, error: null });
    try {
      const response = await enrichmentApi.clearCache(sourceId);
      // Refresh stats after clearing
      await get().fetchCacheStats();
      set({ loading: false });
      return response.cleared_entries;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Preview enrichment
  previewEnrichment: async (data, sources, sampleSize = 5) => {
    set({ loading: true, error: null, previewResult: null });
    try {
      const response = await enrichmentApi.previewEnrichment({ data, sources, sampleSize });
      set({ previewResult: response, loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Enrich data
  enrichData: async (data, sources, options = {}) => {
    set({ loading: true, error: null, enrichmentResult: null });
    try {
      const response = await enrichmentApi.enrichData({ data, sources, options });
      set({ enrichmentResult: response, loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset state
  reset: () => set({
    previewResult: null,
    enrichmentResult: null,
    error: null,
  }),
}));

export default useEnrichmentStore;

/**
 * Search Store - Zustand store for search and discovery.
 */
import { create } from 'zustand';
import * as searchApi from '../api/search';

const useSearchStore = create((set, get) => ({
  // State
  results: [],
  totalResults: 0,
  facets: {},
  savedSearches: [],
  currentSearch: null,
  searchHistory: [],
  analytics: null,
  loading: false,
  searching: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Core Search
  search: async (query, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await searchApi.search(query, options);
      set((state) => ({
        results: response.results || [],
        totalResults: response.total || 0,
        facets: response.facets || {},
        searchHistory: [
          { query, timestamp: new Date().toISOString(), resultCount: response.total },
          ...state.searchHistory.slice(0, 49),
        ],
        searching: false,
      }));
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  semanticSearch: async (query, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await searchApi.semanticSearch(query, options);
      set({
        results: response.results || [],
        totalResults: response.results?.length || 0,
        searching: false,
      });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  regexSearch: async (pattern, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await searchApi.regexSearch(pattern, options);
      set({
        results: response.results || [],
        totalResults: response.results?.length || 0,
        searching: false,
      });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  booleanSearch: async (query, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await searchApi.booleanSearch(query, options);
      set({
        results: response.results || [],
        totalResults: response.results?.length || 0,
        searching: false,
      });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  // Search & Replace
  searchAndReplace: async (searchQuery, replaceWith, options = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await searchApi.searchAndReplace(searchQuery, replaceWith, options);
      set({ loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Similar Documents
  findSimilar: async (documentId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await searchApi.findSimilar(documentId, options);
      set({ loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Saved Searches
  saveSearch: async (name, query, options = {}) => {
    set({ loading: true, error: null });
    try {
      const savedSearch = await searchApi.saveSearch(name, query, options);
      set((state) => ({
        savedSearches: [savedSearch, ...state.savedSearches],
        loading: false,
      }));
      return savedSearch;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchSavedSearches: async () => {
    set({ loading: true, error: null });
    try {
      const searches = await searchApi.listSavedSearches();
      set({ savedSearches: searches || [], loading: false });
      return searches;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  deleteSavedSearch: async (searchId) => {
    set({ loading: true, error: null });
    try {
      await searchApi.deleteSavedSearch(searchId);
      set((state) => ({
        savedSearches: state.savedSearches.filter((s) => s.id !== searchId),
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  runSavedSearch: async (searchId) => {
    set({ searching: true, error: null });
    try {
      const response = await searchApi.runSavedSearch(searchId);
      set({
        results: response.results || [],
        totalResults: response.total || 0,
        searching: false,
      });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  // Analytics
  fetchAnalytics: async (options = {}) => {
    set({ loading: true, error: null });
    try {
      const analytics = await searchApi.getSearchAnalytics(options);
      set({ analytics, loading: false });
      return analytics;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Indexing
  indexDocument: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const result = await searchApi.indexDocument(documentId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  removeFromIndex: async (documentId) => {
    set({ loading: true, error: null });
    try {
      await searchApi.removeFromIndex(documentId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  reindexAll: async () => {
    set({ loading: true, error: null });
    try {
      const result = await searchApi.reindexAll();
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getSavedSearch: async (searchId) => {
    set({ loading: true, error: null });
    try {
      const search = await searchApi.getSavedSearch(searchId);
      set({ currentSearch: search, loading: false });
      return search;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  clearResults: () => set({
    results: [],
    totalResults: 0,
    facets: {},
    error: null,
  }),

  clearHistory: () => set({
    searchHistory: [],
  }),

  reset: () => set({
    results: [],
    totalResults: 0,
    facets: {},
    currentSearch: null,
    error: null,
  }),
}));

export default useSearchStore;

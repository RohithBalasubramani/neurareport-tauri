/**
 * Zustand store for Natural Language to SQL feature
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import * as nl2sqlApi from '../api/nl2sql'

const useQueryStore = create(
  persist(
    (set, get) => ({
      // Current query state
      currentQuestion: '',
      generatedSQL: '',
      explanation: '',
      confidence: 0,
      warnings: [],

      // Results
      results: null,
      columns: [],
      totalCount: null,
      executionTimeMs: null,

      // Execution options
      includeTotal: false,

      // UI state
      isGenerating: false,
      isExecuting: false,
      error: null,

      // Saved queries
      savedQueries: [],

      // History
      queryHistory: [],

      // Selected connection
      selectedConnectionId: null,
      selectedTables: [],

      // Actions
      setCurrentQuestion: (question) => set({ currentQuestion: question }),

      setGeneratedSQL: (sql) => set({ generatedSQL: sql }),

      setSelectedConnection: (connectionId) => set({ selectedConnectionId: connectionId, selectedTables: [] }),

      setSelectedTables: (tables) => set({ selectedTables: tables }),

      setGenerationResult: ({ sql, explanation, confidence, warnings, originalQuestion }) =>
        set({
          generatedSQL: sql,
          explanation,
          confidence,
          warnings: warnings || [],
          currentQuestion: originalQuestion,
          error: null,
        }),

      setExecutionResult: ({ columns, rows, rowCount, totalCount, executionTimeMs, truncated }) =>
        set({
          results: rows,
          columns,
          totalCount,
          executionTimeMs,
          error: null,
        }),

      setIncludeTotal: (includeTotal) => set({ includeTotal: Boolean(includeTotal) }),

      setError: (error) => set({ error, isGenerating: false, isExecuting: false }),

      setIsGenerating: (isGenerating) => set({ isGenerating }),

      setIsExecuting: (isExecuting) => set({ isExecuting }),

      clearResults: () =>
        set({
          results: null,
          columns: [],
          totalCount: null,
          executionTimeMs: null,
        }),

      clearAll: () =>
        set({
          currentQuestion: '',
          generatedSQL: '',
          explanation: '',
          confidence: 0,
          warnings: [],
          results: null,
          columns: [],
          totalCount: null,
          executionTimeMs: null,
          error: null,
        }),

      setSavedQueries: (queries) => set({ savedQueries: queries }),

      addSavedQuery: (query) =>
        set((state) => ({
          savedQueries: [query, ...state.savedQueries],
        })),

      removeSavedQuery: (queryId) =>
        set((state) => ({
          savedQueries: state.savedQueries.filter((q) => q.id !== queryId),
        })),

      setQueryHistory: (history) => set({ queryHistory: history }),

      addToHistory: (entry) =>
        set((state) => ({
          queryHistory: [entry, ...state.queryHistory].slice(0, 100),
        })),

      // NL2SQL API Actions
      explainQuery: async (connectionId, sql) => {
        set({ isGenerating: true, error: null });
        try {
          const result = await nl2sqlApi.explainQuery(connectionId, sql);
          set({ explanation: result.explanation || '', isGenerating: false });
          return result;
        } catch (err) {
          set({ error: err.message, isGenerating: false });
          return null;
        }
      },

      fetchSavedQuery: async (queryId) => {
        try {
          const query = await nl2sqlApi.getSavedQuery(queryId);
          return query;
        } catch (err) {
          set({ error: err.message });
          return null;
        }
      },

      fetchQueryHistory: async (connectionId = null) => {
        try {
          const response = await nl2sqlApi.getQueryHistory({ connectionId });
          const history = Array.isArray(response) ? response : (response?.history || []);
          set({ queryHistory: history });
          return history;
        } catch (err) {
          set({ error: err.message });
          return [];
        }
      },

      deleteQueryHistoryEntry: async (entryId) => {
        try {
          await nl2sqlApi.deleteQueryHistoryEntry(entryId);
          set((state) => ({
            queryHistory: state.queryHistory.filter((e) => e.id !== entryId),
          }));
          return true;
        } catch (err) {
          set({ error: err.message });
          return false;
        }
      },

      // Load saved query into editor
      loadSavedQuery: (query) =>
        set({
          currentQuestion: query.original_question || '',
          generatedSQL: query.sql,
          selectedConnectionId: query.connection_id,
          explanation: '',
          confidence: 0,
          warnings: [],
          results: null,
          columns: [],
          error: null,
        }),
    }),
    {
      name: 'neura-query-store',
      partialize: (state) => ({
        selectedConnectionId: state.selectedConnectionId,
        queryHistory: state.queryHistory.slice(0, 20), // Only persist recent history
      }),
      onRehydrateStorage: () => (state) => {
        // Validate persisted selectedConnectionId is a non-empty string.
        // The actual connection-existence check happens when the connection
        // list loads; here we only reject clearly invalid values.
        if (state && state.selectedConnectionId != null) {
          const id = state.selectedConnectionId
          if (typeof id !== 'string' || id.trim() === '') {
            state.selectedConnectionId = null
          }
        }
      },
    }
  )
)

export default useQueryStore

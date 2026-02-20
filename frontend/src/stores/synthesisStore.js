/**
 * Multi-Document Synthesis Store
 */
import { create } from 'zustand';
import * as synthesisApi from '../api/synthesis';

const useSynthesisStore = create((set, get) => ({
  // State
  sessions: [],
  currentSession: null,
  inconsistencies: [],
  synthesisResult: null,
  loading: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch all sessions
  fetchSessions: async () => {
    set({ loading: true, error: null });
    try {
      const response = await synthesisApi.listSessions();
      set({ sessions: response.sessions || [], loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  // Create session
  createSession: async (name) => {
    set({ loading: true, error: null });
    try {
      const response = await synthesisApi.createSession(name);
      const session = response.session;
      set((state) => ({
        sessions: [...state.sessions, session].slice(0, 100),
        currentSession: session,
        loading: false,
      }));
      return session;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Get session
  getSession: async (sessionId) => {
    set({ loading: true, error: null });
    try {
      const response = await synthesisApi.getSession(sessionId);
      set({ currentSession: response.session, loading: false });
      return response.session;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Delete session
  deleteSession: async (sessionId) => {
    set({ loading: true, error: null });
    try {
      await synthesisApi.deleteSession(sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== sessionId),
        currentSession: state.currentSession?.id === sessionId ? null : state.currentSession,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Add document
  addDocument: async (sessionId, documentData) => {
    set({ loading: true, error: null });
    try {
      const response = await synthesisApi.addDocument(sessionId, documentData);
      // Refresh current session
      await get().getSession(sessionId);
      set({ loading: false });
      return response.document;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Remove document
  removeDocument: async (sessionId, documentId) => {
    set({ loading: true, error: null });
    try {
      await synthesisApi.removeDocument(sessionId, documentId);
      await get().getSession(sessionId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Find inconsistencies
  findInconsistencies: async (sessionId) => {
    set({ loading: true, error: null });
    try {
      const response = await synthesisApi.findInconsistencies(sessionId);
      set({ inconsistencies: response.inconsistencies || [], loading: false });
      return response.inconsistencies;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Synthesize documents
  synthesize: async (sessionId, options = {}) => {
    set({ loading: true, error: null, synthesisResult: null });
    try {
      const response = await synthesisApi.synthesize(sessionId, options);
      set({ synthesisResult: response.result, loading: false });
      return response.result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset state
  reset: () => set({
    currentSession: null,
    inconsistencies: [],
    synthesisResult: null,
    error: null,
  }),
}));

export default useSynthesisStore;

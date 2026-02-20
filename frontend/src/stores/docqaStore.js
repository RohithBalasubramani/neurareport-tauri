/**
 * Document Q&A Chat Store
 */
import { create } from 'zustand';
import * as docqaApi from '../api/docqa';

const useDocQAStore = create((set, get) => ({
  // State
  sessions: [],
  currentSession: null,
  messages: [],
  loading: false,
  asking: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch all sessions
  fetchSessions: async () => {
    set({ loading: true, error: null });
    try {
      const response = await docqaApi.listSessions();
      set({ sessions: response.sessions || [], loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  // Create session
  createSession: async (name) => {
    set({ loading: true, error: null });
    try {
      const response = await docqaApi.createSession(name);
      const session = response.session;
      set((state) => ({
        sessions: [...state.sessions, session].slice(0, 100),
        currentSession: session,
        messages: [],
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
      const response = await docqaApi.getSession(sessionId);
      let messages = response.session?.messages || [];
      try {
        const history = await docqaApi.getChatHistory(sessionId, 50);
        if (Array.isArray(history?.messages)) {
          messages = history.messages;
        }
      } catch {
        // Fall back to session messages if history lookup fails.
      }
      set({
        currentSession: response.session,
        messages,
        loading: false,
      });
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
      await docqaApi.deleteSession(sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== sessionId),
        currentSession: state.currentSession?.id === sessionId ? null : state.currentSession,
        messages: state.currentSession?.id === sessionId ? [] : state.messages,
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
      const response = await docqaApi.addDocument(sessionId, documentData);
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
      await docqaApi.removeDocument(sessionId, documentId);
      await get().getSession(sessionId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Ask question
  askQuestion: async (sessionId, question, options = {}) => {
    // Add user message optimistically
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
      citations: [],
    };

    set((state) => ({
      messages: [...state.messages, userMessage].slice(-500),
      asking: true,
      error: null,
    }));

    try {
      const response = await docqaApi.askQuestion(sessionId, {
        question,
        ...options,
      });

      // Replace temp message with actual and add assistant response
      set((state) => ({
        messages: [
          ...state.messages.filter((m) => m.id !== userMessage.id),
          { ...userMessage, id: response.response?.message?.id || userMessage.id },
          response.response?.message,
        ].filter(Boolean),
        asking: false,
      }));

      return response.response;
    } catch (err) {
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== userMessage.id),
        error: err.message,
        asking: false,
      }));
      return null;
    }
  },

  // Clear history
  clearHistory: async (sessionId) => {
    set({ loading: true, error: null });
    try {
      await docqaApi.clearHistory(sessionId);
      set({ messages: [], loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Submit feedback for a message
  submitFeedback: async (sessionId, messageId, feedbackType, comment = null) => {
    try {
      const response = await docqaApi.submitFeedback(sessionId, messageId, {
        feedbackType,
        comment,
      });

      // Update the message in state with feedback
      set((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === messageId
            ? { ...msg, feedback: response.message?.feedback }
            : msg
        ),
      }));

      return response.message;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Regenerate a response
  regenerateResponse: async (sessionId, messageId, options = {}) => {
    set({ asking: true, error: null });
    try {
      const response = await docqaApi.regenerateResponse(sessionId, messageId, options);

      // Update the message in state with regenerated content
      set((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === messageId ? response.response?.message : msg
        ),
        asking: false,
      }));

      return response.response;
    } catch (err) {
      set({ error: err.message, asking: false });
      return null;
    }
  },

  // Reset state
  reset: () => set({
    currentSession: null,
    messages: [],
    error: null,
  }),
}));

export default useDocQAStore;

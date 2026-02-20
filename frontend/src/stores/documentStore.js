/**
 * Document Store - Zustand store for document editing and collaboration.
 */
import { create } from 'zustand';
import * as documentsApi from '../api/documents';

const useDocumentStore = create((set, get) => ({
  // State
  documents: [],
  currentDocument: null,
  versions: [],
  comments: [],
  collaborators: [],
  loading: false,
  saving: false,
  savingComment: false,
  error: null,
  aiResult: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch all documents
  fetchDocuments: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await documentsApi.listDocuments(params);
      set({ documents: response.documents || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Create document
  createDocument: async (data) => {
    set({ loading: true, error: null });
    try {
      const document = await documentsApi.createDocument(data);
      set((state) => ({
        documents: [document, ...state.documents],
        currentDocument: document,
        loading: false,
      }));
      return document;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Get document
  getDocument: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const document = await documentsApi.getDocument(documentId);
      set({ currentDocument: document, loading: false });
      return document;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Update document
  updateDocument: async (documentId, data) => {
    set({ saving: true, error: null });
    try {
      const document = await documentsApi.updateDocument(documentId, data);
      set((state) => ({
        documents: state.documents.map((d) => (d.id === documentId ? document : d)),
        currentDocument: state.currentDocument?.id === documentId ? document : state.currentDocument,
        saving: false,
      }));
      return document;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  // Delete document
  deleteDocument: async (documentId) => {
    set({ loading: true, error: null });
    try {
      await documentsApi.deleteDocument(documentId);
      set((state) => ({
        documents: state.documents.filter((d) => d.id !== documentId),
        currentDocument: state.currentDocument?.id === documentId ? null : state.currentDocument,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Version History
  fetchVersions: async (documentId) => {
    try {
      const response = await documentsApi.getVersions(documentId);
      set({ versions: response.versions || [] });
      return response.versions;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  getVersion: async (documentId, versionId) => {
    try {
      const version = await documentsApi.getVersion(documentId, versionId);
      return version;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  restoreVersion: async (documentId, versionId) => {
    set({ loading: true, error: null });
    try {
      const document = await documentsApi.restoreVersion(documentId, versionId);
      set((state) => ({
        currentDocument: document,
        loading: false,
      }));
      return document;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Comments
  fetchComments: async (documentId) => {
    try {
      const response = await documentsApi.getComments(documentId);
      set({ comments: response.comments || [] });
      return response.comments;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  addComment: async (documentId, data) => {
    set({ savingComment: true, error: null });
    try {
      const comment = await documentsApi.addComment(documentId, data);
      set((state) => ({
        comments: [...state.comments, comment],
        savingComment: false,
      }));
      return comment;
    } catch (err) {
      set({ error: err.message, savingComment: false });
      return null;
    }
  },

  resolveComment: async (documentId, commentId, resolved = true) => {
    set({ savingComment: true, error: null });
    try {
      await documentsApi.resolveComment(documentId, commentId, resolved);
      set((state) => ({
        comments: state.comments.map((c) =>
          c.id === commentId ? { ...c, resolved } : c
        ),
        savingComment: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, savingComment: false });
      return false;
    }
  },

  replyToComment: async (documentId, commentId, data) => {
    set({ savingComment: true, error: null });
    try {
      const reply = await documentsApi.replyToComment(documentId, commentId, data);
      set((state) => ({
        comments: state.comments.map((c) =>
          c.id === commentId
            ? { ...c, replies: [...(c.replies || []), reply] }
            : c
        ),
        savingComment: false,
      }));
      return reply;
    } catch (err) {
      set({ error: err.message, savingComment: false });
      return null;
    }
  },

  deleteComment: async (documentId, commentId) => {
    set({ savingComment: true, error: null });
    try {
      await documentsApi.deleteComment(documentId, commentId);
      set((state) => ({
        comments: state.comments.filter((c) => c.id !== commentId),
        savingComment: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, savingComment: false });
      return false;
    }
  },

  // Collaboration
  startCollaboration: async (documentId, data = {}) => {
    try {
      const session = await documentsApi.startCollaboration(documentId, data);
      return session;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  fetchCollaborators: async (documentId) => {
    try {
      const response = await documentsApi.getCollaborators(documentId);
      set({ collaborators: response.collaborators || [] });
      return response.collaborators;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  updatePresence: async (documentId, data) => {
    try {
      await documentsApi.updatePresence(documentId, data);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  // PDF Operations
  mergePdfs: async (documentIds) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.mergePdfs(documentIds);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  addWatermark: async (documentId, data) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.addWatermark(documentId, data);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  reorderPages: async (documentId, pageOrder) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.reorderPages(documentId, pageOrder);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  redactRegions: async (documentId, regions) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.redactRegions(documentId, regions);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  splitPdf: async (documentId, splitConfig) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.splitPdf(documentId, splitConfig);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  rotatePdf: async (documentId, rotations) => {
    set({ loading: true, error: null });
    try {
      const result = await documentsApi.rotatePdf(documentId, rotations);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Templates
  listTemplates: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await documentsApi.listTemplates(params);
      set({ loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Export
  exportDocument: async (documentId, format, options = {}) => {
    try {
      const result = await documentsApi.exportDocument(documentId, format, options);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // AI Writing
  checkGrammar: async (documentId, text, options = {}) => {
    try {
      const result = await documentsApi.checkGrammar(documentId, text, options);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  summarize: async (documentId, text, length = 'medium', style = 'paragraph') => {
    try {
      const result = await documentsApi.summarize(documentId, text, length, style);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  rewrite: async (documentId, text, tone = 'professional', style = 'clear') => {
    try {
      const result = await documentsApi.rewrite(documentId, text, tone, style);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  translate: async (documentId, text, targetLanguage) => {
    try {
      const result = await documentsApi.translate(documentId, text, targetLanguage);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  expand: async (documentId, text, targetLength = 'double') => {
    try {
      const result = await documentsApi.expand(documentId, text, targetLength);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  adjustTone: async (documentId, text, targetTone) => {
    try {
      const result = await documentsApi.adjustTone(documentId, text, targetTone);
      set({ aiResult: result });
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  clearAiResult: () => set({ aiResult: null }),

  // Reset
  reset: () => set({
    currentDocument: null,
    versions: [],
    comments: [],
    collaborators: [],
    aiResult: null,
    error: null,
  }),

  clearDocuments: () => set({
    documents: [],
    currentDocument: null,
  }),
}));

export default useDocumentStore;

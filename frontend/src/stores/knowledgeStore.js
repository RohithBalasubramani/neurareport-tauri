/**
 * Knowledge Store - Zustand store for document library and knowledge management.
 */
import { create } from 'zustand';
import * as knowledgeApi from '../api/knowledge';

const normalizeSearchResults = (response) => {
  const rows = Array.isArray(response?.results) ? response.results : [];
  return rows
    .map((row) => {
      const doc = row?.document && typeof row.document === 'object' ? row.document : row;
      if (!doc || typeof doc !== 'object') return null;
      return {
        ...doc,
        _score: row?.score,
        _highlights: Array.isArray(row?.highlights) ? row.highlights : [],
      };
    })
    .filter(Boolean);
};

const normalizeRelatedDocuments = (response) => {
  const rows = Array.isArray(response?.related) ? response.related : [];
  return rows
    .map((row) => row?.document)
    .filter((doc) => doc && typeof doc === 'object');
};

const normalizeFaq = (response) => {
  if (Array.isArray(response?.faq?.items)) return response.faq.items;
  if (Array.isArray(response?.items)) return response.items;
  if (Array.isArray(response?.faq)) return response.faq;
  return [];
};

const useKnowledgeStore = create((set, get) => ({
  // State
  documents: [],
  collections: [],
  tags: [],
  currentDocument: null,
  currentCollection: null,
  searchResults: [],
  relatedDocuments: [],
  knowledgeGraph: null,
  faq: [],
  stats: null,
  totalDocuments: 0,
  loading: false,
  searching: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Documents
  addDocument: async (data) => {
    set({ loading: true, error: null });
    try {
      const doc = await knowledgeApi.addDocument(data);
      set((state) => ({
        documents: [doc, ...state.documents].slice(0, 500),
        currentDocument: doc,
        loading: false,
      }));
      return doc;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchDocuments: async (options = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await knowledgeApi.listDocuments(options);
      set({
        documents: response.documents || [],
        totalDocuments: response.total || 0,
        loading: false
      });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getDocument: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const doc = await knowledgeApi.getDocument(documentId);
      set({ currentDocument: doc, loading: false });
      return doc;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  updateDocument: async (documentId, data) => {
    set({ loading: true, error: null });
    try {
      const doc = await knowledgeApi.updateDocument(documentId, data);
      set((state) => ({
        documents: state.documents.map((d) => (d.id === documentId ? doc : d)),
        currentDocument: state.currentDocument?.id === documentId ? doc : state.currentDocument,
        loading: false,
      }));
      return doc;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteDocument: async (documentId) => {
    set({ loading: true, error: null });
    try {
      await knowledgeApi.deleteDocument(documentId);
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

  toggleFavorite: async (documentId) => {
    try {
      const result = await knowledgeApi.toggleFavorite(documentId);
      set((state) => ({
        documents: state.documents.map((d) =>
          d.id === documentId ? { ...d, is_favorite: result.is_favorite } : d
        ),
        currentDocument: state.currentDocument?.id === documentId
          ? { ...state.currentDocument, is_favorite: result.is_favorite }
          : state.currentDocument,
      }));
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Collections
  createCollection: async (data) => {
    set({ loading: true, error: null });
    try {
      const collection = await knowledgeApi.createCollection(data);
      set((state) => ({
        collections: [collection, ...state.collections].slice(0, 200),
        currentCollection: collection,
        loading: false,
      }));
      return collection;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchCollections: async () => {
    set({ loading: true, error: null });
    try {
      const collections = await knowledgeApi.listCollections();
      set({ collections: collections || [], loading: false });
      return collections;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getCollection: async (collectionId) => {
    set({ loading: true, error: null });
    try {
      const collection = await knowledgeApi.getCollection(collectionId);
      set({ currentCollection: collection, loading: false });
      return collection;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  updateCollection: async (collectionId, data) => {
    set({ loading: true, error: null });
    try {
      const collection = await knowledgeApi.updateCollection(collectionId, data);
      set((state) => ({
        collections: state.collections.map((c) => (c.id === collectionId ? collection : c)),
        currentCollection: state.currentCollection?.id === collectionId ? collection : state.currentCollection,
        loading: false,
      }));
      return collection;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteCollection: async (collectionId) => {
    set({ loading: true, error: null });
    try {
      await knowledgeApi.deleteCollection(collectionId);
      set((state) => ({
        collections: state.collections.filter((c) => c.id !== collectionId),
        currentCollection: state.currentCollection?.id === collectionId ? null : state.currentCollection,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  addDocumentToCollection: async (collectionId, documentId) => {
    try {
      await knowledgeApi.addDocumentToCollection(collectionId, documentId);
      // Refresh collection
      await get().getCollection(collectionId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  removeDocumentFromCollection: async (collectionId, documentId) => {
    try {
      await knowledgeApi.removeDocumentFromCollection(collectionId, documentId);
      // Refresh collection
      await get().getCollection(collectionId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  // Tags
  createTag: async (name, color = null) => {
    set({ loading: true, error: null });
    try {
      const tag = await knowledgeApi.createTag(name, color);
      set((state) => ({
        tags: [tag, ...state.tags].slice(0, 500),
        loading: false,
      }));
      return tag;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchTags: async () => {
    try {
      const tags = await knowledgeApi.listTags();
      set({ tags: tags || [] });
      return tags;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  deleteTag: async (tagId) => {
    try {
      await knowledgeApi.deleteTag(tagId);
      set((state) => ({
        tags: state.tags.filter((t) => t.id !== tagId),
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  addTagToDocument: async (documentId, tagId) => {
    try {
      await knowledgeApi.addTagToDocument(documentId, tagId);
      await get().getDocument(documentId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  removeTagFromDocument: async (documentId, tagId) => {
    try {
      await knowledgeApi.removeTagFromDocument(documentId, tagId);
      await get().getDocument(documentId);
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  getDocumentActivity: async (documentId) => {
    try {
      const activity = await knowledgeApi.getDocumentActivity(documentId);
      return activity;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Search
  searchDocuments: async (query, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await knowledgeApi.searchDocuments(query, options);
      set({ searchResults: normalizeSearchResults(response), searching: false });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  semanticSearch: async (query, options = {}) => {
    set({ searching: true, error: null });
    try {
      const response = await knowledgeApi.semanticSearch(query, options);
      set({ searchResults: normalizeSearchResults(response), searching: false });
      return response;
    } catch (err) {
      set({ error: err.message, searching: false });
      return null;
    }
  },

  // AI Features
  autoTag: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const result = await knowledgeApi.autoTag(documentId);
      // Refresh document to get updated tags
      await get().getDocument(documentId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  findRelated: async (documentId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const related = await knowledgeApi.findRelated(documentId, options);
      set({ relatedDocuments: normalizeRelatedDocuments(related), loading: false });
      return related;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  buildKnowledgeGraph: async (options = {}) => {
    set({ loading: true, error: null });
    try {
      const graph = await knowledgeApi.buildKnowledgeGraph(options);
      set({ knowledgeGraph: graph, loading: false });
      return graph;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  generateFaq: async (options = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await knowledgeApi.generateFaq(options);
      set({ faq: normalizeFaq(response), loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Analytics
  fetchStats: async () => {
    try {
      const stats = await knowledgeApi.getLibraryStats();
      set({ stats });
      return stats;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Reset
  clearSearchResults: () => set({ searchResults: [] }),

  reset: () => set({
    currentDocument: null,
    currentCollection: null,
    searchResults: [],
    relatedDocuments: [],
    error: null,
  }),
}));

export default useKnowledgeStore;

/**
 * Ingestion Store - Zustand store for document ingestion and import.
 */
import { create } from 'zustand';
import * as ingestionApi from '../api/ingestion';

const useIngestionStore = create((set, get) => ({
  // State
  uploads: [],
  watchers: [],
  transcriptionJobs: [],
  imapAccounts: [],
  currentUpload: null,
  uploadProgress: {},
  loading: false,
  uploading: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // File Upload
  uploadFile: async (file, options = {}) => {
    const fileId = crypto.randomUUID();
    set((state) => ({ uploading: true, error: null, uploadProgress: { ...state.uploadProgress, [fileId]: 0 } }));
    try {
      const result = await ingestionApi.uploadFile(file, {
        ...options,
        onProgress: (event) => {
          const progress = Math.round((event.loaded * 100) / event.total);
          set((state) => ({ uploadProgress: { ...state.uploadProgress, [fileId]: progress } }));
        },
      });
      set((state) => ({
        uploads: [result, ...state.uploads],
        currentUpload: result,
        uploading: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, uploading: false });
      return null;
    }
  },

  uploadBulk: async (files, options = {}) => {
    set({ uploading: true, error: null });
    try {
      const results = await ingestionApi.uploadBulk(files, options);
      set((state) => ({
        uploads: [...results, ...state.uploads],
        uploading: false,
      }));
      return results;
    } catch (err) {
      set({ error: err.message, uploading: false });
      return [];
    }
  },

  uploadZip: async (file, options = {}) => {
    set({ uploading: true, error: null });
    try {
      const result = await ingestionApi.uploadZip(file, options);
      set((state) => ({
        uploads: [result, ...state.uploads],
        currentUpload: result,
        uploading: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, uploading: false });
      return null;
    }
  },

  // URL Import
  importFromUrl: async (url, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.importFromUrl(url, options);
      set((state) => ({
        uploads: [result, ...state.uploads],
        currentUpload: result,
        loading: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Structured Data
  importStructuredData: async (data, format, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.importStructuredData(data, format, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Web Clipper
  clipUrl: async (url, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.clipUrl(url, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  clipSelection: async (content, sourceUrl, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.clipSelection(content, sourceUrl, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Folder Watchers
  createWatcher: async (folderPath, options = {}) => {
    set({ loading: true, error: null });
    try {
      const watcher = await ingestionApi.createWatcher(folderPath, options);
      set((state) => ({
        watchers: [watcher, ...state.watchers],
        loading: false,
      }));
      return watcher;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchWatchers: async () => {
    set({ loading: true, error: null });
    try {
      const watchers = await ingestionApi.listWatchers();
      set({ watchers: watchers || [], loading: false });
      return watchers;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getWatcher: async (watcherId) => {
    set({ loading: true, error: null });
    try {
      const watcher = await ingestionApi.getWatcher(watcherId);
      set({ loading: false });
      return watcher;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  startWatcher: async (watcherId) => {
    try {
      await ingestionApi.startWatcher(watcherId);
      set((state) => ({
        watchers: state.watchers.map((w) =>
          w.id === watcherId ? { ...w, status: 'running' } : w
        ),
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  stopWatcher: async (watcherId) => {
    try {
      await ingestionApi.stopWatcher(watcherId);
      set((state) => ({
        watchers: state.watchers.map((w) =>
          w.id === watcherId ? { ...w, status: 'stopped' } : w
        ),
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  deleteWatcher: async (watcherId) => {
    set({ loading: true, error: null });
    try {
      await ingestionApi.deleteWatcher(watcherId);
      set((state) => ({
        watchers: state.watchers.filter((w) => w.id !== watcherId),
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  scanFolder: async (watcherId) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.scanFolder(watcherId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Transcription
  transcribeFile: async (file, options = {}) => {
    set({ uploading: true, error: null });
    try {
      const job = await ingestionApi.transcribeFile(file, options);
      set((state) => ({
        transcriptionJobs: [job, ...state.transcriptionJobs],
        uploading: false,
      }));
      return job;
    } catch (err) {
      set({ error: err.message, uploading: false });
      return null;
    }
  },

  getTranscriptionStatus: async (jobId) => {
    try {
      const status = await ingestionApi.getTranscriptionStatus(jobId);
      set((state) => ({
        transcriptionJobs: state.transcriptionJobs.map((j) =>
          j.id === jobId ? { ...j, ...status } : j
        ),
      }));
      return status;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Email Import
  connectImapAccount: async (config) => {
    set({ loading: true, error: null });
    try {
      const account = await ingestionApi.connectImapAccount(config);
      set((state) => ({
        imapAccounts: [account, ...state.imapAccounts],
        loading: false,
      }));
      return account;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchImapAccounts: async () => {
    set({ loading: true, error: null });
    try {
      const accounts = await ingestionApi.listImapAccounts();
      set({ imapAccounts: accounts || [], loading: false });
      return accounts;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  syncImapAccount: async (accountId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.syncImapAccount(accountId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  parseEmail: async (emailData, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await ingestionApi.parseEmail(emailData, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  clearUploads: () => set({
    uploads: [],
    currentUpload: null,
    uploadProgress: {},
  }),

  reset: () => set({
    currentUpload: null,
    uploadProgress: {},
    error: null,
  }),
}));

export default useIngestionStore;

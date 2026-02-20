/**
 * Export Store - Zustand store for document export and distribution.
 */
import { create } from 'zustand';
import * as exportApi from '../api/export';

const useExportStore = create((set, get) => ({
  // State
  exportJobs: [],
  currentJob: null,
  embedTokens: [],
  printers: [],
  loading: false,
  exporting: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Export Formats
  exportToPdf: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToPdf(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToPdfA: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToPdfA(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToDocx: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToDocx(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToPptx: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToPptx(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToEpub: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToEpub(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToLatex: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToLatex(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToMarkdown: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToMarkdown(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  exportToHtml: async (documentId, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const result = await exportApi.exportToHtml(documentId, options);
      set({ exporting: false });
      return result;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  // Bulk Export
  bulkExport: async (documentIds, format, options = {}) => {
    set({ exporting: true, error: null });
    try {
      const job = await exportApi.bulkExport(documentIds, format, options);
      set((state) => ({
        exportJobs: [job, ...state.exportJobs].slice(0, 200),
        currentJob: job,
        exporting: false,
      }));
      return job;
    } catch (err) {
      set({ error: err.message, exporting: false });
      return null;
    }
  },

  getBulkExportStatus: async (jobId) => {
    try {
      const status = await exportApi.getBulkExportStatus(jobId);
      set((state) => ({
        exportJobs: state.exportJobs.map((j) => (j.id === jobId ? { ...j, ...status } : j)),
        currentJob: state.currentJob?.id === jobId ? { ...state.currentJob, ...status } : state.currentJob,
      }));
      return status;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  downloadBulkExport: async (jobId) => {
    try {
      const blob = await exportApi.downloadBulkExport(jobId);
      return blob;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Distribution
  sendEmail: async (documentId, options) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.sendEmail(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  sendToSlack: async (documentId, options) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.sendToSlack(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  sendToTeams: async (documentId, options) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.sendToTeams(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  sendWebhook: async (documentId, options) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.sendWebhook(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  publishToPortal: async (documentId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.publishToPortal(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Embed
  generateEmbedToken: async (documentId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const token = await exportApi.generateEmbedToken(documentId, options);
      set((state) => ({
        embedTokens: [token, ...state.embedTokens].slice(0, 200),
        loading: false,
      }));
      return token;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  revokeEmbedToken: async (tokenId) => {
    try {
      await exportApi.revokeEmbedToken(tokenId);
      set((state) => ({
        embedTokens: state.embedTokens.filter((t) => t.id !== tokenId),
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  fetchEmbedTokens: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const tokens = await exportApi.listEmbedTokens(documentId);
      set({ embedTokens: tokens || [], loading: false });
      return tokens;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Print
  printDocument: async (documentId, options = {}) => {
    set({ loading: true, error: null });
    try {
      const result = await exportApi.printDocument(documentId, options);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchPrinters: async () => {
    try {
      const printers = await exportApi.listPrinters();
      set({ printers: printers || [] });
      return printers;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Export Jobs
  fetchExportJobs: async (options = {}) => {
    set({ loading: true, error: null });
    try {
      const jobs = await exportApi.listExportJobs(options);
      set({ exportJobs: jobs || [], loading: false });
      return jobs;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getExportJob: async (jobId) => {
    try {
      const job = await exportApi.getExportJob(jobId);
      set({ currentJob: job });
      return job;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  cancelExportJob: async (jobId) => {
    try {
      await exportApi.cancelExportJob(jobId);
      set((state) => ({
        exportJobs: state.exportJobs.map((j) =>
          j.id === jobId ? { ...j, status: 'cancelled' } : j
        ),
      }));
      return true;
    } catch (err) {
      set({ error: err.message });
      return false;
    }
  },

  // Reset
  reset: () => set({
    currentJob: null,
    error: null,
  }),
}));

export default useExportStore;

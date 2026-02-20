/**
 * Health Store - Zustand store for system health monitoring.
 */
import { create } from 'zustand';
import * as healthApi from '../api/health';

const useHealthStore = create((set) => ({
  // State
  detailedHealth: null,
  emailStatus: null,
  readiness: null,
  systemHealth: null,
  loading: false,
  error: null,

  // Actions
  setError: (error) => set({ error }),

  getDetailedHealth: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.getDetailedHealth();
      set({ detailedHealth: result, loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getEmailStatus: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.getEmailStatus();
      set({ emailStatus: result, loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  testEmailConnection: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.testEmailConnection();
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  refreshEmailConfig: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.refreshEmailConfig();
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  checkReadiness: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.checkReadiness();
      set({ readiness: result, loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  getSystemHealth: async () => {
    set({ loading: true, error: null });
    try {
      const result = await healthApi.getSystemHealth();
      set({ systemHealth: result, loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  reset: () => set({
    detailedHealth: null,
    emailStatus: null,
    readiness: null,
    systemHealth: null,
    error: null,
  }),
}));

export default useHealthStore;

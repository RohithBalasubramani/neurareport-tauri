import { create } from 'zustand'

/**
 * Job and run tracking store.
 *
 * Extracted from useAppStore to provide focused background job management.
 * Handles job lifecycle, run history, and download tracking.
 */
export const useJobStore = create((set) => ({
  // Jobs for background processing
  jobs: [],
  setJobs: (jobs) => set({ jobs: Array.isArray(jobs) ? jobs : [] }),
  addJob: (job) => set((state) => ({ jobs: [job, ...state.jobs] })),
  updateJob: (jobId, updates) =>
    set((state) => ({
      jobs: state.jobs.map((j) => (j.id === jobId ? { ...j, ...updates } : j)),
    })),
  removeJob: (jobId) =>
    set((state) => ({ jobs: state.jobs.filter((j) => j.id !== jobId) })),

  // Run history
  runs: [],
  setRuns: (runs) => set({ runs }),

  // Recently downloaded artifacts
  downloads: [],
  addDownload: (item) =>
    set((state) => ({ downloads: [item, ...state.downloads].slice(0, 20) })),
}))

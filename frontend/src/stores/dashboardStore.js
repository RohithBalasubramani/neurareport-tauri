/**
 * Dashboard Store - Zustand store for dashboard building and analytics.
 */
import { create } from 'zustand';
import * as dashboardsApi from '../api/dashboards';

const useDashboardStore = create((set, get) => ({
  // State
  dashboards: [],
  currentDashboard: null,
  widgets: [],
  filters: [],
  insights: [],
  loading: false,
  saving: false,
  refreshing: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Fetch all dashboards
  fetchDashboards: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await dashboardsApi.listDashboards(params);
      set({ dashboards: response.dashboards || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Create dashboard
  createDashboard: async (data) => {
    set({ loading: true, error: null });
    try {
      const dashboard = await dashboardsApi.createDashboard(data);
      set((state) => ({
        dashboards: [dashboard, ...state.dashboards].slice(0, 100),
        currentDashboard: dashboard,
        widgets: dashboard.widgets || [],
        filters: dashboard.filters || [],
        loading: false,
      }));
      return dashboard;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Get dashboard
  getDashboard: async (dashboardId) => {
    set({ loading: true, error: null });
    try {
      const dashboard = await dashboardsApi.getDashboard(dashboardId);
      set({
        currentDashboard: dashboard,
        widgets: dashboard.widgets || [],
        filters: dashboard.filters || [],
        loading: false,
      });
      return dashboard;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Update dashboard
  updateDashboard: async (dashboardId, data) => {
    set({ saving: true, error: null });
    try {
      const dashboard = await dashboardsApi.updateDashboard(dashboardId, data);
      set((state) => ({
        dashboards: state.dashboards.map((d) => (d.id === dashboardId ? dashboard : d)),
        currentDashboard: state.currentDashboard?.id === dashboardId ? dashboard : state.currentDashboard,
        widgets: state.currentDashboard?.id === dashboardId ? (dashboard.widgets || []) : state.widgets,
        saving: false,
      }));
      return dashboard;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  // Delete dashboard
  deleteDashboard: async (dashboardId) => {
    set({ loading: true, error: null });
    try {
      await dashboardsApi.deleteDashboard(dashboardId);
      set((state) => ({
        dashboards: state.dashboards.filter((d) => d.id !== dashboardId),
        currentDashboard: state.currentDashboard?.id === dashboardId ? null : state.currentDashboard,
        widgets: state.currentDashboard?.id === dashboardId ? [] : state.widgets,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Widget Operations
  addWidget: async (dashboardId, widget) => {
    set({ saving: true, error: null });
    try {
      const newWidget = await dashboardsApi.addWidget(dashboardId, widget);
      set((state) => ({
        widgets: [...state.widgets, newWidget].slice(0, 200),
        saving: false,
      }));
      return newWidget;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  updateWidget: async (dashboardId, widgetId, data) => {
    set({ saving: true, error: null });
    try {
      const updatedWidget = await dashboardsApi.updateWidget(dashboardId, widgetId, data);
      set((state) => ({
        widgets: state.widgets.map((w) => (w.id === widgetId ? updatedWidget : w)),
        saving: false,
      }));
      return updatedWidget;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  deleteWidget: async (dashboardId, widgetId) => {
    set({ saving: true, error: null });
    try {
      await dashboardsApi.deleteWidget(dashboardId, widgetId);
      set((state) => ({
        widgets: state.widgets.filter((w) => w.id !== widgetId),
        saving: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  updateWidgetLayout: async (dashboardId, layouts) => {
    set({ saving: true, error: null });
    try {
      await dashboardsApi.updateWidgetLayout(dashboardId, layouts);
      set((state) => ({
        widgets: state.widgets.map((w) => {
          const layout = layouts.find((l) => l.id === w.id);
          return layout ? { ...w, x: layout.x, y: layout.y, w: layout.w, h: layout.h } : w;
        }),
        saving: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  // Data & Refresh
  refreshDashboard: async (dashboardId) => {
    set({ refreshing: true, error: null });
    try {
      await dashboardsApi.refreshDashboard(dashboardId);
      await get().getDashboard(dashboardId);
      set({ refreshing: false });
      return true;
    } catch (err) {
      set({ error: err.message, refreshing: false });
      return false;
    }
  },

  executeWidgetQuery: async (dashboardId, widgetId, filters = {}) => {
    try {
      const result = await dashboardsApi.executeWidgetQuery(dashboardId, widgetId, filters);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Snapshot & Embed
  createSnapshot: async (dashboardId, format = 'png') => {
    set({ loading: true, error: null });
    try {
      const result = await dashboardsApi.createSnapshot(dashboardId, format);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  generateEmbedToken: async (dashboardId, expiresHours = 24) => {
    try {
      const result = await dashboardsApi.generateEmbedToken(dashboardId, expiresHours);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // AI Analytics
  generateInsights: async (data, context = null) => {
    set({ loading: true, error: null });
    try {
      const result = await dashboardsApi.generateInsights(data, context);
      set({ insights: result.insights || [], loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  predictTrends: async (data, dateColumn, valueColumn, periods = 12) => {
    try {
      const result = await dashboardsApi.predictTrends(data, dateColumn, valueColumn, periods);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  detectAnomalies: async (data, columns, method = 'zscore') => {
    try {
      const result = await dashboardsApi.detectAnomalies(data, columns, method);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  findCorrelations: async (data, columns = null) => {
    try {
      const result = await dashboardsApi.findCorrelations(data, columns);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Templates
  createFromTemplate: async (templateId, name) => {
    set({ loading: true, error: null });
    try {
      const dashboard = await dashboardsApi.createFromTemplate(templateId, name);
      set((state) => ({
        dashboards: [dashboard, ...state.dashboards].slice(0, 100),
        currentDashboard: dashboard,
        loading: false,
      }));
      return dashboard;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  saveAsTemplate: async (dashboardId, name, description = null) => {
    try {
      const result = await dashboardsApi.saveAsTemplate(dashboardId, name, description);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Snapshot URL
  getSnapshotUrl: async (dashboardId) => {
    try {
      const result = await dashboardsApi.getSnapshotUrl(dashboardId);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Filters
  addFilter: async (dashboardId, filter) => {
    set({ saving: true, error: null });
    try {
      const result = await dashboardsApi.addFilter(dashboardId, filter);
      set((state) => ({
        filters: [...state.filters, result],
        saving: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  updateFilter: async (dashboardId, filterId, data) => {
    set({ saving: true, error: null });
    try {
      const result = await dashboardsApi.updateFilter(dashboardId, filterId, data);
      set((state) => ({
        filters: state.filters.map((f) => (f.id === filterId ? result : f)),
        saving: false,
      }));
      return result;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  deleteFilter: async (dashboardId, filterId) => {
    set({ saving: true, error: null });
    try {
      await dashboardsApi.deleteFilter(dashboardId, filterId);
      set((state) => ({
        filters: state.filters.filter((f) => f.id !== filterId),
        saving: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  // Variables & What-If
  setVariable: async (dashboardId, variable) => {
    try {
      const result = await dashboardsApi.setVariable(dashboardId, variable);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  runWhatIfSimulation: async (dashboardId, scenario) => {
    set({ loading: true, error: null });
    try {
      const result = await dashboardsApi.runWhatIfSimulation(dashboardId, scenario);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Dashboard Templates
  listDashboardTemplates: async () => {
    set({ loading: true, error: null });
    try {
      const templates = await dashboardsApi.listDashboardTemplates();
      set({ loading: false });
      return templates;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  // Sharing & Export
  shareDashboard: async (dashboardId, data) => {
    try {
      const result = await dashboardsApi.shareDashboard(dashboardId, data);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  exportDashboard: async (dashboardId, format = 'pdf') => {
    set({ loading: true, error: null });
    try {
      const result = await dashboardsApi.exportDashboard(dashboardId, format);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  reset: () => set({
    currentDashboard: null,
    widgets: [],
    filters: [],
    insights: [],
    error: null,
  }),

  clearDashboards: () => set({
    dashboards: [],
    currentDashboard: null,
    widgets: [],
  }),
}));

export default useDashboardStore;

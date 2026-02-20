/**
 * Visualization Store - Zustand store for diagrams and charts.
 */
import { create } from 'zustand';
import * as visualizationApi from '../api/visualization';

const useVisualizationStore = create((set, get) => ({
  // State
  diagrams: [],
  currentDiagram: null,
  diagramTypes: [],
  chartTypes: [],
  loading: false,
  generating: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Diagram Generation
  generateFlowchart: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateFlowchart(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateMindmap: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateMindmap(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateOrgChart: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateOrgChart(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateTimeline: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateTimeline(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateGantt: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateGantt(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateNetworkGraph: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateNetworkGraph(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateKanban: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateKanban(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateSequenceDiagram: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateSequenceDiagram(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateWordcloud: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const diagram = await visualizationApi.generateWordcloud(data, options);
      set((state) => ({
        diagrams: [diagram, ...state.diagrams].slice(0, 200),
        currentDiagram: diagram,
        generating: false,
      }));
      return diagram;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  // Chart Generation
  tableToChart: async (tableData, options = {}) => {
    set({ generating: true, error: null });
    try {
      const chart = await visualizationApi.tableToChart(tableData, options);
      set({ currentDiagram: chart, generating: false });
      return chart;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  generateSparklines: async (data, options = {}) => {
    set({ generating: true, error: null });
    try {
      const sparklines = await visualizationApi.generateSparklines(data, options);
      set({ generating: false });
      return sparklines;
    } catch (err) {
      set({ error: err.message, generating: false });
      return null;
    }
  },

  // Export
  exportAsMermaid: async (diagramId) => {
    set({ loading: true, error: null });
    try {
      const response = await visualizationApi.exportDiagramAsMermaid(diagramId);
      set({ loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  exportAsSvg: async (diagramId) => {
    set({ loading: true, error: null });
    try {
      const response = await visualizationApi.exportDiagramAsSvg(diagramId);
      set({ loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  exportAsPng: async (diagramId) => {
    set({ loading: true, error: null });
    try {
      const blob = await visualizationApi.exportDiagramAsPng(diagramId);
      set({ loading: false });
      return blob;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Types
  fetchDiagramTypes: async () => {
    try {
      const types = await visualizationApi.listDiagramTypes();
      set({ diagramTypes: types || [] });
      return types;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  fetchChartTypes: async () => {
    try {
      const types = await visualizationApi.listChartTypes();
      set({ chartTypes: types || [] });
      return types;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Reset
  setCurrentDiagram: (diagram) => set({ currentDiagram: diagram }),

  clearDiagrams: () => set({
    diagrams: [],
    currentDiagram: null,
  }),

  reset: () => set({
    currentDiagram: null,
    error: null,
  }),
}));

export default useVisualizationStore;

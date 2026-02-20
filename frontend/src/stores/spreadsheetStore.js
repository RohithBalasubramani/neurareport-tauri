/**
 * Spreadsheet Store - Zustand store for spreadsheet editing.
 */
import { create } from 'zustand';
import * as spreadsheetsApi from '../api/spreadsheets';

const useSpreadsheetStore = create((set, get) => ({
  // State
  spreadsheets: [],
  currentSpreadsheet: null,
  activeSheetIndex: 0,
  selectedCells: null,
  pivotTables: [],
  loading: false,
  saving: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setActiveSheetIndex: (index) => set({ activeSheetIndex: index }),
  setSelectedCells: (cells) => set({ selectedCells: cells }),

  // Fetch all spreadsheets
  fetchSpreadsheets: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await spreadsheetsApi.listSpreadsheets(params);
      set({ spreadsheets: response.spreadsheets || [], loading: false });
      return response;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Create spreadsheet
  createSpreadsheet: async (data) => {
    set({ loading: true, error: null });
    try {
      const spreadsheet = await spreadsheetsApi.createSpreadsheet(data);
      set((state) => ({
        spreadsheets: [spreadsheet, ...state.spreadsheets].slice(0, 200),
        currentSpreadsheet: spreadsheet,
        activeSheetIndex: 0,
        loading: false,
      }));
      return spreadsheet;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Get spreadsheet
  getSpreadsheet: async (spreadsheetId) => {
    set({ loading: true, error: null });
    try {
      const spreadsheet = await spreadsheetsApi.getSpreadsheet(spreadsheetId);
      set({
        currentSpreadsheet: spreadsheet,
        activeSheetIndex: 0,
        loading: false,
      });
      return spreadsheet;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Update spreadsheet
  updateSpreadsheet: async (spreadsheetId, data) => {
    set({ saving: true, error: null });
    try {
      const spreadsheet = await spreadsheetsApi.updateSpreadsheet(spreadsheetId, data);
      set((state) => ({
        spreadsheets: state.spreadsheets.map((s) => (s.id === spreadsheetId ? spreadsheet : s)),
        currentSpreadsheet: state.currentSpreadsheet?.id === spreadsheetId ? spreadsheet : state.currentSpreadsheet,
        saving: false,
      }));
      return spreadsheet;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  // Delete spreadsheet
  deleteSpreadsheet: async (spreadsheetId) => {
    set({ loading: true, error: null });
    try {
      await spreadsheetsApi.deleteSpreadsheet(spreadsheetId);
      set((state) => ({
        spreadsheets: state.spreadsheets.filter((s) => s.id !== spreadsheetId),
        currentSpreadsheet: state.currentSpreadsheet?.id === spreadsheetId ? null : state.currentSpreadsheet,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Cell Operations
  updateCells: async (spreadsheetId, sheetIndex, updates) => {
    set({ saving: true, error: null });
    try {
      const result = await spreadsheetsApi.updateCells(spreadsheetId, sheetIndex, updates);
      // Refresh current spreadsheet to get updated data
      if (get().currentSpreadsheet?.id === spreadsheetId) {
        await get().getSpreadsheet(spreadsheetId);
      }
      set({ saving: false });
      return result;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  getCellRange: async (spreadsheetId, sheetIndex, range) => {
    try {
      const result = await spreadsheetsApi.getCellRange(spreadsheetId, sheetIndex, range);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Sheet Operations
  addSheet: async (spreadsheetId, name) => {
    set({ loading: true, error: null });
    try {
      const result = await spreadsheetsApi.addSheet(spreadsheetId, name);
      await get().getSpreadsheet(spreadsheetId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteSheet: async (spreadsheetId, sheetIndex) => {
    set({ loading: true, error: null });
    try {
      const currentSpreadsheet = get().currentSpreadsheet;
      const sheetId = currentSpreadsheet?.sheets?.[sheetIndex]?.id ?? sheetIndex;
      await spreadsheetsApi.deleteSheet(spreadsheetId, sheetId);
      const state = get();
      if (state.activeSheetIndex >= sheetIndex && state.activeSheetIndex > 0) {
        set({ activeSheetIndex: state.activeSheetIndex - 1 });
      }
      await get().getSpreadsheet(spreadsheetId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  renameSheet: async (spreadsheetId, sheetIndex, newName) => {
    set({ saving: true, error: null });
    try {
      const currentSpreadsheet = get().currentSpreadsheet;
      const sheetId = currentSpreadsheet?.sheets?.[sheetIndex]?.id ?? sheetIndex;
      await spreadsheetsApi.renameSheet(spreadsheetId, sheetId, newName);
      await get().getSpreadsheet(spreadsheetId);
      set({ saving: false });
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  freezePanes: async (spreadsheetId, sheetIndex, row, col) => {
    set({ saving: true, error: null });
    try {
      const currentSpreadsheet = get().currentSpreadsheet;
      const sheetId = currentSpreadsheet?.sheets?.[sheetIndex]?.id ?? sheetIndex;
      await spreadsheetsApi.freezePanes(spreadsheetId, sheetId, row, col);
      await get().getSpreadsheet(spreadsheetId);
      set({ saving: false });
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  // Conditional Formatting
  addConditionalFormat: async (spreadsheetId, sheetIndex, rule) => {
    set({ saving: true, error: null });
    try {
      const result = await spreadsheetsApi.addConditionalFormat(spreadsheetId, sheetIndex, rule);
      set({ saving: false });
      return result;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  removeConditionalFormat: async (spreadsheetId, sheetIndex, ruleId) => {
    set({ saving: true, error: null });
    try {
      await spreadsheetsApi.removeConditionalFormat(spreadsheetId, sheetIndex, ruleId);
      set({ saving: false });
      return true;
    } catch (err) {
      set({ error: err.message, saving: false });
      return false;
    }
  },

  // Data Validation
  addDataValidation: async (spreadsheetId, sheetIndex, validation) => {
    set({ saving: true, error: null });
    try {
      const result = await spreadsheetsApi.addDataValidation(spreadsheetId, sheetIndex, validation);
      set({ saving: false });
      return result;
    } catch (err) {
      set({ error: err.message, saving: false });
      return null;
    }
  },

  // Pivot Tables
  createPivotTable: async (spreadsheetId, config) => {
    set({ loading: true, error: null });
    try {
      const pivot = await spreadsheetsApi.createPivotTable(spreadsheetId, config);
      set((state) => ({
        pivotTables: [...state.pivotTables, pivot].slice(0, 100),
        loading: false,
      }));
      return pivot;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  refreshPivotTable: async (spreadsheetId, pivotId) => {
    try {
      const pivot = await spreadsheetsApi.refreshPivotTable(spreadsheetId, pivotId);
      set((state) => ({
        pivotTables: state.pivotTables.map((p) => (p.id === pivotId ? pivot : p)),
      }));
      return pivot;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  updatePivotTable: async (spreadsheetId, pivotId, config) => {
    set({ loading: true, error: null });
    try {
      const pivot = await spreadsheetsApi.updatePivotTable(spreadsheetId, pivotId, config);
      set((state) => ({
        pivotTables: state.pivotTables.map((p) => (p.id === pivotId ? pivot : p)),
        loading: false,
      }));
      return pivot;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deletePivotTable: async (spreadsheetId, pivotId) => {
    set({ loading: true, error: null });
    try {
      await spreadsheetsApi.deletePivotTable(spreadsheetId, pivotId);
      set((state) => ({
        pivotTables: state.pivotTables.filter((p) => p.id !== pivotId),
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Formula Engine
  evaluateFormula: async (spreadsheetId, formula, sheetIndex = 0) => {
    try {
      const result = await spreadsheetsApi.evaluateFormula(spreadsheetId, formula, sheetIndex);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  validateFormula: async (spreadsheetId, formula) => {
    try {
      const result = await spreadsheetsApi.validateFormula(spreadsheetId, formula);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  listFunctions: async () => {
    try {
      const result = await spreadsheetsApi.listFunctions();
      return result;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Import/Export
  importCsv: async (file, options = {}) => {
    set({ loading: true, error: null });
    try {
      const spreadsheet = await spreadsheetsApi.importCsv(file, options);
      set((state) => ({
        spreadsheets: [spreadsheet, ...state.spreadsheets].slice(0, 200),
        currentSpreadsheet: spreadsheet,
        loading: false,
      }));
      return spreadsheet;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  importExcel: async (file, options = {}) => {
    set({ loading: true, error: null });
    try {
      const spreadsheet = await spreadsheetsApi.importExcel(file, options);
      set((state) => ({
        spreadsheets: [spreadsheet, ...state.spreadsheets].slice(0, 200),
        currentSpreadsheet: spreadsheet,
        loading: false,
      }));
      return spreadsheet;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  exportSpreadsheet: async (spreadsheetId, format) => {
    try {
      const blob = await spreadsheetsApi.exportSpreadsheet(spreadsheetId, format);
      return blob;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // AI Features
  generateFormula: async (spreadsheetId, naturalLanguage, context = {}) => {
    try {
      const result = await spreadsheetsApi.generateFormula(spreadsheetId, naturalLanguage, context);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  explainFormula: async (spreadsheetId, formula) => {
    try {
      const result = await spreadsheetsApi.explainFormula(spreadsheetId, formula);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  detectAnomalies: async (spreadsheetId, column, options = {}) => {
    try {
      const result = await spreadsheetsApi.detectAnomalies(spreadsheetId, column, options);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  suggestDataCleaning: async (spreadsheetId, options = {}) => {
    try {
      const result = await spreadsheetsApi.suggestDataCleaning(spreadsheetId, options);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  predictColumn: async (spreadsheetId, column, options = {}) => {
    try {
      const result = await spreadsheetsApi.predictColumn(spreadsheetId, column, options);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  suggestFormulas: async (spreadsheetId, context = {}) => {
    try {
      const result = await spreadsheetsApi.suggestFormulas(spreadsheetId, context);
      return result;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Collaboration
  startCollaboration: async (spreadsheetId, data = {}) => {
    try {
      const session = await spreadsheetsApi.startSpreadsheetCollaboration(spreadsheetId, data);
      return session;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  fetchCollaborators: async (spreadsheetId) => {
    try {
      const response = await spreadsheetsApi.getSpreadsheetCollaborators(spreadsheetId);
      return response;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Reset
  reset: () => set({
    currentSpreadsheet: null,
    activeSheetIndex: 0,
    selectedCells: null,
    pivotTables: [],
    error: null,
  }),

  clearSpreadsheets: () => set({
    spreadsheets: [],
    currentSpreadsheet: null,
  }),
}));

export default useSpreadsheetStore;

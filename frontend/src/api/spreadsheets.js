/**
 * Spreadsheets API Client
 * Handles spreadsheet operations, formulas, pivot tables, and AI features.
 */
import { api } from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

function parseA1Range(range) {
  if (!range || typeof range !== 'string') return null;
  const [start, end] = range.split(':');
  const parseCell = (cell) => {
    if (!cell) return null;
    const m = String(cell).trim().toUpperCase().match(/^([A-Z]+)(\d+)$/);
    if (!m) return null;
    const [, letters, rowStr] = m;
    let col = 0;
    for (let i = 0; i < letters.length; i += 1) {
      col = col * 26 + (letters.charCodeAt(i) - 64);
    }
    return { row: Number(rowStr) - 1, col: col - 1 };
  };
  const s = parseCell(start);
  const e = parseCell(end || start);
  if (!s || !e) return null;
  return {
    start_row: Math.max(0, Math.min(s.row, e.row)),
    end_row: Math.max(0, Math.max(s.row, e.row)),
    start_col: Math.max(0, Math.min(s.col, e.col)),
    end_col: Math.max(0, Math.max(s.col, e.col)),
  };
}

function indexToColumnLabel(index) {
  let col = Number(index) + 1;
  let label = '';
  while (col > 0) {
    const rem = (col - 1) % 26;
    label = String.fromCharCode(65 + rem) + label;
    col = Math.floor((col - 1) / 26);
  }
  return label;
}

function matrixToCellMap(matrix) {
  if (!Array.isArray(matrix)) return {};
  const cellMap = {};
  matrix.forEach((row, rowIndex) => {
    if (!Array.isArray(row)) return;
    row.forEach((rawValue, colIndex) => {
      if (rawValue == null || rawValue === '') return;
      const cellRef = `${indexToColumnLabel(colIndex)}${rowIndex + 1}`;
      const isFormula = typeof rawValue === 'string' && rawValue.startsWith('=');
      cellMap[cellRef] = {
        value: isFormula ? '' : rawValue,
        formula: isFormula ? rawValue : null,
      };
    });
  });
  return cellMap;
}

function normalizeSheetPayload(detail, fallback = {}) {
  const index = fallback.index ?? 0;
  const rawData = Array.isArray(detail?.data) ? detail.data : [];
  return {
    id: detail?.sheet_id || fallback.id || `sheet-${index}`,
    name: detail?.sheet_name || fallback.name || `Sheet ${index + 1}`,
    index,
    row_count: rawData.length,
    col_count: rawData[0]?.length || 0,
    data: matrixToCellMap(rawData),
    raw_data: rawData,
    formats: detail?.formats || {},
    column_widths: detail?.column_widths || {},
    row_heights: detail?.row_heights || {},
    frozen_rows: detail?.frozen_rows ?? 0,
    frozen_cols: detail?.frozen_cols ?? 0,
    conditional_formats: Array.isArray(detail?.conditional_formats) ? detail.conditional_formats : [],
    data_validations: Array.isArray(detail?.data_validations) ? detail.data_validations : [],
  };
}

function normalizeSpreadsheetPayload(payload, sheetFallbacks = []) {
  if (!payload || typeof payload !== 'object') return payload;
  if (Array.isArray(payload.sheets)) {
    return payload;
  }
  const base = {
    id: payload.id,
    name: payload.name,
  };
  const fallback = sheetFallbacks[0] || { index: 0 };
  return {
    ...base,
    sheets: [normalizeSheetPayload(payload, fallback)],
  };
}

function parseCellRef(cellRef) {
  if (typeof cellRef !== 'string') return null;
  const match = cellRef.trim().toUpperCase().match(/^([A-Z]+)(\d+)$/);
  if (!match) return null;
  const [, letters, rowStr] = match;
  let col = 0;
  for (let i = 0; i < letters.length; i += 1) {
    col = col * 26 + (letters.charCodeAt(i) - 64);
  }
  return { row: Number(rowStr) - 1, col: col - 1 };
}

// ============================================
// Spreadsheet CRUD
// ============================================

export async function createSpreadsheet(data) {
  const response = await api.post('/spreadsheets', data);
  return response.data;
}

export async function getSpreadsheet(spreadsheetId) {
  const firstResponse = await api.get(`/spreadsheets/${spreadsheetId}`);
  const firstPayload = firstResponse.data;

  if (firstPayload && typeof firstPayload === 'object' && Array.isArray(firstPayload.sheets)) {
    return firstPayload;
  }

  let sheetFallbacks = [{ index: 0 }];
  try {
    const listResponse = await api.get('/spreadsheets', { params: { limit: 500, offset: 0 } });
    const listPayload = listResponse.data;
    const spreadsheets = asArray(listPayload, ['spreadsheets', 'items', 'results']);
    const matched = spreadsheets.find((item) => item?.id === spreadsheetId);
    if (Array.isArray(matched?.sheets) && matched.sheets.length > 0) {
      sheetFallbacks = matched.sheets
        .map((sheet, idx) => ({
          id: sheet?.id,
          name: sheet?.name,
          index: typeof sheet?.index === 'number' ? sheet.index : idx,
        }))
        .sort((a, b) => a.index - b.index);
    }
  } catch {
    // Fallback to a single-sheet projection if metadata lookup fails.
  }

  if (sheetFallbacks.length <= 1) {
    return normalizeSpreadsheetPayload(firstPayload, sheetFallbacks);
  }

  const detailsByIndex = new Map();
  detailsByIndex.set(0, firstPayload);

  const pendingIndexes = sheetFallbacks
    .map((sheet) => sheet.index)
    .filter((index) => index !== 0);

  await Promise.all(
    pendingIndexes.map(async (sheetIndex) => {
      try {
        const detailResponse = await api.get(`/spreadsheets/${spreadsheetId}`, {
          params: { sheet_index: sheetIndex },
        });
        detailsByIndex.set(sheetIndex, detailResponse.data);
      } catch {
        // Keep missing sheets out of the normalized response.
      }
    })
  );

  const sheets = sheetFallbacks
    .map((fallback) => normalizeSheetPayload(detailsByIndex.get(fallback.index), fallback))
    .filter((sheet) => sheet && sheet.id);

  return {
    id: firstPayload?.id || spreadsheetId,
    name: firstPayload?.name || 'Spreadsheet',
    sheets: sheets.length ? sheets : [normalizeSheetPayload(firstPayload, { index: 0 })],
  };
}

export async function updateSpreadsheet(spreadsheetId, data) {
  const response = await api.put(`/spreadsheets/${spreadsheetId}`, data);
  return response.data;
}

export async function deleteSpreadsheet(spreadsheetId) {
  const response = await api.delete(`/spreadsheets/${spreadsheetId}`);
  return response.data;
}

export async function listSpreadsheets(params = {}) {
  const response = await api.get('/spreadsheets', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { spreadsheets: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const spreadsheets = asArray(payload, ['spreadsheets', 'items', 'results']);
    return { ...payload, spreadsheets, total: payload.total ?? spreadsheets.length };
  }
  return { spreadsheets: [], total: 0 };
}

// ============================================
// Cell Operations
// ============================================

export async function updateCells(spreadsheetId, sheetIndex, updates) {
  const normalizedUpdates = Array.isArray(updates)
    ? updates
    : Object.entries(updates || {}).map(([cellRef, payload]) => {
        const position = parseCellRef(cellRef);
        if (!position) return null;
        const value = payload?.formula || payload?.value || '';
        return { row: position.row, col: position.col, value };
      }).filter(Boolean);

  const response = await api.put(`/spreadsheets/${spreadsheetId}/cells`, { updates: normalizedUpdates }, {
    params: { sheet_index: sheetIndex },
  });
  return response.data;
}

export async function getCellRange(spreadsheetId, sheetIndex, startCellOrRange, endCell = null) {
  const rangeParams = parseA1Range(
    endCell == null && typeof startCellOrRange === 'string'
      ? startCellOrRange
      : `${startCellOrRange || ''}:${endCell || ''}`
  );
  const params = { sheet_index: sheetIndex };
  if (rangeParams) {
    Object.assign(params, rangeParams);
  }
  const response = await api.get(`/spreadsheets/${spreadsheetId}/cells`, { params });
  return response.data;
}

// ============================================
// Sheet Operations
// ============================================

export async function addSheet(spreadsheetId, name) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/sheets`, { name });
  return response.data;
}

export async function deleteSheet(spreadsheetId, sheetIndex) {
  const response = await api.delete(`/spreadsheets/${spreadsheetId}/sheets/${sheetIndex}`);
  return response.data;
}

export async function renameSheet(spreadsheetId, sheetId, newName) {
  const response = await api.put(`/spreadsheets/${spreadsheetId}/sheets/${sheetId}/rename`, null, {
    params: { name: newName },
  });
  return response.data;
}

export async function freezePanes(spreadsheetId, sheetId, rows, columns) {
  const response = await api.put(`/spreadsheets/${spreadsheetId}/sheets/${sheetId}/freeze`, {
    rows,
    cols: columns,
  });
  return response.data;
}

// ============================================
// Formatting
// ============================================

export async function addConditionalFormat(spreadsheetId, sheetIndex, format) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/sheets/${sheetIndex}/conditional-format`, format);
  return response.data;
}

export async function removeConditionalFormat(spreadsheetId, sheetIndex, formatId) {
  const response = await api.delete(`/spreadsheets/${spreadsheetId}/sheets/${sheetIndex}/conditional-formats/${formatId}`);
  return response.data;
}

export async function addDataValidation(spreadsheetId, sheetIndex, validation) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/sheets/${sheetIndex}/validation`, validation);
  return response.data;
}

// ============================================
// Pivot Tables
// ============================================

export async function createPivotTable(spreadsheetId, config) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/pivot`, config);
  return response.data;
}

export async function updatePivotTable(spreadsheetId, pivotId, config) {
  const response = await api.put(`/spreadsheets/${spreadsheetId}/pivot/${pivotId}`, config);
  return response.data;
}

export async function deletePivotTable(spreadsheetId, pivotId) {
  const response = await api.delete(`/spreadsheets/${spreadsheetId}/pivot/${pivotId}`);
  return response.data;
}

export async function refreshPivotTable(spreadsheetId, pivotId) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/pivot/${pivotId}/refresh`);
  return response.data;
}

// ============================================
// Formula Engine
// ============================================

export async function evaluateFormula(spreadsheetId, formula, sheetIndex = 0) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/evaluate`, null, {
    params: { formula, sheet_index: sheetIndex },
  });
  return response.data;
}

export async function validateFormula(formulaOrSpreadsheetId, maybeFormula) {
  const formula = maybeFormula ?? formulaOrSpreadsheetId;
  const response = await api.post('/spreadsheets/formula/validate', { formula });
  return response.data;
}

export async function listFunctions() {
  const response = await api.get('/spreadsheets/formula/functions');
  return asArray(response.data, ['functions', 'items', 'results']);
}

// ============================================
// Import/Export
// ============================================

export async function importCsv(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  Object.entries(options).forEach(([key, value]) => {
    formData.append(key, value);
  });
  const response = await api.post('/spreadsheets/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function importExcel(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  Object.entries(options).forEach(([key, value]) => {
    formData.append(key, value);
  });
  const response = await api.post('/spreadsheets/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function exportSpreadsheet(spreadsheetId, format) {
  const response = await api.get(`/spreadsheets/${spreadsheetId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}

// ============================================
// AI Features
// ============================================

export async function generateFormula(spreadsheetId, description, options = {}) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/formula`, {
    description,
    available_columns: options.availableColumns || [],
    sheet_context: options.context || null,
  });
  return response.data;
}

export async function explainFormula(spreadsheetId, formula) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/explain`, null, {
    params: { formula },
  });
  return response.data;
}

export async function suggestDataCleaning(spreadsheetId, sheetIndexOrOptions = 0, column = null) {
  const options = sheetIndexOrOptions && typeof sheetIndexOrOptions === 'object'
    ? sheetIndexOrOptions
    : { sheetIndex: sheetIndexOrOptions, column };
  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/clean`, null, {
    params: {
      sheet_index: options.sheetIndex ?? options.sheet_index ?? 0,
      column: options.column ?? null,
    },
  });
  return response.data;
}

export async function detectAnomalies(spreadsheetId, column, options = {}) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/anomalies`, null, {
    params: {
      column,
      sheet_index: options.sheetIndex || 0,
      sensitivity: options.sensitivity || 'medium',
    },
  });
  return response.data;
}

export async function predictColumn(spreadsheetId, targetDescriptionOrColumn, basedOnColumnsOrOptions, options = {}) {
  const legacyColumn = targetDescriptionOrColumn;
  const inferredOptions = basedOnColumnsOrOptions && typeof basedOnColumnsOrOptions === 'object' && !Array.isArray(basedOnColumnsOrOptions)
    ? basedOnColumnsOrOptions
    : options;
  const targetDescription = inferredOptions.targetDescription || inferredOptions.target_description || legacyColumn;
  const basedOnColumns = Array.isArray(inferredOptions.basedOnColumns)
    ? inferredOptions.basedOnColumns
    : (Array.isArray(basedOnColumnsOrOptions) ? basedOnColumnsOrOptions : []);

  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/predict`, null, {
    params: {
      target_description: targetDescription,
      based_on_columns: basedOnColumns.length ? basedOnColumns.join(',') : undefined,
      sheet_index: inferredOptions.sheetIndex ?? inferredOptions.sheet_index ?? 0,
    },
  });
  return response.data;
}

export async function suggestFormulas(spreadsheetId, options = {}) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/ai/suggest`, null, {
    params: {
      sheet_index: options.sheetIndex || 0,
      analysis_goals: options.analysisGoals || null,
    },
  });
  return response.data;
}

// ============================================
// Collaboration
// ============================================

export async function startSpreadsheetCollaboration(spreadsheetId, data = {}) {
  const response = await api.post(`/spreadsheets/${spreadsheetId}/collaborate`, data);
  return response.data;
}

export async function getSpreadsheetCollaborators(spreadsheetId) {
  const response = await api.get(`/spreadsheets/${spreadsheetId}/collaborators`);
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { collaborators: payload };
  }
  if (payload && typeof payload === 'object') {
    const collaborators = asArray(payload, ['collaborators', 'users', 'participants']);
    return { ...payload, collaborators };
  }
  return { collaborators: [] };
}

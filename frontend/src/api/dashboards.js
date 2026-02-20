/**
 * Dashboards API Client
 * Handles dashboard building, widgets, analytics, and AI insights.
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

// ============================================
// Dashboard CRUD
// ============================================

export async function createDashboard(data) {
  const response = await api.post('/dashboards', data);
  return response.data;
}

export async function getDashboard(dashboardId) {
  const response = await api.get(`/dashboards/${dashboardId}`);
  return response.data;
}

export async function updateDashboard(dashboardId, data) {
  const response = await api.put(`/dashboards/${dashboardId}`, data);
  return response.data;
}

export async function deleteDashboard(dashboardId) {
  const response = await api.delete(`/dashboards/${dashboardId}`);
  return response.data;
}

export async function listDashboards(params = {}) {
  const response = await api.get('/dashboards', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { dashboards: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const dashboards = asArray(payload, ['dashboards', 'items', 'results']);
    return { ...payload, dashboards, total: payload.total ?? dashboards.length };
  }
  return { dashboards: [], total: 0 };
}

// ============================================
// Widget Operations
// ============================================

export async function addWidget(dashboardId, widget) {
  const response = await api.post(`/dashboards/${dashboardId}/widgets`, widget);
  return response.data;
}

export async function updateWidget(dashboardId, widgetId, data) {
  const response = await api.put(`/dashboards/${dashboardId}/widgets/${widgetId}`, data);
  return response.data;
}

export async function deleteWidget(dashboardId, widgetId) {
  const response = await api.delete(`/dashboards/${dashboardId}/widgets/${widgetId}`);
  return response.data;
}

export async function updateWidgetLayout(dashboardId, layouts) {
  const response = await api.put(`/dashboards/${dashboardId}/layout`, { layouts });
  return response.data;
}

// ============================================
// Data & Queries
// ============================================

export async function executeWidgetQuery(dashboardId, widgetId, filters = {}) {
  const response = await api.post(`/dashboards/${dashboardId}/query`, { filters }, {
    params: { widget_id: widgetId },
  });
  return response.data;
}

export async function refreshDashboard(dashboardId) {
  const response = await api.post(`/dashboards/${dashboardId}/refresh`);
  return response.data;
}

// ============================================
// Snapshot & Embed
// ============================================

export async function createSnapshot(dashboardId, format = 'png') {
  const response = await api.post(`/dashboards/${dashboardId}/snapshot`, null, {
    params: { format },
  });
  return response.data;
}

export async function generateEmbedToken(dashboardId, expiresHours = 24) {
  const response = await api.post(`/dashboards/${dashboardId}/embed`, null, {
    params: { expires_hours: expiresHours },
  });
  return response.data;
}

export async function getSnapshotUrl(snapshotId) {
  const response = await api.get(`/dashboards/snapshots/${snapshotId}`);
  return response.data;
}

// ============================================
// Filters & Variables
// ============================================

export async function addFilter(dashboardId, filter) {
  const response = await api.post(`/dashboards/${dashboardId}/filters`, filter);
  return response.data;
}

export async function updateFilter(dashboardId, filterId, data) {
  const response = await api.put(`/dashboards/${dashboardId}/filters/${filterId}`, data);
  return response.data;
}

export async function deleteFilter(dashboardId, filterId) {
  const response = await api.delete(`/dashboards/${dashboardId}/filters/${filterId}`);
  return response.data;
}

export async function setVariable(dashboardId, variableName, value) {
  if (variableName && typeof variableName === 'object') {
    const variable = variableName;
    const resolvedName = variable.name || variable.variable_name || variable.key;
    const resolvedValue = Object.prototype.hasOwnProperty.call(variable, 'value')
      ? variable.value
      : variable.current_value;
    if (!resolvedName) {
      throw new Error('setVariable requires a variable name');
    }
    const response = await api.put(`/dashboards/${dashboardId}/variables/${resolvedName}`, {
      value: resolvedValue,
    });
    return response.data;
  }
  const response = await api.put(`/dashboards/${dashboardId}/variables/${variableName}`, { value });
  return response.data;
}

// ============================================
// AI Analytics
// ============================================

export async function generateInsights(data, context = null) {
  const response = await api.post('/dashboards/analytics/insights', { data, context });
  return response.data;
}

export async function predictTrends(data, dateColumn, valueColumn, periods = 12) {
  const response = await api.post('/dashboards/analytics/trends', {
    data,
    date_column: dateColumn,
    value_column: valueColumn,
  }, {
    params: { periods },
  });
  return response.data;
}

export async function detectAnomalies(data, columns, method = 'zscore') {
  const response = await api.post('/dashboards/analytics/anomalies', {
    data,
    columns,
  }, {
    params: { method },
  });
  return response.data;
}

export async function findCorrelations(data, columns = null) {
  const response = await api.post('/dashboards/analytics/correlations', {
    data,
    columns,
  });
  return response.data;
}

export async function runWhatIfSimulation(dashboardId, scenarios) {
  const response = await api.post(`/dashboards/${dashboardId}/what-if`, { scenarios });
  return response.data;
}

// ============================================
// Templates & Sharing
// ============================================

export async function listDashboardTemplates(params = {}) {
  const response = await api.get('/dashboards/templates', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { templates: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const templates = asArray(payload, ['templates', 'dashboards', 'items', 'results']);
    return { ...payload, templates, total: payload.total ?? templates.length };
  }
  return { templates: [], total: 0 };
}

export async function createFromTemplate(templateId, name) {
  const response = await api.post(`/dashboards/templates/${templateId}/create`, { name });
  return response.data;
}

export async function saveAsTemplate(dashboardId, name, description = null) {
  const response = await api.post(`/dashboards/${dashboardId}/save-as-template`, { name, description });
  return response.data;
}

export async function shareDashboard(dashboardId, shareSettings) {
  const response = await api.post(`/dashboards/${dashboardId}/share`, shareSettings);
  return response.data;
}

// ============================================
// Export
// ============================================

export async function exportDashboard(dashboardId, format) {
  const response = await api.get(`/dashboards/${dashboardId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}

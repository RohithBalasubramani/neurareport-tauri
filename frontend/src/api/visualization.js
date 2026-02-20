/**
 * Visualization API Client
 * Handles diagram and chart generation.
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
// Diagram Generation
// ============================================

export async function generateFlowchart(data, options = {}) {
  // Backend expects { description: string }
  // Container passes { steps: [...] } — join into a description string
  const description = typeof data === 'string'
    ? data
    : Array.isArray(data?.steps) ? data.steps.join('\n') : JSON.stringify(data);
  const response = await api.post('/visualization/diagrams/flowchart', {
    description,
    title: options.title || null,
  });
  return response.data;
}

export async function generateMindmap(data, options = {}) {
  // Backend expects { content: string }
  const content = typeof data === 'string' ? data : (data?.text || JSON.stringify(data));
  const response = await api.post('/visualization/diagrams/mindmap', {
    content,
    title: options.title || null,
    max_depth: options.maxDepth || 3,
  });
  return response.data;
}

export async function generateOrgChart(data, options = {}) {
  // Backend expects { org_data: list[dict] }
  const orgData = Array.isArray(data) ? data : (data?.org_data || [data]);
  const response = await api.post('/visualization/diagrams/org-chart', {
    org_data: orgData,
    title: options.title || null,
  });
  return response.data;
}

export async function generateTimeline(data, options = {}) {
  // Backend expects { events: list[dict] }
  // Container passes { events: [...strings] } — wrap each string into a dict
  let events = Array.isArray(data) ? data : (data?.events || []);
  events = events.map((e) => (typeof e === 'string' ? { description: e } : e));
  const response = await api.post('/visualization/diagrams/timeline', {
    events,
    title: options.title || null,
  });
  return response.data;
}

export async function generateGantt(data, options = {}) {
  // Backend expects { tasks: list[dict] }
  const tasks = Array.isArray(data) ? data : (data?.tasks || [data]);
  const response = await api.post('/visualization/diagrams/gantt', {
    tasks,
    title: options.title || null,
  });
  return response.data;
}

export async function generateNetworkGraph(data, options = {}) {
  // Backend expects { relationships: list[dict] }
  // Container passes { connections: [...strings] }
  let relationships = Array.isArray(data) ? data : (data?.connections || data?.relationships || []);
  relationships = relationships.map((r) => {
    if (typeof r === 'string') {
      const parts = r.split(/\s*->\s*/);
      return { source: parts[0]?.trim(), target: parts[1]?.trim(), label: parts[2]?.trim() || null };
    }
    return r;
  });
  const response = await api.post('/visualization/diagrams/network', {
    relationships,
    title: options.title || null,
  });
  return response.data;
}

export async function generateKanban(data, options = {}) {
  // Backend expects { items: list[dict] }
  // Container passes { tasks: "string" }
  let items;
  if (typeof data === 'string' || typeof data?.tasks === 'string') {
    const raw = typeof data === 'string' ? data : data.tasks;
    items = raw.split('\n').filter(Boolean).map((line) => {
      const [col, ...rest] = line.split(':');
      return { status: col?.trim(), title: rest.join(':').trim() || col?.trim() };
    });
  } else {
    items = Array.isArray(data) ? data : (data?.items || []);
  }
  const response = await api.post('/visualization/diagrams/kanban', {
    items,
    columns: options.columns || null,
    title: options.title || null,
  });
  return response.data;
}

export async function generateSequenceDiagram(data, options = {}) {
  // Backend expects { interactions: list[dict] }
  // Container passes { interactions: [...strings] }
  let interactions = Array.isArray(data) ? data : (data?.interactions || []);
  interactions = interactions.map((i) => {
    if (typeof i === 'string') {
      const match = i.match(/^(.+?)\s*->\s*(.+?):\s*(.+)$/);
      if (match) return { from: match[1].trim(), to: match[2].trim(), message: match[3].trim() };
      return { from: 'Actor', to: 'System', message: i };
    }
    return i;
  });
  const response = await api.post('/visualization/diagrams/sequence', {
    interactions,
    title: options.title || null,
  });
  return response.data;
}

export async function generateWordcloud(data, options = {}) {
  // Backend expects { text: string }
  // Container passes { text: "..." } or { frequencies: {...} }
  const text = typeof data === 'string'
    ? data
    : (data?.text || (data?.frequencies ? JSON.stringify(data.frequencies) : JSON.stringify(data)));
  const response = await api.post('/visualization/diagrams/wordcloud', {
    text,
    max_words: options.maxWords || 100,
    title: options.title || null,
  });
  return response.data;
}

// ============================================
// Chart Generation
// ============================================

export async function tableToChart(tableData, options = {}) {
  const response = await api.post('/visualization/charts/from-table', {
    data: tableData,
    chart_type: options.chartType || 'bar',
    x_column: options.xColumn || null,
    y_columns: options.yColumns || null,
    title: options.title || null,
  });
  return response.data;
}

export async function generateSparklines(data, valueColumns, options = {}) {
  const response = await api.post('/visualization/charts/sparklines', {
    data,
    value_columns: valueColumns,
  });
  return response.data;
}

// ============================================
// Excel Extraction
// ============================================

export async function extractExcel(file) {
  const form = new FormData();
  form.append('file', file);
  const response = await api.post('/visualization/extract-excel', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

// ============================================
// Export
// ============================================

export async function exportDiagramAsMermaid(diagramId) {
  const response = await api.get(`/visualization/diagrams/${diagramId}/mermaid`);
  return response.data;
}

export async function exportDiagramAsSvg(diagramId) {
  const response = await api.get(`/visualization/diagrams/${diagramId}/svg`);
  return response.data;
}

export async function exportDiagramAsPng(diagramId) {
  const response = await api.get(`/visualization/diagrams/${diagramId}/png`, {
    responseType: 'blob',
  });
  return response.data;
}

// ============================================
// Diagram Types
// ============================================

export async function listDiagramTypes() {
  const response = await api.get('/visualization/types/diagrams');
  return asArray(response.data, ['types', 'diagram_types', 'items', 'results']);
}

export async function listChartTypes() {
  const response = await api.get('/visualization/types/charts');
  return asArray(response.data, ['types', 'chart_types', 'items', 'results']);
}

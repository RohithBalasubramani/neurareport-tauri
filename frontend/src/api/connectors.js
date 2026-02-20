/**
 * Connectors API Client
 * Handles database and cloud storage connector operations.
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
// Connector Discovery
// ============================================

export async function listConnectorTypes() {
  const response = await api.get('/connectors/types');
  const payload = response.data;
  return asArray(payload, ['types', 'connectors']);
}

export async function getConnectorType(connectorType) {
  const response = await api.get(`/connectors/types/${connectorType}`);
  const payload = response.data;
  if (payload && typeof payload === 'object' && payload.type) {
    return payload.type;
  }
  return payload;
}

export async function listConnectorsByCategory(category) {
  const response = await api.get(`/connectors/types/by-category/${category}`);
  const payload = response.data;
  return asArray(payload, ['types', 'connectors']);
}

// ============================================
// Connection Test
// ============================================

export async function testConnection(connectorType, config) {
  const response = await api.post(`/connectors/${connectorType}/test`, {
    connector_type: connectorType,
    config,
  });
  return response.data;
}

// ============================================
// Connection CRUD
// ============================================

export async function createConnection(connectorType, name, config) {
  const response = await api.post(`/connectors/${connectorType}/connect`, {
    name,
    connector_type: connectorType,
    config,
  });
  return response.data;
}

export async function getConnection(connectionId) {
  const response = await api.get(`/connectors/${connectionId}`);
  return response.data;
}

export async function listConnections(params = {}) {
  const response = await api.get('/connectors', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { connections: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const connections = asArray(payload, ['connections', 'items', 'results']);
    return { ...payload, connections, total: payload.total ?? connections.length };
  }
  return { connections: [], total: 0 };
}

export async function deleteConnection(connectionId) {
  const response = await api.delete(`/connectors/${connectionId}`);
  return response.data;
}

// ============================================
// Connection Health & Schema
// ============================================

export async function checkConnectionHealth(connectionId) {
  const response = await api.post(`/connectors/${connectionId}/health`);
  return response.data;
}

export async function getConnectionSchema(connectionId) {
  const response = await api.get(`/connectors/${connectionId}/schema`);
  return response.data;
}

// ============================================
// Query Execution
// ============================================

export async function executeQuery(connectionId, query, parameters = null, limit = 1000) {
  const response = await api.post(`/connectors/${connectionId}/query`, {
    query,
    parameters,
    limit,
  });
  return response.data;
}

// ============================================
// OAuth
// ============================================

export async function getOAuthUrl(connectorType, redirectUri, state = null) {
  const response = await api.get(`/connectors/${connectorType}/oauth/authorize`, {
    params: { redirect_uri: redirectUri, state },
  });
  return response.data;
}

export async function handleOAuthCallback(connectorType, code, redirectUri, state = null) {
  const response = await api.post(`/connectors/${connectorType}/oauth/callback`, null, {
    params: { code, redirect_uri: redirectUri, state },
  });
  return response.data;
}

// Legacy OAuth popup endpoint (returns auth_url)
// Uses the /oauth/authorize endpoint which is the actual backend route
export async function getOAuthPopupUrl(connectorType, redirectUri = window.location.origin + '/oauth/callback') {
  const response = await api.get(`/connectors/${connectorType}/oauth/authorize`, {
    params: { redirect_uri: redirectUri },
  })
  return response.data
}

// ============================================
// Cloud Storage Operations
// ============================================

export async function listFiles(connectionId, path = '/') {
  const response = await api.get(`/connectors/${connectionId}/files`, {
    params: { path },
  });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { files: payload };
  }
  if (payload && typeof payload === 'object') {
    const files = asArray(payload, ['files', 'items', 'entries']);
    return { ...payload, files };
  }
  return { files: [] };
}

export async function downloadFile(connectionId, filePath) {
  const response = await api.get(`/connectors/${connectionId}/files/download`, {
    params: { path: filePath },
    responseType: 'blob',
  });
  return response.data;
}

export async function uploadFile(connectionId, file, destinationPath) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('path', destinationPath);
  const response = await api.post(`/connectors/${connectionId}/files/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

// ============================================
// Sync Operations
// ============================================

export async function syncConnection(connectionId, options = {}) {
  const response = await api.post(`/connectors/${connectionId}/sync`, options);
  return response.data;
}

export async function getSyncStatus(connectionId) {
  const response = await api.get(`/connectors/${connectionId}/sync/status`);
  return response.data;
}

export async function scheduleSyncJob(connectionId, schedule) {
  const response = await api.post(`/connectors/${connectionId}/sync/schedule`, schedule);
  return response.data;
}

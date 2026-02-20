/**
 * Cross-Database Federation API Client
 */
import apiClient from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

/**
 * Create a virtual schema
 */
export async function createVirtualSchema({ name, connectionIds, description }) {
  const response = await apiClient.post('/federation/schemas', {
    name,
    connection_ids: connectionIds,
    description,
  });
  return response.data;
}

/**
 * List virtual schemas
 */
export async function listVirtualSchemas({ limit, offset } = {}) {
  const params = {};
  if (limit != null) params.limit = limit;
  if (offset != null) params.offset = offset;
  const response = await apiClient.get('/federation/schemas', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { schemas: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const schemas = asArray(payload, ['schemas', 'items', 'results']);
    return { ...payload, schemas, total: payload.total ?? schemas.length };
  }
  return { schemas: [], total: 0 };
}

/**
 * Get a virtual schema by ID
 */
export async function getVirtualSchema(schemaId) {
  const response = await apiClient.get(`/federation/schemas/${schemaId}`);
  const payload = response.data;
  if (payload && typeof payload === 'object' && payload.schema) {
    return payload;
  }
  if (payload && typeof payload === 'object') {
    return { status: 'ok', schema: payload };
  }
  return { status: 'ok', schema: null };
}

/**
 * Get join suggestions for connections
 */
export async function suggestJoins(connectionIds) {
  const response = await apiClient.post('/federation/suggest-joins', {
    connection_ids: connectionIds,
  });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { suggestions: payload };
  }
  if (payload && typeof payload === 'object') {
    return { ...payload, suggestions: asArray(payload, ['suggestions', 'joins']) };
  }
  return { suggestions: [] };
}

/**
 * Execute a federated query
 */
export async function executeFederatedQuery({ schemaId, query, limit = 100 }) {
  const response = await apiClient.post('/federation/query', {
    virtual_schema_id: schemaId,
    sql: query,
    limit,
  });
  const payload = response.data;
  if (payload && typeof payload === 'object' && Object.prototype.hasOwnProperty.call(payload, 'result')) {
    return payload;
  }
  return { status: 'ok', result: payload };
}

/**
 * Delete a virtual schema
 */
export async function deleteVirtualSchema(schemaId) {
  const response = await apiClient.delete(`/federation/schemas/${schemaId}`);
  return response.data;
}

export default {
  createVirtualSchema,
  listVirtualSchemas,
  getVirtualSchema,
  suggestJoins,
  executeFederatedQuery,
  deleteVirtualSchema,
};

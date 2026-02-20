/**
 * API client for Natural Language to SQL feature
 */
import { api, API_BASE } from './client'

const asArray = (payload, keys = []) => {
  if (Array.isArray(payload)) return payload
  if (!payload || typeof payload !== 'object') return []
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key]
  }
  return []
}

/**
 * Generate SQL from a natural language question
 * @param {Object} params
 * @param {string} params.question - Natural language question
 * @param {string} params.connectionId - Connection ID
 * @param {string[]} [params.tables] - Optional list of tables to query
 * @param {string} [params.context] - Optional additional context
 * @returns {Promise<Object>} Generated SQL with explanation
 */
export async function generateSQL({ question, connectionId, tables, context }) {
  const { data } = await api.post('/nl2sql/generate', {
    question,
    connection_id: connectionId,
    tables: tables?.length ? tables : undefined,
    context: context || undefined,
  })
  return data
}

/**
 * Execute a SQL query
 * @param {Object} params
 * @param {string} params.sql - SQL query to execute
 * @param {string} params.connectionId - Connection ID
 * @param {number} [params.limit=100] - Max rows to return
 * @param {number} [params.offset=0] - Row offset
 * @returns {Promise<Object>} Query results
 */
export async function executeQuery({ sql, connectionId, limit = 100, offset = 0, includeTotal = false }) {
  const { data } = await api.post('/nl2sql/execute', {
    sql,
    connection_id: connectionId,
    limit,
    offset,
    include_total: includeTotal,
  })
  return data
}

/**
 * Get a natural language explanation of a SQL query
 * @param {string} sql - SQL query to explain
 * @returns {Promise<Object>} Explanation
 */
export async function explainQuery(sqlOrConnectionId, maybeSql) {
  const sql = maybeSql ?? sqlOrConnectionId
  const { data } = await api.post('/nl2sql/explain', null, {
    params: { sql },
  })
  return data
}

/**
 * Save a query as a reusable data source
 * @param {Object} params
 * @param {string} params.name - Name for the saved query
 * @param {string} params.sql - SQL query
 * @param {string} params.connectionId - Connection ID
 * @param {string} [params.description] - Optional description
 * @param {string} [params.originalQuestion] - Original NL question
 * @param {string[]} [params.tags] - Optional tags
 * @returns {Promise<Object>} Saved query
 */
export async function saveQuery({ name, sql, connectionId, description, originalQuestion, tags }) {
  const { data } = await api.post('/nl2sql/save', {
    name,
    sql,
    connection_id: connectionId,
    description: description || undefined,
    original_question: originalQuestion || undefined,
    tags: tags?.length ? tags : undefined,
  })
  return data
}

/**
 * List saved queries
 * @param {Object} [params]
 * @param {string} [params.connectionId] - Filter by connection
 * @param {string[]} [params.tags] - Filter by tags
 * @returns {Promise<Object>} List of saved queries
 */
export async function listSavedQueries({ connectionId, tags } = {}) {
  const { data } = await api.get('/nl2sql/saved', {
    params: {
      connection_id: connectionId || undefined,
      tags: tags?.length ? tags : undefined,
    },
  })
  if (Array.isArray(data)) {
    return { queries: data, total: data.length }
  }
  if (data && typeof data === 'object') {
    const queries = asArray(data, ['queries', 'saved_queries', 'items', 'results'])
    return { ...data, queries, total: data.total ?? data.count ?? queries.length }
  }
  return { queries: [], total: 0 }
}

/**
 * Get a saved query by ID
 * @param {string} queryId - Query ID
 * @returns {Promise<Object>} Saved query
 */
export async function getSavedQuery(queryId) {
  const { data } = await api.get(`/nl2sql/saved/${encodeURIComponent(queryId)}`)
  if (data && typeof data === 'object' && data.query) {
    return data.query
  }
  return data
}

/**
 * Delete a saved query
 * @param {string} queryId - Query ID
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteSavedQuery(queryId) {
  const { data } = await api.delete(`/nl2sql/saved/${encodeURIComponent(queryId)}`)
  return data
}

/**
 * Get query history
 * @param {Object} [params]
 * @param {string} [params.connectionId] - Filter by connection
 * @param {number} [params.limit=50] - Max entries to return
 * @returns {Promise<Object>} Query history
 */
export async function getQueryHistory(params = {}) {
  const options = typeof params === 'string'
    ? { connectionId: params, limit: 50 }
    : (params || {})
  const { connectionId, limit = 50 } = options
  const { data } = await api.get('/nl2sql/history', {
    params: {
      connection_id: connectionId || undefined,
      limit,
    },
  })
  if (Array.isArray(data)) {
    return { history: data, total: data.length }
  }
  if (data && typeof data === 'object') {
    const history = asArray(data, ['history', 'queries', 'items', 'results'])
    return { ...data, history, total: data.total ?? data.count ?? history.length }
  }
  return { history: [], total: 0 }
}

/**
 * Delete a query history entry
 * @param {string} entryId - History entry ID
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteQueryHistoryEntry(entryId) {
  const { data } = await api.delete(`/nl2sql/history/${encodeURIComponent(entryId)}`)
  return data
}

/**
 * Widget Intelligence API client.
 *
 * Provides access to the widget catalog, AI-powered widget selection,
 * grid packing, validation, and formatting.
 */
import { api } from './client'

/**
 * Get the full widget catalog with all registered scenarios.
 * @returns {Promise<{widgets: Array, count: number}>}
 */
export async function getWidgetCatalog() {
  const response = await api.get('/widgets/catalog')
  return response.data
}

/**
 * AI-powered widget selection for a dashboard query.
 * @param {Object} params
 * @param {string} params.query - Natural language query
 * @param {string} [params.queryType='overview'] - Query type
 * @param {Object} [params.dataProfile] - Data profile for scoring
 * @param {number} [params.maxWidgets=10] - Maximum widgets to select
 * @returns {Promise<{widgets: Array, count: number}>}
 */
export async function selectWidgets({
  query,
  queryType = 'overview',
  dataProfile = null,
  maxWidgets = 10,
}) {
  const response = await api.post('/widgets/select', {
    query,
    query_type: queryType,
    data_profile: dataProfile,
    max_widgets: maxWidgets,
  })
  return response.data
}

/**
 * Pack selected widgets into a CSS grid layout.
 * @param {Array} widgets - Widget slots to pack
 * @returns {Promise<{cells: Array, total_cols: number, total_rows: number, utilization_pct: number}>}
 */
export async function packGrid(widgets) {
  const response = await api.post('/widgets/pack-grid', { widgets })
  return response.data
}

/**
 * Validate data shape for a widget scenario.
 * @param {string} scenario - Widget scenario name
 * @param {Object} data - Data to validate
 * @returns {Promise<{scenario: string, valid: boolean, errors: Array}>}
 */
export async function validateWidgetData(scenario, data) {
  const response = await api.post(`/widgets/${scenario}/validate`, { data })
  return response.data
}

/**
 * Format raw data into frontend-ready shape.
 * @param {string} scenario - Widget scenario name
 * @param {Object} data - Raw data to format
 * @returns {Promise<{scenario: string, data: Object}>}
 */
export async function formatWidgetData(scenario, data) {
  const response = await api.post(`/widgets/${scenario}/format`, { data })
  return response.data
}

/**
 * Submit reward signal for Thompson Sampling learning.
 * @param {string} scenario - Widget scenario name
 * @param {number} reward - Reward value (-1.0 to 1.0)
 * @returns {Promise<{status: string, scenario: string}>}
 */
export async function submitWidgetFeedback(scenario, reward) {
  const response = await api.post('/widgets/feedback', { scenario, reward })
  return response.data
}

/**
 * Fetch live data from an active DB connection using a widget's RAG strategy.
 * @param {Object} params
 * @param {string} params.connectionId - Active DB connection ID
 * @param {string} params.scenario - Widget scenario name
 * @param {string} [params.variant] - Optional variant
 * @param {Object} [params.filters] - Optional query filters
 * @param {number} [params.limit=100] - Max rows
 * @returns {Promise<{data: Object, source: string, strategy: string, table_used: string}>}
 */
export async function getWidgetData({ connectionId, scenario, variant, filters, limit = 100 }) {
  const response = await api.post('/widgets/data', {
    connection_id: connectionId,
    scenario,
    variant,
    filters,
    limit,
  })
  return response.data
}

/**
 * Fetch widget data from a report run's extracted tables and content.
 * @param {Object} params
 * @param {string} params.runId - Report run ID
 * @param {string} params.scenario - Widget scenario name
 * @param {string} [params.variant] - Optional variant
 * @returns {Promise<{scenario: string, data: Object, source: string, strategy: string}>}
 */
export async function getWidgetReportData({ runId, scenario, variant }) {
  const response = await api.post('/widgets/data/report', {
    run_id: runId,
    scenario,
    variant,
  })
  return response.data
}

/**
 * Get dynamic widget recommendations for a connected database.
 * Analyzes the DB schema and returns optimal widgets using data-driven scoring.
 * @param {Object} params
 * @param {string} params.connectionId - Active DB connection ID
 * @param {string} [params.query='overview'] - Natural language query for intent
 * @param {number} [params.maxWidgets=8] - Maximum widgets to recommend
 * @returns {Promise<{widgets: Array, count: number, grid: Object, profile: Object}>}
 */
export async function recommendWidgets({ connectionId, query = 'overview', maxWidgets = 8 }) {
  const response = await api.post('/widgets/recommend', {
    connection_id: connectionId,
    query,
    max_widgets: maxWidgets,
  })
  return response.data
}

/**
 * Auto-compose widgets for an existing dashboard.
 * @param {string} dashboardId - Dashboard ID
 * @param {Object} params
 * @param {string} params.query - Natural language query
 * @param {string} [params.queryType='overview'] - Query type
 * @param {number} [params.maxWidgets=8] - Maximum widgets
 * @returns {Promise<{dashboard: Object, added_widgets: number}>}
 */
export async function autoComposeDashboard(dashboardId, { query, queryType = 'overview', maxWidgets = 8 }) {
  const response = await api.post(`/dashboards/${dashboardId}/auto-compose`, {
    query,
    query_type: queryType,
    max_widgets: maxWidgets,
  })
  return response.data
}

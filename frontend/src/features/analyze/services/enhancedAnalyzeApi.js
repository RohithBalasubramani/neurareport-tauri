/**
 * Enhanced Analyze API - Client for AI-powered document analysis
 *
 * Features:
 * - Document upload with streaming progress
 * - Natural language Q&A
 * - Chart generation from queries
 * - Multi-format export
 * - Collaboration features
 */

import { API_BASE, fetchWithIntent, handleStreamingResponse } from '@/api/client'

const API_V2 = `${API_BASE}/analyze/v2`

/**
 * Upload and analyze a document with enhanced AI features
 *
 * @param {Object} options
 * @param {File} options.file - The document file to analyze
 * @param {Object} [options.preferences] - Analysis preferences
 * @param {Function} [options.onProgress] - Callback for progress events
 * @param {AbortSignal} [options.signal] - Abort signal for cancellation
 * @returns {Promise<Object>} The final analysis result
 */
export async function uploadAndAnalyzeEnhanced({
  file,
  preferences = {},
  onProgress,
  signal,
}) {
  if (!file) {
    throw new Error('No file provided for analysis')
  }

  const form = new FormData()
  form.append('file', file)

  if (Object.keys(preferences).length > 0) {
    form.append('preferences', JSON.stringify(preferences))
  }

  const res = await fetchWithIntent(`${API_V2}/upload`, {
    method: 'POST',
    body: form,
    signal,
  })

  return handleStreamingResponse(res, {
    onEvent: onProgress,
    errorMessage: 'Enhanced document analysis failed',
  })
}

/**
 * Get a previously computed analysis result
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} The analysis result
 */
export async function getEnhancedAnalysis(analysisId) {
  if (!analysisId) throw new Error('Analysis ID is required')

  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}`)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Failed to get analysis (${res.status})`)
  }
  return res.json()
}

/**
 * Ask a natural language question about the analyzed document
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} options
 * @param {string} options.question - The question to ask
 * @param {boolean} [options.includeSources=true] - Include source citations
 * @param {number} [options.maxContextChunks=5] - Max context chunks to use
 * @returns {Promise<Object>} The answer with sources
 */
export async function askQuestion(analysisId, { question, includeSources = true, maxContextChunks = 5 }) {
  if (!analysisId) throw new Error('Analysis ID is required')
  if (!question) throw new Error('Question is required')

  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      include_sources: includeSources,
      max_context_chunks: maxContextChunks,
    }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Failed to ask question (${res.status})`)
  }
  return res.json()
}

/**
 * Get suggested questions for an analysis
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Suggested questions
 */
export async function getSuggestedQuestions(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/suggested-questions`)
  if (!res.ok) {
    throw new Error('Failed to get suggested questions')
  }
  return res.json()
}

/**
 * Generate charts from natural language query
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} options
 * @param {string} options.query - Natural language chart request
 * @param {boolean} [options.includeTrends=true] - Include trend lines
 * @param {boolean} [options.includeForecasts=false] - Include forecasts
 * @returns {Promise<Object>} Generated charts
 */
export async function generateCharts(analysisId, { query, includeTrends = true, includeForecasts = false }) {
  if (!analysisId) throw new Error('Analysis ID is required')
  if (!query) throw new Error('Query is required')

  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/charts/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      include_trends: includeTrends,
      include_forecasts: includeForecasts,
    }),
  })

  if (!res.ok) {
    throw new Error('Failed to generate charts')
  }
  return res.json()
}

/**
 * Get all charts for an analysis
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Charts and suggestions
 */
export async function getCharts(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/charts`)
  if (!res.ok) {
    throw new Error('Failed to get charts')
  }
  return res.json()
}

/**
 * Get extracted tables
 *
 * @param {string} analysisId - The analysis ID
 * @param {number} [limit=10] - Maximum tables to return
 * @returns {Promise<Object>} Tables data
 */
export async function getTables(analysisId, limit = 10) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/tables?limit=${limit}`)
  if (!res.ok) {
    throw new Error('Failed to get tables')
  }
  return res.json()
}

/**
 * Get extracted metrics
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Metrics data
 */
export async function getMetrics(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/metrics`)
  if (!res.ok) {
    throw new Error('Failed to get metrics')
  }
  return res.json()
}

/**
 * Get extracted entities
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Entities data
 */
export async function getEntities(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/entities`)
  if (!res.ok) {
    throw new Error('Failed to get entities')
  }
  return res.json()
}

/**
 * Get insights, risks, and opportunities
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Insights data
 */
export async function getInsights(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/insights`)
  if (!res.ok) {
    throw new Error('Failed to get insights')
  }
  return res.json()
}

/**
 * Get data quality assessment
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Data quality report
 */
export async function getDataQuality(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/quality`)
  if (!res.ok) {
    throw new Error('Failed to get data quality')
  }
  return res.json()
}

/**
 * Get a specific summary mode
 *
 * @param {string} analysisId - The analysis ID
 * @param {string} mode - Summary mode (executive, data, quick, comprehensive, action_items, risks, opportunities)
 * @returns {Promise<Object>} Summary data
 */
export async function getSummary(analysisId, mode) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/summary/${mode}`)
  if (!res.ok) {
    throw new Error(`Failed to get ${mode} summary`)
  }
  return res.json()
}

/**
 * Export analysis in various formats
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} options
 * @param {string} options.format - Export format (json, csv, excel, pdf, markdown, html)
 * @param {boolean} [options.includeRawData=true] - Include raw data
 * @param {boolean} [options.includeCharts=true] - Include charts
 * @returns {Promise<Blob>} The exported file
 */
export async function exportAnalysis(analysisId, { format = 'json', includeRawData = true, includeCharts = true }) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      format,
      include_raw_data: includeRawData,
      include_charts: includeCharts,
    }),
  })

  if (!res.ok) {
    throw new Error('Failed to export analysis')
  }

  return res.blob()
}

/**
 * Compare two documents
 *
 * @param {string} analysisId1 - First analysis ID
 * @param {string} analysisId2 - Second analysis ID
 * @returns {Promise<Object>} Comparison result
 */
export async function compareDocuments(analysisId1, analysisId2) {
  const res = await fetchWithIntent(`${API_V2}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      analysis_id_1: analysisId1,
      analysis_id_2: analysisId2,
    }),
  })

  if (!res.ok) {
    throw new Error('Failed to compare documents')
  }
  return res.json()
}

/**
 * Add a comment to an analysis
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} options
 * @param {string} options.content - Comment content
 * @param {string} [options.elementType] - Type of element (table, chart, insight, metric)
 * @param {string} [options.elementId] - ID of the element
 * @param {string} [options.userId] - User ID
 * @param {string} [options.userName] - User name
 * @returns {Promise<Object>} Created comment
 */
export async function addComment(analysisId, { content, elementType, elementId, userId = 'anonymous', userName = 'Anonymous' }) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content,
      element_type: elementType,
      element_id: elementId,
      user_id: userId,
      user_name: userName,
    }),
  })

  if (!res.ok) {
    throw new Error('Failed to add comment')
  }
  return res.json()
}

/**
 * Get comments for an analysis
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} Comments
 */
export async function getComments(analysisId) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/comments`)
  if (!res.ok) {
    throw new Error('Failed to get comments')
  }
  return res.json()
}

/**
 * Create a share link for an analysis
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} options
 * @param {string} [options.accessLevel='view'] - Access level (view, comment, edit)
 * @param {number} [options.expiresHours] - Hours until expiration
 * @param {boolean} [options.passwordProtected=false] - Require password
 * @param {string[]} [options.allowedEmails=[]] - Allowed email addresses
 * @returns {Promise<Object>} Share link info
 */
export async function createShareLink(analysisId, { accessLevel = 'view', expiresHours, passwordProtected = false, allowedEmails = [] }) {
  const res = await fetchWithIntent(`${API_V2}/${encodeURIComponent(analysisId)}/share`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      access_level: accessLevel,
      expires_hours: expiresHours,
      password_protected: passwordProtected,
      allowed_emails: allowedEmails,
    }),
  })

  if (!res.ok) {
    throw new Error('Failed to create share link')
  }
  return res.json()
}

/**
 * Get available industry options
 *
 * @returns {Promise<Object>} Industry options
 */
export async function getIndustryOptions() {
  const res = await fetchWithIntent(`${API_V2}/config/industries`)
  if (!res.ok) {
    throw new Error('Failed to get industry options')
  }
  return res.json()
}

/**
 * Get available export formats
 *
 * @returns {Promise<Object>} Export formats
 */
export async function getExportFormats() {
  const res = await fetchWithIntent(`${API_V2}/config/export-formats`)
  if (!res.ok) {
    throw new Error('Failed to get export formats')
  }
  return res.json()
}

/**
 * Get available chart types
 *
 * @returns {Promise<Object>} Chart types
 */
export async function getChartTypes() {
  const res = await fetchWithIntent(`${API_V2}/config/chart-types`)
  if (!res.ok) {
    throw new Error('Failed to get chart types')
  }
  return res.json()
}

/**
 * Get available summary modes
 *
 * @returns {Promise<Object>} Summary modes
 */
export async function getSummaryModes() {
  const res = await fetchWithIntent(`${API_V2}/config/summary-modes`)
  if (!res.ok) {
    throw new Error('Failed to get summary modes')
  }
  return res.json()
}

export default {
  uploadAndAnalyzeEnhanced,
  getEnhancedAnalysis,
  askQuestion,
  getSuggestedQuestions,
  generateCharts,
  getCharts,
  getTables,
  getMetrics,
  getEntities,
  getInsights,
  getDataQuality,
  getSummary,
  exportAnalysis,
  compareDocuments,
  addComment,
  getComments,
  createShareLink,
  getIndustryOptions,
  getExportFormats,
  getChartTypes,
  getSummaryModes,
}

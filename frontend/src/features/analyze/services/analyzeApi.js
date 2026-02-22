import { API_BASE, fetchWithIntent, handleStreamingResponse } from '@/api/client'

/**
 * Upload and analyze a document (PDF or Excel).
 * Returns streaming NDJSON events with progress and final result.
 *
 * @param {Object} options
 * @param {File} options.file - The document file to analyze
 * @param {string} [options.templateId] - Optional template ID to link
 * @param {string} [options.connectionId] - Optional connection ID
 * @param {Function} [options.onProgress] - Callback for progress events
 * @param {boolean} [options.background=false] - Queue analysis as a background job
 * @param {AbortSignal} [options.signal] - Abort signal for cancelling the request
 * @returns {Promise<Object>} The final analysis result
 */
export async function uploadAndAnalyze({
  file,
  templateId,
  connectionId,
  onProgress,
  background = false,
  signal,
}) {
  if (!file) {
    throw new Error('No file provided for analysis')
  }

  const form = new FormData()
  form.append('file', file)
  if (templateId) form.append('template_id', templateId)
  if (connectionId) form.append('connection_id', connectionId)

  if (background) {
    const res = await fetchWithIntent(`${API_BASE}/analyze/upload?background=true`, {
      method: 'POST',
      body: form,
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(text || `Failed to queue analysis (${res.status})`)
    }
    return res.json()
  }

  const res = await fetchWithIntent(`${API_BASE}/analyze/upload`, {
    method: 'POST',
    body: form,
    signal,
  })

  return handleStreamingResponse(res, {
    onEvent: onProgress,
    errorMessage: 'Document analysis failed',
  })
}

/**
 * Get a previously computed analysis result.
 *
 * @param {string} analysisId - The analysis ID
 * @returns {Promise<Object>} The analysis result
 */
export async function getAnalysis(analysisId) {
  if (!analysisId) throw new Error('Analysis ID is required')

  const res = await fetchWithIntent(`${API_BASE}/analyze/${encodeURIComponent(analysisId)}`)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Failed to get analysis (${res.status})`)
  }
  return res.json()
}

/**
 * Get raw data from an analysis for charting.
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} [options]
 * @param {number} [options.limit=500] - Maximum rows to return
 * @param {number} [options.offset=0] - Offset for pagination
 * @returns {Promise<Object>} The raw data
 */
export async function getAnalysisData(analysisId, { limit = 500, offset = 0 } = {}) {
  if (!analysisId) throw new Error('Analysis ID is required')

  const params = new URLSearchParams()
  if (limit) params.set('limit', String(limit))
  if (offset) params.set('offset', String(offset))

  const query = params.toString()
  const res = await fetchWithIntent(`${API_BASE}/analyze/${encodeURIComponent(analysisId)}/data${query ? `?${query}` : ''}`)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Failed to get analysis data (${res.status})`)
  }
  return res.json()
}

/**
 * Get additional chart suggestions for an analysis.
 *
 * @param {string} analysisId - The analysis ID
 * @param {Object} [options]
 * @param {string} [options.question] - Natural language question for chart suggestions
 * @param {boolean} [options.includeSampleData=true] - Include sample data in response
 * @param {string[]} [options.tableIds] - Filter to specific tables
 * @returns {Promise<Object>} Chart suggestions and optional sample data
 */
export async function suggestAnalysisCharts(analysisId, { question, includeSampleData = true, tableIds } = {}) {
  if (!analysisId) throw new Error('Analysis ID is required')

  const payload = {
    question: question || '',
    include_sample_data: includeSampleData,
  }
  if (Array.isArray(tableIds) && tableIds.length) {
    payload.table_ids = tableIds
  }

  const res = await fetchWithIntent(`${API_BASE}/analyze/${encodeURIComponent(analysisId)}/charts/suggest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Failed to get chart suggestions (${res.status})`)
  }
  return res.json()
}

/**
 * Normalize a chart spec from the API response.
 *
 * @param {Object} chart - Raw chart spec from API
 * @param {number} idx - Index for fallback ID
 * @returns {Object|null} Normalized chart spec
 */
export function normalizeChartSpec(chart, idx = 0) {
  if (!chart || typeof chart !== 'object') return null

  const type = typeof chart.type === 'string' ? chart.type.toLowerCase().trim() : 'bar'
  // Backend returns snake_case (x_field), frontend uses camelCase (xField) — accept both
  const rawX = chart.xField ?? chart.x_field ?? ''
  const xField = typeof rawX === 'string' ? rawX.trim() : ''

  let yFields = chart.yFields ?? chart.y_fields
  if (typeof yFields === 'string') {
    yFields = [yFields]
  }
  if (!Array.isArray(yFields)) {
    yFields = []
  }
  const normalizedY = yFields
    .map((v) => (typeof v === 'string' ? v.trim() : String(v)))
    .filter(Boolean)

  if (!xField || !normalizedY.length) return null

  return {
    id: chart.id ? String(chart.id) : `chart_${idx + 1}`,
    type,
    xField,
    yFields: normalizedY,
    groupField: chart.groupField ?? null,
    aggregation: chart.aggregation ?? null,
    title: chart.title ?? null,
    description: chart.description ?? null,
  }
}

/**
 * Validate that a file is a supported document type.
 *
 * @param {File} file - The file to validate
 * @returns {{ valid: boolean, error?: string }}
 */
export function validateDocumentFile(file) {
  if (!file) {
    return { valid: false, error: 'No file selected' }
  }

  const maxSizeMB = 50
  if (file.size > maxSizeMB * 1024 * 1024) {
    return { valid: false, error: `File too large. Maximum size is ${maxSizeMB}MB.` }
  }

  const name = file.name.toLowerCase()
  const validExtensions = ['.pdf', '.xlsx', '.xls', '.xlsm']
  const hasValidExt = validExtensions.some((ext) => name.endsWith(ext))

  if (!hasValidExt) {
    return { valid: false, error: 'Only PDF and Excel files are supported.' }
  }

  return { valid: true }
}

export default {
  uploadAndAnalyze,
  getAnalysis,
  getAnalysisData,
  suggestAnalysisCharts,
  normalizeChartSpec,
  validateDocumentFile,
}

/**
 * Centralized Job Status Utilities
 *
 * This module provides consistent job status normalization and display
 * configuration across all components.
 */

/**
 * Canonical job status values used throughout the application.
 * Backend may return different values (succeeded, queued) which get normalized.
 */
export const JobStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  CANCELLING: 'cancelling',
}

/**
 * Status values considered "active" (job is still processing)
 */
export const ACTIVE_STATUSES = new Set([JobStatus.PENDING, JobStatus.RUNNING, JobStatus.CANCELLING])

/**
 * Status values considered "terminal" (job has finished)
 */
export const TERMINAL_STATUSES = new Set([
  JobStatus.COMPLETED,
  JobStatus.FAILED,
  JobStatus.CANCELLED,
])

/**
 * Status values considered "failure" states
 */
export const FAILURE_STATUSES = new Set([JobStatus.FAILED, JobStatus.CANCELLED])

/**
 * Normalize a job status string to a canonical value.
 * Handles various backend representations (succeeded, queued, etc.)
 *
 * @param {string|undefined|null} status - Raw status value
 * @returns {string} Normalized status
 */
export function normalizeJobStatus(status) {
  const value = (status || '').toString().toLowerCase().trim()

  // Map backend "succeeded" to frontend "completed"
  if (value === 'succeeded' || value === 'success' || value === 'done') {
    return JobStatus.COMPLETED
  }

  // Map "queued" to "pending" for consistent display
  if (value === 'queued') {
    return JobStatus.PENDING
  }

  // Handle in_progress variant
  if (value === 'in_progress' || value === 'started') {
    return JobStatus.RUNNING
  }

  // Handle error variant
  if (value === 'error') {
    return JobStatus.FAILED
  }

  // Handle canceled spelling variant
  if (value === 'canceled') {
    return JobStatus.CANCELLED
  }

  // Handle cancelling state
  if (value === 'canceling') {
    return JobStatus.CANCELLING
  }

  // Return as-is if it's a known canonical status
  if (Object.values(JobStatus).includes(value)) {
    return value
  }

  // Default to pending for unknown statuses
  return JobStatus.PENDING
}

/**
 * Normalize step status (may have different values than job status)
 *
 * @param {string|undefined|null} status - Raw step status
 * @returns {string} Normalized status
 */
export function normalizeStepStatus(status) {
  const value = (status || '').toString().toLowerCase().trim()

  // Steps may report "complete" instead of "completed"
  if (value === 'complete' || value === 'done' || value === 'success') {
    return JobStatus.COMPLETED
  }

  // Steps report "skipped" which we treat as completed
  if (value === 'skipped') {
    return JobStatus.COMPLETED
  }

  return normalizeJobStatus(value)
}

/**
 * Check if a job status indicates the job is still active/processing
 *
 * @param {string} status - Job status (can be raw or normalized)
 * @returns {boolean}
 */
export function isActiveStatus(status) {
  return ACTIVE_STATUSES.has(normalizeJobStatus(status))
}

/**
 * Check if a job status indicates the job has completed (successfully or not)
 *
 * @param {string} status - Job status (can be raw or normalized)
 * @returns {boolean}
 */
export function isTerminalStatus(status) {
  return TERMINAL_STATUSES.has(normalizeJobStatus(status))
}

/**
 * Check if a job status indicates a failure
 *
 * @param {string} status - Job status (can be raw or normalized)
 * @returns {boolean}
 */
export function isFailureStatus(status) {
  return FAILURE_STATUSES.has(normalizeJobStatus(status))
}

/**
 * Check if a job can be retried (must be in a failure state)
 *
 * @param {string} status - Job status
 * @returns {boolean}
 */
export function canRetryJob(status) {
  return normalizeJobStatus(status) === JobStatus.FAILED
}

/**
 * Check if a job can be cancelled (must be active)
 *
 * @param {string} status - Job status
 * @returns {boolean}
 */
export function canCancelJob(status) {
  return isActiveStatus(status)
}

/**
 * Get human-readable label for a status
 *
 * @param {string} status - Job status (can be raw or normalized)
 * @returns {string}
 */
export function getStatusLabel(status) {
  const normalized = normalizeJobStatus(status)
  const labels = {
    [JobStatus.PENDING]: 'Pending',
    [JobStatus.RUNNING]: 'Running',
    [JobStatus.COMPLETED]: 'Completed',
    [JobStatus.FAILED]: 'Failed',
    [JobStatus.CANCELLED]: 'Cancelled',
    [JobStatus.CANCELLING]: 'Cancelling',
  }
  return labels[normalized] || 'Unknown'
}

/**
 * Normalize a job object, converting all status-related fields
 *
 * @param {Object} job - Raw job object from API
 * @returns {Object} Normalized job object
 */
export function normalizeJob(job = {}) {
  const status = normalizeJobStatus(job.status || job.state)
  const result = job.result || {}
  const meta = job.meta || job.metadata || {}

  const artifacts = job.artifacts || result.artifacts || {
    html_url: result.html_url,
    pdf_url: result.pdf_url,
    docx_url: result.docx_url,
    xlsx_url: result.xlsx_url,
  }

  // Normalize step statuses if present
  const steps = Array.isArray(job.steps)
    ? job.steps.map(step => ({
        ...step,
        status: normalizeStepStatus(step.status),
      }))
    : job.steps

  return {
    ...job,
    status,
    steps,
    templateName: job.templateName || job.template_name || job.template || job.templateTitle,
    templateId: job.templateId || job.template_id,
    templateKind: job.templateKind || job.template_kind || job.kind,
    connectionId: job.connectionId || job.connection_id,
    createdAt: job.createdAt || job.created_at || job.startedAt || job.started_at || job.queuedAt || job.queued_at,
    startedAt: job.startedAt || job.started_at || job.created_at || job.queuedAt || job.queued_at,
    finishedAt: job.finishedAt || job.finished_at || job.completed_at || job.completedAt,
    startDate: meta.start_date || meta.startDate || job.start_date || job.startDate,
    endDate: meta.end_date || meta.endDate || job.end_date || job.endDate,
    keyValues: meta.key_values || meta.keyValues || job.key_values || job.keyValues,
    artifacts,
    meta,
  }
}

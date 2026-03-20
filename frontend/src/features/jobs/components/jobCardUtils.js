/**
 * Utility functions for JobCard component.
 */
import { normalizeJobStatus } from '@/utils/jobStatus'
import WorkHistoryOutlinedIcon from '@mui/icons-material/WorkHistoryOutlined'
import RefreshIcon from '@mui/icons-material/Refresh'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'

export const STATUS_CHIP_PROPS = {
  queued: { label: 'Queued', color: 'default', Icon: WorkHistoryOutlinedIcon },
  pending: { label: 'Pending', color: 'default', Icon: WorkHistoryOutlinedIcon },
  running: { label: 'Running', color: 'default', Icon: RefreshIcon },
  completed: { label: 'Completed', color: 'default', Icon: TaskAltIcon },
  succeeded: { label: 'Completed', color: 'default', Icon: TaskAltIcon },
  failed: { label: 'Failed', color: 'default', Icon: ErrorOutlineIcon },
  cancelled: { label: 'Cancelled', color: 'default', Icon: ErrorOutlineIcon },
}

export const STEP_STATUS_COLORS = {
  queued: 'default',
  pending: 'default',
  running: 'default',
  completed: 'default',
  succeeded: 'default',
  failed: 'default',
  cancelled: 'default',
}

export const formatTimestamp = (value) => {
  if (!value) return '\u2014'
  try {
    const date = new Date(value)
    return date.toLocaleString()
  } catch {
    return value
  }
}

export const pickMetaValue = (meta, ...keys) => {
  if (!meta) return undefined
  for (const key of keys) {
    if (meta[key] != null) return meta[key]
  }
  return undefined
}

const formatDateToken = (value) => {
  if (!value) return null
  if (typeof value === 'string') {
    const trimmed = value.trim()
    const match = trimmed.match(/^(\d{4}-\d{2}-\d{2})/)
    if (match) return match[1]
  }
  try {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toISOString().slice(0, 10)
  } catch {
    return String(value)
  }
}

export const formatDateRange = (start, end) => {
  const startLabel = formatDateToken(start)
  const endLabel = formatDateToken(end)
  if (startLabel && endLabel) return `${startLabel} -> ${endLabel}`
  if (startLabel) return `${startLabel} -> ongoing`
  if (endLabel) return `through ${endLabel}`
  return 'Not provided'
}

const normalizeErrorText = (raw) => {
  if (raw == null) return ''
  if (typeof raw === 'string') return raw
  if (typeof raw === 'object') {
    if (typeof raw.message === 'string') return raw.message
    try { return JSON.stringify(raw) } catch { return String(raw) }
  }
  return String(raw)
}

const toArray = (value) => {
  if (value == null) return []
  return Array.isArray(value) ? value : [value]
}

export const extractJobIssues = (job) => {
  const issues = []
  if (!job) return issues
  const seen = new Set()
  const pushIssue = (source, raw) => {
    toArray(raw).forEach((item) => {
      const message = normalizeErrorText(item)
      if (!message) return
      const key = `${source}:${message}`
      if (seen.has(key)) return
      seen.add(key)
      issues.push({ source, message })
    })
  }
  if (job.error) pushIssue('Job', job.error)
  const meta = job.meta || job.metadata
  if (meta) {
    if (meta.error) pushIssue('Meta', meta.error)
    if (meta.errors) pushIssue('Meta', meta.errors)
  }
  const result = job.result
  if (result) {
    if (result.error) pushIssue('Result', result.error)
    if (result.errors) pushIssue('Result', result.errors)
  }
  return issues
}

import { useCallback, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Drawer,
  Box,
  Stack,
  Typography,
  IconButton,
  Chip,
  LinearProgress,
  Divider,
  Tooltip,
  Button,
  Alert,
} from '@mui/material'
import { alpha } from '@mui/material'
import { neutral, status, palette } from '@/app/theme'
import CloseIcon from '@mui/icons-material/Close'
import RefreshIcon from '@mui/icons-material/Refresh'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import WorkHistoryOutlinedIcon from '@mui/icons-material/WorkHistoryOutlined'
import CancelIcon from '@mui/icons-material/Cancel'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useQueryClient } from '@tanstack/react-query'
import { useJobsList } from '@/hooks/useJobs'
import { useAppStore } from '@/stores'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import { cancelJob as cancelJobRequest } from '@/api/client'
import {
  normalizeJob,
  normalizeJobStatus,
  isActiveStatus,
  isFailureStatus,
  JobStatus,
} from '@/utils/jobStatus'

const STATUS_FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
]

const STATUS_CHIP_PROPS = {
  queued: { label: 'Queued', color: 'default', Icon: WorkHistoryOutlinedIcon },
  pending: { label: 'Pending', color: 'default', Icon: WorkHistoryOutlinedIcon },
  running: { label: 'Running', color: 'default', Icon: RefreshIcon },
  completed: { label: 'Completed', color: 'default', Icon: TaskAltIcon },
  succeeded: { label: 'Completed', color: 'default', Icon: TaskAltIcon },
  failed: { label: 'Failed', color: 'default', Icon: ErrorOutlineIcon },
  cancelled: { label: 'Cancelled', color: 'default', Icon: ErrorOutlineIcon },
}

const STEP_STATUS_COLORS = {
  queued: 'default',
  pending: 'default',
  running: 'default',
  completed: 'default',
  succeeded: 'default',
  failed: 'default',
  cancelled: 'default',
}

const formatTimestamp = (value) => {
  if (!value) return '\u2014'
  try {
    const date = new Date(value)
    return date.toLocaleString()
  } catch {
    return value
  }
}

const pickMetaValue = (meta, ...keys) => {
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

const formatDateRange = (start, end) => {
  const startLabel = formatDateToken(start)
  const endLabel = formatDateToken(end)
  if (startLabel && endLabel) {
    return `${startLabel} -> ${endLabel}`
  }
  if (startLabel) {
    return `${startLabel} -> ongoing`
  }
  if (endLabel) {
    return `through ${endLabel}`
  }
  return 'Not provided'
}

const normalizeErrorText = (raw) => {
  if (raw == null) return ''
  if (typeof raw === 'string') return raw
  if (typeof raw === 'object') {
    if (typeof raw.message === 'string') return raw.message
    try {
      return JSON.stringify(raw)
    } catch {
      return String(raw)
    }
  }
  return String(raw)
}

const toArray = (value) => {
  if (value == null) return []
  return Array.isArray(value) ? value : [value]
}

const extractJobIssues = (job) => {
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
  if (job.error) {
    pushIssue('Job', job.error)
  }
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

function StepBadge({ step }) {
  const status = normalizeJobStatus(step?.status || 'queued')
  const color = STEP_STATUS_COLORS[status] || 'default'
  const label = step?.label || step?.name || 'Step'
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="body2" sx={{ mr: 1 }}>
        {label}
      </Typography>
      <Chip
        size="small"
        label={status.charAt(0).toUpperCase() + status.slice(1)}
        color={color === 'default' ? 'default' : color}
        variant={color === 'default' ? 'outlined' : 'filled'}
      />
    </Stack>
  )
}

function JobDetailField({ label, value }) {
  const text = value || '\u2014'
  return (
    <Box sx={{ flex: 1, minWidth: 0 }}>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ letterSpacing: '0.08em', fontWeight: 600, textTransform: 'uppercase' }}
      >
        {label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 500 }} title={typeof text === 'string' ? text : undefined}>
        {text}
      </Typography>
    </Box>
  )
}

function JobCard({ job, onNavigate, onSetupNavigate, connectionName, onCancel, onForceCancel }) {
  const status = normalizeJobStatus(job?.status || 'queued')
  const chip = STATUS_CHIP_PROPS[status] || STATUS_CHIP_PROPS.pending
  const progressValue = job?.progress == null ? (status === 'completed' ? 100 : 0) : job.progress
  const steps = Array.isArray(job?.steps) ? job.steps : []
  const readableType = (job?.type || job?.job_type || 'run_report').replace(/_/g, ' ')
  const meta = job?.meta || job?.metadata || {}
  const startDate = pickMetaValue(meta, 'start_date', 'startDate') || job?.start_date || job?.startDate
  const endDate = pickMetaValue(meta, 'end_date', 'endDate') || job?.end_date || job?.endDate
  const connectionLabel =
    connectionName
    || meta.connection_name
    || meta.connectionName
    || job?.connectionId
    || job?.connection_id
    || 'No connection selected'
  const jobIssues = extractJobIssues(job)
  const isActive = isActiveStatus(status)
  const canOpenGenerate = Boolean(job?.templateId && onNavigate)
  const canOpenSetup = Boolean(job?.connectionId && onSetupNavigate)
  return (
    <Box
      sx={{
        borderRadius: 1,  // Figma spec: 8px
        border: '1px solid',
        borderColor: 'divider',
        p: 2,
        bgcolor: 'background.paper',
        boxShadow: `0 6px 18px ${alpha(neutral[900], 0.05)}`,
      }}
      data-testid="job-card"
    >
      <Stack spacing={0.75}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle1" noWrap title={job?.templateName || job?.templateId || 'Job'}>
              {job?.templateName || job?.templateId || 'Job'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {readableType} {' \u00b7 '}{(job?.templateKind || job?.kind || 'pdf').toUpperCase()}
            </Typography>
            {job?.templateId && (
              <Typography variant="caption" color="text.secondary">
                {job.templateId}
              </Typography>
            )}
          </Box>
          <Chip
            size="small"
            icon={<chip.Icon fontSize="inherit" />}
            label={chip.label}
            color={chip.color === 'default' ? 'default' : chip.color}
            variant={chip.color === 'default' ? 'outlined' : 'filled'}
            data-testid="job-status"
          />
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Started: {formatTimestamp(job?.startedAt || job?.queuedAt)} {' \u00b7 '} Finished:{' '}
          {formatTimestamp(job?.finishedAt)}
        </Typography>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={{ xs: 1, sm: 2 }}
          sx={{ mt: 0.5, flexWrap: 'wrap' }}
        >
          <JobDetailField label="Template ID" value={job?.templateId || 'Unknown template'} />
          <JobDetailField label="Connection" value={connectionLabel} />
          <JobDetailField label="Date range" value={formatDateRange(startDate, endDate)} />
        </Stack>
        {jobIssues.length > 0 && (
          <Stack spacing={0.5}>
            {jobIssues.map((issue, idx) => (
              <Alert
                key={`${job.id || 'job'}-${issue.source}-${idx}`}
                severity="error"
                variant="outlined"
                icon={<ErrorOutlineIcon fontSize="inherit" />}
              >
                <Typography variant="body2">
                  <strong>{issue.source}:</strong> {issue.message}
                </Typography>
              </Alert>
            ))}
          </Stack>
        )}
        <LinearProgress
          variant="determinate"
          value={Math.min(100, Math.max(0, progressValue || 0))}
          sx={{ mt: 1, borderRadius: 1 }}
        />
        <Stack spacing={0.5} sx={{ mt: 1 }}>
          {steps.map((step) => (
            <StepBadge key={step.id || step.name} step={step} />
          ))}
          {!steps.length && (
            <Typography variant="body2" color="text.secondary">
              Awaiting updates...
            </Typography>
          )}
        </Stack>
        {(canOpenGenerate || canOpenSetup) && (
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
            {canOpenGenerate && (
              <Button
                size="small"
                variant="contained"
                color="primary"
                onClick={() => onNavigate(job.templateId)}
              >
                Open Report
              </Button>
            )}
            {canOpenSetup && (
              <Button
                size="small"
                variant="outlined"
                sx={{ color: 'text.secondary' }}
                onClick={() => onSetupNavigate(job.connectionId)}
              >
                Go to Setup
              </Button>
            )}
            {isActive && (
              <Stack direction="row" spacing={1}>
                <Button
                  size="small"
                  variant="outlined"
                  sx={{ color: 'text.secondary' }}
                  startIcon={<CancelIcon fontSize="small" />}
                  onClick={() => onCancel?.(job.id)}
                >
                  Cancel
                </Button>
                <Button
                  size="small"
                  variant="text"
                  sx={{ color: 'text.secondary' }}
                  onClick={() => onForceCancel?.(job.id)}
                >
                  Force stop
                </Button>
              </Stack>
            )}
          </Stack>
        )}
      </Stack>
    </Box>
  )
}

export default function JobsPanel({ open, onClose }) {
  const navigate = useNavigate()
  const { execute } = useInteraction()
  const queryClient = useQueryClient()
  const savedConnections = useAppStore((state) => state.savedConnections)
  const setActiveConnectionId = useAppStore((state) => state.setActiveConnectionId)
  const setSetupNav = useAppStore((state) => state.setSetupNav)
  const jobsQuery = useJobsList({ limit: 30 }) || {}
  const { data, isLoading, isFetching, error, refetch } = jobsQuery
  const [statusFilter, setStatusFilter] = useState('all')
  const jobs = data?.jobs || []
  const normalizedJobs = useMemo(
    () => jobs.map((job) => normalizeJob(job)),
    [jobs],
  )

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'jobs-panel', ...intent },
      action,
    })
  }, [execute])

  const handleNavigate = useCallback((path, options = {}) => {
    const {
      label = `Open ${path}`,
      intent = {},
      navigateOptions,
      beforeNavigate,
    } = options
    return execute({
      type: InteractionType.NAVIGATE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'jobs-panel', path, ...intent },
      action: () => {
        beforeNavigate?.()
        return navigate(path, navigateOptions)
      },
    })
  }, [execute, navigate])

  const markJobCancelled = useCallback((jobId) => {
    if (!jobId || !queryClient) return
    const queries = queryClient.getQueriesData({ queryKey: ['jobs'] }) || []
    queries.forEach(([queryKey, value]) => {
      if (!value) return
      if (Array.isArray(value.jobs)) {
        const updatedJobs = value.jobs.map((job) => {
          if (job.id !== jobId) return job
          const steps = Array.isArray(job.steps)
            ? job.steps.map((step) => {
                const status = (step?.status || '').toLowerCase()
                if (status === 'succeeded' || status === 'failed' || status === 'cancelled') {
                  return step
                }
                return { ...step, status: 'cancelled' }
              })
            : job.steps
          return { ...job, status: 'cancelled', steps }
        })
        queryClient.setQueryData(queryKey, { ...value, jobs: updatedJobs })
      } else if (value.id === jobId) {
        queryClient.setQueryData(queryKey, { ...value, status: 'cancelled' })
      }
    })
  }, [queryClient])

  const handleCancelJob = useCallback((jobId, options = {}) => {
    if (!jobId) return undefined
    const force = Boolean(options?.force)
    return execute({
      type: InteractionType.UPDATE,
      label: force ? 'Force stop job' : 'Cancel job',
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      intent: { source: 'jobs-panel', jobId, force },
      action: async () => {
        await cancelJobRequest(jobId, { force })
        markJobCancelled(jobId)
        await refetch?.()
      },
    })
  }, [execute, markJobCancelled, refetch])

  const handleForceCancelJob = useCallback(
    (jobId) => handleCancelJob(jobId, { force: true }),
    [handleCancelJob],
  )

  const filteredJobs = useMemo(() => {
    if (statusFilter === 'all') {
      return normalizedJobs
    }
    if (statusFilter === 'active') {
      return normalizedJobs.filter((job) => isActiveStatus(job.status))
    }
    if (statusFilter === 'completed') {
      return normalizedJobs.filter((job) => job.status === JobStatus.COMPLETED)
    }
    if (statusFilter === 'failed') {
      return normalizedJobs.filter((job) => isFailureStatus(job.status))
    }
    return normalizedJobs
  }, [normalizedJobs, statusFilter])

  const activeCount = useMemo(
    () => normalizedJobs.filter((job) => isActiveStatus(job.status)).length,
    [normalizedJobs],
  )
  const showEmptyState = !filteredJobs.length && !isLoading && !isFetching && !error

  const connectionLookup = useMemo(() => {
    const lookup = new Map()
    savedConnections.forEach((conn) => {
      if (!conn?.id) return
      lookup.set(conn.id, conn.name || conn.id)
    })
    return lookup
  }, [savedConnections])

  const handleClosePanel = useCallback(() => {
    return executeUI('Close jobs panel', () => onClose?.())
  }, [executeUI, onClose])

  const handleFilterChange = useCallback((filter) => {
    return executeUI('Filter jobs', () => setStatusFilter(filter), { filter })
  }, [executeUI])

  const handleRetry = useCallback(() => {
    return executeUI('Retry jobs refresh', () => refetch?.(), { action: 'refetch' })
  }, [executeUI, refetch])

  const onJobNavigate = useCallback((templateId) => {
    if (!templateId) return undefined
    return handleNavigate(`/reports?template=${encodeURIComponent(templateId)}`, {
      label: 'Open report',
      intent: { templateId },
      beforeNavigate: () => onClose?.(),
    })
  }, [handleNavigate, onClose])

  const onSetupNavigate = useCallback((connectionId) => {
    if (!connectionId) return undefined
    return handleNavigate('/setup/wizard', {
      label: 'Open setup wizard',
      intent: { connectionId },
      beforeNavigate: () => {
        setSetupNav('connect')
        setActiveConnectionId(connectionId)
        onClose?.()
      },
    })
  }, [handleNavigate, setActiveConnectionId, setSetupNav, onClose])

  const emptyDescription =
    statusFilter === 'all'
      ? 'Jobs launched from the Reports page will appear here so you can check progress without leaving your work.'
      : 'No jobs match the selected filter. Try another status or start a new run.'

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={handleClosePanel}
      PaperProps={{
        sx: {
          backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(12px)',
        },
      }}
    >
      <Box
        sx={{
          width: { xs: '100vw', sm: 420 },
          maxWidth: '100vw',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <Stack spacing={2}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="h6">Background Jobs</Typography>
              <Typography variant="body2" color="text.secondary">
                {activeCount ? `${activeCount} active` : 'No active jobs'}
              </Typography>
            </Box>
            <IconButton onClick={handleClosePanel} aria-label="Close jobs panel">
              <CloseIcon />
            </IconButton>
          </Stack>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            flexWrap="wrap"
            data-testid="jobs-filter-group"
          >
            <Typography variant="body2" color="text.secondary">
              Status:
            </Typography>
            {STATUS_FILTERS.map((filter) => (
              <Chip
                key={filter.value}
                size="small"
                label={filter.label}
                sx={statusFilter === filter.value ? { bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' } : undefined}
                variant={statusFilter === filter.value ? 'filled' : 'outlined'}
                onClick={() => handleFilterChange(filter.value)}
                data-testid={`jobs-filter-${filter.value}`}
              />
            ))}
          </Stack>
          {error && (
            <Alert
              severity="error"
              action={
                <Button color="inherit" size="small" onClick={handleRetry}>
                  Retry
                </Button>
              }
            >
              Failed to load jobs: {error.message || String(error)}
            </Alert>
          )}
          {(isLoading || isFetching) && <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }} aria-label="Loading jobs" />}
        </Stack>
        <Divider />
        {showEmptyState ? (
          <EmptyState
            title="No jobs to display"
            description={emptyDescription}
            action={
              statusFilter !== 'all' ? (
                <Button size="small" variant="outlined" onClick={() => handleFilterChange('all')}>
                  Clear filters
                </Button>
              ) : null
            }
          />
        ) : (
          <Stack
            spacing={2}
            sx={{ flex: 1, overflowY: 'auto', pr: 1 }}
            data-testid="jobs-list"
          >
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onNavigate={onJobNavigate}
                onSetupNavigate={onSetupNavigate}
                connectionName={connectionLookup.get(job.connectionId)}
                onCancel={handleCancelJob}
                onForceCancel={handleForceCancelJob}
              />
            ))}
            {!filteredJobs.length && (
              <Tooltip title="Jobs refresh automatically every few seconds" arrow>
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  No jobs yet. Run a report to see progress here.
                </Typography>
              </Tooltip>
            )}
          </Stack>
        )}
      </Box>
    </Drawer>
  )
}


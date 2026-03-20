/**
 * Job Card Component
 * Displays details for a single job with progress, steps, and actions.
 */
import {
  Box,
  Stack,
  Typography,
  Chip,
  LinearProgress,
  Button,
  Alert,
} from '@mui/material'
import { alpha } from '@mui/material'
import { neutral } from '@/app/theme'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import CancelIcon from '@mui/icons-material/Cancel'
import { normalizeJobStatus, isActiveStatus } from '@/utils/jobStatus'
import {
  STATUS_CHIP_PROPS,
  STEP_STATUS_COLORS,
  formatTimestamp,
  pickMetaValue,
  formatDateRange,
  extractJobIssues,
} from './jobCardUtils'

function StepBadge({ step }) {
  const status = normalizeJobStatus(step?.status || 'queued')
  const color = STEP_STATUS_COLORS[status] || 'default'
  const label = step?.label || step?.name || 'Step'
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="body2" sx={{ mr: 1 }}>{label}</Typography>
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

export default function JobCard({ job, onNavigate, onSetupNavigate, connectionName, onCancel, onForceCancel }) {
  const status = normalizeJobStatus(job?.status || 'queued')
  const chip = STATUS_CHIP_PROPS[status] || STATUS_CHIP_PROPS.pending
  const progressValue = job?.progress == null ? (status === 'completed' ? 100 : 0) : job.progress
  const steps = Array.isArray(job?.steps) ? job.steps : []
  const readableType = (job?.type || job?.job_type || 'run_report').replace(/_/g, ' ')
  const meta = job?.meta || job?.metadata || {}
  const startDate = pickMetaValue(meta, 'start_date', 'startDate') || job?.start_date || job?.startDate
  const endDate = pickMetaValue(meta, 'end_date', 'endDate') || job?.end_date || job?.endDate
  const connectionLabel = connectionName || meta.connection_name || meta.connectionName || job?.connectionId || job?.connection_id || 'No connection selected'
  const jobIssues = extractJobIssues(job)
  const isActive = isActiveStatus(status)
  const canOpenGenerate = Boolean(job?.templateId && onNavigate)
  const canOpenSetup = Boolean(job?.connectionId && onSetupNavigate)

  return (
    <Box
      sx={{
        borderRadius: 1,
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
              <Typography variant="caption" color="text.secondary">{job.templateId}</Typography>
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
          Started: {formatTimestamp(job?.startedAt || job?.queuedAt)} {' \u00b7 '} Finished: {formatTimestamp(job?.finishedAt)}
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 1, sm: 2 }} sx={{ mt: 0.5, flexWrap: 'wrap' }}>
          <JobDetailField label="Template ID" value={job?.templateId || 'Unknown template'} />
          <JobDetailField label="Connection" value={connectionLabel} />
          <JobDetailField label="Date range" value={formatDateRange(startDate, endDate)} />
        </Stack>
        {jobIssues.length > 0 && (
          <Stack spacing={0.5}>
            {jobIssues.map((issue, idx) => (
              <Alert key={`${job.id || 'job'}-${issue.source}-${idx}`} severity="error" variant="outlined" icon={<ErrorOutlineIcon fontSize="inherit" />}>
                <Typography variant="body2"><strong>{issue.source}:</strong> {issue.message}</Typography>
              </Alert>
            ))}
          </Stack>
        )}
        <LinearProgress variant="determinate" value={Math.min(100, Math.max(0, progressValue || 0))} sx={{ mt: 1, borderRadius: 1 }} />
        <Stack spacing={0.5} sx={{ mt: 1 }}>
          {steps.map((step) => (<StepBadge key={step.id || step.name} step={step} />))}
          {!steps.length && (<Typography variant="body2" color="text.secondary">Awaiting updates...</Typography>)}
        </Stack>
        {(canOpenGenerate || canOpenSetup) && (
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
            {canOpenGenerate && (
              <Button size="small" variant="contained" color="primary" onClick={() => onNavigate(job.templateId)}>Open Report</Button>
            )}
            {canOpenSetup && (
              <Button size="small" variant="outlined" sx={{ color: 'text.secondary' }} onClick={() => onSetupNavigate(job.connectionId)}>Go to Setup</Button>
            )}
            {isActive && (
              <Stack direction="row" spacing={1}>
                <Button size="small" variant="outlined" sx={{ color: 'text.secondary' }} startIcon={<CancelIcon fontSize="small" />} onClick={() => onCancel?.(job.id)}>Cancel</Button>
                <Button size="small" variant="text" sx={{ color: 'text.secondary' }} onClick={() => onForceCancel?.(job.id)}>Force stop</Button>
              </Stack>
            )}
          </Stack>
        )}
      </Stack>
    </Box>
  )
}

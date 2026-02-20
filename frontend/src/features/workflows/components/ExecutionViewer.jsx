/**
 * Execution Viewer Component
 * Real-time workflow execution monitoring with logs and status tracking.
 */
import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  Button,
  Stack,
  Divider,
  Chip,
  LinearProgress,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Replay as ReplayIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Schedule as PendingIcon,
  Loop as RunningIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Terminal as LogIcon,
  Timer as TimerIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const ViewerContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
}))

const ViewerHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const ViewerContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const StepCard = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'status',
})(({ theme, status }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  border: `1px solid ${
    status === 'success'
      ? alpha(theme.palette.mode === 'dark' ? neutral[500] : neutral[700], 0.3)
      : status === 'error'
      ? alpha(theme.palette.mode === 'dark' ? neutral[700] : neutral[900], 0.3)
      : status === 'running'
      ? alpha(theme.palette.mode === 'dark' ? neutral[500] : neutral[500], 0.3)
      : alpha(theme.palette.divider, 0.2)
  }`,
  backgroundColor:
    status === 'success'
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50])
      : status === 'error'
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50])
      : status === 'running'
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50])
      : 'transparent',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const LogContainer = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.common.black, 0.9),
  borderRadius: 8,
  padding: theme.spacing(1.5),
  fontFamily: 'monospace',
  fontSize: '0.75rem',
  maxHeight: 300,
  overflow: 'auto',
  color: theme.palette.common.white,
}))

const LogLine = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'level',
})(({ theme, level }) => ({
  padding: theme.spacing(0.25, 0),
  borderLeft: `2px solid ${
    level === 'error'
      ? neutral[700]
      : level === 'warning'
      ? neutral[500]
      : level === 'success'
      ? neutral[500]
      : 'transparent'
  }`,
  paddingLeft: level ? theme.spacing(1) : 0,
  color:
    level === 'error'
      ? neutral[300]
      : level === 'warning'
      ? neutral[300]
      : level === 'success'
      ? neutral[300]
      : alpha(theme.palette.common.white, 0.8),
}))

const StatusChip = styled(Chip)(({ theme }) => ({
  borderRadius: 4,
  fontWeight: 600,
  fontSize: '12px',
}))

const TimelineConnector = styled(Box)(({ theme }) => ({
  position: 'absolute',
  left: 19,
  top: 40,
  bottom: 0,
  width: 2,
  backgroundColor: alpha(theme.palette.divider, 0.3),
}))

// =============================================================================
// STATUS HELPERS
// =============================================================================

const STATUS_CONFIG = {
  pending: { icon: PendingIcon, color: 'default', label: 'Pending' },
  running: { icon: RunningIcon, color: 'primary', label: 'Running' },
  success: { icon: SuccessIcon, color: 'success', label: 'Success' },
  error: { icon: ErrorIcon, color: 'error', label: 'Failed' },
  warning: { icon: WarningIcon, color: 'warning', label: 'Warning' },
  skipped: { icon: PendingIcon, color: 'default', label: 'Skipped' },
  cancelled: { icon: StopIcon, color: 'default', label: 'Cancelled' },
}

const formatDuration = (ms) => {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${secs}s`
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleTimeString()
}

// =============================================================================
// STEP COMPONENT
// =============================================================================

function ExecutionStep({ step, isLast, onRetry }) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(step.status === 'error')
  const statusConfig = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending
  const StatusIcon = statusConfig.icon

  return (
    <Box sx={{ position: 'relative' }}>
      {!isLast && <TimelineConnector />}

      <StepCard elevation={0} status={step.status}>
        <Stack direction="row" alignItems="flex-start" spacing={1.5}>
          {/* Status Icon */}
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: alpha(theme.palette[statusConfig.color]?.main || neutral[500], 0.15),
            }}
          >
            {step.status === 'running' ? (
              <CircularProgress size={16} color={statusConfig.color} />
            ) : (
              <StatusIcon
                sx={{
                  fontSize: 18,
                  color: `${statusConfig.color}.main`,
                }}
              />
            )}
          </Box>

          {/* Step Info */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {step.name}
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1}>
                {step.duration && (
                  <Chip
                    icon={<TimerIcon sx={{ fontSize: 12 }} />}
                    label={formatDuration(step.duration)}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '10px' }}
                  />
                )}
                <StatusChip
                  label={statusConfig.label}
                  size="small"
                  sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                />
              </Stack>
            </Stack>

            <Typography variant="caption" color="text.secondary">
              {step.nodeType} • Started: {formatTimestamp(step.startedAt)}
            </Typography>

            {/* Error Message */}
            {step.error && (
              <Alert severity="error" sx={{ mt: 1, py: 0, fontSize: '0.75rem' }}>
                {step.error}
              </Alert>
            )}

            {/* Expand/Collapse for details */}
            {(step.logs?.length > 0 || step.output) && (
              <Button
                size="small"
                onClick={() => setExpanded(!expanded)}
                endIcon={expanded ? <CollapseIcon /> : <ExpandIcon />}
                sx={{ mt: 1, fontSize: '12px', textTransform: 'none' }}
              >
                {expanded ? 'Hide Details' : 'Show Details'}
              </Button>
            )}

            <Collapse in={expanded}>
              {/* Logs */}
              {step.logs?.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, mb: 0.5, display: 'block' }}>
                    Logs
                  </Typography>
                  <LogContainer>
                    {step.logs.map((log, i) => (
                      <LogLine key={i} level={log.level}>
                        <span style={{ opacity: 0.5 }}>[{formatTimestamp(log.timestamp)}]</span>{' '}
                        {log.message}
                      </LogLine>
                    ))}
                  </LogContainer>
                </Box>
              )}

              {/* Output */}
              {step.output && (
                <Box sx={{ mt: 1.5 }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      Output
                    </Typography>
                    <Tooltip title="Copy output">
                      <IconButton
                        size="small"
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(step.output, null, 2))}
                      >
                        <CopyIcon sx={{ fontSize: 14 }} />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                  <LogContainer>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(step.output, null, 2)}
                    </pre>
                  </LogContainer>
                </Box>
              )}

              {/* Retry button for failed steps */}
              {step.status === 'error' && onRetry && (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<ReplayIcon />}
                  onClick={() => onRetry(step.id)}
                  sx={{ mt: 1.5 }}
                >
                  Retry This Step
                </Button>
              )}
            </Collapse>
          </Box>
        </Stack>
      </StepCard>
    </Box>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ExecutionViewer({
  execution = null,
  onStop,
  onPause,
  onResume,
  onRetry,
  onRetryStep,
  onDownloadLogs,
  onClose,
  onFullscreen,
}) {
  const theme = useTheme()
  const logsEndRef = useRef(null)
  const [autoScroll, setAutoScroll] = useState(true)

  // Auto scroll to bottom of logs
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [execution?.steps, autoScroll])

  // Calculate progress
  const progress = useMemo(() => {
    if (!execution?.steps?.length) return 0
    const completed = execution.steps.filter((s) => ['success', 'error', 'skipped'].includes(s.status)).length
    return (completed / execution.steps.length) * 100
  }, [execution?.steps])

  // Calculate totals
  const stats = useMemo(() => {
    if (!execution?.steps) return { success: 0, error: 0, pending: 0 }
    return {
      success: execution.steps.filter((s) => s.status === 'success').length,
      error: execution.steps.filter((s) => s.status === 'error').length,
      pending: execution.steps.filter((s) => s.status === 'pending').length,
      running: execution.steps.filter((s) => s.status === 'running').length,
    }
  }, [execution?.steps])

  if (!execution) {
    return (
      <ViewerContainer>
        <ViewerHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Execution Viewer
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </ViewerHeader>
        <ViewerContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <RunningIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No execution selected
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Run a workflow to see execution details
            </Typography>
          </Box>
        </ViewerContent>
      </ViewerContainer>
    )
  }

  const overallStatus = STATUS_CONFIG[execution.status] || STATUS_CONFIG.pending
  const OverallIcon = overallStatus.icon

  return (
    <ViewerContainer>
      <ViewerHeader>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <OverallIcon sx={{ color: `${overallStatus.color}.main`, fontSize: 24 }} />
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {execution.workflowName || 'Workflow Execution'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              ID: {execution.id}
            </Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Download logs">
            <IconButton size="small" onClick={onDownloadLogs}>
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {onFullscreen && (
            <Tooltip title="Fullscreen">
              <IconButton size="small" onClick={onFullscreen}>
                <FullscreenIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Stack>
      </ViewerHeader>

      {/* Progress Bar */}
      {execution.status === 'running' && (
        <LinearProgress variant="determinate" value={progress} />
      )}

      {/* Status Summary */}
      <Box sx={{ px: 2, py: 1.5, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Stack direction="row" spacing={2}>
            <StatusChip
              label={overallStatus.label}
              size="small"
              sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
            />
            <Typography variant="caption" color="text.secondary">
              {formatTimestamp(execution.startedAt)} • Duration: {formatDuration(execution.duration)}
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1}>
            {execution.status === 'running' && (
              <>
                <Tooltip title="Pause">
                  <IconButton size="small" onClick={onPause}>
                    <PauseIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Stop">
                  <IconButton size="small" onClick={onStop} sx={{ color: 'text.secondary' }}>
                    <StopIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </>
            )}
            {execution.status === 'paused' && (
              <Button
                size="small"
                variant="outlined"
                startIcon={<PlayIcon />}
                onClick={onResume}
              >
                Resume
              </Button>
            )}
            {['error', 'cancelled'].includes(execution.status) && onRetry && (
              <Button
                size="small"
                variant="outlined"
                startIcon={<ReplayIcon />}
                onClick={onRetry}
              >
                Retry
              </Button>
            )}
          </Stack>
        </Stack>

        {/* Stats */}
        <Stack direction="row" spacing={3} mt={1.5}>
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <SuccessIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption">{stats.success} Success</Typography>
          </Stack>
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <ErrorIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption">{stats.error} Failed</Typography>
          </Stack>
          <Stack direction="row" alignItems="center" spacing={0.5}>
            <PendingIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption">{stats.pending} Pending</Typography>
          </Stack>
          {stats.running > 0 && (
            <Stack direction="row" alignItems="center" spacing={0.5}>
              <CircularProgress size={14} />
              <Typography variant="caption">{stats.running} Running</Typography>
            </Stack>
          )}
        </Stack>
      </Box>

      <ViewerContent>
        {/* Execution Steps */}
        {execution.steps?.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              Waiting for execution to start...
            </Typography>
          </Box>
        ) : (
          <>
            {execution.steps.map((step, index) => (
              <ExecutionStep
                key={step.id}
                step={step}
                isLast={index === execution.steps.length - 1}
                onRetry={onRetryStep}
              />
            ))}
            <div ref={logsEndRef} />
          </>
        )}

        {/* Global Error */}
        {execution.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Execution Error
            </Typography>
            {execution.error}
          </Alert>
        )}

        {/* Success Message */}
        {execution.status === 'success' && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Workflow completed successfully in {formatDuration(execution.duration)}
          </Alert>
        )}
      </ViewerContent>
    </ViewerContainer>
  )
}

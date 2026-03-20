/**
 * Styled components and helpers for ExecutionViewer.
 */
import {
  Box,
  Paper,
  Chip,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Schedule as PendingIcon,
  Loop as RunningIcon,
  Stop as StopIcon,
} from '@mui/icons-material'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const ViewerContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
}))

export const ViewerHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const ViewerContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

export const StepCard = styled(Paper, {
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

export const LogContainer = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.common.black, 0.9),
  borderRadius: 8,
  padding: theme.spacing(1.5),
  fontFamily: 'monospace',
  fontSize: '0.75rem',
  maxHeight: 300,
  overflow: 'auto',
  color: theme.palette.common.white,
}))

export const LogLine = styled(Box, {
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

export const StatusChip = styled(Chip)(({ theme }) => ({
  borderRadius: 4,
  fontWeight: 600,
  fontSize: '12px',
}))

export const TimelineConnector = styled(Box)(({ theme }) => ({
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

export const STATUS_CONFIG = {
  pending: { icon: PendingIcon, color: 'default', label: 'Pending' },
  running: { icon: RunningIcon, color: 'primary', label: 'Running' },
  success: { icon: SuccessIcon, color: 'success', label: 'Success' },
  error: { icon: ErrorIcon, color: 'error', label: 'Failed' },
  warning: { icon: WarningIcon, color: 'warning', label: 'Warning' },
  skipped: { icon: PendingIcon, color: 'default', label: 'Skipped' },
  cancelled: { icon: StopIcon, color: 'default', label: 'Cancelled' },
}

export const formatDuration = (ms) => {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${secs}s`
}

export const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleTimeString()
}

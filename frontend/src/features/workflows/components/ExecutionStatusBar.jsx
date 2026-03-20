/**
 * ExecutionStatusBar — status summary + controls for ExecutionViewer.
 */
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Button,
  Stack,
  CircularProgress,
  alpha,
  useTheme,
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Replay as ReplayIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { StatusChip, formatDuration, formatTimestamp } from './ExecutionViewerStyles'

export default function ExecutionStatusBar({ execution, overallStatus, stats, onStop, onPause, onResume, onRetry }) {
  const theme = useTheme()

  return (
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
            <Button size="small" variant="outlined" startIcon={<PlayIcon />} onClick={onResume}>
              Resume
            </Button>
          )}
          {['error', 'cancelled'].includes(execution.status) && onRetry && (
            <Button size="small" variant="outlined" startIcon={<ReplayIcon />} onClick={onRetry}>
              Retry
            </Button>
          )}
        </Stack>
      </Stack>

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
  )
}

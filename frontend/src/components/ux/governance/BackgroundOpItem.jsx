/**
 * Background Operation List Item
 *
 * Renders a single background operation with status, progress, and cancel.
 */
import {
  Box,
  Typography,
  IconButton,
  LinearProgress,
  ListItem,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Notifications as NotifyIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Schedule as ScheduledIcon,
  Refresh as RunningIcon,
  Cancel as CancelIcon,
  CloudSync as SyncIcon,
  Settings as SystemIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { BackgroundOperationType, BackgroundOperationStatus } from './backgroundConstants'

function getStatusIcon(status, theme) {
  switch (status) {
    case BackgroundOperationStatus.COMPLETED:
      return <SuccessIcon sx={{ color: theme.palette.text.secondary }} />
    case BackgroundOperationStatus.FAILED:
      return <ErrorIcon sx={{ color: theme.palette.text.secondary }} />
    case BackgroundOperationStatus.RUNNING:
      return <RunningIcon sx={{ color: theme.palette.mode === 'dark' ? neutral[300] : neutral[900] }} />
    case BackgroundOperationStatus.CANCELLED:
      return <CancelIcon sx={{ color: theme.palette.text.secondary }} />
    default:
      return <PendingIcon sx={{ color: theme.palette.text.secondary }} />
  }
}

function getTypeIcon(type) {
  switch (type) {
    case BackgroundOperationType.SCHEDULED_REPORT:
      return <ScheduledIcon />
    case BackgroundOperationType.DATA_SYNC:
      return <SyncIcon />
    case BackgroundOperationType.CACHE_REFRESH:
    case BackgroundOperationType.INDEX_REBUILD:
    case BackgroundOperationType.HEALTH_CHECK:
      return <SystemIcon />
    default:
      return <NotifyIcon />
  }
}

export default function BackgroundOpItem({ op, onCancel }) {
  const theme = useTheme()

  return (
    <ListItem
      sx={{
        flexDirection: 'column',
        alignItems: 'stretch',
        gap: 1,
        py: 1.5,
        px: 2,
        bgcolor: alpha(theme.palette.background.paper, 0.4),
        borderRadius: 1,  // Figma spec: 8px
        mb: 1,
      }}
    >
      {/* Main row */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, width: '100%' }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            color: 'text.secondary',
          }}
        >
          {getTypeIcon(op.type)}
        </Box>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body2" fontWeight={500} noWrap>
            {op.label}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            {getStatusIcon(op.status, theme)}
            <Typography variant="caption" color="text.secondary">
              {op.status.charAt(0).toUpperCase() + op.status.slice(1)}
            </Typography>
          </Box>
        </Box>

        {/* Cancel button */}
        {op.cancelable &&
          (op.status === BackgroundOperationStatus.PENDING ||
            op.status === BackgroundOperationStatus.RUNNING) && (
            <IconButton
              size="small"
              onClick={() => onCancel(op.id)}
              sx={{
                color: theme.palette.text.secondary,
                '&:hover': {
                  bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                },
              }}
            >
              <CancelIcon fontSize="small" />
            </IconButton>
          )}
      </Box>

      {/* Progress bar */}
      {op.status === BackgroundOperationStatus.RUNNING && (
        <LinearProgress
          variant={op.progress > 0 ? 'determinate' : 'indeterminate'}
          value={op.progress}
          sx={{
            height: 4,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            '& .MuiLinearProgress-bar': {
              bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
            },
          }}
        />
      )}

      {/* Error message */}
      {op.error && (
        <Alert severity="error" sx={{ py: 0, fontSize: '0.75rem' }}>
          {op.error}
        </Alert>
      )}
    </ListItem>
  )
}

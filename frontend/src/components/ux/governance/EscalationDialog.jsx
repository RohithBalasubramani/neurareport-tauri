/**
 * Escalation Dialog
 *
 * Shows when an operation exceeds its expected time or times out.
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RetryIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { EscalationLevel } from './timeConstants'

function getEscalationConfig(level, theme) {
  const configs = {
    [EscalationLevel.WARNING]: {
      icon: WarningIcon,
      color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      title: 'Operation Taking Longer Than Expected',
      message: 'This operation is taking longer than usual. You can wait, retry, or cancel.',
    },
    [EscalationLevel.TIMEOUT]: {
      icon: ErrorIcon,
      color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      title: 'Operation Timed Out',
      message: 'This operation has exceeded its time limit. Please retry or cancel.',
    },
  }
  return configs[level] || configs[EscalationLevel.WARNING]
}

export default function EscalationDialog({
  open,
  level,
  operation,
  operationId,
  onClose,
  onRetry,
  onCancel,
}) {
  const theme = useTheme()

  if (level === EscalationLevel.NONE) return null

  const escalationConfig = getEscalationConfig(level, theme)
  const EscalationIcon = escalationConfig.icon

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 1,  // Figma spec: 8px
          border: `2px solid ${escalationConfig.color}`,
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
        }}
      >
        <EscalationIcon sx={{ color: escalationConfig.color }} />
        <Typography variant="h6" fontWeight={600}>
          {escalationConfig.title}
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        <Alert severity={level === EscalationLevel.TIMEOUT ? 'error' : 'warning'} sx={{ mb: 2 }}>
          {escalationConfig.message}
        </Alert>

        {operation && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Operation: <strong>{operation.label}</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Elapsed: <strong>{Math.round((Date.now() - operation.startTime) / 1000)}s</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Expected: <strong>{operation.timeConfig.label}</strong>
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
        <Button
          onClick={onClose}
          variant="outlined"
        >
          Keep Waiting
        </Button>
        {operation?.onRetry && (
          <Button
            onClick={() => onRetry(operationId)}
            startIcon={<RetryIcon />}
            variant="outlined"
          >
            Retry
          </Button>
        )}
        <Button
          onClick={() => onCancel(operationId)}
          startIcon={<CancelIcon />}
          variant="contained"
          sx={{ color: 'text.secondary' }}
        >
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  )
}

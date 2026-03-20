/**
 * Status chip for displaying system health status
 */
import { Chip, useTheme, alpha } from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningIcon from '@mui/icons-material/Warning'
import ErrorIcon from '@mui/icons-material/Error'
import { neutral } from '@/app/theme'

const STATUS_CONFIG = {
  healthy: { color: 'success', icon: CheckCircleIcon },
  configured: { color: 'success', icon: CheckCircleIcon },
  ready: { color: 'success', icon: CheckCircleIcon },
  ok: { color: 'success', icon: CheckCircleIcon },
  warning: { color: 'warning', icon: WarningIcon },
  degraded: { color: 'warning', icon: WarningIcon },
  error: { color: 'error', icon: ErrorIcon },
  not_configured: { color: 'default', icon: WarningIcon },
  unknown: { color: 'default', icon: WarningIcon },
}

export default function StatusChip({ status }) {
  const theme = useTheme()
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.unknown
  const Icon = cfg.icon

  return (
    <Chip
      size="small"
      icon={<Icon sx={{ fontSize: 14 }} />}
      label={status?.replace(/_/g, ' ') || 'unknown'}
      sx={{ textTransform: 'capitalize', fontSize: '0.75rem', borderRadius: 1, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
    />
  )
}

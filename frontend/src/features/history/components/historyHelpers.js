/**
 * Status and kind configuration helpers for HistoryPage
 */
import { alpha } from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import CancelIcon from '@mui/icons-material/Cancel'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import { neutral } from '@/app/theme'

export const getStatusConfig = (theme, status) => {
  const completedCfg = {
    icon: CheckCircleIcon,
    color: theme.palette.text.secondary,
    bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    label: 'Completed',
  }
  const configs = {
    completed: completedCfg,
    succeeded: completedCfg,
    failed: {
      icon: ErrorIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Failed',
    },
    running: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Running',
    },
    pending: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
      label: 'Pending',
    },
    queued: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
      label: 'Queued',
    },
    cancelled: {
      icon: CancelIcon,
      color: theme.palette.text.secondary,
      bgColor: alpha(theme.palette.text.secondary, 0.08),
      label: 'Cancelled',
    },
  }
  return configs[status] || configs.pending
}

export const getKindConfig = (theme, kind) => {
  const configs = {
    pdf: { icon: PictureAsPdfIcon, color: theme.palette.text.secondary },
    excel: { icon: TableChartIcon, color: theme.palette.text.secondary },
  }
  return configs[kind] || configs.pdf
}

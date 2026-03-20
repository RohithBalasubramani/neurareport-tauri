/**
 * Config helpers for template kind and status display
 */
import { alpha } from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import { neutral, status as statusColors } from '@/app/theme'

export const getKindConfig = (theme, kind) => {
  const configs = {
    pdf: {
      icon: PictureAsPdfIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    },
    excel: {
      icon: TableChartIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    },
  }
  return configs[kind] || configs.pdf
}

export const getStatusConfig = (theme, status) => {
  const s = (status || '').toLowerCase()
  const configs = {
    approved: {
      color: statusColors.success,
      bgColor: alpha(statusColors.success, 0.1),
    },
    failed: {
      color: statusColors.destructive,
      bgColor: alpha(statusColors.destructive, 0.1),
    },
    pending: {
      color: statusColors.warning,
      bgColor: alpha(statusColors.warning, 0.1),
    },
    draft: {
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
    },
    archived: {
      color: theme.palette.text.secondary,
      bgColor: alpha(theme.palette.text.secondary, 0.08),
    },
  }
  return configs[s] || configs.approved
}

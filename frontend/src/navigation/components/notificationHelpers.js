/**
 * Notification helpers (type configs, time formatting, animations)
 */
import { keyframes } from '@mui/material'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'

export const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

export const getTypeConfig = (theme, type) => {
  const configs = {
    info: {
      icon: InfoOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    success: {
      icon: CheckCircleOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    warning: {
      icon: WarningAmberOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    error: {
      icon: ErrorOutlineIcon,
      color: theme.palette.text.secondary,
    },
  }
  return configs[type] || configs.info
}

export function formatTimeAgo(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)

  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
  return date.toLocaleDateString()
}

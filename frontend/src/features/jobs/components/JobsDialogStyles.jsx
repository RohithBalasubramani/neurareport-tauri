/**
 * Jobs Page - Dialog Styled Components & Status Config
 */
import {
  Box,
  IconButton,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Alert,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { fadeInUp } from '@/styles'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import CancelIcon from '@mui/icons-material/Cancel'

export const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.6),
    backdropFilter: 'blur(8px)',
  },
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: 8,  // Figma spec: 8px
    boxShadow: `0 24px 64px ${alpha(theme.palette.common.black, 0.25)}`,
    animation: `${fadeInUp} 0.3s ease-out`,
  },
}))

export const DialogHeader = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2.5, 3),
  fontSize: '1.125rem',
  fontWeight: 600,
}))

export const CloseButton = styled(IconButton)(({ theme }) => ({
  width: 32,
  height: 32,
  borderRadius: 8,  // Figma spec: 8px
  color: theme.palette.text.secondary,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.primary,
    transform: 'rotate(90deg)',
  },
}))

export const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(0, 3, 3),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
}))

export const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  gap: theme.spacing(1),
}))

export const DetailLabel = styled(Typography)(({ theme }) => ({
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: theme.palette.text.secondary,
  marginBottom: theme.spacing(0.5),
}))

export const DetailValue = styled(Typography)(({ theme }) => ({
  fontSize: '14px',
  color: theme.palette.text.primary,
}))

export const ResultBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1),
  padding: theme.spacing(1.5),
  backgroundColor: alpha(theme.palette.background.paper, 0.4),
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  fontFamily: 'var(--font-mono, monospace)',
  fontSize: '0.75rem',
  whiteSpace: 'pre-wrap',
  color: theme.palette.text.secondary,
  maxHeight: 260,
  overflow: 'auto',
  '&::-webkit-scrollbar': {
    width: 6,
  },
  '&::-webkit-scrollbar-track': {
    background: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    background: alpha(theme.palette.text.primary, 0.2),
    borderRadius: 1,  // Figma spec: 8px
  },
}))

export const StyledDivider = styled(Divider)(({ theme }) => ({
  borderColor: alpha(theme.palette.divider, 0.08),
  margin: theme.spacing(2, 0),
}))

export const ErrorAlert = styled(Alert)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '& .MuiAlert-icon': {
    color: theme.palette.text.secondary,
  },
}))

export const getStatusConfig = (theme, status) => {
  const configs = {
    pending: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
      label: 'Pending',
    },
    running: {
      icon: PlayArrowIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Running',
    },
    completed: {
      icon: CheckCircleIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Completed',
    },
    failed: {
      icon: ErrorIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
      label: 'Failed',
    },
    cancelled: {
      icon: CancelIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
      label: 'Cancelled',
    },
    cancelling: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
      label: 'Cancelling...',
    },
  }
  return configs[status] || configs.pending
}

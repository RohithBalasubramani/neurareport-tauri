/**
 * Styled components for Modal
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  Button,
  Divider,
  CircularProgress,
  styled,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { slideUp } from '@/styles'

export const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.6),
    backdropFilter: 'blur(8px)',
  },
}))

export const DialogPaper = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(20px)',
  border: `1px solid ${alpha(theme.palette.divider, 0.25)}`,
  borderRadius: 8,  // Figma spec: 8px
  boxShadow: `
    0 0 0 1px ${alpha(theme.palette.common.white, 0.05)} inset,
    0 24px 64px ${alpha(theme.palette.common.black, 0.25)},
    0 8px 32px ${alpha(theme.palette.common.black, 0.15)}
  `,
  animation: `${slideUp} 0.3s ease-out`,
  overflow: 'hidden',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 120,
    background: `linear-gradient(180deg, ${alpha(theme.palette.text.primary, 0.02)} 0%, transparent 100%)`,
    pointerEvents: 'none',
  },
}))

export const StyledDialogTitle = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-start',
  justifyContent: 'space-between',
  padding: theme.spacing(3),
  position: 'relative',
  zIndex: 1,
}))

export const TitleText = styled(Typography)(({ theme }) => ({
  fontSize: '1.25rem',
  fontWeight: 600,
  color: theme.palette.text.primary,
  letterSpacing: '-0.02em',
}))

export const SubtitleText = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: theme.palette.text.secondary,
  marginTop: theme.spacing(0.5),
}))

export const CloseButton = styled(IconButton)(({ theme }) => ({
  width: 32,
  height: 32,
  borderRadius: 8,  // Figma spec: 8px
  color: theme.palette.text.secondary,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    color: theme.palette.text.primary,
    transform: 'rotate(90deg)',
  },
}))

export const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(0, 3, 3),
  position: 'relative',
  zIndex: 1,
}))

export const StyledDivider = styled(Divider)(({ theme }) => ({
  borderColor: alpha(theme.palette.divider, 0.25),
  margin: theme.spacing(0, 3),
}))

export const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2.5, 3),
  gap: theme.spacing(1.5),
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

export const CancelButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: theme.spacing(1, 2.5),
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.2),
  transition: 'all 0.2s ease',
  '&:hover': {
    borderColor: alpha(theme.palette.text.primary, 0.3),
    backgroundColor: alpha(theme.palette.text.primary, 0.04),
  },
}))

export const ConfirmButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '0.875rem',
  padding: theme.spacing(1, 2.5),
  transition: 'all 0.2s ease',
  '&.primary': {
    background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    color: theme.palette.common.white,
    boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
    '&:hover': {
      background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
      transform: 'translateY(-1px)',
    },
    '&:active': {
      transform: 'translateY(0)',
    },
  },
  '&.error': {
    background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    color: theme.palette.common.white,
    boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
    '&:hover': {
      background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
      transform: 'translateY(-1px)',
    },
  },
}))

export const LoadingSpinner = styled(CircularProgress)(() => ({
  color: 'inherit',
}))

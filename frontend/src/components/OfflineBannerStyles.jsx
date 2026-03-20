/**
 * Styled components for OfflineBanner
 */
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  styled,
  alpha,
  keyframes,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { slideDown, shimmer } from '@/styles'

// Local animation — differs from shared version
const pulse = keyframes`
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
`

const BannerBase = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: theme.spacing(2),
  padding: theme.spacing(1, 3),
  animation: `${slideDown} 0.3s ease-out`,
  position: 'relative',
  overflow: 'hidden',
}))

export const OfflineBannerContainer = styled(BannerBase)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? `linear-gradient(135deg, ${neutral[700]}, ${neutral[900]})`
    : `linear-gradient(135deg, ${neutral[500]}, ${neutral[700]})`,
  color: theme.palette.common.white,
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `linear-gradient(
      90deg,
      transparent 0%,
      ${alpha(theme.palette.common.white, 0.1)} 50%,
      transparent 100%
    )`,
    backgroundSize: '200% 100%',
    animation: `${shimmer} 3s infinite linear`,
    pointerEvents: 'none',
  },
}))

export const ReconnectedBannerContainer = styled(BannerBase)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? `linear-gradient(135deg, ${neutral[500]}, ${neutral[700]})`
    : `linear-gradient(135deg, ${neutral[700]}, ${neutral[900]})`,
  color: theme.palette.common.white,
  justifyContent: 'center',
}))

export const IconContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 28,
  height: 28,
  borderRadius: 8,
  backgroundColor: alpha(theme.palette.common.white, 0.2),
  flexShrink: 0,
}))

export const PulsingIcon = styled(Box)(() => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  animation: `${pulse} 2s infinite ease-in-out`,
}))

export const StatusText = styled(Typography)(() => ({
  fontSize: '14px',
  fontWeight: 600,
  letterSpacing: '-0.01em',
}))

export const DescriptionText = styled(Typography)(() => ({
  fontSize: '0.75rem',
  opacity: 0.9,
}))

export const RetryButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '0.75rem',
  padding: theme.spacing(0.5, 2),
  minWidth: 90,
  borderColor: alpha(theme.palette.common.white, 0.4),
  color: theme.palette.common.white,
  backdropFilter: 'blur(4px)',
  backgroundColor: alpha(theme.palette.common.white, 0.1),
  transition: 'all 0.2s ease',
  '&:hover': {
    borderColor: theme.palette.common.white,
    backgroundColor: alpha(theme.palette.common.white, 0.2),
    transform: 'translateY(-1px)',
  },
  '&:active': {
    transform: 'translateY(0)',
  },
  '&:disabled': {
    borderColor: alpha(theme.palette.common.white, 0.2),
    color: alpha(theme.palette.common.white, 0.7),
  },
}))

export const SpinningLoader = styled(CircularProgress)(() => ({
  color: 'inherit',
}))

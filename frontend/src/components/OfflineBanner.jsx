/**
 * Premium Offline Banner
 * Elegant network status indicator with animations
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Collapse,
  useTheme,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import {
  SignalWifiOff as OfflineIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  WifiTethering as OnlineIcon,
} from '@mui/icons-material'
import { useNetworkStatus } from '../hooks/useNetworkStatus'
import { slideDown, shimmer, spin } from '@/styles'

// =============================================================================
// ANIMATIONS (local — differs from shared version)
// =============================================================================

const pulse = keyframes`
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

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

const OfflineBannerContainer = styled(BannerBase)(({ theme }) => ({
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

const ReconnectedBannerContainer = styled(BannerBase)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? `linear-gradient(135deg, ${neutral[500]}, ${neutral[700]})`
    : `linear-gradient(135deg, ${neutral[700]}, ${neutral[900]})`,
  color: theme.palette.common.white,
  justifyContent: 'center',
}))

const IconContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 28,
  height: 28,
  borderRadius: 8,
  backgroundColor: alpha(theme.palette.common.white, 0.2),
  flexShrink: 0,
}))

const PulsingIcon = styled(Box)(() => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  animation: `${pulse} 2s infinite ease-in-out`,
}))

const StatusText = styled(Typography)(() => ({
  fontSize: '14px',
  fontWeight: 600,
  letterSpacing: '-0.01em',
}))

const DescriptionText = styled(Typography)(() => ({
  fontSize: '0.75rem',
  opacity: 0.9,
}))

const RetryButton = styled(Button)(({ theme }) => ({
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

const SpinningLoader = styled(CircularProgress)(() => ({
  color: 'inherit',
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function OfflineBanner() {
  const theme = useTheme()
  const { isOnline, checkConnectivity } = useNetworkStatus()
  const [isRetrying, setIsRetrying] = useState(false)
  const [showReconnected, setShowReconnected] = useState(false)
  const wasOfflineRef = useRef(false)
  const reconnectTimeoutRef = useRef(null)

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  // Track when we go offline and show reconnected message when back online
  useEffect(() => {
    if (!isOnline) {
      wasOfflineRef.current = true
    } else if (wasOfflineRef.current) {
      setShowReconnected(true)
      clearReconnectTimer()
      reconnectTimeoutRef.current = setTimeout(() => setShowReconnected(false), 3000)
      wasOfflineRef.current = false
    }
    return () => clearReconnectTimer()
  }, [isOnline, clearReconnectTimer])

  // Redundant cleanup effect removed - already handled in the effect above

  const handleRetry = useCallback(async () => {
    setIsRetrying(true)
    try {
      const online = await checkConnectivity()
      if (online) {
        setShowReconnected(true)
        clearReconnectTimer()
        reconnectTimeoutRef.current = setTimeout(() => setShowReconnected(false), 3000)
      }
    } finally {
      setIsRetrying(false)
    }
  }, [checkConnectivity, clearReconnectTimer])

  // Reconnected banner
  if (showReconnected && isOnline) {
    return (
      <Collapse in={showReconnected}>
        <ReconnectedBannerContainer>
          <PulsingIcon>
            <IconContainer>
              <CheckCircleIcon sx={{ fontSize: 16 }} />
            </IconContainer>
          </PulsingIcon>
          <StatusText sx={{ ml: 1 }}>Connection restored</StatusText>
        </ReconnectedBannerContainer>
      </Collapse>
    )
  }

  if (isOnline) return null

  return (
    <Collapse in={!isOnline}>
      <OfflineBannerContainer>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <PulsingIcon>
            <IconContainer>
              <OfflineIcon sx={{ fontSize: 16 }} />
            </IconContainer>
          </PulsingIcon>
          <Box>
            <StatusText>You&apos;re offline</StatusText>
            <DescriptionText>
              Some features may not work until connection is restored.
            </DescriptionText>
          </Box>
        </Box>
        <RetryButton
          variant="outlined"
          onClick={handleRetry}
          disabled={isRetrying}
          startIcon={
            isRetrying ? (
              <SpinningLoader size={14} />
            ) : (
              <RefreshIcon sx={{ fontSize: 16 }} />
            )
          }
        >
          {isRetrying ? 'Checking...' : 'Retry'}
        </RetryButton>
      </OfflineBannerContainer>
    </Collapse>
  )
}

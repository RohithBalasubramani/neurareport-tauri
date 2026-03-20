/**
 * Premium Offline Banner
 * Elegant network status indicator with animations
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import {
  Box,
  Collapse,
  useTheme,
} from '@mui/material'
import {
  SignalWifiOff as OfflineIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { useNetworkStatus } from '../hooks/useNetworkStatus'
import {
  OfflineBannerContainer,
  ReconnectedBannerContainer,
  IconContainer,
  PulsingIcon,
  StatusText,
  DescriptionText,
  RetryButton,
  SpinningLoader,
} from './OfflineBannerStyles'

export default function OfflineBanner() {
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

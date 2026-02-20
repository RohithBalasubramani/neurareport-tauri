/**
 * Network Status Banner
 * Shows when the user is offline or has connectivity issues
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Never leave the user guessing
 * - Safe defaults (user can do nothing and be fine)
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Box,
  Typography,
  Button,
  Collapse,
  LinearProgress,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import {
  WifiOff as OfflineIcon,
  Wifi as OnlineIcon,
  Refresh as RetryIcon,
  CloudOff as ServerDownIcon,
} from '@mui/icons-material'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { neutral, palette } from '@/app/theme'
import { slideDown } from '@/styles'

// Local pulse — differs from shared version (opacity-based, not scale-based)
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
`

// Status types
export const NetworkStatus = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  RECONNECTING: 'reconnecting',
  SERVER_DOWN: 'server_down',
}

/**
 * Network Status Banner
 * Displays at the top of the page when there are connectivity issues
 */
export default function NetworkStatusBanner({ onRetry }) {
  const theme = useTheme()
  const { isOnline, checkConnectivity, checkServer } = useNetworkStatus()
  const [status, setStatus] = useState(NetworkStatus.ONLINE)
  const [isRetrying, setIsRetrying] = useState(false)
  const [showBanner, setShowBanner] = useState(false)
  const [wasOffline, setWasOffline] = useState(false)
  const successTimeoutRef = useRef(null)
  const prevOnlineRef = useRef(isOnline)
  // Server connectivity check is provided by the network hook

  // Handle retry
  const handleRetry = useCallback(async () => {
    setIsRetrying(true)
    setStatus(NetworkStatus.RECONNECTING)

    try {
      const browserOnline = await checkConnectivity()

      if (browserOnline) {
        const serverUp = await checkServer()

        if (serverUp) {
          setStatus(NetworkStatus.ONLINE)
          setWasOffline(true)
          // Keep banner briefly to show success
          clearTimeout(successTimeoutRef.current)
          successTimeoutRef.current = setTimeout(() => {
            setShowBanner(false)
            setWasOffline(false)
          }, 2000)
        } else {
          setStatus(NetworkStatus.SERVER_DOWN)
        }
      } else {
        setStatus(NetworkStatus.OFFLINE)
      }
    } finally {
      setIsRetrying(false)
    }

    onRetry?.()
  }, [checkConnectivity, checkServer, onRetry])

  // Monitor network status - only retry on actual offline-to-online transitions
  useEffect(() => {
    if (!isOnline) {
      setStatus(NetworkStatus.OFFLINE)
      setShowBanner(true)
    } else if (!prevOnlineRef.current) {
      // Transitioning from offline to online, verify with server
      handleRetry()
    }
    prevOnlineRef.current = isOnline
  }, [isOnline, handleRetry])

  // Periodic check when offline
  useEffect(() => {
    if (status === NetworkStatus.OFFLINE || status === NetworkStatus.SERVER_DOWN) {
      const interval = setInterval(handleRetry, 30000) // Check every 30s
      return () => clearInterval(interval)
    }
  }, [status, handleRetry])

  // Cleanup success timeout on unmount
  useEffect(() => {
    return () => clearTimeout(successTimeoutRef.current)
  }, [])

  // Get banner configuration based on status
  const getBannerConfig = () => {
    const neutralColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
    const neutralBgColor = theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]
    switch (status) {
      case NetworkStatus.OFFLINE:
        return {
          icon: <OfflineIcon />,
          message: "You're offline",
          description: 'Check your internet connection. Changes will sync when you reconnect.',
          color: neutralColor,
          bgColor: neutralBgColor,
          showRetry: true,
        }
      case NetworkStatus.SERVER_DOWN:
        return {
          icon: <ServerDownIcon />,
          message: 'Server temporarily unavailable',
          description: 'We\'re working on it. Your work is saved locally.',
          color: neutralColor,
          bgColor: neutralBgColor,
          showRetry: true,
        }
      case NetworkStatus.RECONNECTING:
        return {
          icon: <RetryIcon sx={{ animation: `spin 1s linear infinite`, '@keyframes spin': { from: { transform: 'rotate(0deg)' }, to: { transform: 'rotate(360deg)' } } }} />,
          message: 'Reconnecting...',
          description: 'Attempting to restore connection',
          color: neutralColor,
          bgColor: neutralBgColor,
          showRetry: false,
        }
      case NetworkStatus.ONLINE:
      default:
        if (wasOffline) {
          return {
            icon: <OnlineIcon />,
            message: 'Back online',
            description: 'Connection restored',
            color: neutralColor,
            bgColor: neutralBgColor,
            showRetry: false,
          }
        }
        return null
    }
  }

  const config = getBannerConfig()

  if (!showBanner || !config) {
    return null
  }

  return (
    <Collapse in={showBanner}>
      <Box
        sx={{
          bgcolor: config.bgColor,
          borderBottom: `1px solid ${alpha(config.color, 0.2)}`,
          animation: `${slideDown} 0.3s ease-out`,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {isRetrying && (
          <LinearProgress
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 2,
              bgcolor: alpha(config.color, 0.1),
              '& .MuiLinearProgress-bar': {
                bgcolor: config.color,
              },
            }}
          />
        )}

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 2,
            py: 1.5,
            px: 3,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              color: config.color,
              animation: status === NetworkStatus.OFFLINE ? `${pulse} 2s infinite` : 'none',
            }}
          >
            {config.icon}
            <Typography variant="body2" fontWeight={600}>
              {config.message}
            </Typography>
          </Box>

          <Typography
            variant="body2"
            sx={{
              color: alpha(theme.palette.text.primary, 0.7),
              display: { xs: 'none', sm: 'block' },
            }}
          >
            {config.description}
          </Typography>

          {config.showRetry && !isRetrying && (
            <Button
              size="small"
              variant="outlined"
              onClick={handleRetry}
              startIcon={<RetryIcon />}
              sx={{
                ml: 2,
                borderColor: alpha(config.color, 0.3),
                color: config.color,
                '&:hover': {
                  borderColor: config.color,
                  bgcolor: alpha(config.color, 0.1),
                },
              }}
            >
              Retry
            </Button>
          )}
        </Box>
      </Box>
    </Collapse>
  )
}

/**
 * Compact inline network indicator for headers/footers
 */
export function NetworkIndicator({ showWhenOnline = false }) {
  const theme = useTheme()
  const { isOnline } = useNetworkStatus()

  if (isOnline && !showWhenOnline) {
    return null
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 0.5,
        color: 'text.secondary',
        fontSize: '0.75rem',
      }}
    >
      {isOnline ? <OnlineIcon fontSize="small" /> : <OfflineIcon fontSize="small" />}
      <Typography variant="caption">
        {isOnline ? 'Online' : 'Offline'}
      </Typography>
    </Box>
  )
}

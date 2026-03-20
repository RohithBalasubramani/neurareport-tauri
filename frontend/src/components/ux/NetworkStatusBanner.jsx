/**
 * Network Status Banner
 * Shows when the user is offline or has connectivity issues
 */
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
import { neutral } from '@/app/theme'
import { slideDown } from '@/styles'
import useNetworkBanner, { NetworkStatus } from './useNetworkBanner'

export { NetworkStatus }

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
`

const STATUS_ICONS = {
  [NetworkStatus.OFFLINE]: OfflineIcon,
  [NetworkStatus.SERVER_DOWN]: ServerDownIcon,
  [NetworkStatus.RECONNECTING]: RetryIcon,
  [NetworkStatus.ONLINE]: OnlineIcon,
}

const STATUS_MESSAGES = {
  [NetworkStatus.OFFLINE]: { message: "You're offline", description: 'Check your internet connection. Changes will sync when you reconnect.', showRetry: true },
  [NetworkStatus.SERVER_DOWN]: { message: 'Server temporarily unavailable', description: "We're working on it. Your work is saved locally.", showRetry: true },
  [NetworkStatus.RECONNECTING]: { message: 'Reconnecting...', description: 'Attempting to restore connection', showRetry: false },
}

export default function NetworkStatusBanner({ onRetry }) {
  const theme = useTheme()
  const { status, isRetrying, showBanner, wasOffline, handleRetry } = useNetworkBanner({ onRetry })

  const neutralColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
  const neutralBgColor = theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]

  let config = STATUS_MESSAGES[status]
  if (status === NetworkStatus.ONLINE && wasOffline) {
    config = { message: 'Back online', description: 'Connection restored', showRetry: false }
  }

  if (!showBanner || !config) return null

  const IconComp = STATUS_ICONS[status] || OnlineIcon
  const iconProps = status === NetworkStatus.RECONNECTING
    ? { sx: { animation: 'spin 1s linear infinite', '@keyframes spin': { from: { transform: 'rotate(0deg)' }, to: { transform: 'rotate(360deg)' } } } }
    : {}

  return (
    <Collapse in={showBanner}>
      <Box sx={{ bgcolor: neutralBgColor, borderBottom: `1px solid ${alpha(neutralColor, 0.2)}`, animation: `${slideDown} 0.3s ease-out`, position: 'relative', overflow: 'hidden' }}>
        {isRetrying && (
          <LinearProgress sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, bgcolor: alpha(neutralColor, 0.1), '& .MuiLinearProgress-bar': { bgcolor: neutralColor } }} />
        )}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, py: 1.5, px: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: neutralColor, animation: status === NetworkStatus.OFFLINE ? `${pulse} 2s infinite` : 'none' }}>
            <IconComp {...iconProps} />
            <Typography variant="body2" fontWeight={600}>{config.message}</Typography>
          </Box>
          <Typography variant="body2" sx={{ color: alpha(theme.palette.text.primary, 0.7), display: { xs: 'none', sm: 'block' } }}>
            {config.description}
          </Typography>
          {config.showRetry && !isRetrying && (
            <Button size="small" variant="outlined" onClick={handleRetry} startIcon={<RetryIcon />}
              sx={{ ml: 2, borderColor: alpha(neutralColor, 0.3), color: neutralColor, '&:hover': { borderColor: neutralColor, bgcolor: alpha(neutralColor, 0.1) } }}>
              Retry
            </Button>
          )}
        </Box>
      </Box>
    </Collapse>
  )
}

export function NetworkIndicator({ showWhenOnline = false }) {
  const { isOnline } = useNetworkStatus()
  if (isOnline && !showWhenOnline) return null
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary', fontSize: '0.75rem' }}>
      {isOnline ? <OnlineIcon fontSize="small" /> : <OfflineIcon fontSize="small" />}
      <Typography variant="caption">{isOnline ? 'Online' : 'Offline'}</Typography>
    </Box>
  )
}

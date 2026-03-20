import { Box, Typography, Button, CircularProgress } from '@mui/material'
import SensorsIcon from '@mui/icons-material/Sensors'
import { GlassCard } from '@/styles/components'
import { LOGGER_URL } from '../hooks/useLoggerPage'

export default function LoggerPluginView({ loggerStatus, iframeRef, handleRetryConnection }) {
  if (loggerStatus === 'checking') {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6, flex: 1 }}>
        <CircularProgress sx={{ mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          Connecting to Logger...
        </Typography>
      </GlassCard>
    )
  }

  if (loggerStatus === 'offline') {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6, flex: 1 }}>
        <SensorsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Logger Not Available
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
          The Logger frontend at <strong>{LOGGER_URL}</strong> is not reachable.
          Make sure the Logger service is running.
        </Typography>
        <Button variant="outlined" onClick={handleRetryConnection}>
          Retry Connection
        </Button>
      </GlassCard>
    )
  }

  return (
    <Box
      sx={{
        flex: 1,
        minHeight: 600,
        borderRadius: 2,
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <iframe
        ref={iframeRef}
        src={LOGGER_URL}
        title="Logger Dashboard"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          display: 'block',
          minHeight: 600,
        }}
      />
    </Box>
  )
}

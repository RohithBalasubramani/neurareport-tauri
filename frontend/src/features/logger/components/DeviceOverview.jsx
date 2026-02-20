import { Box, Chip, Typography, CircularProgress, alpha } from '@mui/material'
import { GlassCard } from '@/styles/components'
import SensorsIcon from '@mui/icons-material/Sensors'
import WifiIcon from '@mui/icons-material/Wifi'
import WifiOffIcon from '@mui/icons-material/WifiOff'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'

const statusConfig = {
  connected: { color: 'success', icon: <WifiIcon sx={{ fontSize: 16 }} />, label: 'Connected' },
  disconnected: { color: 'default', icon: <WifiOffIcon sx={{ fontSize: 16 }} />, label: 'Disconnected' },
  error: { color: 'error', icon: <ErrorOutlineIcon sx={{ fontSize: 16 }} />, label: 'Error' },
}

const protocolLabels = {
  modbus: 'Modbus TCP',
  opcua: 'OPC UA',
}

export default function DeviceOverview({ devices = [], loading }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (devices.length === 0) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <SensorsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">No devices found</Typography>
        <Typography variant="body2" color="text.secondary">
          This Logger database has no registered PLC devices.
        </Typography>
      </GlassCard>
    )
  }

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 2 }}>
      {devices.map((device) => {
        const status = statusConfig[device.status] || statusConfig.disconnected
        return (
          <GlassCard key={device.id} sx={{ '&:hover': { transform: 'none' } }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
              <Box>
                <Typography variant="subtitle1" fontWeight={600}>
                  {device.name}
                </Typography>
                <Chip
                  label={protocolLabels[device.protocol] || device.protocol}
                  size="small"
                  variant="outlined"
                  sx={{ mt: 0.5 }}
                />
              </Box>
              <Chip
                icon={status.icon}
                label={status.label}
                color={status.color}
                size="small"
                variant="outlined"
              />
            </Box>

            {device.latency_ms != null && (
              <Typography variant="body2" color="text.secondary">
                Latency: {device.latency_ms}ms
              </Typography>
            )}

            {device.last_error && (
              <Typography
                variant="caption"
                sx={{
                  color: 'error.main',
                  display: 'block',
                  mt: 1,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {device.last_error}
              </Typography>
            )}

            {device.auto_reconnect && (
              <Chip label="Auto-reconnect" size="small" color="info" variant="outlined" sx={{ mt: 1 }} />
            )}
          </GlassCard>
        )
      })}
    </Box>
  )
}

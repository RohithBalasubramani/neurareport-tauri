import { useMemo } from 'react'
import { Box, Chip, Tooltip } from '@mui/material'
import { keyframes } from '@mui/system'

const pulse = keyframes`
  0% { transform: scale(1); opacity: .8; }
  50% { transform: scale(1.35); opacity: 0; }
  100% { transform: scale(1); opacity: .8; }
`

export default function HeartbeatBadge({
  status = 'unknown', // 'testing' | 'healthy' | 'unreachable' | 'unknown'
  latencyMs,
  label,
  size = 'small',
  withText = true,
  tooltip,
}) {
  const color = useMemo(() => {
    switch (status) {
      case 'testing':
        return 'text.secondary'
      case 'healthy':
        return 'text.secondary'
      case 'unreachable':
        return 'text.secondary'
      default:
        return 'text.disabled'
    }
  }, [status])

  const text = label || (
    status === 'testing' ? 'Pinging...' :
    status === 'healthy' ? (latencyMs != null ? `Healthy (${Math.round(latencyMs)} ms)` : 'Healthy') :
    status === 'unreachable' ? 'Unreachable' : 'Unknown'
  )

  const Dot = (
    <Box sx={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
      <Box sx={{ width: 8, height: 8, borderRadius: 4, bgcolor: color }} />
      {status === 'testing' && (
        <Box sx={{
          position: 'absolute',
          width: 8,
          height: 8,
          borderRadius: 4,
          border: '2px solid',
          borderColor: color,
          animation: `${pulse} 1.2s ease-out infinite`,
        }} />
      )}
    </Box>
  )

  const Content = withText ? (
    <Chip size={size} icon={Dot} label={text} variant="outlined" sx={{ '& .MuiChip-icon': { mr: 0.5 } }} />
  ) : (
    Dot
  )

  return tooltip ? (
    <Tooltip title={tooltip} arrow>{Content}</Tooltip>
  ) : Content
}

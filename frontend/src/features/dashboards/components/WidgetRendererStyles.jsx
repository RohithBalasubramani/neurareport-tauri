/**
 * Styled components and constants for WidgetRenderer.
 */
import {
  Box,
  Typography,
  Chip,
  Tooltip,
  alpha,
  styled,
} from '@mui/material'
import { Storage as DbIcon } from '@mui/icons-material'

// ── Styled Components ──────────────────────────────────────────────────────

export const PlaceholderCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  height: '100%',
  padding: theme.spacing(3),
  borderRadius: 8,
  backgroundColor:
    theme.palette.mode === 'dark'
      ? alpha(theme.palette.primary.main, 0.08)
      : alpha(theme.palette.primary.main, 0.04),
  gap: theme.spacing(1),
}))

export const NarrativeCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  overflow: 'auto',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const AlertListCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5),
  height: '100%',
  overflow: 'auto',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const MetricCard = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const StatusDot = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'status',
})(({ theme, status }) => {
  const colorMap = {
    ok: theme.palette.success.main,
    warning: theme.palette.warning.main,
    critical: theme.palette.error.main,
    offline: theme.palette.text.disabled,
  }
  return {
    width: 12,
    height: 12,
    borderRadius: '50%',
    backgroundColor: colorMap[status] || theme.palette.info.main,
    display: 'inline-block',
  }
})

// ── Severity colors ────────────────────────────────────────────────────────

export const SEVERITY_COLORS = {
  critical: 'error',
  warning: 'warning',
  info: 'info',
  ok: 'success',
}

// ── Data source badge ─────────────────────────────────────────────────────

export function DataSourceBadge({ source }) {
  if (!source) return null
  return (
    <Tooltip title={`Source: ${source}`}>
      <Chip
        icon={<DbIcon sx={{ fontSize: 14 }} />}
        label="Live"
        size="small"
        variant="outlined"
        color="success"
        sx={{
          position: 'absolute',
          top: 4,
          right: 4,
          height: 20,
          fontSize: '10px',
          opacity: 0.8,
          zIndex: 1,
          '& .MuiChip-icon': { fontSize: 14 },
        }}
      />
    </Tooltip>
  )
}

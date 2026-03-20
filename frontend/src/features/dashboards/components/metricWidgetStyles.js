import { Box, alpha, styled } from '@mui/material'
import { neutral } from '@/app/theme'

export const WidgetContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  overflow: 'hidden',
  padding: theme.spacing(2),
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

export const Header = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(1),
}))

export const DragHandle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  cursor: 'grab',
  color: alpha(theme.palette.text.secondary, 0.4),
  marginRight: theme.spacing(1),
  '&:hover': {
    color: theme.palette.text.secondary,
  },
}))

export const ValueContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'baseline',
  gap: theme.spacing(1),
  marginBottom: theme.spacing(0.5),
}))

export const TrendBadge = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'trend',
})(({ theme, trend }) => {
  const colors = {
    up: theme.palette.text.secondary,
    down: theme.palette.text.secondary,
    flat: theme.palette.text.secondary,
  }
  const bgColors = {
    up: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    down: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    flat: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  }

  return {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 2,
    padding: theme.spacing(0.25, 0.75),
    borderRadius: 4,
    fontSize: '0.75rem',
    fontWeight: 600,
    color: colors[trend] || colors.flat,
    backgroundColor: bgColors[trend] || bgColors.flat,
  }
})

export const SparklineContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  minHeight: 40,
  marginTop: theme.spacing(1),
}))

export const formatValue = (value, format = 'number') => {
  if (value === null || value === undefined) return '-'

  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: value >= 1000000 ? 'compact' : 'standard',
        maximumFractionDigits: value >= 1000000 ? 1 : 0,
      }).format(value)

    case 'percent':
      return `${value.toFixed(1)}%`

    case 'compact':
      return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        maximumFractionDigits: 1,
      }).format(value)

    case 'decimal':
      return value.toFixed(2)

    default:
      return new Intl.NumberFormat('en-US').format(value)
  }
}

export const getTrendDirection = (current, previous) => {
  if (!previous || current === previous) return 'flat'
  return current > previous ? 'up' : 'down'
}

export const calculateChange = (current, previous) => {
  if (!previous) return null
  const change = ((current - previous) / previous) * 100
  return change
}

export const METRIC_FORMATS = [
  { value: 'number', label: 'Number' },
  { value: 'currency', label: 'Currency ($)' },
  { value: 'percent', label: 'Percentage (%)' },
  { value: 'compact', label: 'Compact (K, M, B)' },
  { value: 'decimal', label: 'Decimal (2 places)' },
]

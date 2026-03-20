/**
 * Styled components and helpers for DrillDownPanel.
 */
import {
  Box,
  Paper,
  Typography,
  ListItemButton,
  alpha,
  styled,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as FlatIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'

export const PanelContainer = styled(Box)(({ theme }) => ({
  width: 420,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

export const BreadcrumbContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const DataCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

export const DrillableRow = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  border: `1px solid transparent`,
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

export const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '1.5rem',
  fontWeight: 600,
  lineHeight: 1.2,
}))

export const ChangeIndicator = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'trend',
})(({ theme, trend }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  padding: theme.spacing(0.25, 0.75),
  borderRadius: 4,
  fontSize: '0.75rem',
  fontWeight: 600,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  color: theme.palette.text.secondary,
}))

export const ProgressBar = styled(Box)(({ theme }) => ({
  height: 6,
  borderRadius: 1,  // Figma spec: 8px
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
  overflow: 'hidden',
}))

export const ProgressFill = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'width',
})(({ theme, width }) => ({
  height: '100%',
  borderRadius: 1,  // Figma spec: 8px
  backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  width: `${width}%`,
  transition: 'width 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
}))

// =============================================================================
// HELPERS
// =============================================================================

export const formatValue = (value, format = 'number') => {
  if (value === null || value === undefined) return '-'

  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value)
    case 'percent':
      return `${value.toFixed(1)}%`
    case 'decimal':
      return value.toLocaleString('en-US', { minimumFractionDigits: 2 })
    default:
      return value.toLocaleString('en-US')
  }
}

export const getTrendIcon = (trend) => {
  if (trend > 0) return TrendingUpIcon
  if (trend < 0) return TrendingDownIcon
  return FlatIcon
}

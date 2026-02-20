/**
 * Metric Widget Component
 * KPI/metric display with trend indicators and sparklines.
 */
import { forwardRef, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
  DragIndicator as DragIcon,
  MoreVert as MoreIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import ReactECharts from 'echarts-for-react'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const WidgetContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  overflow: 'hidden',
  padding: theme.spacing(2),
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

const Header = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(1),
}))

const DragHandle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  cursor: 'grab',
  color: alpha(theme.palette.text.secondary, 0.4),
  marginRight: theme.spacing(1),
  '&:hover': {
    color: theme.palette.text.secondary,
  },
}))

const ValueContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'baseline',
  gap: theme.spacing(1),
  marginBottom: theme.spacing(0.5),
}))

const TrendBadge = styled(Box, {
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

const SparklineContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  minHeight: 40,
  marginTop: theme.spacing(1),
}))

// =============================================================================
// HELPERS
// =============================================================================

const formatValue = (value, format = 'number') => {
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

const getTrendDirection = (current, previous) => {
  if (!previous || current === previous) return 'flat'
  return current > previous ? 'up' : 'down'
}

const calculateChange = (current, previous) => {
  if (!previous) return null
  const change = ((current - previous) / previous) * 100
  return change
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const MetricWidget = forwardRef(function MetricWidget({
  id,
  title = 'Metric',
  value = 0,
  previousValue,
  format = 'number',
  unit = '',
  sparklineData = [],
  description = '',
  color = 'primary',
  editable = true,
  onDelete,
  style,
  className,
}, ref) {
  const theme = useTheme()

  const trend = useMemo(() => getTrendDirection(value, previousValue), [value, previousValue])
  const change = useMemo(() => calculateChange(value, previousValue), [value, previousValue])
  const formattedValue = useMemo(() => formatValue(value, format), [value, format])

  const sparklineOptions = useMemo(() => {
    if (!sparklineData.length) return null

    const primaryColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]

    return {
      grid: { left: 0, right: 0, top: 5, bottom: 5 },
      xAxis: { type: 'category', show: false },
      yAxis: { type: 'value', show: false },
      series: [
        {
          type: 'line',
          data: sparklineData,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            color: primaryColor,
            width: 2,
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: alpha(primaryColor, 0.3),
                },
                {
                  offset: 1,
                  color: alpha(primaryColor, 0),
                },
              ],
            },
          },
        },
      ],
    }
  }, [sparklineData, color, theme])

  const TrendIcon = trend === 'up' ? TrendUpIcon : trend === 'down' ? TrendDownIcon : TrendFlatIcon

  return (
    <WidgetContainer ref={ref} style={style} className={className}>
      <Header>
        {editable && (
          <DragHandle className="widget-drag-handle">
            <DragIcon fontSize="small" />
          </DragHandle>
        )}
        <Typography
          variant="caption"
          sx={{
            flex: 1,
            color: 'text.secondary',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
          noWrap
        >
          {title}
        </Typography>
        {editable && (
          <Tooltip title="Delete">
            <IconButton size="small" onClick={() => onDelete?.(id)}>
              <DeleteIcon sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
        )}
      </Header>

      <ValueContainer>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 600,
            color: 'text.secondary',
            lineHeight: 1,
          }}
        >
          {formattedValue}
        </Typography>
        {unit && (
          <Typography variant="body2" color="text.secondary">
            {unit}
          </Typography>
        )}
      </ValueContainer>

      {change !== null && (
        <TrendBadge trend={trend}>
          <TrendIcon sx={{ fontSize: 14 }} />
          <span>{change > 0 ? '+' : ''}{change.toFixed(1)}%</span>
        </TrendBadge>
      )}

      {description && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
          {description}
        </Typography>
      )}

      {sparklineOptions && (
        <SparklineContainer>
          <ReactECharts
            option={sparklineOptions}
            style={{ width: '100%', height: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge
            lazyUpdate
          />
        </SparklineContainer>
      )}
    </WidgetContainer>
  )
})

export default MetricWidget

/**
 * Predefined metric formats
 */
export const METRIC_FORMATS = [
  { value: 'number', label: 'Number' },
  { value: 'currency', label: 'Currency ($)' },
  { value: 'percent', label: 'Percentage (%)' },
  { value: 'compact', label: 'Compact (K, M, B)' },
  { value: 'decimal', label: 'Decimal (2 places)' },
]

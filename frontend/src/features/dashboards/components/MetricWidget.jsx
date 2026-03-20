/**
 * Metric Widget Component
 * KPI/metric display with trend indicators and sparklines.
 */
import { forwardRef, useMemo } from 'react'
import {
  Typography,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
  DragIndicator as DragIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import ReactECharts from 'echarts-for-react'
import { neutral } from '@/app/theme'
import {
  WidgetContainer,
  Header,
  DragHandle,
  ValueContainer,
  TrendBadge,
  SparklineContainer,
  formatValue,
  getTrendDirection,
  calculateChange,
} from './metricWidgetStyles'

export { METRIC_FORMATS } from './metricWidgetStyles'

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

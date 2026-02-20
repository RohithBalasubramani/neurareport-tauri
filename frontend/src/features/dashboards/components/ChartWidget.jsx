/**
 * Chart Widget Component
 * ECharts-based chart rendering with multiple chart types.
 */
import { useMemo, useCallback, useRef, useEffect, forwardRef } from 'react'
import ReactECharts from 'echarts-for-react'
import {
  Box,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import {
  MoreVert as MoreIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  DragIndicator as DragIcon,
  BarChart as BarChartIcon,
  ShowChart as LineChartIcon,
  PieChart as PieChartIcon,
  DonutLarge as DonutIcon,
  ScatterPlot as ScatterIcon,
  BubbleChart as BubbleIcon,
  StackedBarChart as StackedIcon,
  AreaChart as AreaIcon,
} from '@mui/icons-material'
import { useState } from 'react'

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
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

const WidgetHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
  minHeight: 48,
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
  '&:active': {
    cursor: 'grabbing',
  },
}))

const WidgetContent = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(1),
  minHeight: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const ChartTypeIcon = {
  bar: BarChartIcon,
  line: LineChartIcon,
  pie: PieChartIcon,
  donut: DonutIcon,
  scatter: ScatterIcon,
  bubble: BubbleIcon,
  stacked: StackedIcon,
  area: AreaIcon,
}

// =============================================================================
// CHART OPTIONS GENERATORS
// =============================================================================

const generateChartOptions = (chartType, data, config, theme) => {
  const baseOptions = {
    animation: true,
    animationDuration: 500,
    grid: {
      left: 50,
      right: 20,
      top: 40,
      bottom: 40,
      containLabel: true,
    },
    tooltip: {
      trigger: chartType === 'pie' || chartType === 'donut' ? 'item' : 'axis',
      backgroundColor: alpha(theme.palette.background.paper, 0.95),
      borderColor: alpha(theme.palette.divider, 0.2),
      textStyle: {
        color: theme.palette.text.primary,
        fontSize: 12,
      },
    },
    // Chart colors — secondary palette values per Design System v4/v5
    color: [
      neutral[700],
      neutral[500],
      neutral[900],
      neutral[400],
      neutral[300],
      neutral[200],
      neutral[100],
      neutral[500],
      neutral[300],
      neutral[400],
    ],
  }

  switch (chartType) {
    case 'bar':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          axisLine: { lineStyle: { color: alpha(theme.palette.divider, 0.3) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'bar',
          data: ds.data || [],
          itemStyle: { borderRadius: [4, 4, 0, 0] },
        })),
      }

    case 'line':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          axisLine: { lineStyle: { color: alpha(theme.palette.divider, 0.3) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'line',
          data: ds.data || [],
          smooth: config?.smooth ?? true,
          symbolSize: 6,
        })),
      }

    case 'area':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          boundaryGap: false,
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'line',
          data: ds.data || [],
          smooth: true,
          areaStyle: {
            opacity: 0.3,
          },
        })),
      }

    case 'pie':
    case 'donut':
      return {
        ...baseOptions,
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { fontSize: 12, color: theme.palette.text.secondary },
        },
        series: [
          {
            type: 'pie',
            radius: chartType === 'donut' ? ['45%', '70%'] : '70%',
            center: ['40%', '50%'],
            data: (data?.labels || []).map((label, idx) => ({
              name: label,
              value: data?.datasets?.[0]?.data?.[idx] || 0,
            })),
            label: {
              show: true,
              fontSize: 12,
              color: theme.palette.text.secondary,
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.2)',
              },
            },
          },
        ],
      }

    case 'scatter':
      return {
        ...baseOptions,
        xAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'scatter',
          data: ds.data || [],
          symbolSize: 10,
        })),
      }

    case 'stacked':
      return {
        ...baseOptions,
        xAxis: {
          type: 'category',
          data: data?.labels || [],
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
        },
        yAxis: {
          type: 'value',
          axisLabel: { fontSize: 12, color: theme.palette.text.secondary },
          splitLine: { lineStyle: { color: alpha(theme.palette.divider, 0.1) } },
        },
        series: (data?.datasets || []).map((ds, idx) => ({
          name: ds.label || `Series ${idx + 1}`,
          type: 'bar',
          stack: 'total',
          data: ds.data || [],
          itemStyle: { borderRadius: idx === (data?.datasets?.length || 1) - 1 ? [4, 4, 0, 0] : 0 },
        })),
      }

    case 'heatmap': {
      const xLabels = data?.xLabels || data?.labels || []
      const yLabels = data?.yLabels || []
      const heatData = data?.heatmapData || data?.data || []
      // Convert {labels, datasets} → heatmap [[x,y,val], ...] if needed
      let points = heatData
      const yLabelsFinal = [...yLabels]
      if (!Array.isArray(heatData) || (heatData.length > 0 && !Array.isArray(heatData[0]))) {
        points = []
        ;(data?.datasets || []).forEach((ds, yi) => {
          ;(ds.data || []).forEach((val, xi) => {
            points.push([xi, yi, val ?? 0])
          })
        })
        if (yLabelsFinal.length === 0 && data?.datasets) {
          data.datasets.forEach((ds) => yLabelsFinal.push(ds.label || ''))
        }
      }
      const allVals = points.map((p) => (Array.isArray(p) ? p[2] : 0)).filter((v) => v != null)
      const minVal = allVals.length ? Math.min(...allVals) : 0
      const maxVal = allVals.length ? Math.max(...allVals) : 100
      return {
        ...baseOptions,
        grid: { left: 80, right: 60, top: 20, bottom: 50, containLabel: true },
        xAxis: {
          type: 'category',
          data: xLabels,
          splitArea: { show: true },
          axisLabel: { fontSize: 11, color: theme.palette.text.secondary, rotate: xLabels.length > 10 ? 45 : 0 },
        },
        yAxis: {
          type: 'category',
          data: yLabelsFinal,
          splitArea: { show: true },
          axisLabel: { fontSize: 11, color: theme.palette.text.secondary },
        },
        visualMap: {
          min: minVal,
          max: maxVal,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 0,
          inRange: { color: ['#f5f5f5', neutral[300], neutral[500], neutral[700], neutral[900]] },
          textStyle: { fontSize: 10, color: theme.palette.text.secondary },
        },
        series: [{ type: 'heatmap', data: points, label: { show: points.length <= 50, fontSize: 10 } }],
      }
    }

    case 'sankey': {
      const nodes = (data?.nodes || []).map((n) => (typeof n === 'string' ? { name: n } : n))
      const links = (data?.links || []).map((l) => ({
        source: typeof l.source === 'number' ? (nodes[l.source]?.name || String(l.source)) : String(l.source || ''),
        target: typeof l.target === 'number' ? (nodes[l.target]?.name || String(l.target)) : String(l.target || ''),
        value: l.value ?? 1,
      }))
      return {
        ...baseOptions,
        grid: undefined,
        series: [{
          type: 'sankey',
          layout: 'none',
          emphasis: { focus: 'adjacency' },
          data: nodes,
          links,
          lineStyle: { color: 'gradient', curveness: 0.5 },
          label: { fontSize: 11, color: theme.palette.text.primary },
        }],
      }
    }

    default:
      return baseOptions
  }
}

// =============================================================================
// SAMPLE DATA
// =============================================================================

const SAMPLE_DATA = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    { label: 'Sales', data: [120, 200, 150, 80, 170, 250] },
    { label: 'Expenses', data: [90, 120, 100, 60, 110, 140] },
  ],
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const ChartWidget = forwardRef(function ChartWidget({
  id,
  title = 'Chart',
  chartType = 'bar',
  data = SAMPLE_DATA,
  config = {},
  loading = false,
  editable = true,
  onEdit,
  onDelete,
  onRefresh,
  onExport,
  onFullscreen,
  style,
  className,
}, ref) {
  const theme = useTheme()
  const chartRef = useRef(null)
  const [menuAnchor, setMenuAnchor] = useState(null)

  const chartOptions = useMemo(() => {
    return generateChartOptions(chartType, data, config, theme)
  }, [chartType, data, config, theme])

  const handleOpenMenu = useCallback((e) => {
    e.stopPropagation()
    setMenuAnchor(e.currentTarget)
  }, [])

  const handleCloseMenu = useCallback(() => {
    setMenuAnchor(null)
  }, [])

  const handleAction = useCallback((action) => {
    handleCloseMenu()
    switch (action) {
      case 'edit':
        onEdit?.(id)
        break
      case 'delete':
        onDelete?.(id)
        break
      case 'refresh':
        onRefresh?.(id)
        break
      case 'export':
        if (chartRef.current) {
          const chart = chartRef.current.getEchartsInstance()
          const url = chart.getDataURL({ type: 'png', pixelRatio: 2 })
          const link = document.createElement('a')
          link.download = `${title}.png`
          link.href = url
          link.click()
        }
        onExport?.(id)
        break
      case 'fullscreen':
        onFullscreen?.(id)
        break
    }
  }, [handleCloseMenu, id, onDelete, onEdit, onExport, onFullscreen, onRefresh, title])

  const TypeIcon = ChartTypeIcon[chartType] || BarChartIcon

  return (
    <WidgetContainer ref={ref} style={style} className={className}>
      <WidgetHeader>
        {editable && (
          <DragHandle className="widget-drag-handle">
            <DragIcon fontSize="small" />
          </DragHandle>
        )}
        <TypeIcon sx={{ fontSize: 18, color: 'text.secondary', mr: 1 }} />
        <Typography
          variant="subtitle2"
          sx={{ fontWeight: 600, flex: 1, fontSize: '0.875rem' }}
          noWrap
        >
          {title}
        </Typography>

        <Tooltip title="Refresh">
          <IconButton size="small" onClick={() => handleAction('refresh')}>
            <RefreshIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </Tooltip>
        <IconButton size="small" onClick={handleOpenMenu}>
          <MoreIcon sx={{ fontSize: 18 }} />
        </IconButton>

        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleCloseMenu}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          {editable && (
            <MenuItem onClick={() => handleAction('edit')}>
              <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
              <ListItemText>Edit</ListItemText>
            </MenuItem>
          )}
          <MenuItem onClick={() => handleAction('export')}>
            <ListItemIcon><DownloadIcon fontSize="small" /></ListItemIcon>
            <ListItemText>Export as PNG</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => handleAction('fullscreen')}>
            <ListItemIcon><FullscreenIcon fontSize="small" /></ListItemIcon>
            <ListItemText>Fullscreen</ListItemText>
          </MenuItem>
          {editable && (
            <MenuItem onClick={() => handleAction('delete')} sx={{ color: 'text.secondary' }}>
              <ListItemIcon><DeleteIcon fontSize="small" sx={{ color: 'text.secondary' }} /></ListItemIcon>
              <ListItemText>Delete</ListItemText>
            </MenuItem>
          )}
        </Menu>
      </WidgetHeader>

      <WidgetContent>
        {loading ? (
          <CircularProgress size={32} />
        ) : (
          <ReactECharts
            ref={chartRef}
            option={chartOptions}
            style={{ width: '100%', height: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge
            lazyUpdate
          />
        )}
      </WidgetContent>
    </WidgetContainer>
  )
})

export default ChartWidget

/**
 * Available chart types
 */
export const CHART_TYPES = [
  { type: 'bar', label: 'Bar Chart', icon: BarChartIcon },
  { type: 'line', label: 'Line Chart', icon: LineChartIcon },
  { type: 'area', label: 'Area Chart', icon: AreaIcon },
  { type: 'pie', label: 'Pie Chart', icon: PieChartIcon },
  { type: 'donut', label: 'Donut Chart', icon: DonutIcon },
  { type: 'scatter', label: 'Scatter Plot', icon: ScatterIcon },
  { type: 'stacked', label: 'Stacked Bar', icon: StackedIcon },
]

/**
 * Chart Widget Component
 * ECharts-based chart rendering with multiple chart types.
 */
import { useMemo, useCallback, useRef, forwardRef } from 'react'
import ReactECharts from 'echarts-for-react'
import {
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  CircularProgress,
  useTheme,
} from '@mui/material'
import {
  MoreVert as MoreIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  DragIndicator as DragIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material'
import { useState } from 'react'
import { generateChartOptions } from '../hooks/useChartOptions'
import {
  WidgetContainer,
  WidgetHeader,
  DragHandle,
  WidgetContent,
  ChartTypeIcon,
  SAMPLE_DATA,
} from './ChartWidgetStyles'

const ChartWidget = forwardRef(function ChartWidget(
  {
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
  },
  ref,
) {
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

  const handleAction = useCallback(
    (action) => {
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
    },
    [handleCloseMenu, id, onDelete, onEdit, onExport, onFullscreen, onRefresh, title],
  )

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
        <Typography variant="subtitle2" sx={{ fontWeight: 600, flex: 1, fontSize: '0.875rem' }} noWrap>
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
              <ListItemIcon>
                <EditIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Edit</ListItemText>
            </MenuItem>
          )}
          <MenuItem onClick={() => handleAction('export')}>
            <ListItemIcon>
              <DownloadIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Export as PNG</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => handleAction('fullscreen')}>
            <ListItemIcon>
              <FullscreenIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Fullscreen</ListItemText>
          </MenuItem>
          {editable && (
            <MenuItem onClick={() => handleAction('delete')} sx={{ color: 'text.secondary' }}>
              <ListItemIcon>
                <DeleteIcon fontSize="small" sx={{ color: 'text.secondary' }} />
              </ListItemIcon>
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

// Re-export CHART_TYPES from styles for backward compatibility
export { CHART_TYPES } from './ChartWidgetStyles'

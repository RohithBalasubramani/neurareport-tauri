/**
 * Drill Down Panel Component
 * Interactive panel for exploring hierarchical data in dashboard widgets.
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Stack,
  Divider,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
} from '@mui/icons-material'
import {
  PanelContainer, PanelHeader, PanelContent,
  DataCard, MetricValue, formatValue,
} from './DrillDownPanelStyles'
import DrillDownBreadcrumb from './DrillDownBreadcrumb'
import { DrillDownDataItems, DrillDownItemDetails } from './DrillDownDataList'

export default function DrillDownPanel({
  title = 'Data Explorer', data = [], hierarchy = [], currentPath = [],
  selectedItem = null, loading = false,
  onDrillDown, onDrillUp, onReset, onExport, onRefresh, onClose,
  valueFormat = 'number',
}) {
  const theme = useTheme()
  const [expandedItems, setExpandedItems] = useState([])

  const summary = useMemo(() => {
    if (!data || data.length === 0) return null
    const total = data.reduce((sum, item) => sum + (item.value || 0), 0)
    const count = data.length
    const avg = total / count
    const max = Math.max(...data.map((d) => d.value || 0))
    const maxItem = data.find((d) => d.value === max)
    return { total, count, avg, max, maxItem }
  }, [data])

  const handleItemClick = useCallback((item) => {
    if (item.children || item.drillable) onDrillDown?.(item)
  }, [onDrillDown])

  const handleBreadcrumbClick = useCallback((index) => {
    index === -1 ? onReset?.() : onDrillUp?.(index)
  }, [onDrillUp, onReset])

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <ZoomInIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{title}</Typography>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Refresh"><IconButton size="small" onClick={onRefresh}><RefreshIcon fontSize="small" /></IconButton></Tooltip>
          <Tooltip title="Export"><IconButton size="small" onClick={onExport}><DownloadIcon fontSize="small" /></IconButton></Tooltip>
          <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
        </Stack>
      </PanelHeader>

      <DrillDownBreadcrumb currentPath={currentPath} onDrillUp={onDrillUp} onBreadcrumbClick={handleBreadcrumbClick} />

      {loading && <LinearProgress />}

      <PanelContent>
        {summary && (
          <DataCard elevation={0}>
            <Typography variant="overline" color="text.secondary" sx={{ fontWeight: 600 }}>Summary</Typography>
            <Stack direction="row" spacing={3} mt={1}>
              <Box>
                <Typography variant="caption" color="text.secondary">Total</Typography>
                <MetricValue>{formatValue(summary.total, valueFormat)}</MetricValue>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Items</Typography>
                <MetricValue>{summary.count}</MetricValue>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Average</Typography>
                <MetricValue sx={{ fontSize: '1.25rem' }}>{formatValue(summary.avg, valueFormat)}</MetricValue>
              </Box>
            </Stack>
            {summary.maxItem && (
              <Box sx={{ mt: 2, pt: 1.5, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="caption" color="text.secondary">
                  Top Item: <strong>{summary.maxItem.label}</strong>
                </Typography>
              </Box>
            )}
          </DataCard>
        )}

        {hierarchy.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">Current Level:</Typography>
            <Stack direction="row" spacing={0.5} mt={0.5}>
              {hierarchy.map((level, index) => (
                <Chip key={level.id} label={level.label} size="small"
                  color={index === currentPath.length ? 'primary' : 'default'}
                  variant={index === currentPath.length ? 'filled' : 'outlined'}
                  sx={{ fontSize: '12px' }} />
              ))}
            </Stack>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        <DrillDownDataItems data={data} summary={summary} selectedItem={selectedItem} valueFormat={valueFormat} onItemClick={handleItemClick} />
        <DrillDownItemDetails selectedItem={selectedItem} valueFormat={valueFormat} />
      </PanelContent>
    </PanelContainer>
  )
}

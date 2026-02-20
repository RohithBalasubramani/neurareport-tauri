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
  Paper,
  Button,
  Stack,
  Divider,
  Chip,
  Breadcrumbs,
  Link,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  ChevronRight as ChevronIcon,
  ArrowBack as BackIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as FlatIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as DocumentIcon,
  BarChart as ChartIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 420,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const BreadcrumbContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const DataCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

const DrillableRow = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  border: `1px solid transparent`,
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '1.5rem',
  fontWeight: 600,
  lineHeight: 1.2,
}))

const ChangeIndicator = styled(Box, {
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

const ProgressBar = styled(Box)(({ theme }) => ({
  height: 6,
  borderRadius: 1,  // Figma spec: 8px
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
  overflow: 'hidden',
}))

const ProgressFill = styled(Box, {
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

const formatValue = (value, format = 'number') => {
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

const getTrendIcon = (trend) => {
  if (trend > 0) return TrendingUpIcon
  if (trend < 0) return TrendingDownIcon
  return FlatIcon
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DrillDownPanel({
  title = 'Data Explorer',
  data = [],
  hierarchy = [],
  currentPath = [],
  selectedItem = null,
  loading = false,
  onDrillDown,
  onDrillUp,
  onReset,
  onExport,
  onRefresh,
  onClose,
  valueFormat = 'number',
}) {
  const theme = useTheme()
  const [expandedItems, setExpandedItems] = useState([])

  // Calculate summary metrics
  const summary = useMemo(() => {
    if (!data || data.length === 0) return null

    const total = data.reduce((sum, item) => sum + (item.value || 0), 0)
    const count = data.length
    const avg = total / count
    const max = Math.max(...data.map((d) => d.value || 0))
    const maxItem = data.find((d) => d.value === max)

    return { total, count, avg, max, maxItem }
  }, [data])

  // Handle item click
  const handleItemClick = useCallback((item) => {
    if (item.children || item.drillable) {
      onDrillDown?.(item)
    }
  }, [onDrillDown])

  // Toggle item expansion
  const toggleItemExpand = useCallback((itemId) => {
    setExpandedItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId]
    )
  }, [])

  // Handle breadcrumb click
  const handleBreadcrumbClick = useCallback((index) => {
    if (index === -1) {
      onReset?.()
    } else {
      onDrillUp?.(index)
    }
  }, [onDrillUp, onReset])

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <ZoomInIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={onRefresh}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export">
            <IconButton size="small" onClick={onExport}>
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Stack>
      </PanelHeader>

      {/* Breadcrumb Navigation */}
      <BreadcrumbContainer>
        <Stack direction="row" alignItems="center" spacing={1}>
          {currentPath.length > 0 && (
            <Tooltip title="Go back">
              <IconButton size="small" onClick={() => onDrillUp?.()}>
                <BackIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          <Breadcrumbs
            separator={<ChevronIcon sx={{ fontSize: 16 }} />}
            sx={{ fontSize: '14px' }}
          >
            <Link
              component="button"
              underline="hover"
              color={currentPath.length === 0 ? 'text.primary' : 'inherit'}
              onClick={() => handleBreadcrumbClick(-1)}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <HomeIcon sx={{ fontSize: 16 }} />
              All
            </Link>
            {currentPath.map((item, index) => (
              <Link
                key={item.id}
                component="button"
                underline="hover"
                color={index === currentPath.length - 1 ? 'text.primary' : 'inherit'}
                onClick={() => handleBreadcrumbClick(index)}
                sx={{ fontWeight: index === currentPath.length - 1 ? 600 : 400 }}
              >
                {item.label}
              </Link>
            ))}
          </Breadcrumbs>
        </Stack>
      </BreadcrumbContainer>

      {loading && <LinearProgress />}

      <PanelContent>
        {/* Summary Card */}
        {summary && (
          <DataCard elevation={0}>
            <Typography variant="overline" color="text.secondary" sx={{ fontWeight: 600 }}>
              Summary
            </Typography>
            <Stack direction="row" spacing={3} mt={1}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Total
                </Typography>
                <MetricValue>{formatValue(summary.total, valueFormat)}</MetricValue>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Items
                </Typography>
                <MetricValue>{summary.count}</MetricValue>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Average
                </Typography>
                <MetricValue sx={{ fontSize: '1.25rem' }}>
                  {formatValue(summary.avg, valueFormat)}
                </MetricValue>
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

        {/* Hierarchy Level Info */}
        {hierarchy.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Current Level:
            </Typography>
            <Stack direction="row" spacing={0.5} mt={0.5}>
              {hierarchy.map((level, index) => (
                <Chip
                  key={level.id}
                  label={level.label}
                  size="small"
                  color={index === currentPath.length ? 'primary' : 'default'}
                  variant={index === currentPath.length ? 'filled' : 'outlined'}
                  sx={{ fontSize: '12px' }}
                />
              ))}
            </Stack>
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Data Items */}
        {data.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <FolderOpenIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No data at this level
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {data.map((item, index) => {
              const TrendIcon = getTrendIcon(item.change)
              const trend = item.change > 0 ? 'up' : item.change < 0 ? 'down' : 'flat'
              const isDrillable = item.children || item.drillable
              const percentage = summary ? (item.value / summary.total) * 100 : 0

              return (
                <DrillableRow
                  key={item.id || index}
                  onClick={() => handleItemClick(item)}
                  selected={selectedItem?.id === item.id}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {isDrillable ? (
                      <FolderIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
                    ) : (
                      <DocumentIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
                    )}
                  </ListItemIcon>

                  <ListItemText
                    primary={
                      <Stack direction="row" alignItems="center" justifyContent="space-between">
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {item.label}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {formatValue(item.value, valueFormat)}
                        </Typography>
                      </Stack>
                    }
                    secondary={
                      <Box sx={{ mt: 0.75 }}>
                        <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
                          <ProgressBar sx={{ flex: 1 }}>
                            <ProgressFill width={percentage} />
                          </ProgressBar>
                          <Typography variant="caption" color="text.secondary" sx={{ minWidth: 40 }}>
                            {percentage.toFixed(1)}%
                          </Typography>
                        </Stack>

                        {item.change !== undefined && (
                          <ChangeIndicator trend={trend}>
                            <TrendIcon sx={{ fontSize: 14, mr: 0.25 }} />
                            {item.change > 0 ? '+' : ''}
                            {item.change}%
                          </ChangeIndicator>
                        )}

                        {item.subtitle && (
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                            {item.subtitle}
                          </Typography>
                        )}
                      </Box>
                    }
                  />

                  {isDrillable && (
                    <ChevronIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
                  )}
                </DrillableRow>
              )
            })}
          </List>
        )}

        {/* Selected Item Details */}
        {selectedItem && selectedItem.details && (
          <>
            <Divider sx={{ my: 2 }} />
            <DataCard elevation={0}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
                {selectedItem.label} Details
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {Object.entries(selectedItem.details).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell sx={{ fontWeight: 500, color: 'text.secondary', border: 0, py: 0.5, pl: 0 }}>
                          {key}
                        </TableCell>
                        <TableCell sx={{ border: 0, py: 0.5 }}>
                          {typeof value === 'number' ? formatValue(value, valueFormat) : value}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </DataCard>
          </>
        )}
      </PanelContent>
    </PanelContainer>
  )
}

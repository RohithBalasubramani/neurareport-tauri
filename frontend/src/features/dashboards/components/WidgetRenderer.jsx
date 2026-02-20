/**
 * WidgetRenderer — variant-aware renderer for all 71 widget variants.
 *
 * Uses VARIANT_CONFIG to determine the exact chart type, render mode, and
 * options for each variant. Falls back to scenario-level defaults when
 * no variant is specified.
 */
import { useMemo } from 'react'
import {
  Box,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  CircularProgress,
  Tooltip,
  alpha,
  styled,
} from '@mui/material'
import {
  Storage as DbIcon,
} from '@mui/icons-material'
import {
  TrendingUp as TrendIcon,
  Warning as WarningIcon,
  Timeline as TimelineIcon,
  SmartToy as AgentIcon,
  Devices as DeviceIcon,
  Public as GlobeIcon,
  Lock as VaultIcon,
  People as PeopleIcon,
  Chat as ChatIcon,
  Build as BuildIcon,
  HelpOutline as UncertaintyIcon,
  Hexagon as HexIcon,
  Hub as NetworkIcon,
  AccountTree as SankeyIcon,
  GridView as HeatmapIcon,
  Speed as KpiIcon,
  CheckCircle as OkIcon,
  Error as ErrorIcon,
  Circle as StatusDotIcon,
} from '@mui/icons-material'
import ChartWidget from './ChartWidget'
import MetricWidget from './MetricWidget'
import useWidgetData from '../hooks/useWidgetData'
import {
  VARIANT_CONFIG,
  DEFAULT_VARIANTS,
  getVariantConfig,
} from '../constants/widgetVariants'

// ── Domain icon mapping ───────────────────────────────────────────────────

const DOMAIN_ICONS = {
  'flow-sankey': SankeyIcon,
  'matrix-heatmap': HeatmapIcon,
  diagnosticpanel: BuildIcon,
  uncertaintypanel: UncertaintyIcon,
  peopleview: PeopleIcon,
  peoplehexgrid: HexIcon,
  peoplenetwork: NetworkIcon,
  edgedevicepanel: DeviceIcon,
  supplychainglobe: GlobeIcon,
  chatstream: ChatIcon,
  agentsview: AgentIcon,
  vaultview: VaultIcon,
}

// ── Styled Components ──────────────────────────────────────────────────────

const PlaceholderCard = styled(Box)(({ theme }) => ({
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

const NarrativeCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  overflow: 'auto',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const AlertListCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5),
  height: '100%',
  overflow: 'auto',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const MetricCard = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const StatusDot = styled(Box, {
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

const SEVERITY_COLORS = {
  critical: 'error',
  warning: 'warning',
  info: 'info',
  ok: 'success',
}

// ── Metric sub-renderers ───────────────────────────────────────────────────

function renderMetricVariant(variantKey, vConfig, data, config, props) {
  const value = data?.value ?? data?.summary?.value?.latest ?? 0
  const unit = data?.units || data?.unit || ''
  const title = config?.title || vConfig.label

  // Status KPI — show status dot + on/off label
  if (vConfig.showStatus) {
    const status = data?.status || 'ok'
    return (
      <MetricCard>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <StatusDot status={status} />
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          {status === 'ok' ? 'Online' : status === 'offline' ? 'Offline' : String(value)}
        </Typography>
        {unit && (
          <Typography variant="caption" color="text.secondary">{unit}</Typography>
        )}
      </MetricCard>
    )
  }

  // Threshold KPI — show alert coloring when over/under threshold
  if (vConfig.showThreshold) {
    const threshold = data?.threshold ?? config?.threshold
    const isOver = threshold != null && value > threshold
    return (
      <MetricWidget
        title={title}
        value={value}
        unit={unit}
        format={vConfig.metricFormat || 'number'}
        previousValue={data?.previousValue}
        sparklineData={data?.timeSeries?.map((p) => p.value) || []}
        description={isOver ? `Above threshold (${threshold})` : data?.label || ''}
        {...props}
      />
    )
  }

  // Default metric rendering (live, accumulated, lifecycle)
  return (
    <MetricWidget
      title={title}
      value={value}
      unit={unit}
      format={vConfig.metricFormat || 'number'}
      previousValue={data?.previousValue}
      sparklineData={data?.timeSeries?.map((p) => p.value) || []}
      description={data?.label || ''}
      {...props}
    />
  )
}

// ── Chart sub-renderer ─────────────────────────────────────────────────────

function renderChartVariant(variantKey, vConfig, data, config, props) {
  const chartType = vConfig.chartType || 'bar'
  const title = config?.title || vConfig.label
  const chartOptions = vConfig.chartOptions || {}

  // Merge variant-specific chart options into config
  const mergedConfig = {
    ...config,
    title,
    ...chartOptions,
  }

  return (
    <ChartWidget
      title={title}
      chartType={chartType}
      data={data}
      config={mergedConfig}
      {...props}
    />
  )
}

// ── List sub-renderer (alerts, timeline, eventlog) ─────────────────────────

function renderListVariant(variantKey, vConfig, data, config, props) {
  const listType = vConfig.listType || 'alerts'
  const title = config?.title || vConfig.label

  if (listType === 'alerts') {
    const items = data?.alerts || data?.events || data?.items || []
    return (
      <AlertListCard>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          {title}
        </Typography>
        {items.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No alerts to display.
          </Typography>
        ) : (
          <List dense disablePadding>
            {items.slice(0, 10).map((item, i) => (
              <ListItem key={i} disableGutters sx={{ py: 0.25 }}>
                <ListItemText
                  primary={item.message || item.title || item.text || `Alert ${i + 1}`}
                  secondary={item.timestamp || item.time || ''}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
                {item.severity && (
                  <Chip
                    label={item.severity}
                    size="small"
                    color={SEVERITY_COLORS[item.severity] || 'default'}
                    sx={{ ml: 1 }}
                  />
                )}
              </ListItem>
            ))}
          </List>
        )}
      </AlertListCard>
    )
  }

  if (listType === 'timeline') {
    const items = data?.events || data?.timeline || data?.items || []
    return (
      <AlertListCard>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          {title}
        </Typography>
        {items.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No events to display.
          </Typography>
        ) : (
          <List dense disablePadding>
            {items.slice(0, 15).map((item, i) => (
              <ListItem key={i} disableGutters sx={{ py: 0.25 }}>
                <Box sx={{ mr: 1.5, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <TimelineIcon sx={{ fontSize: 16, color: 'text.disabled' }} />
                  {i < items.length - 1 && (
                    <Box sx={{ width: 1, flex: 1, bgcolor: 'divider', minHeight: 12 }} />
                  )}
                </Box>
                <ListItemText
                  primary={item.message || item.title || item.text || `Event ${i + 1}`}
                  secondary={item.timestamp || item.time || ''}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
              </ListItem>
            ))}
          </List>
        )}
      </AlertListCard>
    )
  }

  // eventlog
  const items = data?.events || data?.logs || data?.items || []
  return (
    <AlertListCard>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        {title}
      </Typography>
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No log entries to display.
        </Typography>
      ) : (
        <List dense disablePadding>
          {items.slice(0, 20).map((item, i) => (
            <ListItem key={i} disableGutters sx={{ py: 0.15 }}>
              <Typography
                variant="caption"
                sx={{ fontFamily: 'monospace', color: 'text.disabled', mr: 1, minWidth: 60 }}
              >
                {item.timestamp || item.time || ''}
              </Typography>
              <ListItemText
                primary={item.message || item.text || `Log ${i + 1}`}
                primaryTypographyProps={{ variant: 'body2', sx: { fontFamily: 'monospace', fontSize: '12px' } }}
              />
              {item.level && (
                <Chip
                  label={item.level}
                  size="small"
                  variant="outlined"
                  sx={{ ml: 1, height: 18, fontSize: '10px' }}
                />
              )}
            </ListItem>
          ))}
        </List>
      )}
    </AlertListCard>
  )
}

// ── Text sub-renderer ──────────────────────────────────────────────────────

function renderTextVariant(variantKey, vConfig, data, config) {
  return (
    <NarrativeCard>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        {data?.title || config?.title || vConfig.label}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
        {data?.text || data?.narrative || 'No narrative available.'}
      </Typography>
      {data?.highlights?.length > 0 && (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1.5 }}>
          {data.highlights.map((h, i) => (
            <Chip key={i} label={h} size="small" variant="outlined" />
          ))}
        </Box>
      )}
    </NarrativeCard>
  )
}

// ── Domain sub-renderer (with ECharts for heatmap/sankey) ─────────────────

function renderDomainVariant(variantKey, vConfig, data, config, props) {
  const domainType = vConfig.domainType || variantKey
  const title = config?.title || vConfig.label

  // Route heatmap and sankey through ChartWidget for actual ECharts rendering
  if (domainType === 'matrix-heatmap' && data && Object.keys(data).length > 0) {
    return (
      <ChartWidget
        title={title}
        chartType="heatmap"
        data={data}
        config={{ ...config, title }}
        editable={false}
        {...props}
      />
    )
  }

  if (domainType === 'flow-sankey' && data && Object.keys(data).length > 0) {
    return (
      <ChartWidget
        title={title}
        chartType="sankey"
        data={data}
        config={{ ...config, title }}
        editable={false}
        {...props}
      />
    )
  }

  // Fallback placeholder for other domain types
  const IconComponent = DOMAIN_ICONS[domainType] || TrendIcon
  return (
    <PlaceholderCard>
      <IconComponent sx={{ fontSize: 40, color: 'primary.main', opacity: 0.6 }} />
      <Typography variant="subtitle2" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="caption" color="text.disabled">
        {vConfig.description || variantKey}
      </Typography>
      {data && Object.keys(data).length > 0 && (
        <Chip label="Data loaded" size="small" color="success" variant="outlined" sx={{ mt: 0.5 }} />
      )}
    </PlaceholderCard>
  )
}

// ── Data source badge ─────────────────────────────────────────────────────

function DataSourceBadge({ source }) {
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

// ── Main Component ─────────────────────────────────────────────────────────

export default function WidgetRenderer({
  scenario,
  variant,
  data: externalData,
  config,
  connectionId,
  reportRunId,
  showSourceBadge = true,
  ...props
}) {
  // Resolve effective variant — prefer explicit variant, else default for scenario
  const effectiveVariant = variant || config?.variant || DEFAULT_VARIANTS[scenario] || scenario
  const vConfig = getVariantConfig(effectiveVariant, scenario)

  // Resolve connection from config if not passed directly
  // useWidgetData will auto-resolve from app store if this is still undefined
  const explicitConnectionId = connectionId || config?.data_source

  // Always fetch — useWidgetData auto-resolves from the active DB in the store
  const {
    data: fetchedData,
    loading,
    error: fetchError,
    source: dataSource,
  } = useWidgetData({
    scenario,
    variant: effectiveVariant,
    connectionId: explicitConnectionId,
    reportRunId,
    autoFetch: !externalData,
  })

  // Use external data if provided, otherwise use fetched data
  const data = externalData || fetchedData

  // If we can't find any config, render a generic fallback
  if (!vConfig) {
    return (
      <PlaceholderCard>
        <TrendIcon sx={{ fontSize: 36, color: 'text.disabled' }} />
        <Typography variant="body2" color="text.secondary">
          {config?.title || scenario}
        </Typography>
        <Typography variant="caption" color="text.disabled">
          Unknown variant: {effectiveVariant}
        </Typography>
      </PlaceholderCard>
    )
  }

  // Show loading state while fetching
  if (loading && !data) {
    return (
      <PlaceholderCard>
        <CircularProgress size={24} />
        <Typography variant="caption" color="text.secondary">
          Loading {vConfig.label}...
        </Typography>
      </PlaceholderCard>
    )
  }

  // Show error/empty state when no data available
  if (!data && !loading) {
    return (
      <PlaceholderCard>
        <ErrorIcon sx={{ fontSize: 36, color: 'text.disabled' }} />
        <Typography variant="body2" color="text.secondary">
          {config?.title || vConfig?.label || scenario}
        </Typography>
        <Typography variant="caption" color="text.disabled">
          {fetchError || 'No data available. Connect a database to see live data.'}
        </Typography>
      </PlaceholderCard>
    )
  }

  const badge = showSourceBadge && !externalData ? (
    <DataSourceBadge source={dataSource} />
  ) : null

  const renderAs = vConfig.renderAs

  if (renderAs === 'metric') {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderMetricVariant(effectiveVariant, vConfig, data, config, props)}
      </Box>
    )
  }

  if (renderAs === 'chart') {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderChartVariant(effectiveVariant, vConfig, data, config, props)}
      </Box>
    )
  }

  if (renderAs === 'list') {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderListVariant(effectiveVariant, vConfig, data, config, props)}
      </Box>
    )
  }

  if (renderAs === 'text') {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderTextVariant(effectiveVariant, vConfig, data, config)}
      </Box>
    )
  }

  if (renderAs === 'domain') {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderDomainVariant(effectiveVariant, vConfig, data, config, props)}
      </Box>
    )
  }

  // Final fallback
  return (
    <PlaceholderCard>
      <TrendIcon sx={{ fontSize: 36, color: 'text.disabled' }} />
      <Typography variant="body2" color="text.secondary">
        {config?.title || vConfig.label || scenario}
      </Typography>
    </PlaceholderCard>
  )
}

/**
 * Check if a widget type is a scenario-based intelligent widget (not legacy).
 */
export function isScenarioWidget(type) {
  const legacyPrefixes = ['chart', 'metric', 'table', 'text', 'filter', 'map', 'image']
  const baseType = type?.split(':')[0]
  return baseType && !legacyPrefixes.includes(baseType)
}

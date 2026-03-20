/**
 * WidgetRenderer — variant-aware renderer for all 71 widget variants.
 *
 * Uses VARIANT_CONFIG to determine the exact chart type, render mode, and
 * options for each variant. Falls back to scenario-level defaults when
 * no variant is specified.
 */
import { Box, Typography, CircularProgress } from '@mui/material'
import {
  TrendingUp as TrendIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import ChartWidget from './ChartWidget'
import useWidgetData from '../hooks/useWidgetData'
import {
  DEFAULT_VARIANTS,
  getVariantConfig,
} from '../constants/widgetVariants'
import { PlaceholderCard, DataSourceBadge } from './WidgetRendererStyles'
import MetricVariantRenderer from './MetricVariantRenderer'
import ListVariantRenderer from './ListVariantRenderer'
import TextVariantRenderer from './TextVariantRenderer'
import DomainVariantRenderer from './DomainVariantRenderer'

// ── Chart sub-renderer (inline — small enough) ─────────────────────────────

function renderChartVariant(variantKey, vConfig, data, config, props) {
  const chartType = vConfig.chartType || 'bar'
  const title = config?.title || vConfig.label
  const chartOptions = vConfig.chartOptions || {}
  const mergedConfig = { ...config, title, ...chartOptions }

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
  const effectiveVariant = variant || config?.variant || DEFAULT_VARIANTS[scenario] || scenario
  const vConfig = getVariantConfig(effectiveVariant, scenario)
  const explicitConnectionId = connectionId || config?.data_source

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

  const data = externalData || fetchedData

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
  const RENDERERS = {
    metric: () => <MetricVariantRenderer variantKey={effectiveVariant} vConfig={vConfig} data={data} config={config} {...props} />,
    chart: () => renderChartVariant(effectiveVariant, vConfig, data, config, props),
    list: () => <ListVariantRenderer variantKey={effectiveVariant} vConfig={vConfig} data={data} config={config} />,
    text: () => <TextVariantRenderer variantKey={effectiveVariant} vConfig={vConfig} data={data} config={config} />,
    domain: () => <DomainVariantRenderer variantKey={effectiveVariant} vConfig={vConfig} data={data} config={config} {...props} />,
  }

  const renderer = RENDERERS[renderAs]
  if (renderer) {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {badge}
        {renderer()}
      </Box>
    )
  }

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

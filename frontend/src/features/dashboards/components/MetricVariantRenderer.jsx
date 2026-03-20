/**
 * Metric variant sub-renderer for WidgetRenderer.
 */
import { Box, Typography } from '@mui/material'
import MetricWidget from './MetricWidget'
import { MetricCard, StatusDot } from './WidgetRendererStyles'

export default function MetricVariantRenderer({ variantKey, vConfig, data, config, ...props }) {
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

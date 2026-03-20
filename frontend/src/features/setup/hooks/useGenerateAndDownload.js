import { useMemo } from 'react'
import { useAppStore } from '@/stores'
import {
  DEFAULT_RESAMPLE_CONFIG,
  RESAMPLE_DIMENSION_OPTIONS,
  RESAMPLE_METRIC_OPTIONS,
  buildResampleComputation,
} from '@/features/generate/utils/resample'

/**
 * Extracts all derived/memoised state for the GenerateAndDownload component.
 */
export function useGenerateAndDownload({
  selectedTemplates,
  start,
  end,
  results,
  keyOptions,
}) {
  const { downloads } = useAppStore()
  const valid = selectedTemplates.length > 0 && !!start && !!end && end.valueOf() >= start.valueOf()
  const targetNames = Object.values(results).map((r) => r.name)
  const firstResult = Object.values(results || {})[0] || null
  const numericBins = firstResult?.numericBins || {}
  const hasDiscoveryTargets = targetNames.length > 0
  const discoveryCountLabel = hasDiscoveryTargets
    ? `${targetNames.length} ${targetNames.length === 1 ? 'template' : 'templates'}`
    : ''
  const resampleConfig = firstResult?.resample?.config || DEFAULT_RESAMPLE_CONFIG

  const dimensionOptions = useMemo(() => {
    if (firstResult?.discoverySchema?.dimensions) {
      return firstResult.discoverySchema.dimensions.map((dim) => ({
        value: dim.name,
        label: dim.name,
        kind: dim.kind || dim.type || 'categorical',
        bucketable: Boolean(dim.bucketable),
      }))
    }
    return RESAMPLE_DIMENSION_OPTIONS
  }, [firstResult])

  const metricOptions = useMemo(() => {
    if (firstResult?.discoverySchema?.metrics) {
      return firstResult.discoverySchema.metrics.map((m) => ({ value: m.name, label: m.name }))
    }
    return RESAMPLE_METRIC_OPTIONS
  }, [firstResult])

  const safeResampleConfig = useMemo(() => {
    const next = { ...DEFAULT_RESAMPLE_CONFIG, ...resampleConfig }
    const activeDim = dimensionOptions.find((opt) => opt.value === next.dimension) || dimensionOptions[0]
    if (activeDim) {
      const kindText = (activeDim.kind || activeDim.type || '').toLowerCase()
      next.dimensionKind = kindText.includes('time')
        ? 'temporal'
        : kindText.includes('num')
          ? 'numeric'
          : 'categorical'
      next.dimension = activeDim.value
    }
    if (!metricOptions.some((opt) => opt.value === next.metric)) {
      next.metric = metricOptions[0]?.value || DEFAULT_RESAMPLE_CONFIG.metric
    }
    return next
  }, [dimensionOptions, metricOptions, resampleConfig])

  const resampleState = useMemo(
    () => buildResampleComputation(firstResult?.batchMetrics, safeResampleConfig, numericBins, firstResult?.categoryGroups),
    [firstResult, safeResampleConfig, numericBins],
  )

  const templatesWithKeys = useMemo(
    () =>
      selectedTemplates
        .map((tpl) => {
          const mappingTokens = Array.isArray(tpl?.mappingKeys)
            ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
            : []
          const templateOptions = keyOptions[tpl.id] || {}
          const sourceTokens = mappingTokens.length ? mappingTokens : Object.keys(templateOptions)
          if (!sourceTokens.length) return null
          const tokens = sourceTokens.map((token) => ({
            name: token,
            required: mappingTokens.includes(token),
            options: templateOptions[token] || [],
          }))
          return { tpl, tokens }
        })
        .filter(Boolean),
    [selectedTemplates, keyOptions],
  )

  const resultCount = useMemo(() => Object.keys(results).length, [results])
  const keyPanelVisible = templatesWithKeys.length > 0 && resultCount > 0

  const discoverySummary = useMemo(() => {
    const entries = Object.values(results || {})
    if (!entries.length) return null
    return entries.reduce(
      (acc, entry) => {
        const batches = typeof entry.batches_count === 'number'
          ? entry.batches_count
          : Array.isArray(entry.batches)
            ? entry.batches.length
            : 0
        const rows = typeof entry.rows_total === 'number'
          ? entry.rows_total
          : Array.isArray(entry.batches)
            ? entry.batches.reduce((sum, batch) => sum + (batch.rows || 0), 0)
            : 0
        const selectedBatches = Array.isArray(entry.batches)
          ? entry.batches.filter((batch) => batch.selected).length
          : 0
        return {
          templates: acc.templates + 1,
          batches: acc.batches + batches,
          rows: acc.rows + rows,
          selected: acc.selected + selectedBatches,
        }
      },
      { templates: 0, batches: 0, rows: 0, selected: 0 },
    )
  }, [results])

  const discoveryDimensions = useMemo(() => {
    if (firstResult?.discoverySchema && Array.isArray(firstResult.discoverySchema.dimensions)) {
      return firstResult.discoverySchema.dimensions
    }
    return []
  }, [firstResult])

  const discoveryMetrics = useMemo(() => {
    if (firstResult?.discoverySchema && Array.isArray(firstResult.discoverySchema.metrics)) {
      return firstResult.discoverySchema.metrics
    }
    return []
  }, [firstResult])

  return {
    valid,
    downloads,
    targetNames,
    hasDiscoveryTargets,
    discoveryCountLabel,
    dimensionOptions,
    metricOptions,
    safeResampleConfig,
    resampleState,
    templatesWithKeys,
    resultCount,
    keyPanelVisible,
    discoverySummary,
    discoveryDimensions,
    discoveryMetrics,
  }
}

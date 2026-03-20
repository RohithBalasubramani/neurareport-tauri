import { useCallback, useEffect, useMemo, useState } from 'react'
import { useMutation } from '@tanstack/react-query'

import { useAppStore } from '@/stores'
import { useTrackedJobs } from '@/hooks/useJobs'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { confirmDelete } from '@/utils/confirmDelete'
import {
  clampBrushRange,
  collectIdsFromSeries,
  DEFAULT_RESAMPLE_CONFIG,
  RESAMPLE_AGGREGATION_OPTIONS,
  RESAMPLE_BUCKET_OPTIONS,
  RESAMPLE_NUMERIC_BUCKET_OPTIONS,
  RESAMPLE_DIMENSION_OPTIONS,
  RESAMPLE_METRIC_OPTIONS,
  buildResampleComputation,
  getTemplateKind,
  toSqlDateTime,
} from '../utils/generateFeatureUtils'
import { suggestCharts } from '../services/generateApi'
import { useSavedCharts } from './useSavedCharts'

const buildFallbackChartsFromSample = (sampleData) => {
  if (!Array.isArray(sampleData) || !sampleData.length) return []
  const firstEntry = sampleData.find((item) => item && typeof item === 'object') || {}
  const keys = Object.keys(firstEntry)
  if (!keys.length) return []
  const preferredX =
    keys.find((key) =>
      ['label', 'bucket', 'bucket_label', 'bucketLabel', 'batch_index', 'batch_id', 'category'].includes(key),
    ) || keys[0]
  const numericKeys = keys.filter((key) => Number.isFinite(Number(firstEntry[key])))
  const preferredY =
    numericKeys.find((key) => key !== preferredX) ||
    numericKeys[0] ||
    keys.find((key) => key !== preferredX) ||
    preferredX
  return [
    {
      id: 'fallback-line',
      type: 'line',
      xField: preferredX,
      yFields: [preferredY],
      title: 'Line distribution',
      description: 'Auto-generated from sample data',
      chartTemplateId: 'sample_line',
      source: 'fallback',
    },
    {
      id: 'fallback-bar',
      type: 'bar',
      xField: preferredX,
      yFields: [preferredY],
      title: 'Bar distribution',
      description: 'Auto-generated from sample data',
      chartTemplateId: 'sample_bar',
      source: 'fallback',
    },
  ]
}

export function useGenerateAndDownload({
  selected,
  selectedTemplates,
  start,
  end,
  keyValues,
  keyOptions,
  keyOptionsLoading,
  onResampleFilter,
  results,
  generatorReady,
  generatorIssues,
  keysReady,
}) {
  const { downloads } = useAppStore()
  const toast = useToast()
  const { execute } = useInteraction()

  const generatorMessages = generatorIssues?.messages || []
  const generatorMissing = generatorIssues?.missing || []
  const generatorNeedsFix = generatorIssues?.needsFix || []
  const selectionReady = selected.length > 0 && generatorReady

  const [chartQuestion, setChartQuestion] = useState('')
  const [chartSuggestions, setChartSuggestions] = useState([])
  const [selectedChartId, setSelectedChartId] = useState(null)
  const [chartSampleData, setChartSampleData] = useState(null)
  const [selectedChartSource, setSelectedChartSource] = useState('suggestion')
  const [selectedSavedChartId, setSelectedSavedChartId] = useState(null)
  const [saveChartLoading, setSaveChartLoading] = useState(false)

  const trackedJobIds = useMemo(
    () => (Array.isArray(selected) ? [] : []),
    [selected],
  )

  const templateKeyTokens = (tpl) => {
    const fromState = Array.isArray(tpl?.mappingKeys)
      ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
      : []
    if (fromState.length) return fromState
    const options = keyOptions?.[tpl?.id] || {}
    return Object.keys(options || {})
  }

  const templatesWithKeys = useMemo(() => (
    selectedTemplates
      .map((tpl) => ({ tpl, tokens: templateKeyTokens(tpl) }))
      .filter(({ tokens }) => tokens.length > 0)
  ), [selectedTemplates, keyOptions])

  const valid = selectionReady && !!start && !!end && new Date(end) >= new Date(start) && keysReady
  const keysMissing = !keysReady && templatesWithKeys.length > 0
  const showGeneratorWarning = selected.length > 0 && (!generatorReady || generatorMissing.length || generatorNeedsFix.length)

  const activeTemplate = useMemo(
    () => (selectedTemplates && selectedTemplates.length ? selectedTemplates[0] : null),
    [selectedTemplates],
  )
  const activeTemplateId = activeTemplate?.id
  const activeTemplateKind = useMemo(
    () => (activeTemplate ? getTemplateKind(activeTemplate) : 'pdf'),
    [activeTemplate],
  )

  const {
    savedCharts,
    savedChartsLoading,
    savedChartsError,
    fetchSavedCharts,
    createSavedChart,
    renameSavedChart,
    deleteSavedChart,
  } = useSavedCharts({ templateId: activeTemplateId, templateKind: activeTemplateKind })

  const activeTemplateResult = activeTemplateId ? results?.[activeTemplateId] : null
  const activeNumericBins = activeTemplateResult?.numericBins
  const activeDateRange = activeTemplateResult?.dateRange

  const activeBatchData = useMemo(() => {
    if (!activeTemplateId || !activeTemplateResult || !Array.isArray(activeTemplateResult.batches)) {
      return []
    }
    return activeTemplateResult.batches.map((batch, index) => {
      const batchId = batch.id != null ? String(batch.id) : String(index + 1)
      const rows = Number(batch.rows || 0)
      const parent = Number(batch.parent || 0)
      const safeParent = parent || 1
      const rowsPerParent = safeParent ? rows / safeParent : rows
      return {
        batch_index: index + 1,
        batch_id: batchId,
        rows,
        parent,
        rows_per_parent: rowsPerParent,
        time: batch.time ?? null,
        category: batch.category ?? null,
      }
    })
  }, [activeTemplateId, activeTemplateResult])

  const fallbackChartsActive = useMemo(
    () => chartSuggestions.some((chart) => chart?.source === 'fallback'),
    [chartSuggestions],
  )

  const { data: previewData, usingSampleData } = useMemo(() => {
    if (fallbackChartsActive && Array.isArray(chartSampleData) && chartSampleData.length) {
      return { data: chartSampleData, usingSampleData: true }
    }
    if (activeBatchData.length) {
      return { data: activeBatchData, usingSampleData: false }
    }
    if (Array.isArray(chartSampleData) && chartSampleData.length) {
      return { data: chartSampleData, usingSampleData: true }
    }
    return { data: [], usingSampleData: false }
  }, [activeBatchData, chartSampleData, fallbackChartsActive])

  const activeFieldCatalog = Array.isArray(activeTemplateResult?.fieldCatalog)
    ? activeTemplateResult.fieldCatalog
    : []

  const activeDiscoverySchema = useMemo(
    () => (activeTemplateResult?.discoverySchema && typeof activeTemplateResult.discoverySchema === 'object'
      ? activeTemplateResult.discoverySchema
      : null),
    [activeTemplateResult],
  )

  const dimensionOptions = useMemo(() => {
    if (activeDiscoverySchema?.dimensions && Array.isArray(activeDiscoverySchema.dimensions)) {
      return activeDiscoverySchema.dimensions.map((dim) => ({
        value: dim.name,
        label: dim.name,
        kind: dim.kind || dim.type || 'categorical',
        bucketable: Boolean(dim.bucketable),
      }))
    }
    const names = new Set(activeFieldCatalog.map((field) => field?.name))
    const base = RESAMPLE_DIMENSION_OPTIONS.filter((option) => {
      if (option.value === 'time') return names.has('time')
      if (option.value === 'category') return names.has('category')
      return true
    })
    if (!base.some((opt) => opt.value === 'batch_index')) {
      const fallback = RESAMPLE_DIMENSION_OPTIONS.find((opt) => opt.value === 'batch_index')
      if (fallback) base.push(fallback)
    }
    return base
  }, [activeDiscoverySchema, activeFieldCatalog])

  const metricOptions = useMemo(() => {
    if (activeDiscoverySchema?.metrics && Array.isArray(activeDiscoverySchema.metrics)) {
      return activeDiscoverySchema.metrics.map((metric) => ({
        value: metric.name,
        label: metric.name,
      }))
    }
    const names = new Set(activeFieldCatalog.map((field) => field?.name))
    const base = RESAMPLE_METRIC_OPTIONS.filter((option) => names.has(option.value))
    if (!base.length) {
      return [...RESAMPLE_METRIC_OPTIONS]
    }
    return base
  }, [activeDiscoverySchema, activeFieldCatalog])

  const resampleConfig = activeTemplateResult?.resample?.config || DEFAULT_RESAMPLE_CONFIG
  const safeResampleConfig = useMemo(() => {
    const next = { ...DEFAULT_RESAMPLE_CONFIG, ...resampleConfig }
    const activeDim = dimensionOptions.find((opt) => opt.value === next.dimension) || dimensionOptions[0]
    if (!activeDim) {
      next.dimension = DEFAULT_RESAMPLE_CONFIG.dimension
      next.dimensionKind = DEFAULT_RESAMPLE_CONFIG.dimensionKind
    } else {
      next.dimension = activeDim.value
      const rawKind = activeDim.kind || activeDim.type || DEFAULT_RESAMPLE_CONFIG.dimensionKind
      const kindText = (rawKind || '').toString().toLowerCase()
      if (kindText.includes('time') || kindText.includes('date')) {
        next.dimensionKind = 'temporal'
      } else if (kindText.includes('num')) {
        next.dimensionKind = 'numeric'
      } else {
        next.dimensionKind = 'categorical'
      }
    }
    if (!metricOptions.some((opt) => opt.value === next.metric)) {
      next.metric = metricOptions[0]?.value || DEFAULT_RESAMPLE_CONFIG.metric
    }
    return next
  }, [resampleConfig, dimensionOptions, metricOptions])

  const resampleState = useMemo(
    () => buildResampleComputation(
      activeTemplateResult?.batchMetrics,
      safeResampleConfig,
      activeNumericBins,
      activeTemplateResult?.categoryGroups,
    ),
    [activeTemplateId, activeTemplateResult?.batchMetrics, safeResampleConfig, activeNumericBins, activeTemplateResult?.categoryGroups],
  )

  const totalBatchCount =
    activeTemplateResult?.allBatches?.length ?? activeTemplateResult?.batches?.length ?? 0
  const filteredBatchCount = activeTemplateResult?.batches?.length ?? 0

  const selectedMetricLabel = useMemo(
    () => metricOptions.find((opt) => opt.value === safeResampleConfig.metric)?.label || 'Metric',
    [metricOptions, safeResampleConfig.metric],
  )

  const resampleBucketHelper =
    (safeResampleConfig.dimensionKind === 'temporal' || safeResampleConfig.dimension === 'time') &&
    safeResampleConfig.bucket === 'auto'
      ? `Auto bucket: ${resampleState.resolvedBucket}`
      : safeResampleConfig.dimensionKind === 'numeric'
        ? 'Buckets group numeric values into ranges'
        : ''

  const bucketOptions =
    safeResampleConfig.dimensionKind === 'numeric' ? RESAMPLE_NUMERIC_BUCKET_OPTIONS : RESAMPLE_BUCKET_OPTIONS

  const applyResampleConfig = useCallback(
    (nextConfig) => {
      if (!activeTemplateId) return
      const computation = buildResampleComputation(
        activeTemplateResult?.batchMetrics,
        nextConfig,
        activeNumericBins,
        activeTemplateResult?.categoryGroups,
      )
      onResampleFilter(activeTemplateId, {
        config: {
          ...nextConfig,
          range: computation.configRange,
        },
        allowedBatchIds: computation.allowedIds ? Array.from(computation.allowedIds) : null,
      })
    },
    [activeTemplateId, activeTemplateResult?.batchMetrics, activeNumericBins, activeTemplateResult?.categoryGroups, onResampleFilter],
  )

  const handleResampleSelectorChange = useCallback(
    (field) => (event) => {
      const { value } = event?.target || {}
      if (value == null) return
      const nextConfig = { ...safeResampleConfig, [field]: value }
      if (field === 'dimension') {
        const selectedDim = dimensionOptions.find((opt) => opt.value === value)
        const rawKind = selectedDim?.kind || selectedDim?.type || DEFAULT_RESAMPLE_CONFIG.dimensionKind
        const kindText = (rawKind || '').toString().toLowerCase()
        if (kindText.includes('time') || kindText.includes('date')) {
          nextConfig.dimensionKind = 'temporal'
        } else if (kindText.includes('num')) {
          nextConfig.dimensionKind = 'numeric'
        } else {
          nextConfig.dimensionKind = 'categorical'
        }
      }
      if (field !== 'range') {
        nextConfig.range = null
      }
      applyResampleConfig(nextConfig)
    },
    [applyResampleConfig, safeResampleConfig],
  )

  const handleResampleBrushChange = useCallback(
    ({ startIndex, endIndex }) => {
      if (
        !activeTemplateId ||
        !Array.isArray(resampleState.series) ||
        !resampleState.series.length
      ) {
        return
      }
      if (!Number.isFinite(startIndex) || !Number.isFinite(endIndex)) return
      const maxIndex = resampleState.series.length - 1
      const nextRange = clampBrushRange([startIndex, endIndex], maxIndex)
      if (!nextRange) return
      const coversAll = nextRange[0] === 0 && nextRange[1] === maxIndex
      const idsSet = coversAll ? null : collectIdsFromSeries(resampleState.series, nextRange)
      onResampleFilter(activeTemplateId, {
        config: {
          ...safeResampleConfig,
          range: coversAll ? null : nextRange,
        },
        allowedBatchIds: idsSet ? Array.from(idsSet) : null,
      })
    },
    [activeTemplateId, onResampleFilter, resampleState.series, safeResampleConfig],
  )

  const handleResampleReset = useCallback(() => {
    if (!activeTemplateId) return
    onResampleFilter(activeTemplateId, {
      config: { ...safeResampleConfig, range: null },
      allowedBatchIds: null,
    })
  }, [activeTemplateId, onResampleFilter, safeResampleConfig])

  const selectedSuggestion = useMemo(() => {
    if (!chartSuggestions.length) return null
    if (selectedChartId) {
      const found = chartSuggestions.find((chart) => chart.id === selectedChartId)
      if (found) return found
    }
    return chartSuggestions[0] || null
  }, [chartSuggestions, selectedChartId])

  const selectedSavedChart = useMemo(
    () => savedCharts.find((chart) => chart.id === selectedSavedChartId) || null,
    [savedCharts, selectedSavedChartId],
  )

  const selectedChartSpec = useMemo(
    () => (selectedChartSource === 'saved' ? selectedSavedChart?.spec || null : selectedSuggestion),
    [selectedChartSource, selectedSavedChart, selectedSuggestion],
  )

  useEffect(() => {
    setChartSuggestions([])
    setSelectedChartId(null)
    setSelectedSavedChartId(null)
    setSelectedChartSource('suggestion')
    setChartSampleData(null)
  }, [activeTemplateId])

  const chartSuggestMutation = useMutation({
    mutationFn: async ({
      templateId,
      kind,
      startDate,
      endDate,
      keyValuesForTemplate,
      question,
    }) => {
      return suggestCharts({
        templateId,
        startDate,
        endDate,
        keyValues: keyValuesForTemplate,
        question,
        kind,
      })
    },
    onSuccess: (data) => {
      const charts = Array.isArray(data?.charts) ? data.charts : []
      const sampleData = Array.isArray(data?.sampleData) ? data.sampleData : null
      const fallbackCharts = charts.length === 0 ? buildFallbackChartsFromSample(sampleData) : []
      const nextCharts = fallbackCharts.length ? fallbackCharts : charts
      setChartSuggestions(nextCharts)
      setSelectedChartId((prev) => {
        if (prev && nextCharts.some((chart) => chart.id === prev)) return prev
        return nextCharts[0]?.id || null
      })
      setSelectedSavedChartId(null)
      setSelectedChartSource('suggestion')
      setChartSampleData(sampleData && sampleData.length ? sampleData : null)
    },
    onError: (error) => {
      toast.show(error?.message || 'Chart suggestions failed', 'error')
    },
  })

  const handleAskCharts = async () => {
    if (!activeTemplate || !start || !end) {
      toast.show('Select a template and valid date range before asking for charts.', 'warning')
      return
    }
    if (!activeBatchData.length) {
      toast.show('Run discovery for this template to unlock chart suggestions.', 'info')
      return
    }
    const startSql = toSqlDateTime(start)
    const endSql = toSqlDateTime(end)
    if (!startSql || !endSql) {
      toast.show('Provide a valid start and end date before asking for charts.', 'warning')
      return
    }
    try {
      await execute({
        type: InteractionType.ANALYZE,
        label: 'Suggest charts',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          templateId: activeTemplate.id,
          action: 'suggest_charts',
        },
        action: async () => {
          setChartSampleData(null)
          return chartSuggestMutation.mutateAsync({
            templateId: activeTemplate.id,
            kind: activeTemplateKind,
            startDate: startSql,
            endDate: endSql,
            keyValuesForTemplate: keyValues?.[activeTemplate.id] || {},
            question: chartQuestion,
          })
        },
      })
    } catch {
      // handled in onError
    }
  }

  const handleSelectSuggestion = (chartId) => {
    setSelectedChartSource('suggestion')
    setSelectedChartId(chartId)
    setSelectedSavedChartId(null)
  }

  const handleSelectSavedChart = (chartId) => {
    setSelectedChartSource('saved')
    setSelectedSavedChartId(chartId)
    setSelectedChartId(null)
  }

  const handleSaveCurrentSuggestion = async () => {
    if (!activeTemplate || !selectedSuggestion) {
      toast.show('Select a template and a suggestion before saving.', 'info')
      return
    }
    if (typeof window === 'undefined') return
    const index = chartSuggestions.indexOf(selectedSuggestion)
    const defaultName =
      selectedSuggestion.title ||
      selectedSuggestion.description ||
      (index >= 0 ? `Suggested chart ${index + 1}` : 'Saved chart')
    const entered = window.prompt('Name this chart', defaultName || 'Saved chart')
    if (!entered || !entered.trim()) return
    const name = entered.trim()
    try {
      await execute({
        type: InteractionType.CREATE,
        label: 'Save chart',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          templateId: activeTemplate.id,
          action: 'save_chart',
        },
        action: async () => {
          setSaveChartLoading(true)
          try {
            const created = await createSavedChart({ name, spec: selectedSuggestion })
            if (created) {
              setSelectedChartSource('saved')
              setSelectedSavedChartId(created.id)
              toast.show(`Saved chart "${created.name}"`, 'success')
            }
            return created
          } finally {
            setSaveChartLoading(false)
          }
        },
      })
    } catch (error) {
      toast.show(error?.message || 'Failed to save chart.', 'error')
    }
  }

  const handleRenameSavedChart = async (event, chart) => {
    event?.stopPropagation()
    if (!chart || !activeTemplate) return
    if (typeof window === 'undefined') return
    const currentName = chart.name || 'Saved chart'
    const entered = window.prompt('Rename chart', currentName)
    if (!entered || !entered.trim()) return
    const name = entered.trim()
    try {
      await execute({
        type: InteractionType.UPDATE,
        label: 'Rename chart',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          chartId: chart.id,
          action: 'rename_chart',
        },
        action: async () => {
          const updated = await renameSavedChart({ chartId: chart.id, name })
          if (updated) {
            toast.show(`Renamed chart to "${updated.name}"`, 'success')
          }
          return updated
        },
      })
    } catch (error) {
      toast.show(error?.message || 'Failed to rename chart.', 'error')
    }
  }

  const handleDeleteSavedChart = async (event, chart) => {
    event?.stopPropagation()
    if (!chart || !activeTemplate) return
    if (typeof window !== 'undefined') {
      const confirmed = confirmDelete(`Delete saved chart "${chart.name || 'Saved chart'}"?`)
      if (!confirmed) return
    }
    try {
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete saved chart',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          chartId: chart.id,
          action: 'delete_chart',
        },
        action: async () => {
          await deleteSavedChart({ chartId: chart.id })
          if (selectedChartSource === 'saved' && selectedSavedChartId === chart.id) {
            setSelectedChartSource('suggestion')
            setSelectedSavedChartId(null)
          }
          toast.show('Deleted saved chart.', 'success')
        },
      })
    } catch (error) {
      toast.show(error?.message || 'Failed to delete chart.', 'error')
    }
  }

  const handleRetrySavedCharts = () => {
    fetchSavedCharts()
  }

  return {
    downloads,
    toast,
    execute,
    generatorMessages,
    generatorMissing,
    generatorNeedsFix,
    selectionReady,
    chartQuestion,
    setChartQuestion,
    chartSuggestions,
    selectedChartId,
    chartSampleData,
    selectedChartSource,
    selectedSavedChartId,
    saveChartLoading,
    templatesWithKeys,
    valid,
    keysMissing,
    showGeneratorWarning,
    activeTemplate,
    activeTemplateId,
    activeTemplateKind,
    savedCharts,
    savedChartsLoading,
    savedChartsError,
    activeTemplateResult,
    activeDateRange,
    activeBatchData,
    previewData,
    usingSampleData,
    dimensionOptions,
    metricOptions,
    safeResampleConfig,
    resampleState,
    totalBatchCount,
    filteredBatchCount,
    selectedMetricLabel,
    resampleBucketHelper,
    bucketOptions,
    handleResampleSelectorChange,
    handleResampleBrushChange,
    handleResampleReset,
    selectedSuggestion,
    selectedSavedChart,
    selectedChartSpec,
    chartSuggestMutation,
    handleAskCharts,
    handleSelectSuggestion,
    handleSelectSavedChart,
    handleSaveCurrentSuggestion,
    handleRenameSavedChart,
    handleDeleteSavedChart,
    handleRetrySavedCharts,
  }
}

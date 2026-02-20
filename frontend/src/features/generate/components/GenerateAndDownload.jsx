import Grid from '@mui/material/Grid2'
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Checkbox,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import BookmarkAddOutlinedIcon from '@mui/icons-material/BookmarkAddOutlined'
import ReplayIcon from '@mui/icons-material/Replay'
import { useMutation } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend as RechartsLegend,
  Brush,
} from 'recharts'

import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { useAppStore } from '@/stores'
import { useTrackedJobs } from '@/hooks/useJobs'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { confirmDelete } from '@/utils/confirmDelete'
import SavedChartsPanel from './run/SavedChartsPanel.jsx'
import {
  clampBrushRange,
  collectIdsFromSeries,
  DEFAULT_RESAMPLE_CONFIG,
  JOB_STATUS_COLORS,
  RESAMPLE_AGGREGATION_OPTIONS,
  RESAMPLE_BUCKET_OPTIONS,
  RESAMPLE_NUMERIC_BUCKET_OPTIONS,
  RESAMPLE_DIMENSION_OPTIONS,
  RESAMPLE_METRIC_OPTIONS,
  buildDownloadUrl,
  buildResampleComputation,
  getTemplateKind,
  surfaceStackSx,
  toLocalInputValue,
  toSqlDateTime,
} from '../utils/generateFeatureUtils'
import {
  suggestCharts,
  withBase,
} from '../services/generateApi'
import { useSavedCharts } from '../hooks/useSavedCharts'
import { secondary } from '@/app/theme'

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

function GenerateAndDownload({
  selected,
  selectedTemplates,
  autoType,
  start,
  end,
  setStart,
  setEnd,
  onFind,
  findDisabled,
  finding,
  results,
  onToggleBatch,
  onGenerate,
  canGenerate,
  generateLabel,
  generation,
  generatorReady,
  generatorIssues,
  keyValues = {},
  onKeyValueChange = () => {},
  keysReady = true,
  keyOptions = {},
  keyOptionsLoading = {},
  onResampleFilter = () => {},
}) {
  const { downloads } = useAppStore()
  const toast = useToast()
  const { execute } = useInteraction()
  const targetNames = selectedTemplates.map((t) => t.name)
  const subline = targetNames.length
    ? `${targetNames.slice(0, 3).join(', ')}${targetNames.length > 3 ? ', ...' : ''}`
    : ''
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
    () => generation.items.map((item) => item.jobId).filter(Boolean),
    [generation.items],
  )
  const { jobsById } = useTrackedJobs(trackedJobIds)
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
  const renderSuggestedChart = useCallback((spec, data, { source } = {}) => {
    if (!spec) {
      return (
        <Typography variant="body2" color="text.secondary">
          Select a suggestion to preview a chart.
        </Typography>
      )
    }
    if (!Array.isArray(data) || data.length === 0) {
      return (
        <Typography variant="body2" color="text.secondary">
          No data available for this template and filters.
        </Typography>
      )
    }
    const sample = data[0] || {}
    const fieldNames = new Set(Object.keys(sample))
    const missingFields = []
    if (!fieldNames.has(spec.xField)) {
      missingFields.push(spec.xField)
    }
    const yFieldsArray = Array.isArray(spec.yFields) && spec.yFields.length ? spec.yFields : ['rows']
    yFieldsArray.forEach((field) => {
      if (!fieldNames.has(field)) {
        missingFields.push(field)
      }
    })
    if (spec.groupField && !fieldNames.has(spec.groupField)) {
      missingFields.push(spec.groupField)
    }
    if (missingFields.length) {
      return (
        <Alert severity="warning" sx={{ mt: 0.5 }}>
          {source === 'saved'
            ? `Saved chart references fields not present in current data (missing: ${missingFields.join(
                ', ',
              )}). Edit or delete this chart.`
            : `Cannot render this chart because the dataset is missing: ${missingFields.join(', ')}.`}
        </Alert>
      )
    }
    const palette = [secondary.violet[500], secondary.emerald[500], secondary.cyan[500], secondary.rose[500], secondary.teal[500], secondary.fuchsia[500], secondary.slate[500]]
    const type = (spec.type || '').toLowerCase()
    const xField = spec.xField
    const yKeys = yFieldsArray.length ? yFieldsArray : ['rows']
    if (type === 'pie') {
      const valueKey = yKeys[0]
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey={valueKey}
              nameKey={xField}
              innerRadius="45%"
              outerRadius="80%"
              paddingAngle={2}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={palette[index % palette.length]} />
              ))}
            </Pie>
            <RechartsTooltip />
            <RechartsLegend />
          </PieChart>
        </ResponsiveContainer>
      )
    }
    if (type === 'scatter') {
      const yKey = yKeys[0]
      return (
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey={xField} name={xField} tick={{ fontSize: 12 }} />
            <YAxis type="number" dataKey={yKey} name={yKey} tick={{ fontSize: 12 }} />
            <RechartsTooltip />
            <RechartsLegend />
            <Scatter data={data} fill={secondary.emerald[500]} />
          </ScatterChart>
        </ResponsiveContainer>
      )
    }
    if (type === 'line') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <RechartsTooltip />
            <RechartsLegend />
            {yKeys.map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={palette[index % palette.length]}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )
    }
    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <RechartsTooltip />
          <RechartsLegend />
          {yKeys.map((key, index) => (
            <Bar key={key} dataKey={key} fill={palette[index % palette.length]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    )
  }, [])
  return (
    <>
      <Surface sx={surfaceStackSx}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          alignItems={{ xs: 'flex-start', sm: 'center' }}
          justifyContent="space-between"
          spacing={{ xs: 1, sm: 2 }}
        >
          <Stack spacing={0.5}>
            <Stack direction="row" alignItems="center" spacing={0.75}>
              <Typography variant="h6">Run Reports</Typography>
              <InfoTooltip
                content={TOOLTIP_COPY.runReports}
                ariaLabel="Run reports guidance"
              />
            </Stack>
            {!!subline && <Typography variant="caption" color="text.secondary">{subline}</Typography>}
            {activeDateRange && (
              <Typography variant="caption" color="text.secondary">
                Range: {activeDateRange.start} → {activeDateRange.end}
                {activeDateRange.time_start && activeDateRange.time_end
                  ? ` • data ${activeDateRange.time_start} → ${activeDateRange.time_end}`
                  : ''}
              </Typography>
            )}
          </Stack>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1}
            alignItems={{ xs: 'stretch', sm: 'center' }}
            sx={{ width: { xs: '100%', sm: 'auto' } }}
          >
            <Tooltip title="Scan your data to see what can be included in this report">
              <span>
                <Button
                  variant="outlined"
                  onClick={onFind}
                  disabled={!valid || findDisabled}
                  sx={{ width: { xs: '100%', sm: 'auto' }, color: 'text.secondary' }}
                >
                  Preview Data
                </Button>
              </span>
            </Tooltip>
            <Tooltip title={generateLabel}>
              <span>
                <Button
                  variant="contained"
                  onClick={onGenerate}
                  disabled={!canGenerate}
                  aria-label={generateLabel}
                  sx={{ width: { xs: '100%', sm: 'auto' } }}
                >
                  {generateLabel}
                </Button>
              </span>
            </Tooltip>
          </Stack>

        {showGeneratorWarning && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            {generatorMissing.length
              ? 'Generate SQL & schema assets for all selected templates before continuing.'
              : 'Resolve SQL & schema asset issues before continuing.'}
            {generatorMessages.length ? (
              <Box component="ul" sx={{ pl: 2, mt: 0.5 }}>
                {generatorMessages.map((msg, idx) => (
                  <Typography key={`generator-msg-${idx}`} component="li" variant="caption">
                    {msg}
                  </Typography>
                ))}
              </Box>
            ) : null}
          </Alert>
        )}
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <TextField
            label="Start Date & Time"
            type="datetime-local"
            InputLabelProps={{ shrink: true }}
            value={toLocalInputValue(start)}
            onChange={(e) => setStart(e.target.value)}
            helperText="Timezone: system"
          />
          <TextField
            label="End Date & Time"
            type="datetime-local"
            InputLabelProps={{ shrink: true }}
            value={toLocalInputValue(end)}
            onChange={(e) => setEnd(e.target.value)}
            error={!!(start && end && new Date(end) < new Date(start))}
            helperText={start && end && new Date(end) < new Date(start) ? 'End must be after Start' : ' '}
          />
          <Chip label={`Auto: ${autoType || '-'}`} size="small" variant="outlined" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }} />
        </Stack>

        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Key Token Values</Typography>
          {keysMissing && (
            <Alert severity="warning">Fill in all key token values to enable discovery and runs.</Alert>
          )}
          {templatesWithKeys.length > 0 ? (
            templatesWithKeys.map(({ tpl, tokens }) => (
              <Box
                key={tpl.id}
                sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.5, bgcolor: 'background.paper' }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600 }}>{tpl.name || tpl.id}</Typography>
                <Stack spacing={1} sx={{ mt: 1 }}>
                  {tokens.map((token) => {
                    const templateOptions = keyOptions?.[tpl.id] || {}
                    const tokenOptions = templateOptions[token] || []
                    const loading = Boolean(keyOptionsLoading?.[tpl.id])
                    const stored = keyValues?.[tpl.id]?.[token]
                    const rawValue = Array.isArray(stored)
                      ? stored
                      : stored
                        ? [stored]
                        : []
                    const uniqueTokenOptions = tokenOptions.filter((opt, idx, arr) => arr.indexOf(opt) === idx)
                    const SELECT_ALL_OPTION = '__NR_SELECT_ALL__'
                    const optionsWithAll = uniqueTokenOptions.length > 1 ? [...uniqueTokenOptions, SELECT_ALL_OPTION] : uniqueTokenOptions
                    const ALL_SENTINELS = new Set(['all', 'select all', SELECT_ALL_OPTION.toLowerCase()])
                    const isAllStored = rawValue.some(
                      (val) => typeof val === 'string' && ALL_SENTINELS.has(val.toLowerCase()),
                    )
                    const displayValue = isAllStored
                      ? [SELECT_ALL_OPTION]
                      : rawValue
                        .filter((val, idx) => rawValue.indexOf(val) === idx)
                        .filter((val) => val !== SELECT_ALL_OPTION)
                    return (
                      <Autocomplete
                        key={token}
                        multiple
                        freeSolo
                        options={optionsWithAll}
                        value={displayValue}
                        getOptionLabel={(option) => (option === SELECT_ALL_OPTION ? 'All values' : option)}
                        filterSelectedOptions
                        renderTags={(value, getTagProps) => {
                          const isAllSelectedExplicit =
                            uniqueTokenOptions.length > 0 &&
                            value.length === uniqueTokenOptions.length &&
                            value.every((item) => uniqueTokenOptions.includes(item))
                          const selectedIncludesAllSentinel = value.some(
                            (item) => typeof item === 'string' && ALL_SENTINELS.has(item.toLowerCase()),
                          )
                          if (isAllSelectedExplicit || selectedIncludesAllSentinel) {
                            return [
                              <Chip
                                {...getTagProps({ index: 0 })}
                                key="all-values"
                                label="All values"
                              />,
                            ]
                          }
                          return value.map((option, index) => (
                            <Chip
                              {...getTagProps({ index })}
                              key={option}
                              label={option === SELECT_ALL_OPTION ? 'All values' : option}
                            />
                          ))
                        }}
                        onChange={(_event, newValue) => {
                          const cleaned = Array.isArray(newValue) ? newValue : []
                          const normalized = cleaned
                            .map((item) => (typeof item === 'string' ? item.trim() : ''))
                            .filter((item) => item.length > 0)
                          const hasSelectAll = normalized.some((item) => {
                            const lower = item.toLowerCase()
                            return item === SELECT_ALL_OPTION || ALL_SENTINELS.has(lower)
                          })
                          const sanitized = normalized.filter(
                            (item) => !ALL_SENTINELS.has(item.toLowerCase()) && item !== SELECT_ALL_OPTION,
                          )
                          if (hasSelectAll) {
                            const allList = uniqueTokenOptions.length
                              ? [SELECT_ALL_OPTION, ...uniqueTokenOptions]
                              : [SELECT_ALL_OPTION]
                            onKeyValueChange(tpl.id, token, allList)
                          } else {
                            onKeyValueChange(tpl.id, token, sanitized)
                          }
                        }}
                        isOptionEqualToValue={(option, optionValue) => option === optionValue}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label={token}
                            required
                            InputProps={{
                              ...params.InputProps,
                              endAdornment: (
                                <>
                                  {loading ? <CircularProgress color="inherit" size={16} /> : null}
                                  {params.InputProps.endAdornment}
                                </>
                              ),
                            }}
                          />
                        )}
                      />
                    )
                  })}
                </Stack>
              </Box>
            ))
          ) : (
            <Box
              sx={{
                border: '1px dashed',
                borderColor: 'divider',
                borderRadius: 1,
                p: 1.5,
                bgcolor: 'background.default',
                color: 'text.secondary',
              }}
            >
              <Typography variant="body2">
                {selected.length === 0
                  ? 'Select a template to configure key token filters.'
                  : 'Selected templates do not define key tokens.'}
              </Typography>
            </Box>
          )}
        </Stack>

        {activeTemplate && (
          <Box>
            <Divider sx={{ my: 2 }} />
            <Stack
              direction={{ xs: 'column', md: 'row' }}
              spacing={{ xs: 0.5, md: 1 }}
              alignItems={{ xs: 'flex-start', md: 'center' }}
              justifyContent="space-between"
            >
              <Stack spacing={0.5}>
                <Typography variant="subtitle1">Filter & Group Data</Typography>
                <Typography variant="body2" color="text.secondary">
                  Narrow down your data before generating reports. Use the chart below to select specific time periods or groups.
                </Typography>
              </Stack>
              <Button
                size="small"
                variant="text"
                onClick={handleResampleReset}
                disabled={!resampleState.filterActive}
              >
                Reset filter
              </Button>
            </Stack>
            {Array.isArray(activeTemplateResult?.batchMetrics) &&
            activeTemplateResult.batchMetrics.length ? (
              <>
                <Stack
                  direction={{ xs: 'column', lg: 'row' }}
                  spacing={1.25}
                  sx={{ mt: 1.5 }}
                >
                  <TextField
                    select
                    size="small"
                    label="Dimension"
                    value={safeResampleConfig.dimension}
                    onChange={handleResampleSelectorChange('dimension')}
                    sx={{ minWidth: { xs: '100%', lg: 180 } }}
                  >
                    {dimensionOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    select
                    size="small"
                    label="Metric"
                    value={safeResampleConfig.metric}
                    onChange={handleResampleSelectorChange('metric')}
                    sx={{ minWidth: { xs: '100%', lg: 180 } }}
                  >
                    {metricOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    select
                    size="small"
                    label="Aggregation"
                    value={safeResampleConfig.aggregation}
                    onChange={handleResampleSelectorChange('aggregation')}
                    sx={{ minWidth: { xs: '100%', lg: 180 } }}
                  >
                    {RESAMPLE_AGGREGATION_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    select
                    size="small"
                    label="Time bucket"
                    value={safeResampleConfig.bucket}
                    onChange={handleResampleSelectorChange('bucket')}
                    disabled={!bucketOptions.length || safeResampleConfig.dimensionKind === 'categorical'}
                    helperText={
                      safeResampleConfig.dimensionKind === 'temporal'
                        ? resampleBucketHelper
                        : safeResampleConfig.dimensionKind === 'numeric'
                          ? 'Applies to numeric bucketing'
                          : 'Not applicable to this dimension'
                    }
                    sx={{ minWidth: { xs: '100%', lg: 180 } }}
                  >
                    {bucketOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Stack>
                <Box sx={{ height: 260, mt: 2 }}>
                  {resampleState.series.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={resampleState.series}
                        margin={{ top: 8, right: 16, bottom: 24, left: 0 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <RechartsTooltip />
                        <Bar dataKey="value" fill={secondary.violet[500]} name={selectedMetricLabel} />
                        <Brush
                          dataKey="label"
                          height={24}
                          stroke={secondary.violet[500]}
                          startIndex={
                            resampleState.displayRange ? resampleState.displayRange[0] : 0
                          }
                          endIndex={
                            resampleState.displayRange
                              ? resampleState.displayRange[1]
                              : Math.max(resampleState.series.length - 1, 0)
                          }
                          travellerWidth={8}
                          onChange={handleResampleBrushChange}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <Stack
                      alignItems="center"
                      justifyContent="center"
                      sx={{ height: '100%' }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No buckets available for this selection. Try a different dimension.
                      </Typography>
                    </Stack>
                  )}
                </Box>
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  alignItems={{ xs: 'flex-start', sm: 'center' }}
                  justifyContent="space-between"
                  spacing={0.5}
                  sx={{ mt: 1 }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Showing {filteredBatchCount}
                    {totalBatchCount && totalBatchCount !== filteredBatchCount
                      ? ` / ${totalBatchCount}`
                      : ''}{' '}
                    {filteredBatchCount === 1 ? 'data section' : 'data sections'}
                  </Typography>
                  {safeResampleConfig.dimension === 'time' && resampleBucketHelper && (
                    <Typography variant="caption" color="text.secondary">
                      {resampleBucketHelper}
                    </Typography>
                  )}
                </Stack>
              </>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
                Run discovery for this template to populate resampling metrics.
              </Typography>
            )}
          </Box>
        )}

        {(finding || Object.keys(results).length > 0) && (
          <Box>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" alignItems="center" spacing={1}>
              <Typography variant="subtitle1">Data Preview</Typography>
              <InfoTooltip
                content="This shows the data sections found in your date range. Each section represents a logical grouping of data (like a time period or category) that will become part of your report."
                ariaLabel="Data preview explanation"
              />
            </Stack>
            {finding ? (
              <Stack spacing={1.25} sx={{ mt: 1.5 }}>
                <LinearProgress aria-label="Scanning your data" />
                <Typography variant="body2" color="text.secondary">
                  Scanning your data...
                </Typography>
              </Stack>
            ) : (
              <Stack spacing={1.5} sx={{ mt: 1.5 }}>
                {Object.keys(results).map((tid) => {
                  const r = results[tid]
                  const filteredCount = r.batches.length
                  const originalCount = r.allBatches?.length ?? r.batches_count ?? filteredCount
                  const filteredRows = r.batches.reduce((acc, batch) => acc + (batch.rows || 0), 0)
                  const summary =
                    originalCount === filteredCount
                      ? `${filteredCount} ${filteredCount === 1 ? 'section' : 'sections'} \u2022 ${filteredRows.toLocaleString()} records`
                      : `${filteredCount} / ${originalCount} sections \u2022 ${filteredRows.toLocaleString()} records`
                  return (
                    <Box
                      key={tid}
                      sx={{
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                        p: 1.5,
                        bgcolor: 'background.paper',
                      }}
                    >
                      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={{ xs: 0.5, sm: 1 }}>
                        <Typography variant="subtitle2">{r.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {summary}
                        </Typography>
                      </Stack>
                      {r.batches.length ? (
                        <Stack spacing={1} sx={{ mt: 1.25 }}>
                          <Typography variant="body2" color="text.secondary">
                            Select which data sections to include in your report:
                          </Typography>
                          {r.batches.map((b, idx) => (
                            <Stack key={b.id || idx} direction="row" spacing={1} alignItems="center">
                              <Checkbox
                                checked={b.selected}
                                onChange={(e) => onToggleBatch(tid, idx, e.target.checked)}
                                inputProps={{ 'aria-label': `Include section ${idx + 1} for ${r.name}` }}
                              />
                              <Typography variant="body2">
                                Section {idx + 1} {'\u2022'} {(b.parent ?? 1)} {(b.parent ?? 1) === 1 ? 'group' : 'groups'} {'\u2022'} {b.rows.toLocaleString()} records
                              </Typography>
                            </Stack>
                          ))}
                        </Stack>
                      ) : (
                        <Typography variant="body2" color="text.secondary">No data found for this date range. Try adjusting your dates.</Typography>
                      )}
                    </Box>
                  )
                })}
              </Stack>
            )}
          </Box>
        )}

        {activeTemplate && (
          <Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1">AI chart suggestions</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Ask about the discovered batches for {activeTemplate.name || activeTemplate.id}.
            </Typography>
            <Stack spacing={1.5} sx={{ mt: 1.5 }}>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25}>
                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={4}
                  label="Ask a question about this template's data"
                  placeholder="e.g. Highlight batches with unusually high row counts"
                  value={chartQuestion}
                  onChange={(event) => setChartQuestion(event.target.value)}
                />
                <Button
                  variant="outlined"
                  onClick={handleAskCharts}
                  disabled={
                    chartSuggestMutation.isLoading ||
                    !activeBatchData.length
                  }
                  sx={{ alignSelf: { xs: 'flex-end', sm: 'flex-start' }, whiteSpace: 'nowrap' }}
                >
                  {chartSuggestMutation.isLoading ? 'Asking for charts...' : 'Ask AI for charts'}
                </Button>
              </Stack>
              {!activeBatchData.length && (
                <Typography variant="caption" color="text.secondary">
                  Run discovery for this template to unlock chart suggestions.
                </Typography>
              )}
              {chartSuggestions.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No suggestions yet. Ask a question to generate chart ideas.
                </Typography>
              ) : (
                <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
                  <Box
                    sx={{
                      flex: 1,
                      minWidth: 0,
                    }}
                  >
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Suggestions
                    </Typography>
                    <Stack spacing={1}>
                      {chartSuggestions.map((chart) => (
                        <Card
                          key={chart.id}
                          variant={
                            selectedChartSource === 'suggestion' && chart.id === selectedChartId
                              ? 'outlined'
                              : 'elevation'
                          }
                          sx={{
                            borderColor:
                              selectedChartSource === 'suggestion' && chart.id === selectedChartId
                                ? 'text.secondary'
                                : 'divider',
                            bgcolor:
                              selectedChartSource === 'suggestion' && chart.id === selectedChartId
                                ? alpha(secondary.violet[500], 0.04)
                                : 'background.paper',
                          }}
                        >
                          <CardActionArea onClick={() => handleSelectSuggestion(chart.id)}>
                            <CardContent>
                              <Typography variant="subtitle2">
                                {chart.title || 'Untitled chart'}
                              </Typography>
                              {chart.description && (
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{ mt: 0.5 }}
                                >
                                  {chart.description}
                                </Typography>
                              )}
                              <Stack direction="row" spacing={1} sx={{ mt: 0.75, flexWrap: 'wrap' }}>
                                <Chip
                                  size="small"
                                  label={chart.type || 'chart'}
                                  variant="outlined"
                                  sx={{ textTransform: 'capitalize' }}
                                />
                                {chart.chartTemplateId && (
                                  <Chip
                                    size="small"
                                    label={chart.chartTemplateId}
                                    variant="outlined"
                                  />
                                )}
                              </Stack>
                            </CardContent>
                          </CardActionArea>
                        </Card>
                      ))}
                    </Stack>
                  </Box>
                  <Box
                    sx={{
                      flex: 2,
                      minHeight: { xs: 260, sm: 300 },
                      borderRadius: 1.5,
                      border: '1px solid',
                      borderColor: 'divider',
                      bgcolor: 'background.paper',
                      p: 1.5,
                      minWidth: 0,
                    }}
                  >
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Preview
                    </Typography>
                    {usingSampleData && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                        Using sample dataset from suggestion response
                      </Typography>
                    )}
                    <Box sx={{ width: '100%', height: { xs: 220, sm: 260 } }}>
                      {renderSuggestedChart(selectedChartSpec, previewData, {
                        source: selectedChartSource,
                      })}
                    </Box>
                    {chartSuggestions.length > 0 && (
                      <Box sx={{ textAlign: 'right', mt: 1 }}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<BookmarkAddOutlinedIcon fontSize="small" />}
                          onClick={handleSaveCurrentSuggestion}
                          disabled={!selectedSuggestion || saveChartLoading}
                        >
                          {saveChartLoading ? 'Saving…' : 'Save this chart'}
                        </Button>
                      </Box>
                    )}
                  </Box>
                </Stack>
              )}
            </Stack>
          </Box>
        )}

        <Box>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1">Saved charts</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Reuse charts you previously saved for {activeTemplate?.name || activeTemplate?.id || 'this template'}.
          </Typography>
          {!activeTemplate && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Select a template to view saved charts.
            </Typography>
          )}
          {activeTemplate && (
            <SavedChartsPanel
              activeTemplate={activeTemplate}
              savedCharts={savedCharts}
              savedChartsLoading={savedChartsLoading}
              savedChartsError={savedChartsError}
              selectedChartSource={selectedChartSource}
              selectedSavedChartId={selectedSavedChartId}
              onRetry={handleRetrySavedCharts}
              onSelectSavedChart={handleSelectSavedChart}
              onRenameSavedChart={handleRenameSavedChart}
              onDeleteSavedChart={handleDeleteSavedChart}
            />
          )}
        </Box>

        <Box>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1">Progress</Typography>
          {generation.items.length > 0 && (
            <Alert severity="info" sx={{ mt: 1 }}>
              Reports continue running in the background. Open the Jobs panel from Notifications in the header to monitor status and download results.
            </Alert>
          )}
          <Stack spacing={1.5} sx={{ mt: 1.5 }}>
            {generation.items.map((item) => {
              const jobDetails = item.jobId ? jobsById?.[item.jobId] : null
              const rawStatus = (jobDetails?.status || item.status || 'queued').toLowerCase()
              const statusLabel = rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1)
              const jobProgress =
                typeof jobDetails?.progress === 'number'
                  ? jobDetails.progress
                  : typeof item.progress === 'number'
                    ? item.progress
                    : null
              const clampedProgress =
                typeof jobProgress === 'number' && Number.isFinite(jobProgress)
                  ? Math.min(100, Math.max(0, jobProgress))
                  : null
              const chipColor = JOB_STATUS_COLORS[rawStatus] || 'default'
              const progressVariant = clampedProgress == null ? 'indeterminate' : 'determinate'
              const errorMessage = jobDetails?.error || item.error
              return (
                <Box
                  key={item.id}
                  sx={{
                    p: 1.5,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    bgcolor: 'background.paper',
                  }}
                >
                  <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={{ xs: 0.5, sm: 1 }}>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {item.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {item.jobId ? `Job ID: ${item.jobId}` : 'Preparing job...'}
                      </Typography>
                    </Box>
                    <Chip
                      size="small"
                      label={statusLabel}
                      color={chipColor === 'default' ? 'default' : chipColor}
                      variant={chipColor === 'default' ? 'outlined' : 'filled'}
                    />
                  </Stack>
                  <LinearProgress
                    variant={progressVariant}
                    value={progressVariant === 'determinate' ? clampedProgress : undefined}
                    sx={{ mt: 1 }}
                    aria-label={`${item.name} progress`}
                  />
                  {errorMessage ? (
                    <Alert severity="error" sx={{ mt: 1 }}>
                      {errorMessage}
                    </Alert>
                  ) : (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                      Keep an eye on the Jobs panel to see when this run finishes and download the files.
                    </Typography>
                  )}
                </Box>
              )
            })}
            {!generation.items.length && <Typography variant="body2" color="text.secondary">No runs yet</Typography>}
          </Stack>
        </Box>
      </Surface>

      <Surface sx={surfaceStackSx}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Recently Downloaded</Typography>
          <InfoTooltip
            content={TOOLTIP_COPY.recentDownloads}
            ariaLabel="Recent downloads guidance"
          />
        </Stack>
        <Stack spacing={1.5}>
          {downloads.map((d, i) => {
            const metaLine = [d.template, d.format ? d.format.toUpperCase() : null, d.size || 'Size unknown']
              .filter(Boolean)
              .join(' \u2022 ')
            const formatChips = [
              d.pdfUrl && { label: 'PDF', color: 'primary' },
              d.docxUrl && { label: 'DOCX', color: 'secondary' },
              d.xlsxUrl && { label: 'XLSX', color: 'info' },
            ].filter(Boolean)
            const actionButtons = [
              {
                key: 'open',
                label: 'Open preview',
                variant: 'outlined',
                color: 'inherit',
                disabled: !d.htmlUrl,
                href: d.htmlUrl ? withBase(d.htmlUrl) : null,
              },
              {
                key: 'pdf',
                label: 'Download PDF',
                variant: 'contained',
                color: 'primary',
                disabled: !d.pdfUrl,
                href: d.pdfUrl ? buildDownloadUrl(withBase(d.pdfUrl)) : null,
              },
              d.docxUrl && {
                key: 'docx',
                label: 'Download DOCX',
                variant: 'outlined',
                color: 'primary',
                href: buildDownloadUrl(withBase(d.docxUrl)),
              },
              d.xlsxUrl && {
                key: 'xlsx',
                label: 'Download XLSX',
                variant: 'outlined',
                color: 'info',
                href: buildDownloadUrl(withBase(d.xlsxUrl)),
              },
            ].filter(Boolean)
            return (
              <Box
                key={`${d.filename}-${i}`}
                sx={{
                  p: { xs: 1.5, md: 2 },
                  borderRadius: 1,  // Figma spec: 8px
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'background.paper',
                  boxShadow: `0 6px 20px ${alpha(neutral[900], 0.06)}`,
                  transition: 'border-color 200ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 200ms cubic-bezier(0.22, 1, 0.36, 1), transform 160ms cubic-bezier(0.22, 1, 0.36, 1)',
                  '&:hover': {
                    borderColor: 'primary.light',
                    boxShadow: `0 10px 30px ${alpha(secondary.violet[500], 0.14)}`,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <Stack spacing={1.5}>
                  <Stack
                    direction={{ xs: 'column', md: 'row' }}
                    spacing={1}
                    justifyContent="space-between"
                    alignItems={{ md: 'center' }}
                  >
                    <Box sx={{ minWidth: 0 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap title={d.filename}>
                        {d.filename}
                      </Typography>
                      {metaLine && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mt: 0.5 }}
                          noWrap
                          title={metaLine}
                        >
                          {metaLine}
                        </Typography>
                      )}
                    </Box>
                    {!!formatChips.length && (
                      <Stack direction="row" spacing={0.75} flexWrap="wrap" justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
                        {formatChips.map(({ label, color: colorKey }) => (
                          <Chip
                            key={label}
                            size="small"
                            label={label}
                            sx={(theme) => ({
                              borderRadius: 1,
                              fontWeight: 600,
                              bgcolor: alpha(theme.palette[colorKey].main, 0.12),
                              color: theme.palette[colorKey].dark,
                              border: '1px solid',
                              borderColor: alpha(theme.palette[colorKey].main, 0.3),
                            })}
                          />
                        ))}
                      </Stack>
                    )}
                  </Stack>

                  <Divider />

                  <Stack
                    direction={{ xs: 'column', lg: 'row' }}
                    spacing={1.25}
                    alignItems={{ lg: 'flex-start' }}
                  >
                    <Stack
                      direction="row"
                      spacing={1}
                      flexWrap="wrap"
                      sx={{ flexGrow: 1, columnGap: 1, rowGap: 1 }}
                    >
                      {actionButtons.map((action) => {
                        const linkProps = action.href
                          ? { component: 'a', href: action.href, target: '_blank', rel: 'noopener' }
                          : {}
                        return (
                          <Button
                            key={action.key}
                            size="small"
                            variant={action.variant}
                            color={action.color}
                            disabled={action.disabled}
                            sx={{
                              textTransform: 'none',
                              minWidth: { xs: '100%', sm: 0 },
                              flex: { xs: '1 1 100%', sm: '0 0 auto' },
                              px: 2.5,
                            }}
                            {...linkProps}
                          >
                            {action.label}
                          </Button>
                        )
                      })}
                    </Stack>
                    <Box sx={{ width: { xs: '100%', lg: 'auto' } }}>
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<ReplayIcon fontSize="small" />}
                        onClick={d.onRerun}
                        sx={{ width: { xs: '100%', lg: 'auto' }, textTransform: 'none', px: 2.5 }}
                      >
                        Re-run
                      </Button>
                    </Box>
                  </Stack>
                </Stack>
              </Box>
            )
          })}
          {!downloads.length && <Typography variant="body2" color="text.secondary">No recent downloads yet.</Typography>}
        </Stack>
      </Surface>
    </>
  )
}

export default GenerateAndDownload

/* -----------------------------------------------------------
   Page Shell
----------------------------------------------------------- */

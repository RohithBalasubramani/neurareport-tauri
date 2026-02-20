import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Box, Typography, Stack, Button, TextField, Chip, LinearProgress,
  MenuItem, Paper, Dialog, DialogTitle, DialogContent, DialogActions,
  Tabs, Tab, Collapse, IconButton, Badge, Tooltip, Alert,
  alpha,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import SearchIcon from '@mui/icons-material/Search'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import TuneIcon from '@mui/icons-material/Tune'
import ScheduleIcon from '@mui/icons-material/Schedule'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import { useSearchParams } from 'react-router-dom'
import {
  fetchTemplateKeyOptions,
  discoverReports,
  runReportAsJob,
  listSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
} from '@/api/client'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import TemplatePicker from '@/features/generate/components/TemplatePicker.jsx'
import GenerateAndDownload from '@/features/generate/components/GenerateAndDownload.jsx'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice.jsx'
import {
  ALL_OPTION,
  SCHEDULE_FREQUENCY_OPTIONS,
  parseEmailTargets,
  formatScheduleDate,
  toSqlFromDayjs,
  formatDisplayDate,
  formatTokenLabel,
  getTemplateKind,
} from '../utils/templatesPaneUtils'
import { DEFAULT_RESAMPLE_CONFIG } from '@/features/generate/utils/generateFeatureUtils'


function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`run-tabpanel-${index}`}
      aria-labelledby={`run-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

function CollapsibleSection({ title, icon, badge, defaultExpanded = false, children }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  return (
    <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, overflow: 'hidden' }}>
      <Box
        onClick={() => setExpanded(!expanded)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 1.5,
          cursor: 'pointer',
          bgcolor: expanded ? 'action.hover' : 'background.paper',
          '&:hover': { bgcolor: 'action.hover' },
          transition: 'background-color 150ms cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        <Stack direction="row" alignItems="center" spacing={1}>
          {icon}
          <Typography variant="subtitle2" fontWeight={600}>{title}</Typography>
          {badge && (
            <Chip size="small" label={badge} variant="outlined" sx={{ borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[200], color: 'text.secondary' }} />
          )}
        </Stack>
        <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
          <IconButton
            size="small"
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}
            aria-label={expanded ? 'Collapse section' : 'Expand section'}
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Tooltip>
      </Box>
      <Collapse in={expanded}>
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          {children}
        </Box>
      </Collapse>
    </Box>
  )
}

export default function TemplatesPane() {
  // pull connection if available; API can fallback when not provided
  const templates = useAppStore((state) => state.templates)
  const navigate = useNavigateInteraction()
  const activeConnectionId = useAppStore((state) => state.activeConnectionId)
  const activeConnection = useAppStore((state) => state.activeConnection)
  const finding = useAppStore((state) => state.discoveryFinding)
  const setFinding = useAppStore((state) => state.setDiscoveryFinding)
  const results = useAppStore((state) => state.discoveryResults)
  const discoveryMeta = useAppStore((state) => state.discoveryMeta)
  const setDiscoveryResults = useAppStore((state) => state.setDiscoveryResults)
  const clearDiscoveryResults = useAppStore((state) => state.clearDiscoveryResults)
  const toast = useToast()
  const { execute } = useInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'setup-templates-pane', ...intent } }),
    [navigate]
  )
  const [searchParams, setSearchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const activeTab = tabParam === 'configure' ? 1 : tabParam === 'schedules' ? 2 : 0

  const handleTabChange = useCallback((e, newValue) => {
    const tabMap = { 0: undefined, 1: 'configure', 2: 'schedules' }
    const newTab = tabMap[newValue]
    setSearchParams(newTab ? { tab: newTab } : {}, { replace: true })
  }, [setSearchParams])

  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])
  const [selected, setSelected] = useState([])
  const [tagFilter, setTagFilter] = useState([])
  const [outputFormats, setOutputFormats] = useState({})
  const onToggle = (id) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))
  const selectedTemplates = useMemo(() => approved.filter((t) => selected.includes(t.id)), [approved, selected])
  const selectedTypes = useMemo(
    () => selectedTemplates.map((t) => getTemplateKind(t).toUpperCase()),
    [selectedTemplates],
  )
  const autoType =
    selectedTypes.length === 0
      ? '-'
      : selectedTypes.every((t) => t === selectedTypes[0])
        ? selectedTypes[0]
        : 'Mixed'
  const [keyValues, setKeyValues] = useState({})
  const [keyOptions, setKeyOptions] = useState({})
  const [keyOptionsLoading, setKeyOptionsLoading] = useState({})
  const [start, setStart] = useState(null)
  const [end, setEnd] = useState(null)
  const [emailTargets, setEmailTargets] = useState('')
  const [emailSubject, setEmailSubject] = useState('')
  const [emailMessage, setEmailMessage] = useState('')
  const [scheduleName, setScheduleName] = useState('')
  const [scheduleFrequency, setScheduleFrequency] = useState('daily')
  const [schedules, setSchedules] = useState([])
  const [schedulesLoading, setSchedulesLoading] = useState(false)
  const [scheduleSaving, setScheduleSaving] = useState(false)
  const [deletingScheduleId, setDeletingScheduleId] = useState(null)
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [editScheduleFields, setEditScheduleFields] = useState({})
  const [scheduleUpdating, setScheduleUpdating] = useState(false)
  const scheduleDeleteUndoRef = useRef(null)
  const [deleteScheduleConfirmOpen, setDeleteScheduleConfirmOpen] = useState(false)
  const [scheduleToDelete, setScheduleToDelete] = useState(null)
  const [generation, setGeneration] = useState({ items: [] })
  const queuedJobs = useMemo(
    () => generation.items.filter((item) => item.status === 'queued'),
    [generation.items],
  )
  const queuedJobIds = useMemo(
    () => queuedJobs.map((item) => item.jobId).filter(Boolean),
    [queuedJobs],
  )
  const discoveryResetReady = useRef(false)
  const keyOptionsFetchKeyRef = useRef({})
  const isDevEnv = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV)

  useEffect(() => {
    if (!isDevEnv || typeof window === 'undefined') return
    window.__NR_SETUP_KEY_OPTIONS__ = keyOptions
    window.__NR_SETUP_KEY_VALUES__ = keyValues
  }, [keyOptions, keyValues, isDevEnv])

  useEffect(() => {
    setKeyValues((prev) => {
      const next = {}
      selectedTemplates.forEach((tpl) => {
        if (prev[tpl.id]) next[tpl.id] = prev[tpl.id]
      })
      if (Object.keys(next).length === Object.keys(prev).length) return prev
      return next
    })
  }, [selectedTemplates])
  useEffect(() => {
    setKeyOptions((prev) => {
      const next = {}
      selectedTemplates.forEach((tpl) => {
        if (prev[tpl.id]) next[tpl.id] = prev[tpl.id]
      })
      return next
    })
    setKeyOptionsLoading((prev) => {
      const next = {}
      selectedTemplates.forEach((tpl) => {
        if (prev[tpl.id]) next[tpl.id] = prev[tpl.id]
      })
      return next
    })
  }, [selectedTemplates])

  const refreshSchedules = useCallback(async () => {
    setSchedulesLoading(true)
    try {
      const data = await listSchedules()
      setSchedules(Array.isArray(data) ? data : [])
    } catch (e) {
      toast.show(String(e), 'error')
    } finally {
      setSchedulesLoading(false)
    }
  }, [toast])

  useEffect(() => {
    refreshSchedules()
  }, [refreshSchedules])

  const getTemplateKeyTokens = useCallback(
    (tpl) => {
      if (!tpl) return []
      const fromState = Array.isArray(tpl?.mappingKeys)
        ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
        : []
      if (fromState.length) return fromState
      const existing = keyOptions[tpl.id] || {}
      return Object.keys(existing)
    },
    [keyOptions],
  )

  const requestKeyOptions = useCallback(
    (tpl, startSql, endSql) => {
      if (!startSql || !endSql) return
      const tokens = Array.isArray(tpl?.mappingKeys)
        ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
        : []
      if (!tokens.length) return
      const discoveryConnectionId =
        discoveryMeta?.connectionId && (discoveryMeta?.templateIds || []).includes(tpl.id)
          ? discoveryMeta.connectionId
          : null
      const effectiveConnectionId =
        discoveryConnectionId || activeConnectionId || tpl.lastConnectionId || undefined
      const paramKey = `${effectiveConnectionId || 'auto'}|${startSql}|${endSql}`
      if (keyOptionsFetchKeyRef.current[tpl.id] === paramKey) {
        return
      }
      keyOptionsFetchKeyRef.current[tpl.id] = paramKey
      setKeyOptionsLoading((prev) => ({ ...prev, [tpl.id]: true }))

      fetchTemplateKeyOptions(tpl.id, {
        connectionId: effectiveConnectionId,
        tokens,
        limit: 100,
        startDate: startSql,
        endDate: endSql,
        kind: tpl.kind || 'pdf',
      })
        .then((data) => {
          const incoming = data?.keys && typeof data.keys === 'object' ? data.keys : {}
          const normalizedBatch = {}
          tokens.forEach((token) => {
            const rawValues = incoming[token]
            const normalized = Array.isArray(rawValues)
              ? Array.from(new Set(rawValues.map((value) => (value == null ? '' : String(value).trim())).filter(Boolean)))
              : []
            normalizedBatch[token] = normalized
          })
          if (typeof window !== 'undefined' && typeof window.__nrLogKeyOptions === 'function') {
            try {
              window.__nrLogKeyOptions({
                templateId: tpl.id,
                connectionId: effectiveConnectionId || tpl.lastConnectionId || null,
                tokens,
                payload: incoming,
              })
            } catch (err) {
              console.warn('nr_key_options_log_failed', err)
            }
          }
          setKeyOptions((prev) => {
            const prevTemplateOptions = prev[tpl.id] || {}
            const nextTemplateOptions = { ...prevTemplateOptions }
            Object.entries(normalizedBatch).forEach(([token, values]) => {
              nextTemplateOptions[token] = values
            })
            return { ...prev, [tpl.id]: nextTemplateOptions }
          })
        })
        .catch((err) => {
          console.warn('key_options_fetch_failed', err)
          toast.show(`Failed to load key options for ${tpl.name || tpl.id}`, 'error')
        })
        .finally(() => {
          setKeyOptionsLoading((prev) => ({ ...prev, [tpl.id]: false }))
        })
    },
    [activeConnectionId, discoveryMeta, toast],
  )

  useEffect(() => {
    if (!start || !end) return
    const startSql = toSqlFromDayjs(start)
    const endSql = toSqlFromDayjs(end)
    if (!startSql || !endSql) return
    selectedTemplates.forEach((tpl) => requestKeyOptions(tpl, startSql, endSql))
  }, [selectedTemplates, start, end, requestKeyOptions])

  const keysReady = useMemo(() => {
    return selectedTemplates.every((tpl) => {
      const tokens = getTemplateKeyTokens(tpl)
      if (!tokens.length) return true
      const provided = keyValues[tpl.id] || {}
      return tokens.every((token) => {
        const values = provided[token]
        if (!Array.isArray(values) || values.length === 0) return false
        if (values.includes(ALL_OPTION)) return true
        return values.some((value) => value && value.trim())
      })
    })
  }, [selectedTemplates, keyValues, getTemplateKeyTokens])

  const collectMissingKeys = useCallback(() => {
    const missing = []
    selectedTemplates.forEach((tpl) => {
      const tokens = getTemplateKeyTokens(tpl)
      if (!tokens.length) return
      const provided = keyValues[tpl.id] || {}
      const absent = tokens.filter((token) => {
        const values = provided[token]
        if (!Array.isArray(values) || values.length === 0) return true
        if (values.includes(ALL_OPTION)) return false
        return !values.some((value) => value && value.trim())
      })
      if (absent.length) {
        missing.push({ tpl, tokens: absent.map((token) => formatTokenLabel(token)) })
      }
    })
    return missing
  }, [selectedTemplates, getTemplateKeyTokens, keyValues])

  const handleKeyValueChange = useCallback((templateId, token, values) => {
    setKeyValues((prev) => {
      const next = { ...prev }
      const existing = { ...(next[templateId] || {}) }
      let normalized = Array.isArray(values) ? values.map((value) => (value == null ? '' : String(value).trim())) : []
      normalized = normalized.filter(Boolean)
      if (normalized.includes(ALL_OPTION)) {
        normalized = [ALL_OPTION]
      } else {
        normalized = Array.from(new Set(normalized))
      }
      if (normalized.length) {
        existing[token] = normalized
        next[templateId] = existing
      } else {
        delete existing[token]
        if (Object.keys(existing).length) next[templateId] = existing
        else delete next[templateId]
      }
      return next
    })
  }, [])

  const buildKeyFiltersForTemplate = useCallback((templateId) => {
    const provided = keyValues[templateId] || {}
    const payload = {}
    Object.entries(provided).forEach(([token, values]) => {
      if (!Array.isArray(values) || values.length === 0) return
      if (values.includes(ALL_OPTION)) {
        const options = keyOptions[templateId]?.[token] || []
        const normalizedOptions = Array.from(
          new Set(
            options
              .map((option) => (option == null ? '' : String(option).trim()))
              .filter(Boolean),
          ),
        )
        if (normalizedOptions.length) {
          payload[token] = normalizedOptions.length === 1 ? normalizedOptions[0] : normalizedOptions
        } else {
          return // options not loaded yet; skip filtering to avoid forcing "All"
        }
        return
      }
      const normalized = Array.from(
        new Set(values.filter((value) => value && value.trim() && value !== ALL_OPTION)),
      )
      if (!normalized.length) return
      payload[token] = normalized.length === 1 ? normalized[0] : normalized
    })
    return payload
  }, [keyValues, keyOptions])

  // Run Config state (key-driven discovery & generation)

  useEffect(() => {
    if (!discoveryResetReady.current) {
      discoveryResetReady.current = true
      return
    }
    clearDiscoveryResults()
    setFinding(false)
  }, [clearDiscoveryResults, setFinding, selected, start?.valueOf(), end?.valueOf()])

  const runFind = async () => {
    if (!selectedTemplates.length || !start || !end) return toast.show('Select a design and choose a start/end date.', 'warning')
    const startSql = toSqlFromDayjs(start)
    const endSql = toSqlFromDayjs(end)
    if (!startSql || !endSql) return toast.show('Provide a valid start and end date.', 'warning')

    setKeyOptions({})
    keyOptionsFetchKeyRef.current = {}
    setKeyOptionsLoading({})
    setFinding(true)
    try {
      const r = {}
      for (const t of selectedTemplates) {
        const keyFilters = buildKeyFiltersForTemplate(t.id)
        requestKeyOptions(t, startSql, endSql)
        const data = await discoverReports({
          templateId: t.id,
          startDate: startSql,
          endDate: endSql,
          connectionId: activeConnectionId || undefined,
          keyValues: Object.keys(keyFilters).length ? keyFilters : undefined,
          kind: getTemplateKind(t),
        })
        const rawBatches = Array.isArray(data.batches) ? data.batches : []
        const normalizedBatches = rawBatches.map((batch, index) => {
          const batchId = Object.prototype.hasOwnProperty.call(batch, 'id') ? batch.id : `${index + 1}`
          const rows = Number(batch.rows || 0)
          const parent = Number(batch.parent || 0)
          const safeParent = parent || 1
          const time = batch.time ?? null
          const category = batch.category ?? null
          return {
            ...batch,
            id: batchId,
            rows,
            parent,
            selected: batch.selected ?? true,
            time,
            category,
            rows_per_parent: safeParent ? rows / safeParent : rows,
          }
        })
        const fieldCatalog = Array.isArray(data.field_catalog) ? data.field_catalog : []
        const discoverySchema = data.discovery_schema && typeof data.discovery_schema === 'object' ? data.discovery_schema : null
        const defaultDimension = discoverySchema?.defaults?.dimension
          || (fieldCatalog.some((field) => field?.name === 'time')
            ? 'time'
            : fieldCatalog.some((field) => field?.name === 'category')
              ? 'category'
              : 'batch_index')
        const defaultMetric = discoverySchema?.defaults?.metric
          || (fieldCatalog.some((field) => field?.name === 'rows')
            ? 'rows'
            : fieldCatalog.some((field) => field?.name === 'rows_per_parent')
              ? 'rows_per_parent'
              : 'parent')
        const dimensionKind = discoverySchema?.dimensions?.find?.((dim) => dim?.name === defaultDimension)?.kind || 'categorical'
        const batchMetrics = Array.isArray(data.batch_metrics)
          ? data.batch_metrics
          : normalizedBatches.map((entry, index) => ({
              batch_index: index + 1,
              batch_id: entry.id ?? index + 1,
              rows: entry.rows ?? 0,
              parent: entry.parent ?? 0,
              rows_per_parent: entry.rows_per_parent ?? 0,
              time: entry.time ?? null,
              category: entry.category ?? null,
            }))
        r[t.id] = {
          name: t.name,
          batches: normalizedBatches,
          allBatches: normalizedBatches,
          batches_count: data.batches_count ?? normalizedBatches.length,
          rows_total: data.rows_total ?? normalizedBatches.reduce((a, b) => a + (b.rows || 0), 0),
          fieldCatalog,
          batchMetrics,
          discoverySchema,
          numericBins: data.numeric_bins && typeof data.numeric_bins === 'object' ? data.numeric_bins : {},
          categoryGroups: data.category_groups && typeof data.category_groups === 'object' ? data.category_groups : {},
          resample: {
            config: {
              ...DEFAULT_RESAMPLE_CONFIG,
              dimension: defaultDimension,
              metric: defaultMetric,
              dimensionKind,
            },
            filteredIds: null,
          },
        }
      }
      setDiscoveryResults(r, {
        startSql,
        endSql,
        startDisplay: formatDisplayDate(start),
        endDisplay: formatDisplayDate(end),
        templateSummary: selectedTemplates.map((t) => ({
          id: t.id,
          name: t.name,
          kind: getTemplateKind(t),
        })),
        templateIds: selectedTemplates.map((t) => t.id),
        connectionId: activeConnectionId || null,
        connectionName: activeConnection?.name || activeConnection?.connection_name || '',
        autoType,
        fetchedAt: new Date().toISOString(),
      })
    } catch (e) {
      toast.show(String(e), 'error')
      throw e
    } finally {
      setFinding(false)
    }
  }

  const onFind = async () => {
    await execute({
      type: InteractionType.ANALYZE,
      label: 'Discover batches',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateIds: selectedTemplates.map((t) => t.id),
        connectionId: activeConnectionId || null,
        action: 'discover_reports',
      },
      action: async () => runFind(),
    })
  }

  const onToggleBatch = (id, idx, val) => {
    setDiscoveryResults((prev) => {
      const target = prev[id]
      if (!target || !Array.isArray(target.batches)) return prev
      const targetBatch = target.batches[idx]
      if (!targetBatch) return prev
      const batchId = targetBatch.id
      const baseAll = (target.allBatches || target.batches || []).map((batch) => {
        if (String(batch.id) === String(batchId)) {
          return { ...batch, selected: val }
        }
        return batch
      })
      const allowedSet = target.resample?.filteredIds
      const nextBatches = allowedSet
        ? baseAll.filter((batch) => allowedSet.has(String(batch.id)))
        : baseAll
      return {
        ...prev,
        [id]: {
          ...target,
          allBatches: baseAll,
          batches: nextBatches,
        },
      }
    })
  }

  const handleResampleFilter = useCallback((templateId, payload) => {
    if (!templateId) return
    setDiscoveryResults((prev) => {
      const target = prev[templateId]
      if (!target) return prev
      const baseAll = target.allBatches || target.batches || []
      const allowedList = Array.isArray(payload?.allowedBatchIds)
        ? payload.allowedBatchIds.map((id) => String(id))
        : null
      const allowedSet = allowedList ? new Set(allowedList) : null
      const nextBatches = allowedSet
        ? baseAll.filter((batch) => allowedSet.has(String(batch.id)))
        : baseAll
      const incomingConfig = payload?.config
      const mergedConfig = incomingConfig
        ? { ...(target.resample?.config || DEFAULT_RESAMPLE_CONFIG), ...incomingConfig }
        : target.resample?.config || DEFAULT_RESAMPLE_CONFIG
      return {
        ...prev,
        [templateId]: {
          ...target,
          batches: nextBatches,
          resample: {
            config: mergedConfig,
            filteredIds: allowedSet,
          },
        },
      }
    })
  }, [setDiscoveryResults])

  const canGenerate = useMemo(() => {
    const hasSel = Object.values(results).length > 0 && Object.values(results).some((r) => r.batches.some((b) => b.selected))
    const rangeReady = !!start && !!end && end.valueOf() >= start.valueOf()
    return hasSel && rangeReady && keysReady
  }, [results, start, end, keysReady])

  const canSchedule = useMemo(() => {
    if (selectedTemplates.length !== 1) return false
    if (!start || !end) return false
    if (end.valueOf() < start.valueOf()) return false
    return Boolean(activeConnectionId)
  }, [selectedTemplates, start, end, activeConnectionId])

  const generateLabel = useMemo(
    () => (selectedTemplates.length ? `Run Reports (${selectedTemplates.length})` : 'Run Reports'),
    [selectedTemplates],
  )

  const batchIdsFor = (tplId) =>
    (results[tplId]?.batches || []).filter(b => b.selected).map(b => b.id)

  const runGenerate = async () => {
    if (!selectedTemplates.length) return toast.show('Select at least one design.', 'warning')
    if (!start || !end) return toast.show('Choose a start and end date before running.', 'warning')
    const startSql = toSqlFromDayjs(start)
    const endSql = toSqlFromDayjs(end)
    if (!startSql || !endSql) return toast.show('Provide a valid date range.', 'warning')
    const missing = collectMissingKeys()
    if (missing.length) {
      const message = missing.map(({ tpl, tokens }) => `${tpl.name || tpl.id}: ${tokens.join(', ')}`).join('; ')
      toast.show(`Provide values for key tokens before running (${message}).`, 'warning')
      return
    }

    const timestamp = Date.now()
    const emailList = parseEmailTargets(emailTargets)
    const seed = selectedTemplates.map((t, idx) => ({
      id: `${t.id}-${timestamp + idx}`,
      tplId: t.id,
      name: t.name,
      kind: getTemplateKind(t),
      status: 'queued',
      progress: 5,
      jobId: null,
      error: null,
    }))
    setGeneration({ items: seed })

    for (const it of seed) {
      try {
        const keyFilters = buildKeyFiltersForTemplate(it.tplId)
        const requestDocx = true
        const requestXlsx = it.kind === 'excel'
        const response = await runReportAsJob({
          templateId: it.tplId,
          templateName: it.name,
          startDate: startSql,
          endDate: endSql,
          batchIds: batchIdsFor(it.tplId),
          connectionId: activeConnectionId || undefined,
          keyValues: Object.keys(keyFilters).length ? keyFilters : undefined,
          docx: requestDocx,
          xlsx: requestXlsx,
          kind: it.kind,
          emailRecipients: emailList.length ? emailList : undefined,
          emailSubject: emailSubject || undefined,
          emailMessage: emailMessage || undefined,
        })
        const jobId = response?.job_id || null
        setGeneration((prev) => ({
          items: prev.items.map((x) =>
            x.id === it.id
              ? {
                  ...x,
                  progress: jobId ? 15 : 10,
                  status: 'queued',
                  jobId,
                  error: null,
                }
              : x,
          ),
        }))
        if (jobId) {
          toast.show(`Queued job ${jobId} for ${it.name}`, 'success')
        }
      } catch (e) {
        setGeneration((prev) => ({
          items: prev.items.map((x) =>
            x.id === it.id ? { ...x, progress: 100, status: 'failed', error: String(e) } : x,
          ),
        }))
        toast.show(String(e), 'error')
      }
    }
  }

  const onGenerate = async () => {
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Run reports',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateIds: selectedTemplates.map((t) => t.id),
        connectionId: activeConnectionId || null,
        action: 'run_reports',
      },
      action: async () => runGenerate(),
    })
  }

  const handleCreateSchedule = async () => {
    if (selectedTemplates.length !== 1) {
      toast.show('Select exactly one design to create a schedule.', 'warning')
      return
    }
    if (!start || !end) {
      toast.show('Choose a start and end date before scheduling.', 'warning')
      return
    }
    if (!activeConnectionId) {
      toast.show('Select a connection before scheduling.', 'warning')
      return
    }
    const startSql = toSqlFromDayjs(start)
    const endSql = toSqlFromDayjs(end)
    if (!startSql || !endSql) {
      toast.show('Provide a valid date range.', 'warning')
      return
    }
    const template = selectedTemplates[0]
    const keyFilters = buildKeyFiltersForTemplate(template.id)
    const emailList = parseEmailTargets(emailTargets)
    await execute({
      type: InteractionType.CREATE,
      label: 'Create schedule',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId: template.id,
        connectionId: activeConnectionId,
        action: 'create_schedule',
      },
      action: async () => {
        setScheduleSaving(true)
        try {
          await createSchedule({
            templateId: template.id,
            connectionId: activeConnectionId,
            startDate: startSql,
            endDate: endSql,
            keyValues: Object.keys(keyFilters).length ? keyFilters : undefined,
            batchIds: batchIdsFor(template.id),
            docx: true,
            xlsx: getTemplateKind(template) === 'excel',
            emailRecipients: emailList.length ? emailList : undefined,
            emailSubject: emailSubject || undefined,
            emailMessage: emailMessage || undefined,
            frequency: scheduleFrequency,
            name: scheduleName || undefined,
          })
          toast.show('Scheduled job created. The first run will begin soon.', 'success')
          refreshSchedules()
        } catch (e) {
          toast.show(String(e), 'error')
          throw e
        } finally {
          setScheduleSaving(false)
        }
      },
    })
  }

  const handleDeleteScheduleRequest = useCallback((schedule) => {
    if (!schedule?.id) return
    setScheduleToDelete(schedule)
    setDeleteScheduleConfirmOpen(true)
  }, [])

  const handleDeleteScheduleConfirm = useCallback(async () => {
    if (!scheduleToDelete?.id) {
      setDeleteScheduleConfirmOpen(false)
      return
    }
    const schedule = scheduleToDelete
    const scheduleId = schedule.id
    const scheduleIndex = schedules.findIndex((item) => item.id === scheduleId)
    setDeleteScheduleConfirmOpen(false)
    setScheduleToDelete(null)

    if (scheduleDeleteUndoRef.current?.timeoutId) {
      clearTimeout(scheduleDeleteUndoRef.current.timeoutId)
      scheduleDeleteUndoRef.current = null
    }

    setSchedules((prev) => prev.filter((item) => item.id !== scheduleId))

    let undone = false
    const timeoutId = setTimeout(async () => {
      if (undone) return
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete schedule',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          scheduleId,
          action: 'delete_schedule',
        },
        action: async () => {
          setDeletingScheduleId(scheduleId)
          try {
            await deleteSchedule(scheduleId)
            toast.show('Schedule removed. Future runs stopped; past downloads remain.', 'success')
            refreshSchedules()
          } catch (e) {
            setSchedules((prev) => {
              if (prev.some((item) => item.id === scheduleId)) return prev
              const next = [...prev]
              if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
                next.splice(scheduleIndex, 0, schedule)
              } else {
                next.push(schedule)
              }
              return next
            })
            toast.show(String(e), 'error')
            throw e
          } finally {
            setDeletingScheduleId(null)
            scheduleDeleteUndoRef.current = null
          }
        },
      })
    }, 5000)

    scheduleDeleteUndoRef.current = { timeoutId, schedule }

    toast.showWithUndo(
      `Schedule "${schedule.name || schedule.template_name || schedule.template_id}" removed`,
      () => {
        undone = true
        clearTimeout(timeoutId)
        scheduleDeleteUndoRef.current = null
        setSchedules((prev) => {
          if (prev.some((item) => item.id === scheduleId)) return prev
          const next = [...prev]
          if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
            next.splice(scheduleIndex, 0, schedule)
          } else {
            next.push(schedule)
          }
          return next
        })
        toast.show('Schedule restored', 'success')
      },
      { severity: 'info' }
    )
  }, [scheduleToDelete, schedules, toast, refreshSchedules, execute])

  const handleOpenEditSchedule = (schedule) => {
    setEditingSchedule(schedule)
    setEditScheduleFields({
      name: schedule.name || '',
      frequency: schedule.frequency || 'daily',
      active: schedule.active !== false,
    })
  }

  const handleCloseEditSchedule = () => {
    setEditingSchedule(null)
    setEditScheduleFields({})
  }

  const handleUpdateSchedule = async () => {
    if (!editingSchedule) return
    await execute({
      type: InteractionType.UPDATE,
      label: 'Update schedule',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        scheduleId: editingSchedule.id,
        action: 'update_schedule',
      },
      action: async () => {
        setScheduleUpdating(true)
        try {
          const payload = {}
          if (editScheduleFields.name !== (editingSchedule.name || '')) {
            payload.name = editScheduleFields.name || null
          }
          if (editScheduleFields.frequency !== (editingSchedule.frequency || 'daily')) {
            payload.frequency = editScheduleFields.frequency
          }
          if (editScheduleFields.active !== (editingSchedule.active !== false)) {
            payload.active = editScheduleFields.active
          }
          if (Object.keys(payload).length === 0) {
            toast.show('No changes to save.', 'info')
            handleCloseEditSchedule()
            return
          }
          await updateSchedule(editingSchedule.id, payload)
          toast.show('Schedule updated.', 'success')
          refreshSchedules()
          handleCloseEditSchedule()
        } catch (e) {
          toast.show(String(e), 'error')
          throw e
        } finally {
          setScheduleUpdating(false)
        }
      },
    })
  }

  const dateRangeValid = !!start && !!end && end.valueOf() >= start.valueOf()
  const hasResults = Object.keys(results).length > 0
  const batchCount = Object.values(results).reduce((acc, r) => acc + (r.batches?.filter(b => b.selected)?.length || 0), 0)

  return (
    <>
      {/* Compact Header with Quick Actions */}
      <Surface sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }} justifyContent="space-between">
          <Stack direction="row" alignItems="center" spacing={1}>
            <Typography variant="h6" fontWeight={600}>Run Reports</Typography>
            <InfoTooltip content={TOOLTIP_COPY.runReports} ariaLabel="Run report guidance" />
          </Stack>

          {/* Quick Status Chips */}
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              size="small"
              icon={<CheckRoundedIcon />}
              label={`${selected.length} design${selected.length !== 1 ? 's' : ''}`}
              variant={selected.length > 0 ? 'filled' : 'outlined'}
              sx={{ bgcolor: selected.length > 0 ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] : undefined, color: 'text.secondary' }}
            />
            <Chip
              size="small"
              icon={<CalendarMonthIcon />}
              label={dateRangeValid ? 'Date set' : 'No date'}
              variant={dateRangeValid ? 'filled' : 'outlined'}
              sx={{ bgcolor: dateRangeValid ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] : undefined, color: 'text.secondary' }}
            />
            {hasResults && (
              <Chip
                size="small"
                icon={<SearchIcon />}
                label={`${batchCount} batch${batchCount !== 1 ? 'es' : ''}`}
                variant="filled"
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            )}
          </Stack>

          {/* Primary Actions */}
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<SearchIcon />}
              onClick={onFind}
              disabled={finding || !selected.length || !dateRangeValid}
            >
              {finding ? 'Finding...' : 'Find Reports'}
            </Button>
            <Button
              variant="contained"
              size="small"
              startIcon={<PlayArrowIcon />}
              onClick={onGenerate}
              disabled={!canGenerate}
            >
              {generateLabel}
            </Button>
          </Stack>
        </Stack>
      </Surface>

      <Box sx={{ mt: 2 }}>
        <ReportGlossaryNotice dense showChips={false} />
      </Box>

      {/* Tabbed Interface */}
      <Surface sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              px: 2,
              '& .MuiTab-root': {
                minHeight: 48,
                textTransform: 'none',
                fontWeight: 600,
              },
            }}
          >
            <Tab
              icon={<Badge badgeContent={selected.length} sx={{ '& .MuiBadge-badge': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white' } }}><CheckRoundedIcon /></Badge>}
              iconPosition="start"
              label="Designs"
            />
            <Tab
              icon={<TuneIcon />}
              iconPosition="start"
              label="Configure"
            />
            <Tab
              icon={<Badge badgeContent={schedules.length || undefined} sx={{ '& .MuiBadge-badge': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'common.white' } }}><ScheduleIcon /></Badge>}
              iconPosition="start"
              label="Schedules"
            />
          </Tabs>
        </Box>

        {/* Tab 0: Designs */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ px: 2, pb: 2 }}>
            <TemplatePicker
              selected={selected}
              onToggle={onToggle}
              outputFormats={outputFormats}
              setOutputFormats={setOutputFormats}
              tagFilter={tagFilter}
              setTagFilter={setTagFilter}
              onEditTemplate={(tpl) => {
                if (!tpl?.id) return
                handleNavigate(`/templates/${tpl.id}/edit`, 'Edit template', {
                  templateId: tpl.id,
                  from: '/',
                })
              }}
            />
          </Box>
        </TabPanel>

        {/* Tab 1: Configure */}
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ px: 2, pb: 2 }}>
            <Stack spacing={2}>
              <Alert severity="info" sx={{ borderRadius: 1 }}>
                Runs start as background jobs. Track progress in Jobs, and download outputs from History.
              </Alert>
              {queuedJobs.length > 0 && (
                <Alert
                  severity="info"
                  action={(
                    <Button
                      size="small"
                      onClick={() => handleNavigate('/jobs', 'Open jobs')}
                      sx={{ textTransform: 'none' }}
                    >
                      View Jobs
                    </Button>
                  )}
                >
                  Reports queued in background.
                  {queuedJobIds.length > 0 ? ` Job IDs: ${queuedJobIds.slice(0, 3).join(', ')}` : ' Track progress in Jobs.'}
                </Alert>
              )}
              <GenerateAndDownload
                selected={selected}
                selectedTemplates={selectedTemplates}
                autoType={autoType}
                start={start}
                end={end}
                setStart={setStart}
                setEnd={setEnd}
                onFind={onFind}
                findDisabled={finding}
                finding={finding}
                results={results}
                onToggleBatch={onToggleBatch}
                onGenerate={onGenerate}
                canGenerate={canGenerate}
                generateLabel={generateLabel}
                generation={generation}
                generatorReady
                generatorIssues={{ missing: [], needsFix: [], messages: [] }}
                keyValues={keyValues}
                onKeyValueChange={handleKeyValueChange}
                keysReady={keysReady}
                keyOptions={keyOptions}
                keyOptionsLoading={keyOptionsLoading}
                onResampleFilter={handleResampleFilter}
              />

              {/* Delivery Options - Collapsed by default */}
              <CollapsibleSection
                title="Email Delivery"
                icon={<ScheduleIcon fontSize="small" color="action" />}
                badge={emailTargets ? 'Configured' : null}
              >
                <Stack spacing={2}>
                  <TextField
                    label="Email recipients"
                    placeholder="ops@example.com, finance@example.com"
                    value={emailTargets}
                    onChange={(e) => setEmailTargets(e.target.value)}
                    helperText="Comma or semicolon separated list"
                    size="small"
                    fullWidth
                  />
                  <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
                    <TextField
                      label="Email subject"
                      value={emailSubject}
                      onChange={(e) => setEmailSubject(e.target.value)}
                      size="small"
                      fullWidth
                    />
                  </Stack>
                  <TextField
                    label="Email message (optional)"
                    value={emailMessage}
                    onChange={(e) => setEmailMessage(e.target.value)}
                    multiline
                    minRows={2}
                    size="small"
                  />
                </Stack>
              </CollapsibleSection>
            </Stack>
          </Box>
        </TabPanel>

        {/* Tab 2: Schedules */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ px: 2, pb: 2 }}>
            <Stack spacing={2}>
              <Alert severity="info" sx={{ borderRadius: 1 }}>
                Schedules create future report runs. Deleting a schedule stops future runs and does not remove past downloads.
              </Alert>
              {/* Create Schedule */}
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Create New Schedule
                </Typography>
                <Stack spacing={2}>
                  <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems={{ md: 'flex-end' }}>
                    <TextField
                      label="Schedule name (optional)"
                      value={scheduleName}
                      onChange={(e) => setScheduleName(e.target.value)}
                      size="small"
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      select
                      label="Frequency"
                      value={scheduleFrequency}
                      onChange={(e) => setScheduleFrequency(e.target.value)}
                      size="small"
                      sx={{ minWidth: 150 }}
                    >
                      {SCHEDULE_FREQUENCY_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </TextField>
                    <Button
                      variant="contained"
                      onClick={handleCreateSchedule}
                      disabled={!canSchedule || scheduleSaving}
                      sx={{ whiteSpace: 'nowrap', bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
                    >
                      {scheduleSaving ? 'Creating...' : 'Create Schedule'}
                    </Button>
                  </Stack>
                  {!canSchedule && (
                    <Typography variant="caption" color="text.secondary">
                      Select exactly one design, set a date range, and connect to a database to create a schedule.
                    </Typography>
                  )}
                </Stack>
              </Paper>

              {/* Existing Schedules */}
              <Box>
                <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
                  <Typography variant="subtitle2" fontWeight={600}>Existing Schedules</Typography>
                  {schedulesLoading && <LinearProgress sx={{ flex: 1, height: 4, borderRadius: 2 }} />}
                </Stack>

                {!schedulesLoading && schedules.length === 0 && (
                  <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                      No schedules yet. Create one above.
                    </Typography>
                  </Paper>
                )}

                {!schedulesLoading && schedules.length > 0 && (
                  <Stack spacing={1}>
                    {schedules.map((schedule) => (
                      <Paper
                        key={schedule.id}
                        variant="outlined"
                        sx={{ p: 1.5, borderRadius: 1.5 }}
                      >
                        <Stack direction={{ xs: 'column', md: 'row' }} alignItems={{ md: 'center' }} spacing={1.5} justifyContent="space-between">
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Stack direction="row" alignItems="center" spacing={1}>
                              <Typography variant="subtitle2" noWrap>
                                {schedule.name || schedule.template_name || schedule.template_id}
                              </Typography>
                              {schedule.active === false && (
                                <Chip size="small" label="Paused" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                              )}
                            </Stack>
                            <Typography variant="caption" color="text.secondary">
                              {schedule.frequency || 'custom'} • Next: {formatScheduleDate(schedule.next_run_at)}
                            </Typography>
                          </Box>
                          <Stack direction="row" spacing={1}>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleOpenEditSchedule(schedule)}
                            >
                              Edit
                            </Button>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleDeleteScheduleRequest(schedule)}
                              disabled={deletingScheduleId === schedule.id}
                              sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3) }}
                            >
                              {deletingScheduleId === schedule.id ? '...' : 'Delete'}
                            </Button>
                          </Stack>
                        </Stack>
                      </Paper>
                    ))}
                  </Stack>
                )}
              </Box>
            </Stack>
          </Box>
        </TabPanel>
      </Surface>

      {/* Edit Schedule Dialog */}
      <Dialog open={Boolean(editingSchedule)} onClose={handleCloseEditSchedule} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Schedule</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Schedule name"
              value={editScheduleFields.name || ''}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
              size="small"
            />
            <TextField
              select
              label="Frequency"
              value={editScheduleFields.frequency || 'daily'}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, frequency: e.target.value }))}
              fullWidth
              size="small"
            >
              {SCHEDULE_FREQUENCY_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={editScheduleFields.active !== false ? 'active' : 'paused'}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, active: e.target.value === 'active' }))}
              fullWidth
              size="small"
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="paused">Paused</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditSchedule} disabled={scheduleUpdating}>
            Cancel
          </Button>
          <Button onClick={handleUpdateSchedule} variant="contained" disabled={scheduleUpdating}>
            {scheduleUpdating ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={deleteScheduleConfirmOpen}
        onClose={() => {
          setDeleteScheduleConfirmOpen(false)
          setScheduleToDelete(null)
        }}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Delete Schedule</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Delete "{scheduleToDelete?.name || scheduleToDelete?.template_name || scheduleToDelete?.template_id}"?
            You can undo within a few seconds. This stops future runs; past downloads remain in History.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDeleteScheduleConfirmOpen(false)
              setScheduleToDelete(null)
            }}
            disabled={Boolean(deletingScheduleId)}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleDeleteScheduleConfirm}
            disabled={Boolean(deletingScheduleId)}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

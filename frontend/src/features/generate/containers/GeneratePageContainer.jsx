import Grid from '@mui/material/Grid2'
import { Box, Typography, Stack, Chip, Alert, Button, alpha, Autocomplete, TextField } from '@mui/material'
import { neutral, palette } from '@/app/theme'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import PaletteIcon from '@mui/icons-material/Palette'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useNavigateInteraction } from '@/components/ux/governance'
import { useQueryClient } from '@tanstack/react-query'

import { useAppStore } from '@/stores'
import useDesignStore from '@/stores/designStore'
import { useToast } from '@/components/ToastProvider.jsx'
import TemplatePicker from '../components/TemplatePicker.jsx'
import GenerateAndDownload from '../components/GenerateAndDownload.jsx'
import {
  discoverReports,
  fetchTemplateKeyOptions,
  runReportAsJob,
} from '../services/generateApi'
import {
  DEFAULT_RESAMPLE_CONFIG,
  getTemplateKind,
  toSqlDateTime,
} from '../utils/generateFeatureUtils'

export default function GeneratePage() {
  const templates = useAppStore((state) => state.templates)
  const queryClient = useQueryClient()
  const toast = useToast()
  const location = useLocation()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}, navigateOptions) =>
      navigate(path, { label, intent: { from: 'generate', ...intent }, navigateOptions }),
    [navigate]
  )
  const approved = useMemo(() => templates.filter((t) => t.status === 'approved'), [templates])
  const [selected, setSelected] = useState([])
  const [pendingFocusTemplate, setPendingFocusTemplate] = useState(location.state?.focusTemplateId || null)
  const [outputFormats, setOutputFormats] = useState({})
  const [tagFilter, setTagFilter] = useState([])
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [finding, setFinding] = useState(false)
  const [results, setResults] = useState({})
  const [generation, setGeneration] = useState({ items: [] })
  const [keyValues, setKeyValues] = useState({})
  const [keyOptions, setKeyOptions] = useState({})
  const [keyOptionsLoading, setKeyOptionsLoading] = useState({})
  const [selectedBrandKit, setSelectedBrandKit] = useState(null)
  const { brandKits, fetchBrandKits } = useDesignStore()
  const isDevEnv = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV)

  useEffect(() => {
    if (!isDevEnv || typeof window === 'undefined') return
    window.__NR_GENERATE_KEY_OPTIONS__ = keyOptions
    window.__NR_GENERATE_KEY_VALUES__ = keyValues
  }, [keyOptions, keyValues, isDevEnv])

  useEffect(() => {
    fetchBrandKits().then((kits) => {
      if (!selectedBrandKit && kits?.length) {
        const defaultKit = kits.find((k) => k.is_default)
        if (defaultKit) setSelectedBrandKit(defaultKit)
      }
    })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { setResults({}); setFinding(false) }, [selected, start, end, keyValues])

  const selectedTemplates = useMemo(
    () => approved.filter((t) => selected.includes(t.id)),
    [approved, selected],
  )
  const locationState = location.state
  const focusTemplateIdFromLocation = locationState?.focusTemplateId

  useEffect(() => {
    if (!focusTemplateIdFromLocation) return
    setPendingFocusTemplate(focusTemplateIdFromLocation)
    const nextState = { ...(locationState || {}) }
    delete nextState.focusTemplateId
    handleNavigate(
      location.pathname + location.search,
      'Sync generate route',
      { reason: 'focus-template' },
      { replace: true, state: Object.keys(nextState).length ? nextState : null }
    )
  }, [focusTemplateIdFromLocation, location.pathname, location.search, locationState, handleNavigate])

  useEffect(() => {
    if (!pendingFocusTemplate) return
    const exists = approved.some((tpl) => tpl.id === pendingFocusTemplate)
    if (!exists) return
    setSelected((prev) => (prev.includes(pendingFocusTemplate) ? prev : [...prev, pendingFocusTemplate]))
    setPendingFocusTemplate(null)
  }, [approved, pendingFocusTemplate])

  useEffect(() => {
    setKeyOptions((prev) => {
      const next = {}
      selectedTemplates.forEach((tpl) => {
        if (prev[tpl.id]) {
          next[tpl.id] = prev[tpl.id]
        }
      })
      const prevKeys = Object.keys(prev)
      const nextKeys = Object.keys(next)
      if (prevKeys.length === nextKeys.length && prevKeys.every((key) => prev[key] === next[key])) {
        return prev
      }
      return next
    })
    setKeyOptionsLoading((prev) => {
      const next = {}
      selectedTemplates.forEach((tpl) => {
        if (prev[tpl.id]) {
          next[tpl.id] = prev[tpl.id]
        }
      })
      if (Object.keys(prev).length === Object.keys(next).length) {
        return prev
      }
      return next
    })
  }, [selectedTemplates])
  const generatorSummary = useMemo(() => {
    const missing = selectedTemplates.filter(
      (t) =>
        !t.artifacts?.generator_sql_pack_url ||
        !t.artifacts?.generator_output_schemas_url,
    )
    const needsFix = selectedTemplates.filter((t) => {
      const meta = t.generator || {}
      const issues = Array.isArray(meta.needsUserFix) ? meta.needsUserFix.length : 0
      return meta.invalid || issues > 0
    })
    return {
      missing,
      needsFix,
      messages: needsFix.flatMap((tpl) => tpl.generator?.needsUserFix || []),
      ready: selectedTemplates.length > 0 && missing.length === 0 && needsFix.length === 0,
    }
  }, [selectedTemplates])

  const getTemplateKeyTokens = useCallback(
    (tpl) => {
      const fromState = Array.isArray(tpl?.mappingKeys)
        ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
        : []
      if (fromState.length) return fromState
      const options = keyOptions?.[tpl?.id] || {}
      return Object.keys(options || {})
    },
    [keyOptions],
  )

  useEffect(() => {
    let cancelled = false
    selectedTemplates.forEach((tpl) => {
      const stateTokens = Array.isArray(tpl?.mappingKeys)
        ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
        : []
      const existing = keyOptions[tpl.id] || {}
      const existingTokenKeys = Object.keys(existing)
      let requestTokens
      let shouldFetch = false

      if (stateTokens.length) {
        const missing = stateTokens.filter((token) => !(token in existing))
        if (missing.length || !existingTokenKeys.length) {
          shouldFetch = true
          requestTokens = stateTokens
        }
      } else if (!existingTokenKeys.length) {
        shouldFetch = true
        requestTokens = undefined
      }

      if (!shouldFetch || keyOptionsLoading[tpl.id]) {
        return
      }

      setKeyOptionsLoading((prev) => ({ ...prev, [tpl.id]: true }))
      fetchTemplateKeyOptions(tpl.id, {
        connectionId: tpl.lastConnectionId,
        tokens: requestTokens,
        limit: 100,
        startDate: start,
        endDate: end,
        kind: tpl.kind || 'pdf',
      })
        .then((data) => {
          if (cancelled) return
          const incoming = data?.keys && typeof data.keys === 'object' ? data.keys : {}
          if (typeof window !== 'undefined' && typeof window.__nrLogKeyOptions === 'function') {
            try {
              window.__nrLogKeyOptions({
                templateId: tpl.id,
                connectionId: tpl.lastConnectionId || null,
                tokens: requestTokens,
                payload: incoming,
              })
            } catch (err) {
              console.warn('nr_key_options_log_failed', err)
            }
          }
          setKeyOptions((prev) => {
            const prevTemplateOptions = prev[tpl.id] || {}
            const merged = { ...prevTemplateOptions }
            let changed = false
            const sourceTokens = requestTokens ?? Object.keys(incoming)
            sourceTokens.forEach((token) => {
              const values = Array.isArray(incoming[token]) ? incoming[token] : []
              if (!Array.isArray(prevTemplateOptions[token]) || values.join('|') !== (prevTemplateOptions[token] || []).join('|')) {
                merged[token] = values
                if (values.length || !(token in prevTemplateOptions)) {
                  changed = true
                }
              }
            })
            if (!changed && prev[tpl.id]) {
              return prev
            }
            return { ...prev, [tpl.id]: merged }
          })
        })
        .catch((err) => {
          if (cancelled) return
          console.warn('key_options_fetch_failed', err)
          toast.show(`Failed to load key options for ${tpl.name || tpl.id}`, 'error')
        })
        .finally(() => {
          if (cancelled) return
          setKeyOptionsLoading((prev) => ({ ...prev, [tpl.id]: false }))
        })
    })

    return () => {
      cancelled = true
    }
  }, [selectedTemplates, keyOptions, keyOptionsLoading, toast])

  const collectMissingKeys = () => {
    const missing = []
    selectedTemplates.forEach((tpl) => {
      const required = getTemplateKeyTokens(tpl)
      if (!required.length) return
      const provided = keyValues[tpl.id] || {}
      const absent = required.filter((token) => {
        const raw = provided[token]
        if (Array.isArray(raw)) {
          return !raw.some((entry) => String(entry || '').trim())
        }
        return !raw || !String(raw).trim()
      })
      if (absent.length) {
        missing.push({ tpl, tokens: absent })
      }
    })
    return missing
  }

  const autoType = useMemo(() => {
    if (!selected.length) return '-'
    const types = selectedTemplates.map((t) => getTemplateKind(t).toUpperCase())
    return types.every((t) => t === types[0]) ? types[0] : 'Mixed'
  }, [selected, selectedTemplates])

  const keysReady = useMemo(() => {
    return selectedTemplates.every((tpl) => {
      const required = getTemplateKeyTokens(tpl)
      if (!required.length) return true
      const provided = keyValues[tpl.id] || {}
      return required.every((token) => {
        const raw = provided[token]
        if (Array.isArray(raw)) {
          return raw.some((entry) => String(entry || '').trim())
        }
        return !!raw && String(raw).trim().length > 0
      })
    })
  }, [selectedTemplates, keyValues, getTemplateKeyTokens])

  const onToggle = (id) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))

  const handleKeyValueChange = (templateId, token, values) => {
    setKeyValues((prev) => {
      const next = { ...prev }
      const existing = { ...(next[templateId] || {}) }
      const asArray = Array.isArray(values) ? values : [values]
      const seen = new Set()
      const normalized = []
      asArray.forEach((entry) => {
        const text = entry == null ? '' : String(entry).trim()
        if (!text || seen.has(text)) return
        seen.add(text)
        normalized.push(text)
      })
      if (normalized.length) {
        existing[token] = normalized
        next[templateId] = existing
      } else {
        delete existing[token]
        if (Object.keys(existing).length === 0) {
          delete next[templateId]
        } else {
          next[templateId] = existing
        }
      }
      return next
    })
  }

  const onFind = async () => {
    if (!selectedTemplates.length || !start || !end) return toast.show('Select a template and choose a start/end date.', 'warning')
    if (generatorSummary.missing.length) {
      return toast.show('Generate SQL & schema assets for all selected templates before discovering reports.', 'warning')
    }
    if (generatorSummary.needsFix.length) {
      const detail = generatorSummary.messages.length ? generatorSummary.messages.join(', ') : 'Resolve SQL & schema asset issues before discovery.'
      return toast.show(detail, 'warning')
    }
    const missingKeyEntries = collectMissingKeys()
    if (missingKeyEntries.length) {
      const message = missingKeyEntries.map(({ tpl, tokens }) => `${tpl.name || tpl.id}: ${tokens.join(', ')}`).join('; ')
      toast.show(`Provide values for key tokens before discovery (${message}).`, 'warning')
      return
    }

    const startSql = toSqlDateTime(start)
    const endSql = toSqlDateTime(end)
    if (!startSql || !endSql) {
      toast.show('Provide a valid start and end date.', 'warning')
      return
    }

    setFinding(true)
    try {
      const payload = {}
      const targets = selectedTemplates
      for (const t of targets) {
        const data = await discoverReports({
          templateId: t.id,
          startDate: startSql,
          endDate: endSql,
          keyValues: keyValues[t.id],
          kind: getTemplateKind(t),
        })
        const rawBatches = Array.isArray(data.batches) ? data.batches : []
        const normalizedBatches = rawBatches.map((batch, index) => {
          const batchId = Object.prototype.hasOwnProperty.call(batch, 'id') ? batch.id : `${index + 1}`
          const rows = Number(batch.rows || 0)
          const parent = Number(batch.parent || 0)
          return {
            ...batch,
            id: batchId,
            rows,
            parent,
            selected: batch.selected ?? true,
            time: batch.time ?? null,
            category: batch.category ?? null,
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
        const rawMetrics = Array.isArray(data.batch_metrics) ? data.batch_metrics : null
        const batchMetricsSource = rawMetrics && rawMetrics.length ? rawMetrics : normalizedBatches
        const batchMetrics = batchMetricsSource.map((entry, index) => {
          const base = normalizedBatches[index] || {}
          const rows = Number(entry?.rows ?? base.rows ?? 0)
          const parent = Number(entry?.parent ?? base.parent ?? 0)
          const safeParent = parent || (base.parent || 0)
          return {
            batch_index: entry?.batch_index ?? index + 1,
            batch_id: entry?.batch_id ?? base.id ?? `${index + 1}`,
            rows,
            parent,
            rows_per_parent:
              entry?.rows_per_parent ??
              (safeParent ? rows / safeParent : rows),
            time: entry?.time ?? base.time ?? null,
            category: entry?.category ?? base.category ?? null,
          }
        })
        payload[t.id] = {
          name: t.name,
          batches: normalizedBatches,
          allBatches: normalizedBatches,
          batches_count: data.batches_count ?? normalizedBatches.length,
          rows_total:
            data.rows_total ??
            normalizedBatches.reduce((acc, batch) => acc + (batch.rows || 0), 0),
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
      setResults(payload)
    } catch (error) {
      toast.show(String(error), 'error')
    } finally {
      setFinding(false)
    }
  }

  const onToggleBatch = (id, idx, val) => {
    setResults((prev) => {
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
    setResults((prev) => {
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
  }, [])

  const canGenerate = useMemo(() => {
    const hasBatches = Object.values(results).some((r) => r.batches?.some((b) => b.selected))
    const datesReady = !!start && !!end && new Date(end) >= new Date(start)
    return hasBatches && datesReady && keysReady && generatorSummary.missing.length === 0 && generatorSummary.needsFix.length === 0
  }, [results, start, end, keysReady, generatorSummary.missing.length, generatorSummary.needsFix.length])

  const generateLabel = useMemo(() => {
    const names = selectedTemplates.map((t) => t.name).filter(Boolean)
    if (!names.length) return 'Run Reports'
    const preview = names.slice(0, 2).join(', ')
    const extra = names.length > 2 ? ` +${names.length - 2} more` : ''
    return `Run reports for ${preview}${extra}`
  }, [selectedTemplates])

  const batchIdsFor = (tplId) => (results[tplId]?.batches || []).filter((b) => b.selected).map((b) => b.id)

  const onGenerate = async () => {
    if (!selectedTemplates.length) return
    if (!start || !end) {
      toast.show('Select a start and end date before running.', 'warning')
      return
    }
    const startSql = toSqlDateTime(start)
    const endSql = toSqlDateTime(end)
    if (!startSql || !endSql) {
      toast.show('Provide a valid date range.', 'warning')
      return
    }
    if (generatorSummary.missing.length) {
      return toast.show('Generate SQL & schema assets for all selected templates before generating reports.', 'warning')
    }
    if (generatorSummary.needsFix.length) {
      const detail = generatorSummary.messages.length ? generatorSummary.messages.join(', ') : 'Resolve SQL & schema asset issues before generating reports.'
      return toast.show(detail, 'warning')
    }
    const missingKeyEntries = collectMissingKeys()
    if (missingKeyEntries.length) {
      const message = missingKeyEntries.map(({ tpl, tokens }) => `${tpl.name || tpl.id}: ${tokens.join(', ')}`).join('; ')
      toast.show(`Provide values for key tokens before running (${message}).`, 'warning')
      return
    }

    const timestamp = Date.now()
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

    let queuedJobs = 0

    for (const item of seed) {
      try {
        const rawFormat = outputFormats[item.tplId] || 'auto'
        const normalizedFormat = rawFormat === 'excel' ? 'xlsx' : rawFormat
        const requestDocx = normalizedFormat === 'docx' || normalizedFormat === 'auto'
        const requestXlsx = normalizedFormat === 'xlsx' || (normalizedFormat === 'auto' && item.kind === 'excel')
        const response = await runReportAsJob({
          templateId: item.tplId,
          templateName: item.name,
          startDate: startSql,
          endDate: endSql,
          batchIds: batchIdsFor(item.tplId),
          keyValues: keyValues[item.tplId],
          brandKitId: selectedBrandKit?.id || undefined,
          docx: requestDocx,
          xlsx: requestXlsx,
          kind: item.kind,
        })
        const jobId = response?.job_id || null
        setGeneration((prev) => ({
          items: prev.items.map((x) =>
            x.id === item.id
              ? {
                  ...x,
                  jobId,
                  status: 'queued',
                  progress: jobId ? 15 : 10,
                  error: null,
                }
              : x,
          ),
        }))
        queuedJobs += 1
        queryClient.invalidateQueries({ queryKey: ['jobs'] })
      } catch (error) {
        const message = error?.message || String(error)
        setGeneration((prev) => ({
          items: prev.items.map((x) =>
            x.id === item.id
              ? {
                  ...x,
                  status: 'failed',
                  progress: 100,
                  error: message,
                }
              : x,
          ),
        }))
        toast.show(String(error), 'error')
      }
    }

    if (queuedJobs > 0) {
      toast.show('Reports are running in the background. Open the Jobs panel to monitor progress.', 'success')
    }
  }

  const hasConnection = useAppStore((state) => !!state.activeConnection?.connection_id)

  return (
    <Box sx={{ py: 3, px: 3 }}>
      {/* Page Header */}
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Generate Reports
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select templates, configure parameters, and generate reports from your data.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          {selected.length > 0 && (
            <Chip
              size="small"
              label={`${selected.length} selected`}
              sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
            />
          )}
          <Chip
            size="small"
            label={`${approved.length} available`}
            variant="outlined"
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        </Stack>
      </Stack>

      <Stack spacing={3}>

        {/* Connection Warning */}
        {!hasConnection && (
          <Alert
            severity="warning"
            action={
              <Button color="inherit" size="small" onClick={() => handleNavigate('/', 'Open dashboard')}>
                Go to Setup
              </Button>
            }
          >
            Connect to a database in Setup to generate reports with real data.
          </Alert>
        )}

        {/* Main Content */}
        <Grid container spacing={3}>
          <Grid size={12}>
            <TemplatePicker
              selected={selected}
              onToggle={onToggle}
              outputFormats={outputFormats}
              setOutputFormats={setOutputFormats}
              tagFilter={tagFilter}
              setTagFilter={setTagFilter}
              onEditTemplate={(tpl) => {
                if (!tpl?.id) return
                handleNavigate(
                  `/templates/${tpl.id}/edit`,
                  'Edit template',
                  { templateId: tpl.id },
                  { state: { from: '/generate' } }
                )
              }}
            />
          </Grid>
          {/* Brand Kit selector */}
          {brandKits.length > 0 && (
            <Grid size={12}>
              <Autocomplete
                size="small"
                options={brandKits}
                value={selectedBrandKit}
                onChange={(_, kit) => setSelectedBrandKit(kit)}
                getOptionLabel={(kit) => kit.name || ''}
                isOptionEqualToValue={(opt, val) => opt?.id === val?.id}
                renderOption={(props, kit) => (
                  <li {...props} key={kit.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 14, height: 14, borderRadius: '50%', bgcolor: kit.primary_color, border: '1px solid rgba(0,0,0,0.15)', flexShrink: 0 }} />
                      <Typography variant="body2">{kit.name}</Typography>
                      {kit.is_default && <Chip label="default" size="small" variant="outlined" sx={{ ml: 'auto', height: 18, fontSize: 11 }} />}
                    </Box>
                  </li>
                )}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Brand Kit"
                    placeholder="Select brand kit for report styling"
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: (
                        <>
                          <PaletteIcon fontSize="small" sx={{ color: 'text.secondary', mr: 0.5 }} />
                          {params.InputProps.startAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                sx={{ maxWidth: 360 }}
              />
            </Grid>
          )}

          <Grid size={12} sx={{ minWidth: 0 }}>
            <GenerateAndDownload
              selected={selectedTemplates.map((t) => t.id)}
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
              generatorReady={generatorSummary.ready}
              generatorIssues={generatorSummary}
              keyValues={keyValues}
              onKeyValueChange={handleKeyValueChange}
              keysReady={keysReady}
              keyOptions={keyOptions}
              keyOptionsLoading={keyOptionsLoading}
              onResampleFilter={handleResampleFilter}
            />
          </Grid>
        </Grid>
      </Stack>
    </Box>
  )
}

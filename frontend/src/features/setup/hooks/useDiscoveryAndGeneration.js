import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { InteractionType, Reversibility } from '@/components/ux/governance'
import { discoverReports, runReportAsJob } from '@/api/client'
import { DEFAULT_RESAMPLE_CONFIG } from '@/features/generate/utils/generateFeatureUtils'
import {
  parseEmailTargets,
  toSqlFromDayjs,
  formatDisplayDate,
  getTemplateKind,
} from '../utils/templatesPaneUtils'

export function useDiscoveryAndGeneration({
  selectedTemplates,
  selected,
  start,
  end,
  activeConnectionId,
  activeConnection,
  autoType,
  finding,
  setFinding,
  results,
  setDiscoveryResults,
  clearDiscoveryResults,
  toast,
  execute,
  buildKeyFiltersForTemplate,
  requestKeyOptions,
  keysReady,
  collectMissingKeys,
  keyOptionsFetchKeyRef,
  emailTargets,
  emailSubject,
  emailMessage,
}) {
  const discoveryResetReady = useRef(false)
  const [generation, setGeneration] = useState({ items: [] })

  const queuedJobs = useMemo(
    () => generation.items.filter((item) => item.status === 'queued'),
    [generation.items],
  )
  const queuedJobIds = useMemo(
    () => queuedJobs.map((item) => item.jobId).filter(Boolean),
    [queuedJobs],
  )

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

    keyOptionsFetchKeyRef.current = {}
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

  return {
    generation,
    queuedJobs,
    queuedJobIds,
    onFind,
    onToggleBatch,
    handleResampleFilter,
    canGenerate,
    canSchedule,
    generateLabel,
    batchIdsFor,
    onGenerate,
  }
}

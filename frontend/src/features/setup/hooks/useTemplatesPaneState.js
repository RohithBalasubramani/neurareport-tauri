import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useInteraction, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { fetchTemplateKeyOptions } from '@/api/client'
import {
  ALL_OPTION,
  toSqlFromDayjs,
  formatTokenLabel,
  getTemplateKind,
} from '../utils/templatesPaneUtils'

export function useTemplatesPaneState() {
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

  const [start, setStart] = useState(null)
  const [end, setEnd] = useState(null)
  const [emailTargets, setEmailTargets] = useState('')
  const [emailSubject, setEmailSubject] = useState('')
  const [emailMessage, setEmailMessage] = useState('')

  return {
    templates,
    activeConnectionId,
    activeConnection,
    finding,
    setFinding,
    results,
    discoveryMeta,
    setDiscoveryResults,
    clearDiscoveryResults,
    toast,
    execute,
    handleNavigate,
    activeTab,
    handleTabChange,
    approved,
    selected,
    setSelected,
    tagFilter,
    setTagFilter,
    outputFormats,
    setOutputFormats,
    onToggle,
    selectedTemplates,
    autoType,
    start,
    setStart,
    end,
    setEnd,
    emailTargets,
    setEmailTargets,
    emailSubject,
    setEmailSubject,
    emailMessage,
    setEmailMessage,
  }
}

export function useKeyOptions({
  selectedTemplates,
  activeConnectionId,
  discoveryMeta,
  toast,
  start,
  end,
  keyOptions,
  setKeyOptions,
  keyValues,
  setKeyValues,
  keyOptionsLoading,
  setKeyOptionsLoading,
}) {
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
  }, [selectedTemplates, setKeyValues])

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
  }, [selectedTemplates, setKeyOptions, setKeyOptionsLoading])

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
    [activeConnectionId, discoveryMeta, toast, setKeyOptions, setKeyOptionsLoading],
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
  }, [setKeyValues])

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
          return
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

  return {
    keyValues,
    keyOptions,
    keyOptionsLoading,
    keysReady,
    getTemplateKeyTokens,
    requestKeyOptions,
    collectMissingKeys,
    handleKeyValueChange,
    buildKeyFiltersForTemplate,
    keyOptionsFetchKeyRef,
  }
}

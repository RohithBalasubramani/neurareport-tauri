import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import {
  isMock,
  deleteConnection as apiDeleteConnection,
  healthcheckConnection as apiHealthcheckConnection,
} from '@/api/client'
import * as mock from '@/api/mock'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import {
  sanitizeDbType,
  formatHostPort,
  deriveSqliteUrl,
  payloadFromNormalized,
  computeCurrentSignature,
  DEFAULT_FORM_VALUES,
} from '../constants/connectDB'

export function useConnectionList({
  setCanSave,
  setLastLatencyMs,
  reset,
}) {
  const {
    connection,
    setConnection,
    savedConnections,
    addSavedConnection,
    updateSavedConnection,
    removeSavedConnection,
    activeConnectionId,
    setActiveConnectionId,
  } = useAppStore()

  const toast = useToast()
  const { execute } = useInteraction()

  const [confirmSelect, setConfirmSelect] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [detailId, setDetailId] = useState(null)
  const [detailAnchor, setDetailAnchor] = useState(null)
  const [rowHeartbeat, setRowHeartbeat] = useState({})
  const [editingId, setEditingId] = useState(null)
  const [showDetails, setShowDetails] = useState(false)

  const deleteUndoRef = useRef(null)
  const listRef = useRef(null)
  const panelRef = useRef(null)

  const detailConnection = useMemo(
    () => savedConnections.find((c) => c.id === detailId) || null,
    [savedConnections, detailId],
  )
  const detailHeartbeat = detailConnection ? rowHeartbeat[detailConnection.id] : null
  const detailStatus = detailConnection
    ? (detailHeartbeat?.status || (detailConnection.status === 'connected' ? 'healthy' : (detailConnection.status === 'failed' ? 'unreachable' : 'unknown')))
    : 'unknown'
  const detailLatency = detailConnection
    ? (detailHeartbeat?.latencyMs != null
      ? detailHeartbeat.latencyMs
      : detailConnection.lastLatencyMs != null
      ? detailConnection.lastLatencyMs
      : undefined)
    : undefined
  const detailNote = detailConnection ? (detailConnection.details || detailConnection.lastMessage || 'No recent notes') : 'No recent notes'

  useEffect(() => {
    if (!savedConnections.length) {
      if (detailId !== null) setDetailId(null)
      return
    }
    if (detailId == null) return
    const hasSelection = savedConnections.some((c) => c.id === detailId)
    if (!hasSelection) setDetailId(null)
  }, [savedConnections, detailId])

  useLayoutEffect(() => {
    if (typeof window === 'undefined') return undefined
    if (!detailConnection || !listRef.current) {
      setDetailAnchor(null)
      return undefined
    }

    const updatePosition = () => {
      const el = listRef.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0
      const maxViewportWidth = Math.max(320, viewportWidth - 32)
      const clampedWidth = Math.max(480, Math.min(640, rect.width))
      const width = Math.min(clampedWidth, maxViewportWidth)
      const panelEl = panelRef.current
      const measuredHeight = panelEl ? Math.min(panelEl.offsetHeight, viewportHeight - 96) : 0
      const fallbackHeight = Math.min(rect.height + 260, viewportHeight - 96)
      const height = measuredHeight || fallbackHeight
      const maxTop = Math.max(viewportHeight - height - 16, 16)
      const top = Math.min(Math.max(rect.top, 16), maxTop)
      const left = Math.min(Math.max(rect.left, 16), Math.max(viewportWidth - width - 16, 16))
      setDetailAnchor((prev) => {
        if (prev && prev.top === top && prev.left === left && prev.width === width) return prev
        return { top, left, width }
      })
    }

    updatePosition()
    const raf = window.requestAnimationFrame(updatePosition)
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)
    return () => {
      window.cancelAnimationFrame(raf)
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition, true)
    }
  }, [detailConnection, detailId, savedConnections.length])

  const applySelection = useCallback((record) => {
    if (!record) return
    const targetId = record.backend_connection_id || record.id
    setActiveConnectionId(targetId)
    const fallbackUrl =
      record.db_url ||
      (sanitizeDbType(record.db_type) === 'sqlite'
        ? deriveSqliteUrl(record.databasePath || record.database || record.summary || '')
        : null)
    setConnection({
      saved: true,
      name: record.name,
      status: record.status,
      db_url: fallbackUrl || null,
      latencyMs: record.lastLatencyMs ?? null,
      lastMessage: record.details || record.status,
      details: record.details || record.status,
      connectionId: targetId,
      db_type: record.db_type,
      host: record.host ?? null,
      port: record.port ?? null,
      database: record.database ?? (sanitizeDbType(record.db_type) === 'sqlite' ? record.databasePath : null),
      driver: record.driver ?? null,
      ssl: record.ssl ?? false,
    })
    setDetailId(null)
    toast.show('Connection selected', 'success')
  }, [setActiveConnectionId, setConnection, toast])

  const requestSelect = useCallback((record) => {
    if (!record) return
    const targetId = record.backend_connection_id || record.id
    if (activeConnectionId && activeConnectionId !== targetId) {
      setConfirmSelect(record.id)
    } else {
      applySelection(record)
    }
  }, [activeConnectionId, applySelection])

  const beginEditConnection = useCallback((record) => {
    if (!record) return
    setEditingId(record.id)
    const typeKey = sanitizeDbType(record.db_type || 'sqlite')
    const databaseValue =
      typeKey === 'sqlite'
        ? record.databasePath || record.database || record.summary || ''
        : record.database || ''
    const hostValue = typeKey === 'sqlite' ? '' : (record.host || '')
    const portValue =
      typeKey === 'sqlite'
        ? ''
        : record.port != null && record.port !== ''
          ? String(record.port)
          : ''
    reset({
      name: record.name || '',
      db_type: typeKey || 'sqlite',
      host: hostValue,
      port: portValue,
      db_name: databaseValue,
      username: '',
      password: '',
      ssl: Boolean(record.ssl),
    })
    setCanSave(false)
    setDetailId(null)
    setShowDetails(false)
    const normalizedUrl =
      record.db_url ||
      (sanitizeDbType(record.db_type) === 'sqlite'
        ? deriveSqliteUrl(record.databasePath || record.database || record.summary || '')
        : null)
    setConnection((prev) => ({
      ...prev,
      saved: true,
      status: record.status || prev.status || 'connected',
      name: record.name || prev.name || record.displayName || '',
      db_url: normalizedUrl,
      latencyMs: record.lastLatencyMs ?? prev.latencyMs ?? null,
      lastMessage: record.details || prev.lastMessage || '',
      details: record.details || prev.details || '',
      connectionId: record.backend_connection_id || prev.connectionId || record.id || null,
    }))
    setLastLatencyMs(record.lastLatencyMs ?? null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [reset, setCanSave, setConnection, setLastLatencyMs])

  /** ---- Row healthcheck for saved rows ---- */
  const runRowTest = async (row) => {
    if (!row) return
    const now = new Date().toISOString()
    const connectionId = row.backend_connection_id || row.id
    const storeId = row.id || connectionId
    if (!storeId) {
      toast.show('Connection reference is missing. Please re-test and save this connection.', 'error')
      return
    }

    try {
      let latency = null
      let details = 'Healthcheck succeeded'
      const typeKey = sanitizeDbType(row.db_type)
      if (isMock) {
        const normalized = {
          db_type: typeKey,
          db_url:
            row.db_url ||
            (typeKey === 'sqlite'
              ? deriveSqliteUrl(row.databasePath || row.database || '')
              : undefined),
          host: row.host ?? null,
          port: row.port ?? null,
          database: row.database || row.databasePath || '',
          username: row.username || '',
          password: '',
          ssl: row.ssl ?? false,
          driver: row.driver ?? null,
        }
        const payload = payloadFromNormalized(normalized)
        const result = await mock.testConnection(payload)
        latency = result.latencyMs ?? result.latency_ms ?? null
        details = result.details || 'Connected'
        updateSavedConnection(storeId, {
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          details,
          db_url: normalized.db_url,
          host: normalized.host ?? (typeKey === 'sqlite' ? normalized.database : null),
          port: normalized.port ?? null,
          database: normalized.database,
          databasePath: typeKey === 'sqlite' ? normalized.database : null,
          driver: normalized.driver,
          ssl: normalized.ssl,
          backend_connection_id: connectionId || storeId,
        })
      } else {
        if (!connectionId) throw new Error('Connection is missing a server identifier. Please re-test and save it.')
        const res = await apiHealthcheckConnection(connectionId)
        latency = typeof res.latency_ms === 'number' ? res.latency_ms : null
        updateSavedConnection(storeId, {
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          details,
          backend_connection_id: connectionId,
          db_url:
            row.db_url ||
            (typeKey === 'sqlite'
              ? deriveSqliteUrl(row.databasePath || row.database || row.summary || '')
              : row.db_url || null),
          host:
            typeKey === 'sqlite'
              ? row.databasePath || row.database || null
              : row.host ?? null,
          port: row.port ?? null,
          database: row.database ?? (typeKey === 'sqlite' ? row.databasePath : null),
          databasePath: typeKey === 'sqlite' ? (row.databasePath || row.database || null) : null,
          driver: row.driver ?? null,
          ssl: row.ssl ?? undefined,
        })
      }

      setRowHeartbeat((prev) => ({
        ...prev,
        [storeId]: { status: 'healthy', latencyMs: latency, ts: Date.now() },
      }))

      if (
        activeConnectionId &&
        (activeConnectionId === connectionId || activeConnectionId === storeId)
      ) {
        const fallbackUrl =
          row.db_url ||
          (typeKey === 'sqlite'
            ? deriveSqliteUrl(row.databasePath || row.database || row.summary || '')
            : null)
        setConnection({
          status: 'connected',
          saved: true,
          name: row.name,
          db_url: fallbackUrl || null,
          latencyMs: latency,
          lastMessage: details,
          details,
          lastCheckedAt: now,
          connectionId: connectionId || storeId,
          db_type: row.db_type,
          host: row.host ?? (typeKey === 'sqlite' ? row.databasePath || row.database || null : null),
          port: row.port ?? null,
          database: row.database ?? (typeKey === 'sqlite' ? row.databasePath : null),
          driver: row.driver ?? null,
          ssl: row.ssl ?? false,
        })
        if (!isMock && connectionId) setActiveConnectionId(connectionId)
      }
      toast.show('Healthcheck succeeded', 'success')
    } catch (error) {
      const detail = error?.message || 'Healthcheck failed'
      updateSavedConnection(storeId, { status: 'failed', details: detail })
      setRowHeartbeat((prev) => ({
        ...prev,
        [storeId]: { status: 'unreachable', latencyMs: null, ts: Date.now() },
      }))
      if (
        activeConnectionId &&
        (activeConnectionId === connectionId || activeConnectionId === storeId)
      ) {
        setConnection({ status: 'failed', lastMessage: detail, details: detail, lastCheckedAt: now })
      }
      toast.show(detail, 'error')
      throw error
    } finally {
      const snapshot = useAppStore.getState()
      savePersistedCache({
        connections: snapshot.savedConnections,
        templates: snapshot.templates,
        lastUsed: snapshot.lastUsed,
      })
      setTimeout(() => setRowHeartbeat((prev) => {
        const next = { ...prev }
        Object.keys(next).forEach((k) => {
          if (Date.now() - next[k].ts > 2500) delete next[k]
        })
        return next
      }), 3000)
    }
  }

  const handleRowTest = async (row) => {
    if (!row) return
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Healthcheck connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: row.backend_connection_id || row.id || null,
        dbType: sanitizeDbType(row.db_type),
        action: 'connection_healthcheck',
      },
      action: async () => runRowTest(row),
    })
  }

  const handleConfirmSelectAction = useCallback(() => {
    const id = confirmSelect
    const selected = savedConnections.find((x) => x.id === id)
    if (selected) applySelection(selected)
    setConfirmSelect(null)
  }, [confirmSelect, savedConnections, applySelection])

  const handleConfirmDeleteAction = useCallback(() => {
    const id = confirmDelete
    const record = savedConnections.find((x) => x.id === id)
    if (!record) {
      setConfirmDelete(null)
      toast.show('Connection not found', 'error')
      return
    }
    const connectionId = record.backend_connection_id || record.id
    const wasActive =
      activeConnectionId === record.backend_connection_id ||
      activeConnectionId === record.id ||
      activeConnectionId === connectionId
    const previousConnectionState = connection
    const previousActiveId = activeConnectionId
    const previousDetailId = detailId
    const previousEditingId = editingId
    const previousHeartbeat = rowHeartbeat[id]

    const persistCache = () => {
      const stateNow = useAppStore.getState()
      savePersistedCache({
        connections: stateNow.savedConnections,
        templates: stateNow.templates,
        lastUsed: stateNow.lastUsed,
      })
    }

    const restoreConnection = () => {
      addSavedConnection(record)
      setRowHeartbeat((prev) => ({
        ...prev,
        ...(previousHeartbeat ? { [id]: previousHeartbeat } : {}),
      }))
      if (wasActive) {
        const currentActiveId = useAppStore.getState().activeConnectionId
        if (!currentActiveId) {
          setActiveConnectionId(previousActiveId || record.id)
          setConnection(previousConnectionState)
        }
      }
      if (previousDetailId) setDetailId(previousDetailId)
      if (previousEditingId === id) setEditingId(id)
      persistCache()
    }

    if (deleteUndoRef.current?.timeoutId) {
      clearTimeout(deleteUndoRef.current.timeoutId)
      deleteUndoRef.current = null
    }

    const remaining = savedConnections.filter((x) => x.id !== id)
    removeSavedConnection(id)
    setRowHeartbeat((prev) => {
      if (!prev[id]) return prev
      const next = { ...prev }
      delete next[id]
      return next
    })
    if (wasActive) {
      setActiveConnectionId(null)
      setConnection({ saved: false, status: 'disconnected', name: '', db_url: null, latencyMs: null })
    }
    if (editingId === id) {
      setEditingId(null)
    }
    setDetailId(null)
    if (!remaining.length) {
      setActiveConnectionId(null)
      setConnection({ saved: false, status: 'disconnected', name: '', db_url: null, latencyMs: null })
    }
    setConfirmDelete(null)
    persistCache()

    let undone = false
    const timeoutId = setTimeout(async () => {
      if (undone) return
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete connection',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          connectionId,
          action: 'delete_connection',
        },
        action: async () => {
          try {
            if (!isMock && connectionId) {
              await apiDeleteConnection(connectionId)
            }
            toast.show('Connection deleted', 'success')
          } catch (err) {
            restoreConnection()
            toast.show(err?.message || 'Failed to delete connection', 'error')
            throw err
          } finally {
            deleteUndoRef.current = null
          }
        },
      })
    }, 5000)

    deleteUndoRef.current = { timeoutId, id }

    toast.showWithUndo(
      `Connection "${record.name || record.id}" removed`,
      () => {
        undone = true
        clearTimeout(timeoutId)
        deleteUndoRef.current = null
        restoreConnection()
        toast.show('Connection restored', 'success')
      },
      { severity: 'info' }
    )
  }, [
    confirmDelete, savedConnections, activeConnectionId, connection,
    detailId, editingId, rowHeartbeat, addSavedConnection,
    removeSavedConnection, setActiveConnectionId, setConnection,
    toast, execute,
  ])

  return {
    // state
    confirmSelect,
    setConfirmSelect,
    confirmDelete,
    setConfirmDelete,
    detailId,
    setDetailId,
    detailAnchor,
    rowHeartbeat,
    editingId,
    setEditingId,
    showDetails,
    setShowDetails,
    // refs
    listRef,
    panelRef,
    // derived
    detailConnection,
    detailStatus,
    detailLatency,
    detailNote,
    // handlers
    applySelection,
    requestSelect,
    beginEditConnection,
    handleRowTest,
    handleConfirmSelectAction,
    handleConfirmDeleteAction,
  }
}

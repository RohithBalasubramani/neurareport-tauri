import { useCallback, useMemo, useState } from 'react'
import { bootstrapState, healthcheckConnection, deleteConnection } from '../api/client'
import { useAppStore } from './useAppStore'

const normalizeConnections = (connections) =>
  Array.isArray(connections) ? connections : []

export default function useConnectionStore() {
  const connections = useAppStore((s) => s.savedConnections)
  const setSavedConnections = useAppStore((s) => s.setSavedConnections)
  const updateSavedConnection = useAppStore((s) => s.updateSavedConnection)
  const removeSavedConnection = useAppStore((s) => s.removeSavedConnection)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const normalizedConnections = useMemo(
    () => normalizeConnections(connections),
    [connections]
  )

  const setConnections = useCallback((next) => {
    const resolved = typeof next === 'function' ? next(connections) : next
    setSavedConnections(normalizeConnections(resolved))
  }, [connections, setSavedConnections])

  const fetchConnections = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await bootstrapState()
      const next = normalizeConnections(data?.connections)
      setSavedConnections(next)
      setLoading(false)
      return next
    } catch (err) {
      setError(err.message || 'Failed to load connections')
      setLoading(false)
      return []
    }
  }, [setSavedConnections])

  const healthCheck = useCallback(async (connectionId) => {
    try {
      const result = await healthcheckConnection(connectionId)
      updateSavedConnection(connectionId, {
        lastLatencyMs: result.latency_ms,
        status: 'connected',
      })
      return result
    } catch (err) {
      updateSavedConnection(connectionId, { status: 'error' })
      throw err
    }
  }, [updateSavedConnection])

  const removeConnection = useCallback(async (connectionId) => {
    setLoading(true)
    setError(null)
    try {
      await deleteConnection(connectionId)
      removeSavedConnection(connectionId)
      setLoading(false)
      return true
    } catch (err) {
      setError(err.message || 'Failed to delete connection')
      setLoading(false)
      return false
    }
  }, [removeSavedConnection])

  const getConnection = useCallback(
    (connectionId) =>
      normalizedConnections.find((conn) => conn.id === connectionId) || null,
    [normalizedConnections]
  )

  const reset = useCallback(() => {
    setSavedConnections([])
    setError(null)
  }, [setSavedConnections])

  return useMemo(() => ({
    connections: normalizedConnections,
    loading,
    error,
    setConnections,
    setLoading,
    setError,
    fetchConnections,
    healthCheck,
    removeConnection,
    getConnection,
    reset,
  }), [
    normalizedConnections,
    loading,
    error,
    setConnections,
    setLoading,
    setError,
    fetchConnections,
    healthCheck,
    removeConnection,
    getConnection,
    reset,
  ])
}

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  discoverLoggerDatabases,
  upsertConnection,
  listConnections,
} from '@/api/client'
import { useAppStore } from '@/stores'

// Logger frontend URL — embedded as iframe plugin
export const LOGGER_URL = 'http://localhost:9847?embedded=true'

export function useLoggerPage() {
  const [viewMode, setViewMode] = useState('plugin') // 'plugin' | 'data'
  const [loggerConnections, setLoggerConnections] = useState([])
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [discovering, setDiscovering] = useState(false)
  const [discoveryError, setDiscoveryError] = useState(null)
  const [loggerStatus, setLoggerStatus] = useState('checking') // 'checking' | 'online' | 'offline'
  const iframeRef = useRef(null)

  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)

  // Check if Logger frontend is accessible
  useEffect(() => {
    setLoggerStatus('checking')
    const timeout = setTimeout(() => {
      setLoggerStatus('offline')
    }, 5000)
    fetch(LOGGER_URL, { mode: 'no-cors' })
      .then(() => {
        clearTimeout(timeout)
        setLoggerStatus('online')
      })
      .catch(() => {
        clearTimeout(timeout)
        setLoggerStatus('offline')
      })
    return () => clearTimeout(timeout)
  }, [])

  // Load existing PostgreSQL connections
  useEffect(() => {
    listConnections().then((res) => {
      const conns = (res?.connections || []).filter(
        (c) => c.db_type === 'postgresql' || c.db_type === 'postgres'
      )
      setLoggerConnections(conns)
      if (conns.length > 0 && !selectedConnectionId) {
        setSelectedConnectionId(conns[0].id)
      }
    }).catch(() => {})
  }, [])

  const handleDiscover = useCallback(async () => {
    setDiscovering(true)
    setDiscoveryError(null)
    try {
      const result = await discoverLoggerDatabases()
      const databases = result?.databases || []
      if (databases.length === 0) {
        setDiscoveryError('No Logger databases found on the network.')
        return
      }
      for (const db of databases) {
        try {
          await upsertConnection({
            name: db.name,
            dbType: 'postgresql',
            dbUrl: db.db_url,
            database: db.database,
            status: 'connected',
          })
        } catch {
          // already exists or failed
        }
      }
      const res = await listConnections()
      const conns = (res?.connections || []).filter(
        (c) => c.db_type === 'postgresql' || c.db_type === 'postgres'
      )
      setLoggerConnections(conns)
      if (conns.length > 0 && !selectedConnectionId) {
        setSelectedConnectionId(conns[0].id)
      }
    } catch (err) {
      setDiscoveryError(err?.message || 'Discovery failed')
    } finally {
      setDiscovering(false)
    }
  }, [selectedConnectionId])

  const handleRefreshIframe = useCallback(() => {
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src
    }
  }, [])

  const handleConnectionSelect = useCallback((connId) => {
    setSelectedConnectionId(connId)
    setActiveConnectionId(connId)
  }, [setActiveConnectionId])

  const handleRetryConnection = useCallback(() => {
    setLoggerStatus('checking')
    fetch(LOGGER_URL, { mode: 'no-cors' })
      .then(() => setLoggerStatus('online'))
      .catch(() => setLoggerStatus('offline'))
  }, [])

  return {
    viewMode,
    setViewMode,
    loggerConnections,
    selectedConnectionId,
    discovering,
    discoveryError,
    setDiscoveryError,
    loggerStatus,
    iframeRef,
    handleDiscover,
    handleRefreshIframe,
    handleConnectionSelect,
    handleRetryConnection,
  }
}

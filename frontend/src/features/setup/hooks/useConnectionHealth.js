import { useEffect, useMemo, useState } from 'react'
import { isMock } from '@/api/client'
import * as mock from '@/api/mock'
import { checkHealth } from '@/api/health'
import { useAppStore } from '@/stores'

export function useConnectionHealth({ isTesting = false }) {
  const { connection } = useAppStore()
  const [lastLatencyMs, setLastLatencyMs] = useState(null)
  const [apiStatus, setApiStatus] = useState('unknown')

  /** ---- API health probe (uses real backend when not mock) ---- */
  useEffect(() => {
    let cancelled = false
    const probe = async () => {
      try {
        if (isMock) {
          await mock.health()
        } else {
          const ok = await checkHealth({ timeoutMs: 5000 })
          if (!ok) throw new Error()
        }
        if (!cancelled) setApiStatus('healthy')
      } catch {
        if (!cancelled) setApiStatus('unreachable')
      }
    }
    probe()
    const id = setInterval(probe, 15000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  const lastHeartbeatLabel = useMemo(() => {
    if (!connection.lastCheckedAt) return 'Not tested yet'
    const ts = new Date(connection.lastCheckedAt)
    if (Number.isNaN(ts.getTime())) return 'Not tested yet'
    const delta = Date.now() - ts.getTime()
    if (delta < 0) return 'Just now'
    const seconds = Math.floor(delta / 1000)
    if (seconds < 60) return `${seconds || 1}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }, [connection.lastCheckedAt])

  const hbStatus = useMemo(() => {
    if (isTesting) return 'testing'
    if (connection.status === 'connected') return 'healthy'
    if (connection.status === 'failed') return 'unreachable'
    return apiStatus
  }, [isTesting, connection.status, apiStatus])

  const heartbeatChipColor = useMemo(() => {
    switch (hbStatus) {
      case 'healthy':
        return 'success'
      case 'testing':
        return 'warning'
      case 'unreachable':
        return 'error'
      default:
        return 'default'
    }
  }, [hbStatus])

  const showHeartbeatChip = useMemo(
    () => Boolean(connection.lastCheckedAt) || isTesting,
    [connection.lastCheckedAt, isTesting],
  )

  return {
    lastLatencyMs,
    setLastLatencyMs,
    apiStatus,
    lastHeartbeatLabel,
    hbStatus,
    heartbeatChipColor,
    showHeartbeatChip,
  }
}

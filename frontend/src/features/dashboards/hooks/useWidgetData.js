/**
 * useWidgetData — fetches live data for a widget from the active DB connection
 * or from a report run, using the widget's RAG strategy.
 *
 * Automatically reads activeConnectionId from the app store if no
 * connectionId is explicitly provided.
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { getWidgetData, getWidgetReportData } from '@/api/widgets'
import { useAppStore } from '@/stores'

export default function useWidgetData({
  scenario,
  variant,
  connectionId,
  reportRunId,
  filters,
  limit = 100,
  autoFetch = true,
  refreshInterval = 0,
}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [source, setSource] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const intervalRef = useRef(null)

  // Auto-resolve from global store if no explicit connectionId
  const storeConnectionId = useAppStore((s) => s.activeConnectionId)
  const effectiveConnectionId = connectionId || storeConnectionId

  const fetchData = useCallback(async () => {
    if (!scenario) return

    setLoading(true)
    setError(null)

    try {
      let result

      if (reportRunId) {
        // Tier 1: Report run data (RAG over saved report data)
        result = await getWidgetReportData({ runId: reportRunId, scenario, variant })
      } else if (effectiveConnectionId) {
        // Tier 2: Active database connection (real data)
        result = await getWidgetData({
          connectionId: effectiveConnectionId,
          scenario,
          variant,
          filters,
          limit,
        })
      } else {
        // No data source available
        setError('No data source configured. Connect a database to see live data.')
        setLoading(false)
        return
      }

      // Check if backend returned an error with empty data
      if (result.error && (!result.data || Object.keys(result.data).length === 0)) {
        setError(result.error)
        setData(null)
      } else {
        setData(result.data || result)
        setSource(result.source || effectiveConnectionId || null)
        setStrategy(result.strategy || null)
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to fetch widget data'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [scenario, variant, effectiveConnectionId, reportRunId, filters, limit])

  // Auto-fetch on mount and when dependencies change
  useEffect(() => {
    if (autoFetch) {
      fetchData()
    }
  }, [autoFetch, fetchData])

  // Optional polling interval
  useEffect(() => {
    if (refreshInterval > 0 && autoFetch) {
      intervalRef.current = setInterval(fetchData, refreshInterval)
      return () => clearInterval(intervalRef.current)
    }
  }, [refreshInterval, autoFetch, fetchData])

  return {
    data,
    loading,
    error,
    source,
    strategy,
    connectionId: effectiveConnectionId,
    refresh: fetchData,
  }
}

import { useState, useEffect, useCallback, useMemo } from 'react'
import { recommendWidgets } from '@/api/widgets'
import { useAppStore } from '@/stores'

export function useWidgetRecommendations() {
  const [widgets, setWidgets] = useState([])
  const [grid, setGrid] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('overview')

  const connectionId = useAppStore((s) => s.activeConnectionId)
  const activeConnection = useAppStore((s) => s.activeConnection)
  const connectionName = activeConnection?.name || connectionId || ''

  const loadRecommendations = useCallback(() => {
    if (!connectionId) return
    setLoading(true)
    setError(null)
    recommendWidgets({ connectionId, query, maxWidgets: 12 })
      .then((res) => {
        setWidgets(res.widgets || [])
        setGrid(res.grid || null)
        setProfile(res.profile || null)
      })
      .catch((err) => {
        console.error('[WidgetsPage] Recommendation failed:', err)
        setError(err.userMessage || err.message || 'Failed to get widget recommendations')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [connectionId, query])

  useEffect(() => {
    loadRecommendations()
  }, [loadRecommendations])

  const handleQuerySubmit = useCallback(
    (e) => {
      e.preventDefault()
      loadRecommendations()
    },
    [loadRecommendations],
  )

  // Build a lookup: widget_id -> grid cell placement
  const cellMap = useMemo(() => {
    const map = {}
    if (grid?.cells) {
      for (const c of grid.cells) {
        map[c.widget_id] = c
      }
    }
    return map
  }, [grid])

  const profileChips = profile
    ? [
        `${profile.table_count} tables`,
        `${profile.numeric_columns} numeric cols`,
        profile.has_timeseries ? 'timeseries' : 'no timeseries',
      ]
    : []

  return {
    widgets,
    grid,
    loading,
    error,
    query,
    setQuery,
    connectionId,
    connectionName,
    loadRecommendations,
    handleQuerySubmit,
    cellMap,
    profileChips,
  }
}

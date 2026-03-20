import { useState, useCallback, useEffect, useRef, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTheme } from '@mui/material'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'
import { neutral } from '@/app/theme'

const TAB_MAP = { overview: 0, jobs: 1, templates: 2 }
const TAB_NAMES = ['overview', 'jobs', 'templates']

const getChartColors = (theme) => [
  theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
  theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
  theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  theme.palette.mode === 'dark' ? neutral[300] : neutral[300],
  theme.palette.text.secondary,
]

const getStatusColors = (theme) => ({
  completed: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  failed: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  pending: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
  running: theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
  cancelled: theme.palette.text.secondary,
})

export { TAB_MAP, TAB_NAMES }

export function useUsageStats() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const didLoadRef = useRef(false)

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'stats', ...intent } }),
    [navigate]
  )

  const tabParam = searchParams.get('tab') || 'overview'
  const activeTab = TAB_MAP[tabParam] ?? 0

  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(searchParams.get('period') || 'week')
  const [dashboardData, setDashboardData] = useState(null)
  const [usageData, setUsageData] = useState(null)
  const [historyData, setHistoryData] = useState(null)

  const CHART_COLORS = useMemo(() => getChartColors(theme), [theme])
  const STATUS_COLORS = useMemo(() => getStatusColors(theme), [theme])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [dashboard, usage, history] = await Promise.all([
        api.getDashboardAnalytics(),
        api.getUsageStatistics(period),
        api.getReportHistory({ limit: 100 }),
      ])
      setDashboardData(dashboard)
      setUsageData(usage)
      setHistoryData(history)
    } catch (err) {
      toast.show(err.message || 'Failed to load statistics', 'error')
    } finally {
      setLoading(false)
    }
  }, [period, toast])

  const handleRefresh = useCallback(
    () =>
      execute({
        type: InteractionType.EXECUTE,
        label: 'Refresh usage statistics',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: { period },
        action: fetchData,
      }),
    [execute, fetchData, period]
  )

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchData()
  }, [fetchData])

  useEffect(() => {
    if (!didLoadRef.current) return
    fetchData()
  }, [period, fetchData])

  const summary = dashboardData?.summary || {}
  const metrics = dashboardData?.metrics || {}
  const jobsTrend = dashboardData?.jobsTrend || []
  const topTemplates = dashboardData?.topTemplates || []

  const statusData = useMemo(() => {
    const byStatus = usageData?.byStatus || {}
    return Object.entries(byStatus).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      color: STATUS_COLORS[name] || theme.palette.text.secondary,
    }))
  }, [usageData, STATUS_COLORS, theme])

  const kindData = useMemo(() => {
    const byKind = usageData?.byKind || {}
    return Object.entries(byKind).map(([name, value]) => ({
      name: name.toUpperCase(),
      value,
      color: name === 'pdf'
        ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
        : (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
    }))
  }, [usageData, theme])

  const templateBreakdown = useMemo(() => {
    const breakdown = usageData?.templateBreakdown || []
    if (breakdown.length > 0) return breakdown
    return topTemplates.slice(0, 6).map((t) => ({
      name: t.name || t.id?.slice(0, 12),
      count: t.runCount || 0,
      kind: t.kind || 'pdf',
    }))
  }, [usageData, topTemplates])

  const historyByDay = useMemo(() => {
    const history = historyData?.history || []
    const byDay = {}
    history.forEach((item) => {
      const date = item.createdAt?.split('T')[0]
      if (!date) return
      if (!byDay[date]) {
        byDay[date] = { date, completed: 0, failed: 0, total: 0 }
      }
      byDay[date].total += 1
      if (item.status === 'completed') byDay[date].completed += 1
      else if (item.status === 'failed') byDay[date].failed += 1
    })
    return Object.values(byDay)
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-14)
  }, [historyData])

  const handleExportStats = useCallback(
    () =>
      execute({
        type: InteractionType.DOWNLOAD,
        label: 'Export usage statistics',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        intent: { period },
        action: async () => {
          const exportData = {
            exportedAt: new Date().toISOString(),
            period,
            dashboard: dashboardData,
            usage: usageData,
            historyCount: historyData?.total || 0,
          }
          const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `neurareport-stats-${period}-${Date.now()}.json`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
        },
      }),
    [execute, period, dashboardData, usageData, historyData]
  )

  const handleTabChange = useCallback(
    (e, v) => {
      const newParams = new URLSearchParams(searchParams)
      newParams.set('tab', TAB_NAMES[v])
      setSearchParams(newParams, { replace: true })
    },
    [searchParams, setSearchParams]
  )

  const handlePeriodChange = useCallback(
    (newPeriod) => {
      setPeriod(newPeriod)
      const newParams = new URLSearchParams(searchParams)
      newParams.set('period', newPeriod)
      setSearchParams(newParams, { replace: true })
    },
    [searchParams, setSearchParams]
  )

  return {
    theme,
    loading,
    period,
    activeTab,
    summary,
    metrics,
    jobsTrend,
    statusData,
    kindData,
    templateBreakdown,
    historyByDay,
    CHART_COLORS,
    handleNavigate,
    handleRefresh,
    handleExportStats,
    handleTabChange,
    handlePeriodChange,
    dashboardData,
  }
}

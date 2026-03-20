import { useEffect, useState, useCallback, useRef } from 'react'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useCelebration } from '@/components/SuccessCelebration'
import * as api from '@/api/client'
import * as recommendationsApi from '@/api/recommendations'

export function useDashboardNavigation() {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'dashboard', ...intent } }),
    [navigate]
  )
  return { execute, handleNavigate }
}

export function useDashboardData() {
  const toast = useToast()
  const { execute } = useInteraction()
  const didLoadRef = useRef(false)

  const templates = useAppStore((s) => s.templates)
  const savedConnections = useAppStore((s) => s.savedConnections)
  const activeConnection = useAppStore((s) => s.activeConnection)

  const [jobs, setJobs] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [favorites, setFavorites] = useState({ templates: [], connections: [] })
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)

    try {
      const [state, jobsData, analyticsData, favData] = await Promise.all([
        api.bootstrapState().catch(() => null),
        api.listJobs({ limit: 5 }).catch(() => ({ jobs: [] })),
        api.getDashboardAnalytics().catch(() => null),
        api.getFavorites().catch(() => ({ templates: [], connections: [] })),
      ])

      if (state?.templates) useAppStore.setState({ templates: state.templates })
      if (state?.connections) useAppStore.setState({ savedConnections: state.connections })

      setJobs(jobsData?.jobs || [])
      setAnalytics(analyticsData)
      setFavorites(favData)

      if (!state) toast.show('Failed to load some dashboard data. Try refreshing.', 'warning')
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      toast.show('Failed to load dashboard data. Please try again.', 'error')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [toast])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchData()
  }, [fetchData])

  const handleRefresh = useCallback(
    () =>
      execute({
        type: InteractionType.EXECUTE,
        label: 'Refresh dashboard',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: { source: 'dashboard' },
        action: () => fetchData(true),
      }),
    [execute, fetchData]
  )

  return {
    templates,
    savedConnections,
    activeConnection,
    jobs,
    analytics,
    favorites,
    loading,
    refreshing,
    handleRefresh,
  }
}

export function useRecommendations(templates) {
  const toast = useToast()
  const { execute } = useInteraction()
  const recAttemptedRef = useRef(false)

  const [recommendations, setRecommendations] = useState([])
  const [recLoading, setRecLoading] = useState(false)
  const [recFromAI, setRecFromAI] = useState(true)

  const fetchRecommendations = useCallback(async () => {
    if (recLoading) return
    setRecLoading(true)
    recAttemptedRef.current = true

    const fallbackToLocal = () => {
      const topTpls = templates.slice(0, 4).map((t) => ({
        id: t.id,
        name: t.name,
        description: t.description || `${t.kind?.toUpperCase() || 'PDF'} design`,
        kind: t.kind,
        matchScore: 0.85,
      }))
      setRecommendations(topTpls)
      setRecFromAI(false)
    }

    try {
      const catalog = await recommendationsApi.getCatalog()
      const tpls = catalog?.catalog || catalog?.templates || catalog?.recommendations || []
      if (tpls.length > 0) {
        setRecommendations(tpls.slice(0, 4))
        setRecFromAI(true)
      } else if (templates.length > 0) {
        fallbackToLocal()
      }
    } catch {
      if (templates.length > 0) {
        fallbackToLocal()
      }
    } finally {
      setRecLoading(false)
    }
  }, [recLoading, templates])

  const handleRefreshRecommendations = useCallback(
    () =>
      execute({
        type: InteractionType.EXECUTE,
        label: 'Refresh recommendations',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: { source: 'dashboard', recFromAI },
        action: () => {
          recAttemptedRef.current = false
          return fetchRecommendations()
        },
      }),
    [execute, fetchRecommendations, recFromAI]
  )

  useEffect(() => {
    if (recommendations.length === 0 && templates.length > 0 && !recLoading && !recAttemptedRef.current) {
      fetchRecommendations()
    }
  }, [templates.length, recommendations.length, recLoading, fetchRecommendations])

  return {
    recommendations,
    recLoading,
    recFromAI,
    handleRefreshRecommendations,
  }
}

export function useOnboarding(savedConnections, templates, metrics, execute) {
  const [showOnboarding, setShowOnboarding] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.localStorage.getItem('neurareport_onboarding_dismissed') !== 'true'
  })

  const { celebrating, celebrate, onComplete: onCelebrationComplete } = useCelebration()
  const celebratedRef = useRef(false)

  const allStepsComplete = savedConnections.length > 0 && templates.length > 0 && (metrics.jobsToday ?? 0) > 0
  const needsOnboarding = showOnboarding && (templates.length === 0 || savedConnections.length === 0)

  useEffect(() => {
    if (allStepsComplete && showOnboarding && !celebratedRef.current) {
      celebratedRef.current = true
      celebrate()
    }
  }, [allStepsComplete, showOnboarding, celebrate])

  const handleDismissOnboarding = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Dismiss onboarding',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboard' },
      action: () => {
        setShowOnboarding(false)
        if (typeof window !== 'undefined') {
          window.localStorage.setItem('neurareport_onboarding_dismissed', 'true')
        }
      },
    })
  }, [execute])

  return {
    showOnboarding,
    needsOnboarding,
    celebrating,
    onCelebrationComplete,
    handleDismissOnboarding,
  }
}

export function useCommandPalette() {
  const { execute } = useInteraction()

  const handleOpenCommandPalette = useCallback(() => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Open command palette',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboard' },
      action: () => {
        if (typeof window === 'undefined') return
        window.dispatchEvent(new CustomEvent('neura:open-command-palette'))
      },
    })
  }, [execute])

  return { handleOpenCommandPalette }
}

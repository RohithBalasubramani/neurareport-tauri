/**
 * Custom hook for activity page state and operations
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'

export function useActivity() {
  const toast = useToast()
  const navigate = useNavigateInteraction()
  const { execute } = useInteraction()
  const didLoadRef = useRef(false)

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'activity', ...intent } }),
    [navigate]
  )

  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [entityTypeFilter, setEntityTypeFilter] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false)
  const [clearing, setClearing] = useState(false)

  const fetchActivities = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getActivityLog({
        limit: 100,
        entityType: entityTypeFilter || undefined,
        action: actionFilter || undefined,
      })
      setActivities(data?.activities || [])
    } catch (err) {
      toast.show(err.message || 'Failed to load activity log', 'error')
    } finally {
      setLoading(false)
    }
  }, [entityTypeFilter, actionFilter, toast])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchActivities()
  }, [fetchActivities])

  useEffect(() => {
    if (!didLoadRef.current) return
    fetchActivities()
  }, [entityTypeFilter, actionFilter, fetchActivities])

  const handleClearLog = useCallback(async () => {
    await execute({
      type: InteractionType.DELETE,
      label: 'Clear activity log',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { action: 'clear_activity_log' },
      action: async () => {
        setClearing(true)
        try {
          const result = await api.clearActivityLog()
          setActivities([])
          toast.show(`Cleared ${result.cleared} activity entries`, 'success')
          return result
        } catch (err) {
          toast.show(err.message || 'Failed to clear activity log', 'error')
          throw err
        } finally {
          setClearing(false)
          setClearConfirmOpen(false)
        }
      },
    })
  }, [toast, execute])

  return {
    activities,
    loading,
    entityTypeFilter,
    setEntityTypeFilter,
    actionFilter,
    setActionFilter,
    clearConfirmOpen,
    setClearConfirmOpen,
    clearing,
    fetchActivities,
    handleClearLog,
    handleNavigate,
  }
}

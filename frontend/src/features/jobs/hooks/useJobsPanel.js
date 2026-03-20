/**
 * Hook for managing JobsPanel state and actions.
 */
import { useCallback, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useQueryClient } from '@tanstack/react-query'
import { useJobsList } from '@/hooks/useJobs'
import { useAppStore } from '@/stores'
import { cancelJob as cancelJobRequest } from '@/api/client'
import {
  normalizeJob,
  normalizeJobStatus,
  isActiveStatus,
  isFailureStatus,
  JobStatus,
} from '@/utils/jobStatus'

export function useJobsPanel({ onClose }) {
  const navigate = useNavigate()
  const { execute } = useInteraction()
  const queryClient = useQueryClient()
  const savedConnections = useAppStore((state) => state.savedConnections)
  const setActiveConnectionId = useAppStore((state) => state.setActiveConnectionId)
  const setSetupNav = useAppStore((state) => state.setSetupNav)
  const jobsQuery = useJobsList({ limit: 30 }) || {}
  const { data, isLoading, isFetching, error, refetch } = jobsQuery
  const [statusFilter, setStatusFilter] = useState('all')
  const jobs = data?.jobs || []
  const normalizedJobs = useMemo(
    () => jobs.map((job) => normalizeJob(job)),
    [jobs],
  )

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'jobs-panel', ...intent },
      action,
    })
  }, [execute])

  const handleNavigate = useCallback((path, options = {}) => {
    const {
      label = `Open ${path}`,
      intent = {},
      navigateOptions,
      beforeNavigate,
    } = options
    return execute({
      type: InteractionType.NAVIGATE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'jobs-panel', path, ...intent },
      action: () => {
        beforeNavigate?.()
        return navigate(path, navigateOptions)
      },
    })
  }, [execute, navigate])

  const markJobCancelled = useCallback((jobId) => {
    if (!jobId || !queryClient) return
    const queries = queryClient.getQueriesData({ queryKey: ['jobs'] }) || []
    queries.forEach(([queryKey, value]) => {
      if (!value) return
      if (Array.isArray(value.jobs)) {
        const updatedJobs = value.jobs.map((job) => {
          if (job.id !== jobId) return job
          const steps = Array.isArray(job.steps)
            ? job.steps.map((step) => {
                const status = (step?.status || '').toLowerCase()
                if (status === 'succeeded' || status === 'failed' || status === 'cancelled') {
                  return step
                }
                return { ...step, status: 'cancelled' }
              })
            : job.steps
          return { ...job, status: 'cancelled', steps }
        })
        queryClient.setQueryData(queryKey, { ...value, jobs: updatedJobs })
      } else if (value.id === jobId) {
        queryClient.setQueryData(queryKey, { ...value, status: 'cancelled' })
      }
    })
  }, [queryClient])

  const handleCancelJob = useCallback((jobId, options = {}) => {
    if (!jobId) return undefined
    const force = Boolean(options?.force)
    return execute({
      type: InteractionType.UPDATE,
      label: force ? 'Force stop job' : 'Cancel job',
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      intent: { source: 'jobs-panel', jobId, force },
      action: async () => {
        await cancelJobRequest(jobId, { force })
        markJobCancelled(jobId)
        await refetch?.()
      },
    })
  }, [execute, markJobCancelled, refetch])

  const handleForceCancelJob = useCallback(
    (jobId) => handleCancelJob(jobId, { force: true }),
    [handleCancelJob],
  )

  const filteredJobs = useMemo(() => {
    if (statusFilter === 'all') return normalizedJobs
    if (statusFilter === 'active') return normalizedJobs.filter((job) => isActiveStatus(job.status))
    if (statusFilter === 'completed') return normalizedJobs.filter((job) => job.status === JobStatus.COMPLETED)
    if (statusFilter === 'failed') return normalizedJobs.filter((job) => isFailureStatus(job.status))
    return normalizedJobs
  }, [normalizedJobs, statusFilter])

  const activeCount = useMemo(
    () => normalizedJobs.filter((job) => isActiveStatus(job.status)).length,
    [normalizedJobs],
  )
  const showEmptyState = !filteredJobs.length && !isLoading && !isFetching && !error

  const connectionLookup = useMemo(() => {
    const lookup = new Map()
    savedConnections.forEach((conn) => {
      if (!conn?.id) return
      lookup.set(conn.id, conn.name || conn.id)
    })
    return lookup
  }, [savedConnections])

  const handleClosePanel = useCallback(() => {
    return executeUI('Close jobs panel', () => onClose?.())
  }, [executeUI, onClose])

  const handleFilterChange = useCallback((filter) => {
    return executeUI('Filter jobs', () => setStatusFilter(filter), { filter })
  }, [executeUI])

  const handleRetry = useCallback(() => {
    return executeUI('Retry jobs refresh', () => refetch?.(), { action: 'refetch' })
  }, [executeUI, refetch])

  const onJobNavigate = useCallback((templateId) => {
    if (!templateId) return undefined
    return handleNavigate(`/reports?template=${encodeURIComponent(templateId)}`, {
      label: 'Open report',
      intent: { templateId },
      beforeNavigate: () => onClose?.(),
    })
  }, [handleNavigate, onClose])

  const onSetupNavigate = useCallback((connectionId) => {
    if (!connectionId) return undefined
    return handleNavigate('/setup/wizard', {
      label: 'Open setup wizard',
      intent: { connectionId },
      beforeNavigate: () => {
        setSetupNav('connect')
        setActiveConnectionId(connectionId)
        onClose?.()
      },
    })
  }, [handleNavigate, setActiveConnectionId, setSetupNav, onClose])

  return {
    statusFilter,
    filteredJobs,
    activeCount,
    showEmptyState,
    connectionLookup,
    isLoading,
    isFetching,
    error,
    handleClosePanel,
    handleFilterChange,
    handleRetry,
    onJobNavigate,
    onSetupNavigate,
    handleCancelJob,
    handleForceCancelJob,
  }
}

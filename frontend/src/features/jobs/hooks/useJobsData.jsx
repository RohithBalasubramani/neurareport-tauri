/**
 * Jobs Page - Custom hook for all state, effects, and callbacks
 */
import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import { useTheme } from '@mui/material'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'
import { readPreferences, subscribePreferences } from '@/utils/preferences'
import {
  normalizeJob,
  isActiveStatus,
  canRetryJob,
  canCancelJob,
  JobStatus,
} from '@/utils/jobStatus'
import { getStatusConfig } from '../components/JobsStyledComponents'
import {
  MonoText,
  TypeChip,
  StatusChip,
  StyledLinearProgress,
} from '../components/JobsStyledComponents'
import CancelIcon from '@mui/icons-material/Cancel'
import { Box, Typography, Tooltip } from '@mui/material'

export function useJobsData() {
  const theme = useTheme()
  const toast = useToast()
  const navigate = useNavigateInteraction()
  const { execute } = useInteraction()

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'jobs', ...intent } }),
    [navigate]
  )

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'jobs', ...intent },
      action,
    })
  }, [execute])

  const executeDownload = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.DOWNLOAD,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'jobs', ...intent },
      action,
    })
  }, [execute])

  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false)
  const [cancellingJob, setCancellingJob] = useState(null)
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [menuJob, setMenuJob] = useState(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [detailsJob, setDetailsJob] = useState(null)
  const [retrying, setRetrying] = useState(false)
  const [selectedIds, setSelectedIds] = useState([])
  const [bulkCancelOpen, setBulkCancelOpen] = useState(false)
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const [bulkActionLoading, setBulkActionLoading] = useState(false)
  const [autoRefreshJobs, setAutoRefreshJobs] = useState(
    () => readPreferences().autoRefreshJobs ?? true
  )
  const pollIntervalRef = useRef(null)
  const bulkDeleteUndoRef = useRef(null)
  const isMountedRef = useRef(true)
  const isUserActionInProgressRef = useRef(false)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    const unsubscribe = subscribePreferences((prefs) => {
      setAutoRefreshJobs(prefs?.autoRefreshJobs ?? true)
    })
    return unsubscribe
  }, [])

  const fetchJobs = useCallback(async (force = false) => {
    if (!force && isUserActionInProgressRef.current) {
      return
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    try {
      const data = await api.listJobs({ limit: 50, signal: abortControllerRef.current.signal })
      if (isMountedRef.current && (force || !isUserActionInProgressRef.current)) {
        const normalized = Array.isArray(data.jobs) ? data.jobs.map((job) => normalizeJob(job)) : []
        setJobs(normalized)
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Failed to fetch jobs:', err)
      }
    }
  }, [])

  useEffect(() => {
    isMountedRef.current = true
    setLoading(true)
    fetchJobs(true).finally(() => setLoading(false))

    if (autoRefreshJobs) {
      pollIntervalRef.current = setInterval(() => fetchJobs(false), 5000)
    }

    return () => {
      isMountedRef.current = false
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [fetchJobs, autoRefreshJobs])

  const openMenu = useCallback((anchor, job) => {
    setMenuAnchor(anchor)
    setMenuJob(job)
  }, [])

  const closeMenu = useCallback(() => {
    setMenuAnchor(null)
    setMenuJob(null)
  }, [])

  const openDetails = useCallback((job) => {
    setDetailsJob(job)
    setDetailsDialogOpen(true)
  }, [])

  const closeDetails = useCallback(() => {
    setDetailsDialogOpen(false)
  }, [])

  const handleOpenMenu = useCallback((event, job) => {
    event.stopPropagation()
    const anchor = event.currentTarget
    return executeUI('Open job actions', () => openMenu(anchor, job), { jobId: job?.id })
  }, [executeUI, openMenu])

  const handleCloseMenu = useCallback(() => {
    return executeUI('Close job actions', () => closeMenu())
  }, [executeUI, closeMenu])

  const handleRefresh = useCallback(() => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Refresh jobs',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'jobs', action: 'refresh_jobs' },
      action: async () => {
        setLoading(true)
        try {
          await fetchJobs()
          toast.show('Progress updated', 'info')
        } finally {
          setLoading(false)
        }
      },
    })
  }, [execute, fetchJobs, toast])

  const handleCancelClick = useCallback(() => {
    if (!menuJob) return undefined
    return executeUI('Review cancel job', () => {
      setCancellingJob(menuJob)
      setCancelConfirmOpen(true)
      closeMenu()
    }, { jobId: menuJob.id })
  }, [executeUI, menuJob, closeMenu])

  const handleCancelConfirm = useCallback(async () => {
    if (!cancellingJob) return

    await execute({
      type: InteractionType.UPDATE,
      label: 'Cancel job',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        jobId: cancellingJob.id,
        action: 'cancel_job',
      },
      action: async () => {
        isUserActionInProgressRef.current = true

        setJobs((prev) =>
          prev.map((job) =>
            job.id === cancellingJob.id ? { ...job, status: JobStatus.CANCELLING } : job
          )
        )
        setCancelConfirmOpen(false)

        try {
          await api.cancelJob(cancellingJob.id)
          toast.show('Job cancelled', 'success')
        } catch (err) {
          toast.show(err.message || 'Failed to cancel job', 'error')
          throw err
        } finally {
          setCancellingJob(null)
          isUserActionInProgressRef.current = false
          fetchJobs(true)
        }
      },
    })
  }, [cancellingJob, toast, fetchJobs, execute])

  const handleDownload = useCallback(() => {
    return executeDownload('Download job output', () => {
      if (menuJob?.artifacts?.html_url) {
        window.open(api.withBase(menuJob.artifacts.html_url), '_blank')
      } else {
        toast.show('Download not available', 'warning')
      }
      closeMenu()
    }, { jobId: menuJob?.id, format: 'html' })
  }, [executeDownload, menuJob, toast, closeMenu])

  const handleViewDetails = useCallback(() => {
    if (!menuJob) return undefined
    return executeUI('Open job details', () => {
      openDetails(menuJob)
      closeMenu()
    }, { jobId: menuJob.id })
  }, [executeUI, menuJob, openDetails, closeMenu])

  const handleRowClick = useCallback((row) => {
    return executeUI('Open job details', () => openDetails(row), { jobId: row?.id, source: 'jobs-table' })
  }, [executeUI, openDetails])

  const handleRetry = useCallback(async () => {
    if (!menuJob) return
    await execute({
      type: InteractionType.UPDATE,
      label: 'Retry job',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        jobId: menuJob.id,
        action: 'retry_job',
      },
      action: async () => {
        isUserActionInProgressRef.current = true
        setRetrying(true)
        closeMenu()
        try {
          await api.retryJob(menuJob.id)
          toast.show('Job restarted successfully', 'success')
        } catch (err) {
          toast.show(err.message || 'Failed to retry job', 'error')
          throw err
        } finally {
          setRetrying(false)
          isUserActionInProgressRef.current = false
          fetchJobs(true)
        }
      },
    })
  }, [menuJob, toast, fetchJobs, closeMenu, execute])

  const handleBulkCancelOpen = useCallback(() => {
    if (!selectedIds.length) return undefined
    return executeUI('Review cancel jobs', () => {
      const hasActive = selectedIds.some((id) => {
        const job = jobs.find((item) => item.id === id)
        return isActiveStatus(job?.status)
      })
      if (!hasActive) {
        toast.show('Select running or pending jobs to cancel', 'warning')
        return
      }
      setBulkCancelOpen(true)
    }, { count: selectedIds.length })
  }, [executeUI, jobs, selectedIds, toast])

  const handleBulkCancelConfirm = useCallback(async () => {
    const activeIds = selectedIds.filter((id) => {
      const job = jobs.find((item) => item.id === id)
      return isActiveStatus(job?.status)
    })
    if (!activeIds.length) {
      toast.show('Select running or pending jobs to cancel', 'warning')
      setBulkCancelOpen(false)
      return
    }

    await execute({
      type: InteractionType.UPDATE,
      label: 'Cancel selected jobs',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        jobIds: activeIds,
        action: 'bulk_cancel_jobs',
      },
      action: async () => {
        isUserActionInProgressRef.current = true

        const activeIdSet = new Set(activeIds)
        setJobs((prev) =>
          prev.map((job) =>
            activeIdSet.has(job.id) ? { ...job, status: JobStatus.CANCELLING } : job
          )
        )
        setBulkCancelOpen(false)
        setBulkActionLoading(true)

        try {
          const result = await api.bulkCancelJobs(activeIds)
          const cancelledCount = result?.cancelledCount ?? result?.cancelled?.length ?? 0
          const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
          if (failedCount > 0) {
            toast.show(
              `Cancelled ${cancelledCount} job${cancelledCount !== 1 ? 's' : ''}, ${failedCount} failed`,
              'warning'
            )
          } else {
            toast.show(`Cancelled ${cancelledCount} job${cancelledCount !== 1 ? 's' : ''}`, 'success')
          }
          return result
        } catch (err) {
          toast.show(err.message || 'Failed to cancel jobs', 'error')
          throw err
        } finally {
          setBulkActionLoading(false)
          isUserActionInProgressRef.current = false
          fetchJobs(true)
        }
      },
    })
  }, [selectedIds, jobs, toast, fetchJobs, execute])

  const handleBulkDeleteOpen = useCallback(() => {
    if (!selectedIds.length) return undefined
    return executeUI('Review delete jobs', () => setBulkDeleteOpen(true), { count: selectedIds.length })
  }, [executeUI, selectedIds])

  const handleSelectionChange = useCallback((nextSelection) => {
    return executeUI('Select jobs', () => setSelectedIds(nextSelection), { count: nextSelection.length })
  }, [executeUI])

  const handleCancelConfirmClose = useCallback(() => {
    return executeUI('Close cancel confirmation', () => setCancelConfirmOpen(false))
  }, [executeUI])

  const handleBulkCancelClose = useCallback(() => {
    return executeUI('Close bulk cancel', () => setBulkCancelOpen(false))
  }, [executeUI])

  const handleBulkDeleteClose = useCallback(() => {
    return executeUI('Close bulk delete', () => setBulkDeleteOpen(false))
  }, [executeUI])

  const handleDetailsClose = useCallback(() => {
    return executeUI('Close job details', () => closeDetails())
  }, [executeUI, closeDetails])

  const handleDetailsDownload = useCallback(() => {
    return executeDownload('Download job output', () => {
      const url = detailsJob?.artifacts?.html_url
      if (url) {
        window.open(api.withBase(url), '_blank')
      } else {
        toast.show('Download not available', 'warning')
      }
    }, { jobId: detailsJob?.id, format: 'html' })
  }, [executeDownload, detailsJob, toast])

  const handleDetailsRetry = useCallback(() => {
    if (!detailsJob) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Retry job',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        jobId: detailsJob.id,
        action: 'retry_job',
        source: 'details',
      },
      action: async () => {
        setRetrying(true)
        try {
          await api.retryJob(detailsJob.id)
          toast.show('Job restarted successfully', 'success')
          setDetailsDialogOpen(false)
          fetchJobs()
        } catch (err) {
          toast.show(err.message || 'Failed to retry job', 'error')
          throw err
        } finally {
          setRetrying(false)
        }
      },
    })
  }, [detailsJob, toast, fetchJobs, execute])

  const handleBulkDeleteConfirm = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkDeleteOpen(false)
      return
    }
    const idsToDelete = [...selectedIds]
    const removedJobs = jobs.filter((job) => idsToDelete.includes(job.id))
    if (!removedJobs.length) {
      setBulkDeleteOpen(false)
      return
    }

    setBulkDeleteOpen(false)
    setSelectedIds([])

    if (bulkDeleteUndoRef.current?.timeoutId) {
      clearTimeout(bulkDeleteUndoRef.current.timeoutId)
      bulkDeleteUndoRef.current = null
    }

    isUserActionInProgressRef.current = true
    setJobs((prev) => prev.filter((job) => !idsToDelete.includes(job.id)))

    let undone = false
    const timeoutId = setTimeout(async () => {
      if (undone) return
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete jobs',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          jobIds: idsToDelete,
          action: 'bulk_delete_jobs',
        },
        action: async () => {
          setBulkActionLoading(true)
          try {
            const result = await api.bulkDeleteJobs(idsToDelete)
            const deletedCount = result?.deletedCount ?? result?.deleted?.length ?? 0
            const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
            if (failedCount > 0) {
              toast.show(
                `Removed ${deletedCount} job${deletedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
                'warning'
              )
            } else {
              toast.show(`Removed ${deletedCount} job${deletedCount !== 1 ? 's' : ''}`, 'success')
            }
            return result
          } catch (err) {
            setJobs((prev) => {
              const existing = new Set(prev.map((job) => job.id))
              const restored = removedJobs.filter((job) => !existing.has(job.id))
              return restored.length ? [...prev, ...restored] : prev
            })
            toast.show(err.message || 'Failed to delete jobs', 'error')
            throw err
          } finally {
            setBulkActionLoading(false)
            isUserActionInProgressRef.current = false
            bulkDeleteUndoRef.current = null
            fetchJobs(true)
          }
        },
      })
    }, 5000)

    bulkDeleteUndoRef.current = { timeoutId, ids: idsToDelete, jobs: removedJobs }

    toast.showWithUndo(
      `Removed ${idsToDelete.length} job${idsToDelete.length !== 1 ? 's' : ''} from history`,
      () => {
        undone = true
        clearTimeout(timeoutId)
        bulkDeleteUndoRef.current = null
        setJobs((prev) => {
          const existing = new Set(prev.map((job) => job.id))
          const restored = removedJobs.filter((job) => !existing.has(job.id))
          return restored.length ? [...prev, ...restored] : prev
        })
        isUserActionInProgressRef.current = false
        toast.show('Jobs restored', 'success')
      },
      { severity: 'info' }
    )
  }, [selectedIds, jobs, toast, fetchJobs, execute])

  const columns = useMemo(() => [
    {
      field: 'id',
      headerName: 'Job ID',
      width: 160,
      renderCell: (value) => (
        <MonoText>
          {value?.slice(0, 12)}...
        </MonoText>
      ),
    },
    {
      field: 'type',
      headerName: 'Type',
      width: 140,
      renderCell: (value) => {
        const typeLabels = {
          run_report: 'Report Run',
          verify_template: 'Verify Design',
          verify_excel: 'Verify Excel',
          recommend_templates: 'Recommendations',
          summary_generate: 'Summary',
          summary_report: 'Report Summary',
          chart_analyze: 'Chart Analyze',
          chart_generate: 'Chart Generate',
        }
        const label = typeLabels[value] || (value || 'report').replace(/_/g, ' ')
        return (
          <TypeChip
            label={label}
            size="small"
          />
        )
      },
    },
    {
      field: 'templateName',
      headerName: 'Design',
      width: 220,
      renderCell: (value, row) => (
        <Typography sx={{
          fontSize: '14px',
          color: 'text.secondary',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 200,
        }}>
          {value || row.templateId?.slice(0, 12) || '-'}
        </Typography>
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (value) => {
        const config = getStatusConfig(theme, value)
        const Icon = config.icon

        return (
          <StatusChip
            icon={<Icon sx={{ fontSize: 14 }} />}
            label={config.label}
            size="small"
            statusColor={config.color}
            statusBg={config.bgColor}
          />
        )
      },
    },
    {
      field: 'progress',
      headerName: 'Progress',
      width: 150,
      renderCell: (value, row) => {
        if (row.status === JobStatus.COMPLETED) {
          return (
            <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', fontWeight: 600 }}>
              100%
            </Typography>
          )
        }
        if (row.status === JobStatus.FAILED || row.status === JobStatus.CANCELLED) {
          return (
            <Typography sx={{ fontSize: '0.75rem', color: 'text.disabled' }}>
              -
            </Typography>
          )
        }
        const progress = value || 0
        return (
          <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1 }}>
            <StyledLinearProgress
              variant="determinate"
              value={progress}
              sx={{ flex: 1 }}
            />
            <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', minWidth: 32 }}>
              {progress}%
            </Typography>
          </Box>
        )
      },
    },
    {
      field: 'createdAt',
      headerName: 'Started',
      width: 160,
      renderCell: (value) => {
        if (!value) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(value)
        const now = new Date()
        const diffMs = now - d
        const diffMin = Math.floor(diffMs / 60000)
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        let relative
        if (diffMin < 1) relative = 'Just now'
        else if (diffMin < 60) relative = `${diffMin}m ago`
        else if (diffHr < 24) relative = `${diffHr}h ago`
        else if (diffDay < 7) relative = `${diffDay}d ago`
        else relative = d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
    {
      field: 'finishedAt',
      headerName: 'Completed',
      width: 160,
      renderCell: (value) => {
        if (!value) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(value)
        const now = new Date()
        const diffMs = now - d
        const diffMin = Math.floor(diffMs / 60000)
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        let relative
        if (diffMin < 1) relative = 'Just now'
        else if (diffMin < 60) relative = `${diffMin}m ago`
        else if (diffHr < 24) relative = `${diffHr}h ago`
        else if (diffDay < 7) relative = `${diffDay}d ago`
        else relative = d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
  ], [theme])

  const filters = useMemo(() => [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'pending', label: 'Pending' },
        { value: 'running', label: 'Running' },
        { value: 'completed', label: 'Completed' },
        { value: 'failed', label: 'Failed' },
        { value: 'cancelled', label: 'Cancelled' },
      ],
    },
    {
      key: 'type',
      label: 'Type',
      options: [
        { value: 'run_report', label: 'Report' },
        { value: 'verify_template', label: 'Verify Template' },
        { value: 'verify_excel', label: 'Verify Excel' },
        { value: 'recommend_templates', label: 'Recommendations' },
        { value: 'summary_generate', label: 'Summary' },
        { value: 'summary_report', label: 'Report Summary' },
        { value: 'chart_analyze', label: 'Chart Analyze' },
        { value: 'chart_generate', label: 'Chart Generate' },
      ],
    },
  ], [])

  const activeSelectedCount = useMemo(() => {
    const activeSet = new Set(['running', 'pending'])
    const jobLookup = new Map(jobs.map((job) => [job.id, job.status]))
    return selectedIds.filter((id) => activeSet.has(jobLookup.get(id))).length
  }, [jobs, selectedIds])

  const bulkActions = useMemo(() => ([
    {
      label: 'Cancel',
      icon: <CancelIcon sx={{ fontSize: 16 }} />,
      onClick: handleBulkCancelOpen,
      disabled: bulkActionLoading,
    },
  ]), [bulkActionLoading, handleBulkCancelOpen])

  const activeJobsCount = useMemo(() =>
    jobs.filter((j) => isActiveStatus(j.status)).length
  , [jobs])

  return {
    theme,
    jobs,
    loading,
    cancelConfirmOpen,
    menuAnchor,
    menuJob,
    detailsDialogOpen,
    detailsJob,
    retrying,
    selectedIds,
    bulkCancelOpen,
    bulkDeleteOpen,
    bulkActionLoading,
    columns,
    filters,
    activeSelectedCount,
    bulkActions,
    activeJobsCount,
    handleNavigate,
    handleOpenMenu,
    handleCloseMenu,
    handleRefresh,
    handleCancelClick,
    handleCancelConfirm,
    handleDownload,
    handleViewDetails,
    handleRowClick,
    handleRetry,
    handleBulkCancelConfirm,
    handleBulkDeleteOpen,
    handleSelectionChange,
    handleCancelConfirmClose,
    handleBulkCancelClose,
    handleBulkDeleteClose,
    handleDetailsClose,
    handleDetailsDownload,
    handleDetailsRetry,
    handleBulkDeleteConfirm,
  }
}

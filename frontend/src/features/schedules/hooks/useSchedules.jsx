/**
 * Custom hook for Schedules page state, effects, and handlers.
 */
import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Box, Typography, Stack } from '@mui/material'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import * as api from '@/api/client'
import {
  FREQUENCY_OPTIONS, FrequencyChip, StatusChip, StyledSwitch,
  isSchedulableTemplate,
} from '../components/ScheduleStyles'

export function useSchedules() {
  const toast = useToast()
  const { execute } = useInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const templates = useAppStore((s) => s.templates)
  const savedConnections = useAppStore((s) => s.savedConnections)
  const activeConnectionId = useAppStore((s) => s.activeConnectionId)

  const [schedules, setSchedules] = useState([])
  const [schedulableTemplates, setSchedulableTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState(null)

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [deletingSchedule, setDeletingSchedule] = useState(null)
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [menuSchedule, setMenuSchedule] = useState(null)
  const [togglingId, setTogglingId] = useState(null)
  const [schedulerStatus, setSchedulerStatus] = useState(null)

  const scheduleDeleteUndoRef = useRef(null)
  const didLoadSchedulesRef = useRef(false)
  const didLoadTemplatesRef = useRef(false)

  const templatesFromStore = useMemo(
    () => (Array.isArray(templates) ? templates.filter(isSchedulableTemplate) : []),
    [templates]
  )

  // ---- Data fetching ----

  const fetchSchedules = useCallback(async () => {
    setLoading(true)
    try {
      const schedulesData = await api.listSchedules()
      setSchedules(schedulesData || [])
    } catch (err) {
      toast.show(err.message || 'Failed to load schedules', 'error')
    } finally {
      setLoading(false)
    }
  }, [toast])

  const fetchSchedulerStatus = useCallback(async () => {
    try {
      const status = await api.getSchedulerStatus()
      setSchedulerStatus(status)
    } catch (err) {
      console.warn('Failed to fetch scheduler status:', err)
    }
  }, [])

  useEffect(() => {
    if (didLoadSchedulesRef.current) return
    didLoadSchedulesRef.current = true
    fetchSchedules()
    fetchSchedulerStatus()
  }, [fetchSchedules, fetchSchedulerStatus])

  const fetchTemplates = useCallback(async () => {
    try {
      const templatesData = await api.listApprovedTemplates()
      if (Array.isArray(templatesData) && templatesData.length > 0) {
        setSchedulableTemplates(templatesData)
        return
      }
      setSchedulableTemplates(templatesFromStore)
    } catch (err) {
      setSchedulableTemplates(templatesFromStore)
      toast.show(err.userMessage || err.message || 'Failed to load templates', 'error')
    }
  }, [templatesFromStore, toast])

  useEffect(() => {
    if (didLoadTemplatesRef.current) return
    didLoadTemplatesRef.current = true
    fetchTemplates()
  }, [fetchTemplates])

  useEffect(() => {
    if (schedulableTemplates.length > 0) return
    if (templatesFromStore.length > 0) {
      setSchedulableTemplates(templatesFromStore)
    }
  }, [schedulableTemplates.length, templatesFromStore])

  // ---- Derived state ----

  const templateParam = searchParams.get('template')
  const schedulableTemplateIds = useMemo(
    () => new Set(schedulableTemplates.map((template) => template.id)),
    [schedulableTemplates]
  )
  const defaultTemplateId = templateParam && schedulableTemplateIds.has(templateParam)
    ? templateParam
    : (schedulableTemplates[0]?.id || '')
  const defaultConnectionId = activeConnectionId || savedConnections[0]?.id || ''
  const canCreateSchedule = schedulableTemplates.length > 0 && savedConnections.length > 0

  // ---- URL param auto-open ----

  useEffect(() => {
    if (!templateParam) return
    if (schedulableTemplates.length > 0 && !schedulableTemplateIds.has(templateParam)) {
      toast.show('Selected template is not approved for scheduling. Choose an approved template.', 'warning')
    }
    setEditingSchedule(null)
    setDialogOpen(true)
    const nextParams = new URLSearchParams(searchParams)
    nextParams.delete('template')
    setSearchParams(nextParams, { replace: true })
  }, [templateParam, searchParams, schedulableTemplates, schedulableTemplateIds, setSearchParams, toast])

  // ---- Menu handlers ----

  const handleOpenMenu = useCallback((event, schedule) => {
    event.stopPropagation()
    setMenuAnchor(event.currentTarget)
    setMenuSchedule(schedule)
  }, [])

  const handleCloseMenu = useCallback(() => {
    setMenuAnchor(null)
    setMenuSchedule(null)
  }, [])

  // ---- CRUD handlers ----

  const handleAddSchedule = useCallback(() => {
    if (schedulableTemplates.length === 0) {
      toast.show('No approved templates available. Approve a template first.', 'warning')
      return
    }
    if (savedConnections.length === 0) {
      toast.show('No connections available. Add a connection first.', 'warning')
      return
    }
    setEditingSchedule(null)
    setDialogOpen(true)
  }, [schedulableTemplates.length, savedConnections.length, toast])

  const handleEditSchedule = useCallback(() => {
    setEditingSchedule(menuSchedule)
    setDialogOpen(true)
    handleCloseMenu()
  }, [menuSchedule, handleCloseMenu])

  const handleDeleteClick = useCallback(() => {
    setDeletingSchedule(menuSchedule)
    setDeleteConfirmOpen(true)
    handleCloseMenu()
  }, [menuSchedule, handleCloseMenu])

  const handleToggleSchedule = useCallback(
    async (schedule, nextActive) => {
      if (!schedule) return
      execute({
        type: InteractionType.UPDATE,
        label: `${nextActive ? 'Enable' : 'Pause'} schedule "${schedule.name || schedule.id}"`,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        successMessage: `Schedule ${nextActive ? 'enabled' : 'paused'}`,
        errorMessage: 'Failed to update schedule',
        action: async () => {
          setTogglingId(schedule.id)
          try {
            await api.updateSchedule(schedule.id, { active: nextActive })
            await fetchSchedules()
          } finally { setTogglingId(null) }
        },
      })
    },
    [fetchSchedules, execute]
  )

  const handleToggleEnabled = useCallback(async () => {
    if (!menuSchedule) return
    const currentActive = menuSchedule.active ?? menuSchedule.enabled ?? true
    await handleToggleSchedule(menuSchedule, !currentActive)
    handleCloseMenu()
  }, [menuSchedule, handleCloseMenu, handleToggleSchedule])

  const handleRunNow = useCallback(async () => {
    if (!menuSchedule) return
    handleCloseMenu()
    try {
      const result = await api.triggerSchedule(menuSchedule.id)
      if (result?.status === 'triggered') {
        toast.show(`Schedule "${menuSchedule.name}" triggered`, 'success')
        navigate('/jobs')
      } else {
        toast.show('Schedule triggered', 'success')
      }
    } catch (err) {
      toast.show(err?.response?.data?.detail?.message || 'Failed to trigger schedule', 'error')
    }
  }, [menuSchedule, handleCloseMenu, toast, navigate])

  const handleSaveSchedule = useCallback(
    async (data) => {
      const isEditing = !!editingSchedule
      const result = await execute({
        type: isEditing ? InteractionType.UPDATE : InteractionType.CREATE,
        label: isEditing ? `Update schedule "${data.name}"` : `Create schedule "${data.name}"`,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        successMessage: isEditing ? 'Schedule updated' : 'Schedule created',
        errorMessage: 'Failed to save schedule',
        action: async () => {
          if (isEditing) {
            await api.updateSchedule(editingSchedule.id, data)
          } else {
            await api.createSchedule(data)
          }
          await fetchSchedules()
        },
      })
      if (!result?.success) {
        throw result?.error || new Error('Failed to save schedule')
      }
    },
    [editingSchedule, fetchSchedules, execute]
  )

  const handleDeleteConfirm = useCallback(async () => {
    if (!deletingSchedule) return
    const scheduleToDelete = deletingSchedule
    const scheduleIndex = schedules.findIndex((item) => item.id === scheduleToDelete.id)

    setDeleteConfirmOpen(false)
    setDeletingSchedule(null)

    if (scheduleDeleteUndoRef.current?.timeoutId) {
      clearTimeout(scheduleDeleteUndoRef.current.timeoutId)
      scheduleDeleteUndoRef.current = null
    }

    execute({
      type: InteractionType.DELETE,
      label: `Delete schedule "${scheduleToDelete.name || scheduleToDelete.id}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: 'Schedule removed',
      errorMessage: 'Failed to delete schedule',
      action: async () => {
        setSchedules((prev) => prev.filter((item) => item.id !== scheduleToDelete.id))

        let undone = false
        const timeoutId = setTimeout(async () => {
          if (undone) return
          try {
            await api.deleteSchedule(scheduleToDelete.id)
            fetchSchedules()
          } catch (err) {
            setSchedules((prev) => {
              if (prev.some((item) => item.id === scheduleToDelete.id)) return prev
              const next = [...prev]
              if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
                next.splice(scheduleIndex, 0, scheduleToDelete)
              } else {
                next.push(scheduleToDelete)
              }
              return next
            })
            throw err
          } finally {
            scheduleDeleteUndoRef.current = null
          }
        }, 5000)

        scheduleDeleteUndoRef.current = { timeoutId, schedule: scheduleToDelete }

        toast.showWithUndo(
          `Schedule "${scheduleToDelete.name || scheduleToDelete.id}" removed`,
          () => {
            undone = true
            clearTimeout(timeoutId)
            scheduleDeleteUndoRef.current = null
            setSchedules((prev) => {
              if (prev.some((item) => item.id === scheduleToDelete.id)) return prev
              const next = [...prev]
              if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
                next.splice(scheduleIndex, 0, scheduleToDelete)
              } else {
                next.push(scheduleToDelete)
              }
              return next
            })
            toast.show('Schedule restored', 'success')
          },
          { severity: 'info' }
        )
      },
    })
  }, [deletingSchedule, schedules, fetchSchedules, execute, toast])

  // ---- Table columns ----

  const columns = useMemo(
    () => [
      {
        field: 'name',
        headerName: 'Schedule',
        renderCell: (value, row) => (
          <Box>
            <Typography variant="body2" fontWeight={600}>
              {value || row.id}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {templates.find((t) => t.id === row.template_id)?.name || row.template_name || row.template_id}
            </Typography>
          </Box>
        ),
      },
      {
        field: 'frequency',
        headerName: 'Frequency',
        width: 120,
        renderCell: (value) => {
          const option = FREQUENCY_OPTIONS.find((opt) => opt.value === value)
          const label = option?.label || value || 'daily'
          return <FrequencyChip label={label} size="small" />
        },
      },
      {
        field: 'enabled',
        headerName: 'Status',
        width: 140,
        renderCell: (value, row) => {
          const active = row.active ?? value ?? true
          return (
            <Stack direction="row" alignItems="center" spacing={1}>
              <StyledSwitch
                size="small"
                checked={active}
                disabled={togglingId === row.id}
                onChange={(e) => {
                  e.stopPropagation()
                  handleToggleSchedule(row, e.target.checked)
                }}
              />
              <StatusChip label={active ? 'Active' : 'Paused'} size="small" active={active} />
            </Stack>
          )
        },
      },
      {
        field: 'last_run',
        headerName: 'Last Run',
        width: 180,
        renderCell: (value, row) => {
          const lastRun = value || row.last_run_at
          return (
            <Typography variant="body2" color={lastRun ? 'text.primary' : 'text.secondary'}>
              {lastRun ? new Date(lastRun).toLocaleString(undefined, { timeZoneName: 'short' }) : 'Never'}
            </Typography>
          )
        },
      },
      {
        field: 'next_run',
        headerName: 'Next Run',
        width: 220,
        renderCell: (value, row) => {
          const active = row.active ?? row.enabled ?? true
          const nextRun = value || row.next_run_at
          return (
            <Typography variant="body2" color={active && nextRun ? 'text.primary' : 'text.secondary'}>
              {active && nextRun ? new Date(nextRun).toLocaleString(undefined, { timeZoneName: 'short' }) : '-'}
            </Typography>
          )
        },
      },
    ],
    [templates, handleToggleSchedule, togglingId]
  )

  const filters = useMemo(
    () => [
      { key: 'frequency', label: 'Frequency', options: FREQUENCY_OPTIONS },
      { key: 'active', label: 'Status', options: [{ value: true, label: 'Active' }, { value: false, label: 'Paused' }] },
    ],
    []
  )

  const menuScheduleActive = menuSchedule?.active ?? menuSchedule?.enabled ?? true

  return {
    // Data
    schedules, schedulableTemplates, loading, schedulerStatus,
    templates, savedConnections,
    defaultTemplateId, defaultConnectionId, canCreateSchedule,
    columns, filters,
    // Dialog state
    dialogOpen, setDialogOpen, editingSchedule,
    deleteConfirmOpen, setDeleteConfirmOpen, deletingSchedule,
    // Menu state
    menuAnchor, menuScheduleActive,
    // Handlers
    handleOpenMenu, handleCloseMenu,
    handleAddSchedule, handleEditSchedule, handleDeleteClick,
    handleToggleEnabled, handleRunNow,
    handleSaveSchedule, handleDeleteConfirm,
    toast,
  }
}

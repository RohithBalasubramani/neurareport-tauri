import { useCallback, useRef, useState } from 'react'
import { useEffect } from 'react'
import { InteractionType, Reversibility } from '@/components/ux/governance'
import {
  listSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
} from '@/api/client'
import {
  parseEmailTargets,
  getTemplateKind,
} from '../utils/templatesPaneUtils'

export function useSchedules({ toast, execute }) {
  const [schedules, setSchedules] = useState([])
  const [schedulesLoading, setSchedulesLoading] = useState(false)
  const [scheduleSaving, setScheduleSaving] = useState(false)
  const [deletingScheduleId, setDeletingScheduleId] = useState(null)
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [editScheduleFields, setEditScheduleFields] = useState({})
  const [scheduleUpdating, setScheduleUpdating] = useState(false)
  const scheduleDeleteUndoRef = useRef(null)
  const [deleteScheduleConfirmOpen, setDeleteScheduleConfirmOpen] = useState(false)
  const [scheduleToDelete, setScheduleToDelete] = useState(null)
  const [scheduleName, setScheduleName] = useState('')
  const [scheduleFrequency, setScheduleFrequency] = useState('daily')

  const refreshSchedules = useCallback(async () => {
    setSchedulesLoading(true)
    try {
      const data = await listSchedules()
      setSchedules(Array.isArray(data) ? data : [])
    } catch (e) {
      toast.show(String(e), 'error')
    } finally {
      setSchedulesLoading(false)
    }
  }, [toast])

  useEffect(() => {
    refreshSchedules()
  }, [refreshSchedules])

  const handleCreateSchedule = async ({
    selectedTemplates,
    start,
    end,
    activeConnectionId,
    startSql,
    endSql,
    buildKeyFiltersForTemplate,
    batchIdsFor,
    emailTargets,
    emailSubject,
    emailMessage,
  }) => {
    if (selectedTemplates.length !== 1) {
      toast.show('Select exactly one design to create a schedule.', 'warning')
      return
    }
    if (!start || !end) {
      toast.show('Choose a start and end date before scheduling.', 'warning')
      return
    }
    if (!activeConnectionId) {
      toast.show('Select a connection before scheduling.', 'warning')
      return
    }
    if (!startSql || !endSql) {
      toast.show('Provide a valid date range.', 'warning')
      return
    }
    const template = selectedTemplates[0]
    const keyFilters = buildKeyFiltersForTemplate(template.id)
    const emailList = parseEmailTargets(emailTargets)
    await execute({
      type: InteractionType.CREATE,
      label: 'Create schedule',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId: template.id,
        connectionId: activeConnectionId,
        action: 'create_schedule',
      },
      action: async () => {
        setScheduleSaving(true)
        try {
          await createSchedule({
            templateId: template.id,
            connectionId: activeConnectionId,
            startDate: startSql,
            endDate: endSql,
            keyValues: Object.keys(keyFilters).length ? keyFilters : undefined,
            batchIds: batchIdsFor(template.id),
            docx: true,
            xlsx: getTemplateKind(template) === 'excel',
            emailRecipients: emailList.length ? emailList : undefined,
            emailSubject: emailSubject || undefined,
            emailMessage: emailMessage || undefined,
            frequency: scheduleFrequency,
            name: scheduleName || undefined,
          })
          toast.show('Scheduled job created. The first run will begin soon.', 'success')
          refreshSchedules()
        } catch (e) {
          toast.show(String(e), 'error')
          throw e
        } finally {
          setScheduleSaving(false)
        }
      },
    })
  }

  const handleDeleteScheduleRequest = useCallback((schedule) => {
    if (!schedule?.id) return
    setScheduleToDelete(schedule)
    setDeleteScheduleConfirmOpen(true)
  }, [])

  const handleDeleteScheduleConfirm = useCallback(async () => {
    if (!scheduleToDelete?.id) {
      setDeleteScheduleConfirmOpen(false)
      return
    }
    const schedule = scheduleToDelete
    const scheduleId = schedule.id
    const scheduleIndex = schedules.findIndex((item) => item.id === scheduleId)
    setDeleteScheduleConfirmOpen(false)
    setScheduleToDelete(null)

    if (scheduleDeleteUndoRef.current?.timeoutId) {
      clearTimeout(scheduleDeleteUndoRef.current.timeoutId)
      scheduleDeleteUndoRef.current = null
    }

    setSchedules((prev) => prev.filter((item) => item.id !== scheduleId))

    let undone = false
    const timeoutId = setTimeout(async () => {
      if (undone) return
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete schedule',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          scheduleId,
          action: 'delete_schedule',
        },
        action: async () => {
          setDeletingScheduleId(scheduleId)
          try {
            await deleteSchedule(scheduleId)
            toast.show('Schedule removed. Future runs stopped; past downloads remain.', 'success')
            refreshSchedules()
          } catch (e) {
            setSchedules((prev) => {
              if (prev.some((item) => item.id === scheduleId)) return prev
              const next = [...prev]
              if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
                next.splice(scheduleIndex, 0, schedule)
              } else {
                next.push(schedule)
              }
              return next
            })
            toast.show(String(e), 'error')
            throw e
          } finally {
            setDeletingScheduleId(null)
            scheduleDeleteUndoRef.current = null
          }
        },
      })
    }, 5000)

    scheduleDeleteUndoRef.current = { timeoutId, schedule }

    toast.showWithUndo(
      `Schedule "${schedule.name || schedule.template_name || schedule.template_id}" removed`,
      () => {
        undone = true
        clearTimeout(timeoutId)
        scheduleDeleteUndoRef.current = null
        setSchedules((prev) => {
          if (prev.some((item) => item.id === scheduleId)) return prev
          const next = [...prev]
          if (scheduleIndex >= 0 && scheduleIndex <= next.length) {
            next.splice(scheduleIndex, 0, schedule)
          } else {
            next.push(schedule)
          }
          return next
        })
        toast.show('Schedule restored', 'success')
      },
      { severity: 'info' }
    )
  }, [scheduleToDelete, schedules, toast, refreshSchedules, execute])

  const handleOpenEditSchedule = (schedule) => {
    setEditingSchedule(schedule)
    setEditScheduleFields({
      name: schedule.name || '',
      frequency: schedule.frequency || 'daily',
      active: schedule.active !== false,
    })
  }

  const handleCloseEditSchedule = () => {
    setEditingSchedule(null)
    setEditScheduleFields({})
  }

  const handleUpdateSchedule = async () => {
    if (!editingSchedule) return
    await execute({
      type: InteractionType.UPDATE,
      label: 'Update schedule',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        scheduleId: editingSchedule.id,
        action: 'update_schedule',
      },
      action: async () => {
        setScheduleUpdating(true)
        try {
          const payload = {}
          if (editScheduleFields.name !== (editingSchedule.name || '')) {
            payload.name = editScheduleFields.name || null
          }
          if (editScheduleFields.frequency !== (editingSchedule.frequency || 'daily')) {
            payload.frequency = editScheduleFields.frequency
          }
          if (editScheduleFields.active !== (editingSchedule.active !== false)) {
            payload.active = editScheduleFields.active
          }
          if (Object.keys(payload).length === 0) {
            toast.show('No changes to save.', 'info')
            handleCloseEditSchedule()
            return
          }
          await updateSchedule(editingSchedule.id, payload)
          toast.show('Schedule updated.', 'success')
          refreshSchedules()
          handleCloseEditSchedule()
        } catch (e) {
          toast.show(String(e), 'error')
          throw e
        } finally {
          setScheduleUpdating(false)
        }
      },
    })
  }

  return {
    schedules,
    schedulesLoading,
    scheduleSaving,
    deletingScheduleId,
    editingSchedule,
    editScheduleFields,
    setEditScheduleFields,
    scheduleUpdating,
    deleteScheduleConfirmOpen,
    setDeleteScheduleConfirmOpen,
    scheduleToDelete,
    setScheduleToDelete,
    scheduleName,
    setScheduleName,
    scheduleFrequency,
    setScheduleFrequency,
    handleCreateSchedule,
    handleDeleteScheduleRequest,
    handleDeleteScheduleConfirm,
    handleOpenEditSchedule,
    handleCloseEditSchedule,
    handleUpdateSchedule,
  }
}

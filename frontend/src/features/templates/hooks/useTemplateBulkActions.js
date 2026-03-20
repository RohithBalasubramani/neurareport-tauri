/**
 * Hook: Bulk actions — select, delete, status, tags
 */
import { useState, useCallback, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import * as api from '@/api/client'

export default function useTemplateBulkActions({ templates, setTemplates, fetchTemplatesData }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const [selectedIds, setSelectedIds] = useState([])
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const [bulkStatusOpen, setBulkStatusOpen] = useState(false)
  const [bulkStatus, setBulkStatus] = useState('approved')
  const [bulkTagsOpen, setBulkTagsOpen] = useState(false)
  const [bulkTags, setBulkTags] = useState('')
  const [bulkActionLoading, setBulkActionLoading] = useState(false)
  const bulkDeleteUndoRef = useRef(null)

  const handleBulkDeleteOpen = useCallback(() => {
    if (!selectedIds.length) return
    setBulkDeleteOpen(true)
  }, [selectedIds])

  const handleBulkDeleteConfirm = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkDeleteOpen(false)
      return
    }

    const idsToDelete = [...selectedIds]
    const count = idsToDelete.length
    const removedTemplates = templates.filter((tpl) => idsToDelete.includes(tpl.id))
    if (!removedTemplates.length) {
      setBulkDeleteOpen(false)
      return
    }

    setBulkDeleteOpen(false)
    setSelectedIds([])

    if (bulkDeleteUndoRef.current?.timeoutId) {
      clearTimeout(bulkDeleteUndoRef.current.timeoutId)
      bulkDeleteUndoRef.current = null
    }

    execute({
      type: InteractionType.DELETE,
      label: `Delete ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      errorMessage: 'Failed to remove designs',
      action: async () => {
        setTemplates((prev) => prev.filter((tpl) => !idsToDelete.includes(tpl.id)))

        let undone = false
        const timeoutId = setTimeout(async () => {
          if (undone) return
          setBulkActionLoading(true)
          try {
            const result = await api.bulkDeleteTemplates(idsToDelete)
            const deletedCount = result?.deletedCount ?? result?.deleted?.length ?? 0
            const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
            if (failedCount > 0) {
              toast.show(
                `Removed ${deletedCount} design${deletedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
                'warning'
              )
            } else {
              toast.show(`Removed ${deletedCount} design${deletedCount !== 1 ? 's' : ''}`, 'success')
            }
            await fetchTemplatesData()
          } catch (err) {
            setTemplates((prev) => {
              const existing = new Set(prev.map((tpl) => tpl.id))
              const restored = removedTemplates.filter((tpl) => !existing.has(tpl.id))
              return restored.length ? [...prev, ...restored] : prev
            })
            throw err
          } finally {
            setBulkActionLoading(false)
          }
        }, 5000)

        bulkDeleteUndoRef.current = { timeoutId, ids: idsToDelete, templates: removedTemplates }

        toast.showWithUndo(
          `Removed ${count} design${count !== 1 ? 's' : ''}`,
          () => {
            undone = true
            clearTimeout(timeoutId)
            bulkDeleteUndoRef.current = null
            setTemplates((prev) => {
              const existing = new Set(prev.map((tpl) => tpl.id))
              const restored = removedTemplates.filter((tpl) => !existing.has(tpl.id))
              return restored.length ? [...prev, ...restored] : prev
            })
            toast.show('Designs restored', 'success')
          },
          { severity: 'info' }
        )
      },
    })
  }, [selectedIds, templates, toast, fetchTemplatesData, execute, setTemplates])

  const handleBulkStatusApply = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkStatusOpen(false)
      return
    }

    const count = selectedIds.length
    setBulkStatusOpen(false)

    execute({
      type: InteractionType.UPDATE,
      label: `Update status for ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to update status',
      action: async () => {
        setBulkActionLoading(true)
        try {
          const result = await api.bulkUpdateTemplateStatus(selectedIds, bulkStatus)
          const updatedCount = result?.updatedCount ?? result?.updated?.length ?? 0
          const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
          if (failedCount > 0) {
            toast.show(
              `Updated ${updatedCount} design${updatedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
              'warning'
            )
          } else {
            toast.show(
              `Updated ${updatedCount} design${updatedCount !== 1 ? 's' : ''}`,
              'success'
            )
          }
          await fetchTemplatesData()
        } finally {
          setBulkActionLoading(false)
        }
      },
    })
  }, [selectedIds, bulkStatus, toast, fetchTemplatesData, execute])

  const handleBulkTagsApply = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkTagsOpen(false)
      return
    }
    const tags = bulkTags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)
    if (!tags.length) {
      toast.show('Enter at least one tag', 'error')
      return
    }
    const invalidTag = tags.find((tag) => tag.length > 50)
    if (invalidTag) {
      toast.show(`Tag "${invalidTag.slice(0, 20)}..." exceeds 50 character limit`, 'error')
      return
    }

    const count = selectedIds.length
    setBulkTagsOpen(false)

    execute({
      type: InteractionType.UPDATE,
      label: `Add tags to ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to add tags',
      action: async () => {
        setBulkActionLoading(true)
        try {
          const result = await api.bulkAddTemplateTags(selectedIds, tags)
          const updatedCount = result?.updatedCount ?? result?.updated?.length ?? 0
          const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
          if (failedCount > 0) {
            toast.show(
              `Tagged ${updatedCount} design${updatedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
              'warning'
            )
          } else {
            toast.show(
              `Tagged ${updatedCount} design${updatedCount !== 1 ? 's' : ''}`,
              'success'
            )
          }
          await fetchTemplatesData()
          setBulkTags('')
        } finally {
          setBulkActionLoading(false)
        }
      },
    })
  }, [selectedIds, bulkTags, toast, fetchTemplatesData, execute])

  return {
    selectedIds,
    setSelectedIds,
    bulkDeleteOpen,
    setBulkDeleteOpen,
    bulkStatusOpen,
    setBulkStatusOpen,
    bulkStatus,
    setBulkStatus,
    bulkTagsOpen,
    setBulkTagsOpen,
    bulkTags,
    setBulkTags,
    bulkActionLoading,
    handleBulkDeleteOpen,
    handleBulkDeleteConfirm,
    handleBulkStatusApply,
    handleBulkTagsApply,
  }
}

/**
 * Hook: Row-level actions — delete, menu, duplicate, export, edit
 */
import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import * as api from '@/api/client'

export default function useTemplateActions({ templates, removeTemplate, setTemplates, fetchTemplatesData, handleNavigate }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [deletingTemplate, setDeletingTemplate] = useState(null)
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [menuTemplate, setMenuTemplate] = useState(null)
  const [duplicating, setDuplicating] = useState(false)

  const handleOpenMenu = useCallback((event, template) => {
    event.stopPropagation()
    setMenuAnchor(event.currentTarget)
    setMenuTemplate(template)
  }, [])

  const handleCloseMenu = useCallback(() => {
    setMenuAnchor(null)
    setMenuTemplate(null)
  }, [])

  const handleEditTemplate = useCallback(() => {
    if (menuTemplate) {
      handleNavigate(`/templates/${menuTemplate.id}/edit`, 'Edit template', { templateId: menuTemplate.id })
    }
    handleCloseMenu()
  }, [menuTemplate, handleNavigate, handleCloseMenu])

  const handleDeleteClick = useCallback(() => {
    setDeletingTemplate(menuTemplate)
    setDeleteConfirmOpen(true)
    handleCloseMenu()
  }, [menuTemplate, handleCloseMenu])

  const handleDeleteConfirm = useCallback(async () => {
    if (!deletingTemplate) return
    const templateToDelete = deletingTemplate
    const templateData = templates.find((t) => t.id === templateToDelete.id)

    setDeleteConfirmOpen(false)
    setDeletingTemplate(null)

    execute({
      type: InteractionType.DELETE,
      label: `Delete design "${templateToDelete.name || templateToDelete.id}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      suppressSuccessToast: true,
      blocksNavigation: false,
      action: async () => {
        removeTemplate(templateToDelete.id)

        let undone = false
        const deleteTimeout = setTimeout(async () => {
          if (undone) return
          try {
            await api.deleteTemplate(templateToDelete.id)
          } catch (err) {
            if (templateData) {
              setTemplates((prev) => [...prev, templateData])
            }
            throw err
          }
        }, 5000)

        toast.showWithUndo(
          `"${templateToDelete.name || templateToDelete.id}" removed`,
          () => {
            undone = true
            clearTimeout(deleteTimeout)
            if (templateData) {
              setTemplates((prev) => [...prev, templateData])
            }
            toast.show('Design restored', 'success')
          },
          { severity: 'info' }
        )
      },
    })
  }, [deletingTemplate, templates, removeTemplate, setTemplates, toast, execute])

  const handleExport = useCallback(async () => {
    if (!menuTemplate) return
    const templateToExport = menuTemplate
    handleCloseMenu()

    execute({
      type: InteractionType.DOWNLOAD,
      label: `Export design "${templateToExport.name || templateToExport.id}"`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      successMessage: 'Design exported',
      errorMessage: 'Failed to export design',
      action: async () => {
        await api.exportTemplateZip(templateToExport.id)
      },
    })
  }, [menuTemplate, handleCloseMenu, execute])

  const handleDuplicate = useCallback(async () => {
    if (!menuTemplate) return
    const templateToDuplicate = menuTemplate
    handleCloseMenu()

    execute({
      type: InteractionType.CREATE,
      label: `Duplicate design "${templateToDuplicate.name || templateToDuplicate.id}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to copy design',
      action: async () => {
        setDuplicating(true)
        try {
          const result = await api.duplicateTemplate(templateToDuplicate.id)
          const duplicatedName = result?.name || (templateToDuplicate.name ? `${templateToDuplicate.name} (Copy)` : 'Design (Copy)')
          await fetchTemplatesData()
          toast.show(`Design copied as "${duplicatedName}"`, 'success')
        } finally {
          setDuplicating(false)
        }
      },
    })
  }, [menuTemplate, toast, handleCloseMenu, fetchTemplatesData, execute])

  return {
    deleteConfirmOpen,
    setDeleteConfirmOpen,
    deletingTemplate,
    menuAnchor,
    menuTemplate,
    duplicating,
    handleOpenMenu,
    handleCloseMenu,
    handleEditTemplate,
    handleDeleteClick,
    handleDeleteConfirm,
    handleExport,
    handleDuplicate,
  }
}

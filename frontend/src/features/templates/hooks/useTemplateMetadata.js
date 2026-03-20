/**
 * Hook: Edit template metadata dialog
 */
import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import * as api from '@/api/client'

export default function useTemplateMetadata({ updateTemplate }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const [metadataOpen, setMetadataOpen] = useState(false)
  const [metadataTemplate, setMetadataTemplate] = useState(null)
  const [metadataForm, setMetadataForm] = useState({ name: '', description: '', tags: '', status: 'approved' })
  const [metadataSaving, setMetadataSaving] = useState(false)

  const openMetadataDialog = useCallback((template) => {
    setMetadataTemplate(template)
    setMetadataForm({
      name: template.name || '',
      description: template.description || '',
      tags: Array.isArray(template.tags) ? template.tags.join(', ') : '',
      status: template.status || 'approved',
    })
    setMetadataOpen(true)
  }, [])

  const handleMetadataSave = useCallback(async () => {
    if (!metadataTemplate) return
    const trimmedName = metadataForm.name.trim()
    if (!trimmedName) {
      toast.show('Design name is required', 'error')
      return
    }
    if (trimmedName.length > 200) {
      toast.show('Design name must be 200 characters or less', 'error')
      return
    }
    const tags = metadataForm.tags
      ? metadataForm.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
      : []
    const invalidTag = tags.find((tag) => tag.length > 50)
    if (invalidTag) {
      toast.show(`Tag "${invalidTag.slice(0, 20)}..." exceeds 50 character limit`, 'error')
      return
    }

    const payload = {
      name: trimmedName,
      description: metadataForm.description.trim() || undefined,
      status: metadataForm.status,
      tags,
    }

    execute({
      type: InteractionType.UPDATE,
      label: `Update design details "${trimmedName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Design details updated',
      errorMessage: 'Failed to update design details',
      action: async () => {
        setMetadataSaving(true)
        try {
          const result = await api.updateTemplateMetadata(metadataTemplate.id, payload)
          const updated = result?.template || { ...metadataTemplate, ...payload }
          updateTemplate(metadataTemplate.id, (tpl) => ({ ...tpl, ...updated }))
          setMetadataOpen(false)
        } finally {
          setMetadataSaving(false)
        }
      },
    })
  }, [metadataTemplate, metadataForm, updateTemplate, execute])

  return {
    metadataOpen,
    setMetadataOpen,
    metadataForm,
    setMetadataForm,
    metadataSaving,
    handleMetadataSave,
    openMetadataDialog,
  }
}

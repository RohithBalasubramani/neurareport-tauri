/**
 * Hook: Similar templates discovery
 */
import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'

export default function useSimilarTemplates({ handleNavigate }) {
  const toast = useToast()

  const [similarOpen, setSimilarOpen] = useState(false)
  const [similarTemplate, setSimilarTemplate] = useState(null)
  const [similarTemplates, setSimilarTemplates] = useState([])
  const [similarLoading, setSimilarLoading] = useState(false)

  const handleViewSimilar = useCallback(async (template) => {
    setSimilarTemplate(template)
    setSimilarOpen(true)
    setSimilarLoading(true)
    setSimilarTemplates([])
    try {
      const response = await api.getSimilarTemplates(template.id)
      setSimilarTemplates(response.similar || [])
    } catch (err) {
      console.error('Failed to fetch similar designs:', err)
      toast.show('Failed to load similar designs', 'error')
    } finally {
      setSimilarLoading(false)
    }
  }, [toast])

  const handleSelectSimilarTemplate = useCallback((template) => {
    setSimilarOpen(false)
    handleNavigate(`/reports?template=${template.id}`, 'Open reports', { templateId: template.id })
  }, [handleNavigate])

  return {
    similarOpen,
    setSimilarOpen,
    similarTemplate,
    similarTemplates,
    similarLoading,
    handleViewSimilar,
    handleSelectSimilarTemplate,
  }
}

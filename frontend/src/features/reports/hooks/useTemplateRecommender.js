import { useState, useCallback } from 'react'
import { recommendTemplates, queueRecommendTemplates } from '@/api/client'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useTemplateRecommender({ onSelectTemplate }) {
  const { execute } = useInteraction()
  const [expanded, setExpanded] = useState(false)
  const [requirement, setRequirement] = useState('')
  const [loading, setLoading] = useState(false)
  const [queueing, setQueueing] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [error, setError] = useState(null)
  const toast = useToast()

  const executeUI = useCallback(
    (label, action, intent = {}) =>
      execute({
        type: InteractionType.EXECUTE,
        label,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: { source: 'template_recommender', ...intent },
        action,
      }),
    [execute]
  )

  const handleSearch = useCallback(() => {
    const trimmed = requirement.trim()
    if (!trimmed) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Recommend templates',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'template_recommender', action: 'recommend_templates', requirement: trimmed },
      action: async () => {
        setLoading(true)
        setError(null)
        setRecommendations([])

        try {
          const results = await recommendTemplates({
            requirement: trimmed,
            limit: 5,
          })
          const normalized = Array.isArray(results) ? results : []
          setRecommendations(normalized)
          if (!normalized.length) {
            setError('No matching templates found. Try a different description.')
          }
          return normalized
        } catch (err) {
          setError(err.message || 'Failed to get recommendations')
          throw err
        } finally {
          setLoading(false)
        }
      },
    })
  }, [execute, requirement])

  const handleQueue = useCallback(() => {
    const trimmed = requirement.trim()
    if (!trimmed) return undefined

    return execute({
      type: InteractionType.GENERATE,
      label: 'Queue template recommendations',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'template_recommender', action: 'queue_recommendations', requirement: trimmed },
      action: async () => {
        setQueueing(true)
        setError(null)
        try {
          const response = await queueRecommendTemplates({
            requirement: trimmed,
            limit: 5,
          })
          if (response?.job_id) {
            toast.show('Recommendation job queued. Track it in Jobs.', 'success')
          } else {
            toast.show('Failed to queue recommendation job.', 'error')
          }
          return response
        } catch (err) {
          toast.show(err.message || 'Failed to queue recommendations', 'error')
          throw err
        } finally {
          setQueueing(false)
        }
      },
    })
  }, [execute, requirement, toast])

  const handleSelect = useCallback(
    (template) =>
      executeUI(
        'Select recommended template',
        () => {
          onSelectTemplate?.(template)
          setExpanded(false)
        },
        { templateId: template?.id }
      ),
    [executeUI, onSelectTemplate]
  )

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSearch()
      }
    },
    [handleSearch]
  )

  return {
    expanded,
    setExpanded,
    requirement,
    setRequirement,
    loading,
    queueing,
    recommendations,
    error,
    setError,
    executeUI,
    handleSearch,
    handleQueue,
    handleSelect,
    handleKeyDown,
  }
}

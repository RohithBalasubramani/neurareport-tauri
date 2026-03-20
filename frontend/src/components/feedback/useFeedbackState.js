/**
 * Hook for managing feedback panel state
 */
import { useState, useCallback } from 'react'
import { submitFeedback } from '@/api/feedback'

export default function useFeedbackState({ entityId, source = 'docqa', showCorrection, onSubmit }) {
  const [feedbackType, setFeedbackType] = useState(null) // 'positive' | 'negative'
  const [rating, setRating] = useState(0)
  const [correctionText, setCorrectionText] = useState('')
  const [showCorrectionField, setShowCorrectionField] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleThumb = useCallback((type) => {
    if (submitted) return
    setFeedbackType((prev) => (prev === type ? null : type))
    if (type === 'negative' && showCorrection) {
      setShowCorrectionField(true)
    }
  }, [submitted, showCorrection])

  const handleSubmit = useCallback(async () => {
    if (!feedbackType || !entityId) return
    setSubmitting(true)
    try {
      await submitFeedback(source, entityId, feedbackType, {
        rating: rating > 0 ? rating : null,
        correctionText: correctionText.trim() || null,
        tags: [],
      })
      setSubmitted(true)
      onSubmit?.({ feedbackType, rating, correctionText })
    } catch (err) {
      console.error('Failed to submit feedback:', err)
    } finally {
      setSubmitting(false)
    }
  }, [feedbackType, entityId, source, rating, correctionText, onSubmit])

  return {
    feedbackType,
    rating,
    setRating,
    correctionText,
    setCorrectionText,
    showCorrectionField,
    setShowCorrectionField,
    submitting,
    submitted,
    handleThumb,
    handleSubmit,
  }
}

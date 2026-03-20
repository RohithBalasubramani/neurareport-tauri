import { useCallback, useState } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { askQuestion } from '../services/enhancedAnalyzeApi'

export default function useAnalysisQA({ analysisId }) {
  const [question, setQuestion] = useState('')
  const [isAskingQuestion, setIsAskingQuestion] = useState(false)
  const [qaHistory, setQaHistory] = useState([])
  const [suggestedQuestions, setSuggestedQuestions] = useState([])

  const toast = useToast()
  const { execute } = useInteraction()

  const initSuggestedQuestions = useCallback((questions) => {
    setSuggestedQuestions(questions || [])
  }, [])

  const handleAskQuestion = useCallback(() => {
    if (!analysisId || !question.trim()) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Ask analysis question',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId },
      action: async () => {
        setIsAskingQuestion(true)
        try {
          const response = await askQuestion(analysisId, {
            question: question.trim(),
            includeSources: true,
          })

          setQaHistory((prev) => [
            ...prev,
            {
              question: question.trim(),
              answer: response.answer,
              sources: response.sources,
              timestamp: new Date(),
            },
          ])
          setQuestion('')

          if (response.suggested_followups?.length) {
            setSuggestedQuestions(response.suggested_followups)
          }
        } catch (err) {
          toast.show(err.message || 'Failed to get answer', 'error')
        } finally {
          setIsAskingQuestion(false)
        }
      },
    })
  }, [analysisId, execute, question, toast])

  const resetQA = useCallback(() => {
    setQaHistory([])
    setSuggestedQuestions([])
    setQuestion('')
  }, [])

  return {
    question,
    setQuestion,
    isAskingQuestion,
    qaHistory,
    suggestedQuestions,
    initSuggestedQuestions,
    handleAskQuestion,
    resetQA,
  }
}

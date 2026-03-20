import { useCallback, useState } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { generateCharts } from '../services/enhancedAnalyzeApi'
import { normalizeChartSpec } from '../services/analyzeApi'

export default function useChartGeneration({ analysisId }) {
  const [chartQuery, setChartQuery] = useState('')
  const [isGeneratingCharts, setIsGeneratingCharts] = useState(false)
  const [generatedCharts, setGeneratedCharts] = useState([])

  const toast = useToast()
  const { execute } = useInteraction()

  const initCharts = useCallback((charts) => {
    setGeneratedCharts(charts || [])
  }, [])

  const handleGenerateCharts = useCallback(() => {
    if (!analysisId || !chartQuery.trim()) return undefined

    return execute({
      type: InteractionType.GENERATE,
      label: 'Generate charts',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId },
      action: async () => {
        setIsGeneratingCharts(true)
        try {
          const response = await generateCharts(analysisId, {
            query: chartQuery.trim(),
            includeTrends: true,
            includeForecasts: false,
          })

          if (response.charts?.length) {
            const normalized = response.charts
              .map((c, i) => ({ ...c, ...normalizeChartSpec(c, i) }))
              .filter(Boolean)
            setGeneratedCharts((prev) => [...normalized, ...prev])
            setChartQuery('')
            toast.show(`Generated ${response.charts.length} chart(s)`, 'success')
          } else {
            toast.show(response.message || 'No charts could be generated for this query. Try a different request or re-analyze the document.', 'warning')
          }
        } catch (err) {
          toast.show(err.message || 'Failed to generate charts', 'error')
        } finally {
          setIsGeneratingCharts(false)
        }
      },
    })
  }, [analysisId, chartQuery, execute, toast])

  const resetCharts = useCallback(() => {
    setGeneratedCharts([])
    setChartQuery('')
  }, [])

  return {
    chartQuery,
    setChartQuery,
    isGeneratingCharts,
    generatedCharts,
    initCharts,
    handleGenerateCharts,
    resetCharts,
  }
}

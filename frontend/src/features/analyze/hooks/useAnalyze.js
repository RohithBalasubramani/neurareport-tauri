/**
 * Custom hook for analyze page state and operations
 */
import { useCallback, useEffect, useState, useRef } from 'react'
import { uploadAndAnalyze, suggestAnalysisCharts, normalizeChartSpec } from '../services/analyzeApi'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'

export function useAnalyze() {
  const [activeStep, setActiveStep] = useState(0)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [progressStage, setProgressStage] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState(null)
  const [chartQuestion, setChartQuestion] = useState('')
  const [isLoadingCharts, setIsLoadingCharts] = useState(false)
  const [runInBackground, setRunInBackground] = useState(false)
  const [queuedJobId, setQueuedJobId] = useState(null)
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const abortControllerRef = useRef(null)

  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'analyze', ...intent } }),
    [navigate]
  )

  // Abort in-flight analysis on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
        abortControllerRef.current = null
      }
    }
  }, [])

  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file)
    setError(null)
    setAnalysisResult(null)
    setQueuedJobId(null)
    if (file) {
      setActiveStep(0)
    }
  }, [])

  const handleAnalyze = useCallback(() => {
    if (!selectedFile) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: runInBackground ? 'Queue analysis' : 'Analyze document',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: !runInBackground,
      suppressSuccessToast: true,
      intent: {
        fileName: selectedFile?.name,
        background: runInBackground,
      },
      action: async () => {
        abortControllerRef.current = new AbortController()
        setIsAnalyzing(true)
        setAnalysisProgress(0)
        setProgressStage('Starting analysis...')
        setError(null)
        setQueuedJobId(null)

        if (runInBackground) {
          try {
            const queued = await uploadAndAnalyze({
              file: selectedFile,
              background: true,
              connectionId: selectedConnectionId || undefined,
              templateId: selectedTemplateId || undefined,
            })
            const jobId = queued?.job_id || queued?.jobId || null
            setQueuedJobId(jobId)
            setAnalysisResult(null)
            setActiveStep(0)
            toast.show('Analysis queued in background', 'success')
          } catch (err) {
            if (err.name !== 'AbortError') {
              setError(err.message || 'Failed to queue analysis')
            }
          } finally {
            setIsAnalyzing(false)
            setAnalysisProgress(0)
            setProgressStage('')
            abortControllerRef.current = null
          }
          return
        }

        setActiveStep(1)
        try {
          const result = await uploadAndAnalyze({
            file: selectedFile,
            connectionId: selectedConnectionId || undefined,
            templateId: selectedTemplateId || undefined,
            signal: abortControllerRef.current?.signal,
            onProgress: (event) => {
              if (event.event === 'stage') {
                setAnalysisProgress(event.progress || 0)
                setProgressStage(event.detail || event.stage || 'Processing...')
              }
            },
          })
          if (result.event === 'result') {
            setAnalysisResult(result)
            setActiveStep(2)
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            toast.show('Analysis cancelled', 'info')
            setActiveStep(0)
          } else {
            setError(err.message || 'Analysis failed')
            setActiveStep(0)
          }
        } finally {
          setIsAnalyzing(false)
          setAnalysisProgress(100)
          abortControllerRef.current = null
        }
      },
    })
  }, [execute, selectedFile, runInBackground, toast, selectedConnectionId, selectedTemplateId])

  const handleCancelAnalysis = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Cancel analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'analyze' },
      action: () => {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort()
          setIsAnalyzing(false)
          setActiveStep(0)
          setAnalysisProgress(0)
          setProgressStage('')
          toast.show('Analysis cancelled', 'info')
        }
      },
    })
  }, [execute, toast])

  const handleAskCharts = useCallback(() => {
    if (!analysisResult?.analysis_id || !chartQuestion.trim()) return undefined

    return execute({
      type: InteractionType.GENERATE,
      label: 'Generate charts',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      suppressSuccessToast: true,
      intent: { analysisId: analysisResult.analysis_id },
      action: async () => {
        setIsLoadingCharts(true)
        try {
          const response = await suggestAnalysisCharts(analysisResult.analysis_id, {
            question: chartQuestion,
            includeSampleData: true,
          })
          if (response?.charts) {
            const normalizedCharts = response.charts
              .map((c, idx) => normalizeChartSpec(c, idx))
              .filter(Boolean)
            setAnalysisResult((prev) => ({
              ...prev,
              chart_suggestions: [
                ...normalizedCharts,
                ...(prev.chart_suggestions || []),
              ],
            }))
          }
        } catch (err) {
          setError(err.message || 'Failed to generate charts')
        } finally {
          setIsLoadingCharts(false)
          setChartQuestion('')
        }
      },
    })
  }, [analysisResult?.analysis_id, chartQuestion, execute])

  const handleReset = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Reset analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'analyze' },
      action: () => {
        setSelectedFile(null)
        setAnalysisResult(null)
        setError(null)
        setActiveStep(0)
        setChartQuestion('')
        setQueuedJobId(null)
      },
    })
  }, [execute])

  // Compute status chips
  const getStatusChips = () => {
    const chips = []
    if (selectedFile) {
      chips.push({ label: selectedFile.name, color: 'primary', variant: 'outlined' })
    }
    if (analysisResult) {
      const tableCount = analysisResult.tables?.length || 0
      const chartCount = analysisResult.chart_suggestions?.length || 0
      if (tableCount > 0) chips.push({ label: `${tableCount} table${tableCount !== 1 ? 's' : ''} found`, color: 'success' })
      if (chartCount > 0) chips.push({ label: `${chartCount} chart${chartCount !== 1 ? 's' : ''}`, color: 'info' })
    }
    return chips
  }

  return {
    // Step state
    activeStep,
    // File state
    selectedFile,
    isAnalyzing,
    analysisProgress,
    progressStage,
    analysisResult,
    error,
    // Chart state
    chartQuestion,
    setChartQuestion,
    isLoadingCharts,
    // Background state
    runInBackground,
    setRunInBackground,
    queuedJobId,
    // Selectors
    selectedConnectionId,
    setSelectedConnectionId,
    selectedTemplateId,
    setSelectedTemplateId,
    // Actions
    handleFileSelect,
    handleAnalyze,
    handleCancelAnalysis,
    handleAskCharts,
    handleReset,
    handleNavigate,
    // Computed
    statusChips: getStatusChips(),
  }
}

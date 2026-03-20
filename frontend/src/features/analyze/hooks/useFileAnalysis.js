import { useCallback, useState, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import {
  uploadAndAnalyzeEnhanced,
} from '../services/enhancedAnalyzeApi'
import { normalizeChartSpec } from '../services/analyzeApi'

const DEFAULT_PREFERENCES = {
  analysis_depth: 'standard',
  focus_areas: [],
  output_format: 'executive',
  industry: null,
  enable_predictions: true,
  auto_chart_generation: true,
  max_charts: 10,
}

export default function useFileAnalysis({
  selectedConnectionId,
  selectedTemplateId,
  onAnalysisComplete,
}) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [progressStage, setProgressStage] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState(null)

  const abortControllerRef = useRef(null)
  const fileInputRef = useRef(null)
  const toast = useToast()
  const { execute } = useInteraction()

  const [preferences] = useState(DEFAULT_PREFERENCES)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setAnalysisResult(null)
    }
  }, [])

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setAnalysisResult(null)
    }
  }, [])

  const handleAnalyze = useCallback(() => {
    if (!selectedFile) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Analyze document',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      suppressSuccessToast: true,
      intent: { fileName: selectedFile?.name },
      action: async () => {
        abortControllerRef.current = new AbortController()

        setIsAnalyzing(true)
        setAnalysisProgress(0)
        setProgressStage('Initializing AI analysis...')
        setError(null)

        try {
          const result = await uploadAndAnalyzeEnhanced({
            file: selectedFile,
            preferences,
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
            const charts = (result.chart_suggestions || [])
              .map((c, idx) => ({ ...c, ...normalizeChartSpec(c, idx) }))
              .filter(Boolean)
            onAnalysisComplete?.(result, charts)
            toast.show('Analysis complete!', 'success')
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            toast.show('Analysis cancelled', 'info')
          } else {
            setError(err.message || 'Analysis failed')
          }
        } finally {
          setIsAnalyzing(false)
          setAnalysisProgress(100)
          abortControllerRef.current = null
        }
      },
    })
  }, [execute, selectedFile, preferences, selectedConnectionId, selectedTemplateId, onAnalysisComplete, toast])

  const handleCancelAnalysis = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Cancel analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'enhanced-analyze' },
      action: () => {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort()
          setIsAnalyzing(false)
          setAnalysisProgress(0)
          setProgressStage('')
        }
      },
    })
  }, [execute])

  const handleReset = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Reset analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'enhanced-analyze' },
      action: () => {
        setSelectedFile(null)
        setAnalysisResult(null)
        setError(null)
      },
    })
  }, [execute])

  return {
    selectedFile,
    isDragOver,
    isAnalyzing,
    analysisProgress,
    progressStage,
    analysisResult,
    error,
    fileInputRef,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    handleAnalyze,
    handleCancelAnalysis,
    handleReset,
  }
}

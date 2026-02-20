import { useCallback, useEffect, useState, useRef } from 'react'
import {
  Box,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  Stack,
  Divider,
  Alert,
  FormControlLabel,
  Switch,
  TextField,
  CircularProgress,
  Chip,
  LinearProgress,
  alpha,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import UploadFileOutlinedIcon from '@mui/icons-material/UploadFileOutlined'
import InsightsOutlinedIcon from '@mui/icons-material/InsightsOutlined'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CancelIcon from '@mui/icons-material/Cancel'

import DocumentUpload from '../components/DocumentUpload'
import AnalysisResults from '../components/AnalysisResults'
import { uploadAndAnalyze, suggestAnalysisCharts, normalizeChartSpec } from '../services/analyzeApi'
import Surface from '@/components/layout/Surface'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import { neutral, palette, secondary } from '@/app/theme'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'

const STEPS = [
  { label: 'Upload Document', icon: <UploadFileOutlinedIcon fontSize="small" /> },
  { label: 'AI Analysis', icon: <AutoAwesomeIcon fontSize="small" /> },
  { label: 'View Results', icon: <InsightsOutlinedIcon fontSize="small" /> },
]

export default function AnalyzePageContainer() {
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

  // Abort in-flight analysis on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
        abortControllerRef.current = null
      }
    }
  }, [])

  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'analyze', ...intent } }),
    [navigate]
  )

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
        // Create abort controller for cancellation
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
  }, [execute, selectedFile, runInBackground, toast])

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

  const statusChips = getStatusChips()

  return (
    <Box sx={{ py: 3, px: 3 }}>
      {/* Page Header */}
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Analyze Document
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload PDF or Excel files to extract tables and generate interactive visualizations.
          </Typography>
        </Box>
        {analysisResult && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={handleReset}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            New Analysis
          </Button>
        )}
      </Stack>

      <Stack spacing={3}>
        {/* Status Chips */}
        {statusChips.length > 0 && (
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {statusChips.map((chip, idx) => (
              <Chip
                key={idx}
                label={chip.label}
                size="small"
                variant={chip.variant || 'filled'}
                icon={chip.color === 'success' ? <CheckCircleOutlineIcon /> : undefined}
                sx={{ fontWeight: 500, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            ))}
          </Stack>
        )}

        {queuedJobId && (
          <Alert
            severity="info"
            action={(
              <Button size="small" onClick={() => handleNavigate('/jobs', 'Open jobs')} sx={{ textTransform: 'none' }}>
                View Jobs
              </Button>
            )}
            sx={{ alignItems: 'center' }}
          >
            Analysis queued in background. Job ID: {queuedJobId}
          </Alert>
        )}

        {/* Progress Stepper */}
      <Surface sx={{ p: 3 }}>
        <Stepper
          activeStep={activeStep}
          sx={{
            mb: 3,
            '& .MuiStepLabel-label': {
              fontWeight: 500,
            },
            '& .MuiStepLabel-label.Mui-active': {
              fontWeight: 600,
              color: 'text.secondary',
            },
            '& .MuiStepLabel-label.Mui-completed': {
              fontWeight: 600,
              color: 'text.secondary',
            },
          }}
        >
          {STEPS.map((step, index) => (
            <Step key={step.label} completed={activeStep > index}>
              <StepLabel
                StepIconProps={{
                  sx: {
                    '&.Mui-completed': { color: 'text.secondary' },
                    '&.Mui-active': { color: 'text.secondary' },
                  },
                }}
              >
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  {step.icon}
                  <span>{step.label}</span>
                </Stack>
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step 0: Upload */}
        {activeStep === 0 && (
          <Box>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
              <ConnectionSelector
                value={selectedConnectionId}
                onChange={setSelectedConnectionId}
                label="Analyze from Connection (Optional)"
                size="small"
                showStatus
              />
              <TemplateSelector
                value={selectedTemplateId}
                onChange={setSelectedTemplateId}
                label="Report Template (Optional)"
                size="small"
              />
            </Stack>
            <DocumentUpload
              onFileSelect={handleFileSelect}
              isUploading={isAnalyzing}
              progress={analysisProgress}
              progressStage={progressStage}
              error={error}
              disabled={isAnalyzing}
            />

            {selectedFile && !isAnalyzing && (
              <Stack spacing={2} sx={{ mt: 3 }}>
                <FormControlLabel
                  control={(
                    <Switch
                      checked={runInBackground}
                      onChange={(e) => setRunInBackground(e.target.checked)}
                    />
                  )}
                  label="Run in background"
                  sx={{ alignSelf: 'center' }}
                />
                <Stack direction="row" justifyContent="center">
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleAnalyze}
                    startIcon={<AutoAwesomeIcon />}
                    sx={{
                      px: 4,
                      py: 1.5,
                      fontWeight: 600,
                      fontSize: '1rem',
                      textTransform: 'none',
                      borderRadius: 1,  // Figma spec: 8px
                      boxShadow: `0 4px 14px ${alpha(secondary.violet[500], 0.25)}`,
                      '&:hover': {
                        boxShadow: `0 6px 20px ${alpha(secondary.violet[500], 0.35)}`,
                      },
                    }}
                  >
                    {runInBackground ? 'Queue Analysis' : 'Analyze with AI'}
                  </Button>
                </Stack>
              </Stack>
            )}
          </Box>
        )}

        {/* Step 1: Analyzing */}
        {activeStep === 1 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
              <CircularProgress
                size={80}
                thickness={4}
                variant={analysisProgress > 0 ? 'determinate' : 'indeterminate'}
                value={analysisProgress}
                sx={{ color: 'text.secondary' }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  bottom: 0,
                  right: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  {analysisProgress}%
                </Typography>
              </Box>
            </Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              {progressStage || 'Analyzing document...'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              AI is extracting tables, metrics, and generating chart suggestions
            </Typography>
            <LinearProgress
              variant="determinate"
              value={analysisProgress}
              sx={{
                height: 6,
                borderRadius: 1,  // Figma spec: 8px
                maxWidth: 400,
                mx: 'auto',
                mb: 3,
                bgcolor: 'action.hover',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 1,  // Figma spec: 8px
                },
              }}
            />
            <Button
              variant="outlined"
              color="inherit"
              startIcon={<CancelIcon />}
              onClick={handleCancelAnalysis}
              sx={{
                textTransform: 'none',
                fontWeight: 500,
              }}
            >
              Cancel Analysis
            </Button>
          </Box>
        )}

        {/* Step 2: Results */}
        {activeStep === 2 && analysisResult && (
          <Box>
            <AnalysisResults result={analysisResult} />

            <Divider sx={{ my: 3 }} />

            {/* Ask for more insights */}
            <Surface
              variant="outlined"
              sx={{
                p: 2.5,
                bgcolor: 'action.hover',
                border: '1px dashed',
                borderColor: 'divider',
              }}
            >
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <AutoAwesomeIcon color="inherit" fontSize="small" sx={{ color: 'text.secondary' }} />
                <Typography variant="subtitle1" fontWeight={600}>
                  Ask for more insights
                </Typography>
              </Stack>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField
                  fullWidth
                  placeholder="e.g., Show me revenue trends over time, Compare categories by month..."
                  value={chartQuestion}
                  onChange={(e) => setChartQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleAskCharts()}
                  disabled={isLoadingCharts}
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'background.paper',
                    },
                  }}
                />
                <Button
                  variant="contained"
                  onClick={handleAskCharts}
                  disabled={!chartQuestion.trim() || isLoadingCharts}
                  startIcon={isLoadingCharts ? <CircularProgress size={16} color="inherit" /> : <AutoAwesomeIcon />}
                  sx={{
                    minWidth: 160,
                    textTransform: 'none',
                    fontWeight: 600,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {isLoadingCharts ? 'Generating...' : 'Generate Charts'}
                </Button>
              </Stack>
            </Surface>
          </Box>
        )}

        {/* Error Display */}
        {error && activeStep !== 0 && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Surface>

        {/* Help Text */}
        <Box sx={{ textAlign: 'center', py: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Supported formats: PDF, Excel (XLSX, XLS) • Max file size: 50MB
          </Typography>
          <Typography variant="caption" color="text.disabled">
            AI-powered extraction with zoomable, interactive time series charts
          </Typography>
        </Box>
      </Stack>
    </Box>
  )
}

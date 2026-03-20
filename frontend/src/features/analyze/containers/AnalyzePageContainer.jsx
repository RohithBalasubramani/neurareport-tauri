/**
 * Analyze Page Container
 * Upload PDF or Excel files to extract tables and generate interactive visualizations.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Stack,
  Chip,
  Alert,
  alpha,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import { neutral } from '@/app/theme'
import { useAnalyze } from '../hooks/useAnalyze'
import AnalysisStepper from '../components/AnalysisStepper'

export default function AnalyzePageContainer() {
  const {
    activeStep,
    selectedFile,
    isAnalyzing,
    analysisProgress,
    progressStage,
    analysisResult,
    error,
    chartQuestion,
    setChartQuestion,
    isLoadingCharts,
    runInBackground,
    setRunInBackground,
    queuedJobId,
    selectedConnectionId,
    setSelectedConnectionId,
    selectedTemplateId,
    setSelectedTemplateId,
    handleFileSelect,
    handleAnalyze,
    handleCancelAnalysis,
    handleAskCharts,
    handleReset,
    handleNavigate,
    statusChips,
  } = useAnalyze()

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

        {/* Stepper */}
        <AnalysisStepper
          activeStep={activeStep}
          selectedFile={selectedFile}
          isAnalyzing={isAnalyzing}
          analysisProgress={analysisProgress}
          progressStage={progressStage}
          analysisResult={analysisResult}
          error={error}
          chartQuestion={chartQuestion}
          setChartQuestion={setChartQuestion}
          isLoadingCharts={isLoadingCharts}
          runInBackground={runInBackground}
          setRunInBackground={setRunInBackground}
          selectedConnectionId={selectedConnectionId}
          setSelectedConnectionId={setSelectedConnectionId}
          selectedTemplateId={selectedTemplateId}
          setSelectedTemplateId={setSelectedTemplateId}
          onFileSelect={handleFileSelect}
          onAnalyze={handleAnalyze}
          onCancelAnalysis={handleCancelAnalysis}
          onAskCharts={handleAskCharts}
        />

        {/* Help Text */}
        <Box sx={{ textAlign: 'center', py: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Supported formats: PDF, Excel (XLSX, XLS) &bull; Max file size: 50MB
          </Typography>
          <Typography variant="caption" color="text.disabled">
            AI-powered extraction with zoomable, interactive time series charts
          </Typography>
        </Box>
      </Stack>
    </Box>
  )
}

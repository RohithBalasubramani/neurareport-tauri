/**
 * Analysis progress stepper with upload, analyzing, and results steps
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Stack,
  Alert,
  FormControlLabel,
  Switch,
  Stepper,
  Step,
  StepLabel,
  alpha,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import UploadFileOutlinedIcon from '@mui/icons-material/UploadFileOutlined'
import InsightsOutlinedIcon from '@mui/icons-material/InsightsOutlined'

import DocumentUpload from './DocumentUpload'
import AnalyzingStep from './AnalyzingStep'
import AnalysisResultsStep from './AnalysisResultsStep'
import Surface from '@/components/layout/Surface'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import { secondary } from '@/app/theme'

const STEPS = [
  { label: 'Upload Document', icon: <UploadFileOutlinedIcon fontSize="small" /> },
  { label: 'AI Analysis', icon: <AutoAwesomeIcon fontSize="small" /> },
  { label: 'View Results', icon: <InsightsOutlinedIcon fontSize="small" /> },
]

export default function AnalysisStepper({
  activeStep, selectedFile, isAnalyzing, analysisProgress, progressStage,
  analysisResult, error, chartQuestion, setChartQuestion, isLoadingCharts,
  runInBackground, setRunInBackground, selectedConnectionId, setSelectedConnectionId,
  selectedTemplateId, setSelectedTemplateId, onFileSelect, onAnalyze, onCancelAnalysis, onAskCharts,
}) {
  return (
    <Surface sx={{ p: 3 }}>
      <Stepper activeStep={activeStep} sx={{
        mb: 3,
        '& .MuiStepLabel-label': { fontWeight: 500 },
        '& .MuiStepLabel-label.Mui-active': { fontWeight: 600, color: 'text.secondary' },
        '& .MuiStepLabel-label.Mui-completed': { fontWeight: 600, color: 'text.secondary' },
      }}>
        {STEPS.map((step, index) => (
          <Step key={step.label} completed={activeStep > index}>
            <StepLabel StepIconProps={{ sx: { '&.Mui-completed': { color: 'text.secondary' }, '&.Mui-active': { color: 'text.secondary' } } }}>
              <Stack direction="row" alignItems="center" spacing={0.5}>
                {step.icon}<span>{step.label}</span>
              </Stack>
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && (
        <Box>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
            <ConnectionSelector value={selectedConnectionId} onChange={setSelectedConnectionId} label="Analyze from Connection (Optional)" size="small" showStatus />
            <TemplateSelector value={selectedTemplateId} onChange={setSelectedTemplateId} label="Report Template (Optional)" size="small" />
          </Stack>
          <DocumentUpload onFileSelect={onFileSelect} isUploading={isAnalyzing} progress={analysisProgress} progressStage={progressStage} error={error} disabled={isAnalyzing} />
          {selectedFile && !isAnalyzing && (
            <Stack spacing={2} sx={{ mt: 3 }}>
              <FormControlLabel control={<Switch checked={runInBackground} onChange={(e) => setRunInBackground(e.target.checked)} />} label="Run in background" sx={{ alignSelf: 'center' }} />
              <Stack direction="row" justifyContent="center">
                <Button variant="contained" size="large" onClick={onAnalyze} startIcon={<AutoAwesomeIcon />} sx={{
                  px: 4, py: 1.5, fontWeight: 600, fontSize: '1rem', textTransform: 'none', borderRadius: 1,
                  boxShadow: `0 4px 14px ${alpha(secondary.violet[500], 0.25)}`,
                  '&:hover': { boxShadow: `0 6px 20px ${alpha(secondary.violet[500], 0.35)}` },
                }}>
                  {runInBackground ? 'Queue Analysis' : 'Analyze with AI'}
                </Button>
              </Stack>
            </Stack>
          )}
        </Box>
      )}

      {activeStep === 1 && (
        <AnalyzingStep analysisProgress={analysisProgress} progressStage={progressStage} onCancelAnalysis={onCancelAnalysis} />
      )}

      {activeStep === 2 && analysisResult && (
        <AnalysisResultsStep analysisResult={analysisResult} chartQuestion={chartQuestion} setChartQuestion={setChartQuestion} isLoadingCharts={isLoadingCharts} onAskCharts={onAskCharts} />
      )}

      {error && activeStep !== 0 && (
        <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
      )}
    </Surface>
  )
}

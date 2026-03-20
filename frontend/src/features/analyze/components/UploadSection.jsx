import {
  Box,
  Typography,
  Paper,
  Stack,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import { GlassCard } from '@/styles'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import { neutral } from '@/app/theme'
import { UploadPlaceholder, FileReady, AnalyzingProgress } from './UploadStates'

export default function UploadSection({
  selectedFile,
  isDragOver,
  isAnalyzing,
  analysisProgress,
  progressStage,
  error,
  fileInputRef,
  selectedConnectionId,
  selectedTemplateId,
  onConnectionChange,
  onTemplateChange,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect,
  onAnalyze,
  onCancelAnalysis,
}) {
  const theme = useTheme()

  return (
    <Fade in>
      <Box>
        {/* Data Source Selectors */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={onConnectionChange}
            label="Analyze from Connection (Optional)"
            size="small"
            showStatus
          />
          <TemplateSelector
            value={selectedTemplateId}
            onChange={onTemplateChange}
            label="Report Template (Optional)"
            size="small"
          />
        </Stack>

        {/* Dropzone */}
        <GlassCard
          gradient
          hover={false}
          sx={{
            p: 6,
            textAlign: 'center',
            cursor: 'pointer',
            border: `2px dashed ${isDragOver ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.3)}`,
            bgcolor: isDragOver ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : undefined,
            transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          }}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.xlsx,.xls,.csv,.doc,.docx,.png,.jpg,.jpeg"
            onChange={onFileSelect}
          />

          {!selectedFile && !isAnalyzing && (
            <UploadPlaceholder theme={theme} />
          )}

          {selectedFile && !isAnalyzing && (
            <FileReady file={selectedFile} theme={theme} onAnalyze={onAnalyze} />
          )}

          {isAnalyzing && (
            <AnalyzingProgress
              theme={theme}
              progress={analysisProgress}
              stage={progressStage}
              onCancel={onCancelAnalysis}
            />
          )}
        </GlassCard>

        {error && (
          <Paper
            sx={{
              mt: 2,
              p: 2,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.error.main, 0.1) : alpha(theme.palette.error.main, 0.05),
              border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
              borderRadius: 1,
            }}
          >
            <Typography color="error.main" sx={{ fontWeight: 500 }}>{error}</Typography>
          </Paper>
        )}
      </Box>
    </Fade>
  )
}

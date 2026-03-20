import {
  Box,
  Typography,
  Stack,
  Alert,
} from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import {
  PrimaryButton,
  SecondaryButton,
  TextButton,
  StyledLinearProgress,
} from './ReportsStyledComponents'

export default function ActionBar({
  error,
  generating,
  result,
  selectedTemplate,
  activeConnection,
  onGenerate,
  onClearError,
  onNavigate,
}) {
  return (
    <Box>
      {/* Error alert */}
      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2, borderRadius: 1 }}
          onClose={onClearError}
          action={
            <TextButton color="inherit" size="small" onClick={onGenerate} disabled={generating}>
              Try Again
            </TextButton>
          }
        >
          {error}
        </Alert>
      )}

      {/* Generating progress */}
      {generating && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Generating report...
          </Typography>
          <StyledLinearProgress />
        </Box>
      )}

      {/* Success result */}
      {result && (
        <Alert severity="success" sx={{ mb: 2, borderRadius: 1 }}>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
            <Typography variant="body2">
              Report started! ID: {result.job_id?.slice(0, 8)}...
            </Typography>
            <SecondaryButton
              size="small"
              variant="outlined"
              onClick={() => onNavigate('/jobs', 'Open jobs')}
            >
              View Progress
            </SecondaryButton>
          </Stack>
        </Alert>
      )}

      {/* Primary action row */}
      <Stack direction="row" spacing={2} alignItems="center" justifyContent="flex-end">
        <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
          Reports run in the background.{' '}
          <Typography
            component="span"
            variant="caption"
            sx={{ color: 'primary.main', cursor: 'pointer', textDecoration: 'underline' }}
            onClick={() => onNavigate('/jobs', 'Open jobs')}
          >
            Track progress
          </Typography>
        </Typography>
        <PrimaryButton
          startIcon={<PlayArrowIcon />}
          onClick={onGenerate}
          disabled={!selectedTemplate || !activeConnection || generating}
          sx={{ px: 4, py: 1.5 }}
        >
          Generate Report
        </PrimaryButton>
      </Stack>
    </Box>
  )
}

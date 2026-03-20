import {
  Box,
  Typography,
  Stack,
  Paper,
  useTheme,
  alpha,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import AiUsageNotice from '@/components/ai/AiUsageNotice'
import { neutral } from '@/app/theme'
import {
  SecondaryButton,
  StyledLinearProgress,
} from './ReportsStyledComponents'

export default function RunSummaryPanel({
  summaryLoading,
  runSummary,
  queueingSummary,
  onQueueSummary,
}) {
  const theme = useTheme()

  return (
    <Box sx={{ mt: 1, ml: 2, pl: 2, borderLeft: 2, borderColor: 'divider' }}>
      <AiUsageNotice
        title="AI summary"
        description="Summaries are generated from the selected report run. Review before sharing."
        chips={[
          { label: 'Source: Selected run', color: 'info', variant: 'outlined' },
          { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
        ]}
        dense
        sx={{ mb: 1.5 }}
      />
      {summaryLoading && <StyledLinearProgress sx={{ mb: 1 }} />}
      {!summaryLoading && runSummary ? (
        <Paper
          sx={{
            p: 2,
            borderRadius: 1.5,
            bgcolor: theme.palette.mode === 'dark'
              ? alpha(theme.palette.text.primary, 0.04)
              : neutral[50],
            border: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {typeof runSummary === 'string'
              ? runSummary
              : runSummary.text || runSummary.content || 'No summary available'}
          </Typography>
          {runSummary.key_points && (
            <Box sx={{ mt: 1.5 }}>
              <Typography variant="caption" fontWeight={600} color="text.primary">
                Key Points:
              </Typography>
              <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                {runSummary.key_points.map((point, idx) => (
                  <li key={idx}>
                    <Typography variant="caption">{point}</Typography>
                  </li>
                ))}
              </ul>
            </Box>
          )}
        </Paper>
      ) : !summaryLoading && (
        <Stack spacing={1}>
          <Typography variant="body2" color="text.secondary">
            No summary available for this run.
          </Typography>
          <SecondaryButton
            size="small"
            variant="outlined"
            startIcon={<AutoAwesomeIcon sx={{ fontSize: 14 }} />}
            onClick={onQueueSummary}
            disabled={queueingSummary}
            sx={{ alignSelf: 'flex-start' }}
          >
            {queueingSummary ? 'Queueing...' : 'Generate summary'}
          </SecondaryButton>
        </Stack>
      )}
    </Box>
  )
}

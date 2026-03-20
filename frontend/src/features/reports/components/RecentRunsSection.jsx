import {
  Box,
  Typography,
  Stack,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import RefreshIcon from '@mui/icons-material/Refresh'
import {
  SectionLabel,
  TextButton,
  StyledLinearProgress,
} from './ReportsStyledComponents'
import RunHistoryItem from './RunHistoryItem'

export default function RecentRunsSection({
  runHistory,
  historyLoading,
  selectedRun,
  expandedRunId,
  summaryLoading,
  runSummary,
  queueingSummary,
  generatingDocx,
  onRefresh,
  onSelectRun,
  onQueueSummary,
  onGenerateDocx,
  onNavigate,
  toast,
}) {
  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <SectionLabel sx={{ mb: 0, flex: 1 }}>
          <RefreshIcon sx={{ fontSize: 14 }} />
          Recent Runs
        </SectionLabel>
        <TextButton
          size="small"
          onClick={onRefresh}
          disabled={historyLoading}
          startIcon={<RefreshIcon sx={{ fontSize: 14 }} />}
        >
          Refresh
        </TextButton>
      </Stack>

      {historyLoading && <StyledLinearProgress sx={{ mb: 2 }} />}

      {!historyLoading && runHistory.length === 0 && (
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <DescriptionIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
          <Typography variant="body2" color="text.secondary">
            No report runs yet. Generate a report to get started.
          </Typography>
        </Box>
      )}

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 2,
        }}
      >
        {runHistory.map((run) => (
          <RunHistoryItem
            key={run.id}
            run={run}
            selectedRun={selectedRun}
            expandedRunId={expandedRunId}
            summaryLoading={summaryLoading}
            runSummary={runSummary}
            queueingSummary={queueingSummary}
            generatingDocx={generatingDocx}
            onSelectRun={onSelectRun}
            onQueueSummary={onQueueSummary}
            onGenerateDocx={onGenerateDocx}
            onNavigate={onNavigate}
            toast={toast}
          />
        ))}
      </Box>
    </Box>
  )
}

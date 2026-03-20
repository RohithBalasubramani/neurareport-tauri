/**
 * Agent Result Panel Component
 */
import {
  Box,
  Chip,
  IconButton,
  Typography,
  Button,
  Tooltip,
  alpha,
  useTheme,
} from '@mui/material'
import {
  ContentCopy as CopyIcon,
  Description as ReportIcon,
} from '@mui/icons-material'
import SendToMenu from '@/components/common/SendToMenu'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'
import { ResultCard } from './AgentsStyledComponents'
import ReportAnalystResult from './ReportAnalystResult'

export default function AgentResultPanel({
  result,
  selectedAgent,
  resultRef,
  onCopyResult,
  onGenerateReport,
}) {
  const theme = useTheme()

  if (!result) return null

  const agentOutput = result.result || result.output
  const displayContent = typeof agentOutput === 'string' ? agentOutput : JSON.stringify(agentOutput, null, 2)

  return (
    <ResultCard ref={resultRef}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Result
          {result.status && (
            <Chip
              label={result.status}
              size="small"
              color={result.status === 'completed' ? 'success' : result.status === 'failed' ? 'error' : 'default'}
              sx={{ ml: 1, fontSize: '12px', height: 22 }}
            />
          )}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {result.status === 'completed' && result.task_id && (
            <Tooltip title="Generate a report using this agent's output" arrow>
              <Button
                size="small"
                variant="outlined"
                startIcon={<ReportIcon fontSize="small" />}
                onClick={onGenerateReport}
                sx={{ textTransform: 'none', mr: 0.5 }}
                data-testid="agent-generate-report-button"
              >
                Generate Report
              </Button>
            </Tooltip>
          )}
          <SendToMenu
            outputType={OutputType.TEXT}
            payload={{
              title: `${selectedAgent.name} Result`,
              content: displayContent,
            }}
            sourceFeature={FeatureKey.AGENTS}
          />
          <IconButton size="small" onClick={onCopyResult} aria-label="Copy result" data-testid="agent-copy-result-button">
            <CopyIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {selectedAgent.type === 'report_analyst' && agentOutput && typeof agentOutput === 'object' ? (
        <ReportAnalystResult output={agentOutput} />
      ) : (
        <Typography
          variant="body2"
          component="pre"
          sx={{
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            bgcolor: alpha(theme.palette.background.default, 0.5),
            p: 2,
            borderRadius: 1,
            maxHeight: 400,
            overflow: 'auto',
          }}
        >
          {displayContent}
        </Typography>
      )}
    </ResultCard>
  )
}

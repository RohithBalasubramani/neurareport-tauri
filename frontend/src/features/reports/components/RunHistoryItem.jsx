import {
  Box,
  Typography,
  Stack,
  Collapse,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import TableChartIcon from '@mui/icons-material/TableChart'
import ArticleIcon from '@mui/icons-material/Article'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import * as api from '@/api/client'
import {
  RunHistoryCard,
  DownloadButton,
  downloadFile,
} from './ReportsStyledComponents'
import RunSummaryPanel from './RunSummaryPanel'

export default function RunHistoryItem({
  run,
  selectedRun,
  expandedRunId,
  summaryLoading,
  runSummary,
  queueingSummary,
  generatingDocx,
  onSelectRun,
  onQueueSummary,
  onGenerateDocx,
  onNavigate,
  toast,
}) {
  const isSelected = selectedRun?.id === run.id
  const isExpanded = expandedRunId === run.id

  return (
    <Box>
      <RunHistoryCard
        selected={isSelected}
        onClick={() => onSelectRun(run)}
        title="Click to view summary"
      >
        <Stack spacing={0.5}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Typography variant="body2" fontWeight={600}>
              {run.templateName || run.templateId}
            </Typography>
            <Stack
              direction="row"
              alignItems="center"
              spacing={0.5}
              className="view-summary-hint"
              sx={{ opacity: 0.6, transition: 'all 0.2s' }}
            >
              <Typography variant="caption" color="text.secondary">
                {isSelected ? 'Collapse' : 'Summary'}
              </Typography>
              <ArrowForwardIcon
                sx={{
                  fontSize: 12,
                  transform: isSelected ? 'rotate(90deg)' : 'none',
                  transition: 'transform 0.2s',
                }}
              />
            </Stack>
          </Stack>
          <Typography variant="caption" color="text.secondary">
            {new Date(run.createdAt).toLocaleString()} &middot; {run.startDate} to {run.endDate}
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 0.5 }} flexWrap="wrap" useFlexGap>
            {run.artifacts?.pdf_url && (
              <DownloadButton
                size="small"
                variant="outlined"
                startIcon={<DownloadIcon sx={{ fontSize: 14 }} />}
                onClick={(e) => { e.stopPropagation(); downloadFile(api.withBase(run.artifacts.pdf_url), `${run.templateName || 'report'}.pdf`, toast) }}
              >
                PDF
              </DownloadButton>
            )}
            {run.artifacts?.html_url && (
              <DownloadButton
                size="small"
                variant="outlined"
                startIcon={<DownloadIcon sx={{ fontSize: 14 }} />}
                onClick={(e) => { e.stopPropagation(); downloadFile(api.withBase(run.artifacts.html_url), `${run.templateName || 'report'}.html`, toast) }}
              >
                HTML
              </DownloadButton>
            )}
            {run.artifacts?.xlsx_url && (
              <DownloadButton
                size="small"
                variant="outlined"
                startIcon={<TableChartIcon sx={{ fontSize: 14 }} />}
                onClick={(e) => { e.stopPropagation(); downloadFile(api.withBase(run.artifacts.xlsx_url), `${run.templateName || 'report'}.xlsx`, toast) }}
              >
                XLSX
              </DownloadButton>
            )}
            {run.artifacts?.docx_url ? (
              <DownloadButton
                size="small"
                variant="outlined"
                startIcon={<ArticleIcon sx={{ fontSize: 14 }} />}
                onClick={(e) => { e.stopPropagation(); downloadFile(api.withBase(run.artifacts.docx_url), `${run.templateName || 'report'}.docx`, toast) }}
              >
                DOCX
              </DownloadButton>
            ) : run.artifacts?.pdf_url ? (
              <DownloadButton
                size="small"
                variant="outlined"
                disabled={generatingDocx === run.id}
                startIcon={generatingDocx === run.id
                  ? <Box component="span" sx={{ width: 14, height: 14, border: '2px solid', borderColor: 'text.disabled', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite', '@keyframes spin': { to: { transform: 'rotate(360deg)' } } }} />
                  : <ArticleIcon sx={{ fontSize: 14 }} />}
                onClick={(e) => { e.stopPropagation(); onGenerateDocx(run.id) }}
                title="DOCX conversion may take several minutes for large reports"
              >
                {generatingDocx === run.id ? 'Generating...' : 'Generate DOCX'}
              </DownloadButton>
            ) : null}
            <DownloadButton
              size="small"
              variant="outlined"
              startIcon={<SmartToyIcon sx={{ fontSize: 14 }} />}
              onClick={(e) => {
                e.stopPropagation()
                onNavigate(`/agents?analyzeRunId=${run.id}`, 'Analyze with AI', { runId: run.id })
              }}
              data-testid={`analyze-ai-${run.id}`}
            >
              Analyze
            </DownloadButton>
          </Stack>
        </Stack>
      </RunHistoryCard>

      {/* Expanded inline AI summary */}
      <Collapse in={isExpanded}>
        <RunSummaryPanel
          summaryLoading={summaryLoading}
          runSummary={runSummary}
          queueingSummary={queueingSummary}
          onQueueSummary={onQueueSummary}
        />
      </Collapse>
    </Box>
  )
}

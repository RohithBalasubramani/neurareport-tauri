/**
 * Report Analyst Structured Result Component
 */
import {
  Box,
  Chip,
  Paper,
  Typography,
  Stack,
} from '@mui/material'
import {
  Analytics as DataIcon,
  Description as ReportIcon,
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
  Lightbulb as InsightIcon,
  CheckCircle as CheckIcon,
  QuestionAnswer as QAIcon,
  CompareArrows as CompareIcon,
} from '@mui/icons-material'
import { alpha } from '@mui/material'
import { AnalysisSectionTitle, FindingCard, HighlightRow } from './AgentsStyledComponents'

const TrendIcon = ({ trend }) => {
  if (trend === 'up') return <TrendUpIcon fontSize="small" color="success" />
  if (trend === 'down') return <TrendDownIcon fontSize="small" color="error" />
  if (trend === 'stable') return <TrendFlatIcon fontSize="small" color="action" />
  return null
}

export default function ReportAnalystResult({ output }) {
  if (!output || typeof output !== 'object') return null

  const { summary, answer, key_findings, data_highlights, recommendations, comparison } = output

  return (
    <Stack spacing={2.5}>
      {answer && (
        <Box>
          <AnalysisSectionTitle>
            <QAIcon fontSize="small" color="primary" />
            Answer
          </AnalysisSectionTitle>
          <Paper sx={{ p: 2, bgcolor: (t) => alpha(t.palette.primary.main, 0.06), borderRadius: 2, border: '1px solid', borderColor: (t) => alpha(t.palette.primary.main, 0.15) }}>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{answer}</Typography>
          </Paper>
        </Box>
      )}

      {summary && (
        <Box>
          <AnalysisSectionTitle>
            <ReportIcon fontSize="small" color="action" />
            Summary
          </AnalysisSectionTitle>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{summary}</Typography>
        </Box>
      )}

      {key_findings?.length > 0 && (
        <Box>
          <AnalysisSectionTitle>
            <InsightIcon fontSize="small" sx={{ color: 'warning.main' }} />
            Key Findings ({key_findings.length})
          </AnalysisSectionTitle>
          <Stack spacing={1}>
            {key_findings.map((f, i) => (
              <FindingCard key={i} elevation={0}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 1 }}>
                  <Typography variant="body2">{f.finding || f}</Typography>
                  {f.confidence != null && (
                    <Chip
                      label={`${Math.round(f.confidence * 100)}%`}
                      size="small"
                      color={f.confidence >= 0.8 ? 'success' : f.confidence >= 0.6 ? 'warning' : 'default'}
                      variant="outlined"
                      sx={{ flexShrink: 0, fontSize: '12px', height: 22 }}
                    />
                  )}
                </Box>
                {f.source_section && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    Source: {f.source_section}
                  </Typography>
                )}
              </FindingCard>
            ))}
          </Stack>
        </Box>
      )}

      {data_highlights?.length > 0 && (
        <Box>
          <AnalysisSectionTitle>
            <DataIcon fontSize="small" color="info" />
            Data Highlights ({data_highlights.length})
          </AnalysisSectionTitle>
          <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            {data_highlights.map((d, i) => (
              <HighlightRow key={i}>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body2" fontWeight={600} noWrap>{d.metric}</Typography>
                  {d.context && <Typography variant="caption" color="text.secondary">{d.context}</Typography>}
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
                  <Typography variant="body2" fontWeight={500}>{d.value}</Typography>
                  <TrendIcon trend={d.trend} />
                </Box>
              </HighlightRow>
            ))}
          </Paper>
        </Box>
      )}

      {comparison && (
        <Box>
          <AnalysisSectionTitle>
            <CompareIcon fontSize="small" color="secondary" />
            Comparison
          </AnalysisSectionTitle>
          <Stack spacing={1}>
            {comparison.report_a_period && comparison.report_b_period && (
              <Typography variant="caption" color="text.secondary">
                Comparing: {comparison.report_a_period} vs {comparison.report_b_period}
              </Typography>
            )}
            {comparison.improvements?.length > 0 && (
              <Box>
                <Typography variant="caption" fontWeight={600} color="success.main">Improvements:</Typography>
                <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                  {comparison.improvements.map((item, i) => (
                    <li key={i}><Typography variant="caption">{item}</Typography></li>
                  ))}
                </ul>
              </Box>
            )}
            {comparison.regressions?.length > 0 && (
              <Box>
                <Typography variant="caption" fontWeight={600} color="error.main">Regressions:</Typography>
                <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                  {comparison.regressions.map((item, i) => (
                    <li key={i}><Typography variant="caption">{item}</Typography></li>
                  ))}
                </ul>
              </Box>
            )}
          </Stack>
        </Box>
      )}

      {recommendations?.length > 0 && (
        <Box>
          <AnalysisSectionTitle>
            <CheckIcon fontSize="small" color="success" />
            Recommendations ({recommendations.length})
          </AnalysisSectionTitle>
          <Stack spacing={0.5}>
            {recommendations.map((rec, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, pl: 0.5 }}>
                <Typography variant="body2" color="text.secondary" sx={{ minWidth: 20, fontWeight: 600 }}>{i + 1}.</Typography>
                <Typography variant="body2">{rec}</Typography>
              </Box>
            ))}
          </Stack>
        </Box>
      )}
    </Stack>
  )
}

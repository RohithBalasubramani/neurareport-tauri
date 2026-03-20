import {
  Box,
  Typography,
  Stack,
  Grid,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import ArticleIcon from '@mui/icons-material/Article'
import SpeedIcon from '@mui/icons-material/Speed'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import SecurityIcon from '@mui/icons-material/Security'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import MetricCard from './MetricCard'
import InsightCard from './InsightCard'
import SentimentDisplay from './SentimentDisplay'
import DataQualityGauge from './DataQualityGauge'

export default function OverviewTab({ analysisResult }) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      {/* Executive Summary */}
      <Grid size={{ xs: 12, lg: 8 }}>
        <GlassCard sx={{ height: '100%' }}>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <ArticleIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Executive Summary
            </Typography>
          </Stack>
          <Typography
            variant="body1"
            sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, color: 'text.secondary' }}
          >
            {analysisResult.summaries?.executive?.content ||
              analysisResult.summaries?.comprehensive?.content ||
              'Summary not available'}
          </Typography>

          {analysisResult.summaries?.executive?.bullet_points?.length > 0 && (
            <Box
              sx={{
                mt: 3,
                p: 2.5,
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                borderRadius: 1,  // Figma spec: 8px
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              }}
            >
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Key Points
              </Typography>
              <Stack spacing={1}>
                {analysisResult.summaries.executive.bullet_points.map((point, i) => (
                  <Stack key={i} direction="row" alignItems="flex-start" spacing={1.5}>
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        color: 'common.white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 12,
                        fontWeight: 600,
                        flexShrink: 0,
                        mt: 0.25,
                      }}
                    >
                      {i + 1}
                    </Box>
                    <Typography variant="body2">{point}</Typography>
                  </Stack>
                ))}
              </Stack>
            </Box>
          )}
        </GlassCard>
      </Grid>

      {/* Sidebar */}
      <Grid size={{ xs: 12, lg: 4 }}>
        <Stack spacing={3}>
          <SentimentDisplay sentiment={analysisResult.sentiment} />
          <DataQualityGauge quality={analysisResult.data_quality} />
        </Stack>
      </Grid>

      {/* Key Metrics */}
      <Grid size={12}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <SpeedIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Key Metrics
            </Typography>
          </Stack>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
            {analysisResult.metrics?.slice(0, 8).map((metric, i) => (
              <MetricCard key={metric.id} metric={metric} index={i} />
            ))}
          </Stack>
        </GlassCard>
      </Grid>

      {/* Top Insights Preview */}
      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <LightbulbIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Top Insights
            </Typography>
          </Stack>
          {analysisResult.insights?.slice(0, 3).map((insight, i) => (
            <InsightCard key={insight.id} insight={insight} type="insight" index={i} />
          ))}
        </GlassCard>
      </Grid>

      {/* Risks & Opportunities Preview */}
      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <SecurityIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Risks & Opportunities
            </Typography>
          </Stack>
          {analysisResult.risks?.slice(0, 2).map((risk, i) => (
            <InsightCard key={risk.id} insight={risk} type="risk" index={i} />
          ))}
          {analysisResult.opportunities?.slice(0, 2).map((opp, i) => (
            <InsightCard key={opp.id} insight={opp} type="opportunity" index={i + 2} />
          ))}
        </GlassCard>
      </Grid>
    </Grid>
  )
}

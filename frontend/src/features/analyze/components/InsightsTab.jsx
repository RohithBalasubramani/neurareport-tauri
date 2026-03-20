import {
  Typography,
  Stack,
  Grid,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import SecurityIcon from '@mui/icons-material/Security'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import InsightCard from './InsightCard'

export default function InsightsTab({ analysisResult }) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <LightbulbIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Key Insights ({analysisResult.insights?.length || 0})
            </Typography>
          </Stack>
          {analysisResult.insights?.map((insight, i) => (
            <InsightCard key={insight.id} insight={insight} type="insight" index={i} />
          ))}
        </GlassCard>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <SecurityIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Risks ({analysisResult.risks?.length || 0})
            </Typography>
          </Stack>
          {analysisResult.risks?.map((risk, i) => (
            <InsightCard key={risk.id} insight={risk} type="risk" index={i} />
          ))}
        </GlassCard>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <RocketLaunchIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Opportunities ({analysisResult.opportunities?.length || 0})
            </Typography>
          </Stack>
          {analysisResult.opportunities?.map((opp, i) => (
            <InsightCard key={opp.id} insight={opp} type="opportunity" index={i} />
          ))}
        </GlassCard>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <GlassCard>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <PlaylistAddCheckIcon />
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              Action Items ({analysisResult.action_items?.length || 0})
            </Typography>
          </Stack>
          {analysisResult.action_items?.map((action, i) => (
            <InsightCard key={action.id} insight={action} type="action" index={i} />
          ))}
        </GlassCard>
      </Grid>
    </Grid>
  )
}

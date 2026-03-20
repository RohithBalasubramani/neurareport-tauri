import {
  Box,
  Typography,
  Stack,
  Tooltip,
  useTheme,
} from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import DescriptionIcon from '@mui/icons-material/Description'
import AssessmentIcon from '@mui/icons-material/Assessment'
import ScheduleIcon from '@mui/icons-material/Schedule'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { neutral } from '@/app/theme'
import { GlassCard } from '@/styles'
import { QuickActionCard, MiniChart, ChartBar } from './DashboardStyledComponents'

const QUICK_ACTIONS = [
  { label: 'Manage Connections', icon: StorageIcon, path: '/connections' },
  { label: 'Report Designs', icon: DescriptionIcon, path: '/templates' },
  { label: 'Run Reports', icon: AssessmentIcon, path: '/reports' },
  { label: 'Manage Schedules', icon: ScheduleIcon, path: '/schedules' },
]

export default function QuickActionsPanel({ handleNavigate, jobsTrend, maxTrend }) {
  const theme = useTheme()

  return (
    <GlassCard sx={{ animationDelay: '200ms' }}>
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2.5 }}>
        Quick Actions
      </Typography>
      <Stack spacing={1}>
        {QUICK_ACTIONS.map((action) => (
          <QuickActionCard key={action.path} onClick={() => handleNavigate(action.path, `Open ${action.label}`)}>
            <action.icon className="action-icon" sx={{ fontSize: 20, color: 'text.secondary', transition: 'color 0.2s cubic-bezier(0.22, 1, 0.36, 1)' }} />
            <Typography variant="body2" fontWeight={500} sx={{ flex: 1 }}>
              {action.label}
            </Typography>
            <ArrowForwardIcon
              className="action-arrow"
              sx={{
                fontSize: 16,
                color: 'text.tertiary',
                opacity: 0,
                transform: 'translateX(-4px)',
                transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
              }}
            />
          </QuickActionCard>
        ))}
      </Stack>

      {jobsTrend.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="caption" fontWeight={600} color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Jobs This Week
          </Typography>
          <MiniChart sx={{ mt: 1 }}>
            {jobsTrend.map((item, idx) => (
              <Tooltip key={idx} title={`${item.label}: ${item.total} jobs`} arrow>
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <ChartBar
                    height={Math.max(10, (item.total / maxTrend) * 100)}
                    color={item.failed > 0
                      ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
                      : (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])}
                    delay={idx * 50}
                  />
                  <Typography variant="caption" sx={{ fontSize: '10px', color: 'text.tertiary', mt: 0.5 }}>
                    {item.label}
                  </Typography>
                </Box>
              </Tooltip>
            ))}
          </MiniChart>
        </Box>
      )}
    </GlassCard>
  )
}

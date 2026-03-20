import {
  Box,
  Typography,
  Stack,
  Button,
  Chip,
  Collapse,
  alpha,
  useTheme,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import BoltIcon from '@mui/icons-material/Bolt'
import { neutral } from '@/app/theme'
import { glow, GlassCard } from '@/styles'
import { OnboardingStep } from './DashboardStyledComponents'

function StepChip() {
  return (
    <Chip label="Done" size="small" sx={{ fontWeight: 600, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }} />
  )
}

export default function OnboardingSection({
  needsOnboarding,
  savedConnections,
  templates,
  metrics,
  handleNavigate,
  handleDismissOnboarding,
}) {
  const theme = useTheme()

  return (
    <Collapse in={needsOnboarding}>
      <GlassCard
        sx={{
          mb: 4,
          background: theme.palette.mode === 'dark'
            ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.05)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`
            : undefined,
          animation: `${glow} 3s ease-in-out infinite`,
        }}
      >
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          <Box
            sx={{
              width: { xs: '100%', md: 64 },
              height: 64,
              borderRadius: 1,
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <RocketLaunchIcon sx={{ fontSize: 32, color: 'white' }} />
          </Box>

          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Welcome! Let's create your first report
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Complete these quick steps to get started with NeuraReport
            </Typography>

            <Stack spacing={1.5}>
              <OnboardingStep
                completed={savedConnections.length > 0}
                onClick={() => handleNavigate('/connections', 'Open connections')}
              >
                {savedConnections.length > 0 ? (
                  <CheckCircleIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                ) : (
                  <RadioButtonUncheckedIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Add a data source
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Connect to where your data lives (database, spreadsheet)
                  </Typography>
                </Box>
                {savedConnections.length > 0 && <StepChip />}
              </OnboardingStep>

              <OnboardingStep
                completed={templates.length > 0}
                onClick={() => handleNavigate('/templates', 'Open templates')}
              >
                {templates.length > 0 ? (
                  <CheckCircleIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                ) : (
                  <RadioButtonUncheckedIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Add a report design
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Upload a PDF or Excel design that shows how reports should look
                  </Typography>
                </Box>
                {templates.length > 0 && <StepChip />}
              </OnboardingStep>

              <OnboardingStep
                completed={(metrics.jobsToday ?? 0) > 0}
                disabled={savedConnections.length === 0 || templates.length === 0}
                onClick={() => {
                  if (savedConnections.length > 0 && templates.length > 0) {
                    handleNavigate('/reports', 'Open reports')
                  }
                }}
              >
                {(metrics.jobsToday ?? 0) > 0 ? (
                  <CheckCircleIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                ) : (
                  <RadioButtonUncheckedIcon sx={{ fontSize: 24, color: 'text.secondary' }} />
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Create your first report
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Generate a report using your data and design
                  </Typography>
                </Box>
                {(metrics.jobsToday ?? 0) > 0 && <StepChip />}
              </OnboardingStep>
            </Stack>

            <Stack direction="row" spacing={1.5} sx={{ mt: 3 }}>
              <Button
                variant="contained"
                onClick={() => handleNavigate('/setup/wizard', 'Open setup wizard')}
                startIcon={<BoltIcon />}
                sx={{ borderRadius: 1 }}
              >
                Run Setup Wizard
              </Button>
              <Button
                variant="text"
                onClick={handleDismissOnboarding}
                sx={{ color: 'text.secondary' }}
              >
                Dismiss
              </Button>
            </Stack>
          </Box>
        </Stack>
      </GlassCard>
    </Collapse>
  )
}

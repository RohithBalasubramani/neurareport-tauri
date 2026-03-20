/**
 * Step progress indicator
 * For multi-step operations
 */
import {
  Box,
  Typography,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  CheckCircle as SuccessIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'

export default function StepProgress({
  steps,
  currentStep,
  status = 'in_progress', // 'pending' | 'in_progress' | 'completed' | 'error'
}) {
  const theme = useTheme()

  const getStepStatus = (index) => {
    if (index < currentStep) return 'completed'
    if (index === currentStep) return status
    return 'pending'
  }

  const getStepColor = (stepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
      case 'in_progress':
        return theme.palette.mode === 'dark' ? neutral[300] : neutral[900]
      case 'error':
        return theme.palette.text.secondary
      default:
        return alpha(theme.palette.text.primary, 0.3)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {steps.map((step, index) => {
        const stepStatus = getStepStatus(index)
        const color = getStepColor(stepStatus)

        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: stepStatus === 'completed' ? color : 'transparent',
                border: `2px solid ${color}`,
                transition: 'all 0.3s ease',
              }}
            >
              {stepStatus === 'completed' ? (
                <SuccessIcon sx={{ fontSize: 16, color: 'common.white' }} />
              ) : stepStatus === 'in_progress' ? (
                <CircularProgress size={12} sx={{ color }} />
              ) : (
                <Typography variant="caption" fontWeight={600} sx={{ color }}>
                  {index + 1}
                </Typography>
              )}
            </Box>
            <Typography
              variant="body2"
              sx={{
                color: stepStatus === 'pending'
                  ? alpha(theme.palette.text.primary, 0.5)
                  : theme.palette.text.primary,
                fontWeight: stepStatus === 'in_progress' ? 600 : 400,
              }}
            >
              {step}
            </Typography>
          </Box>
        )
      })}
    </Box>
  )
}

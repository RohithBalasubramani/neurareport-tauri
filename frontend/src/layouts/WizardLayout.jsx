import { Box, Container, Paper, Typography, LinearProgress, Stack, Button } from '@mui/material'
import { neutral, palette } from '@/app/theme'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import CheckIcon from '@mui/icons-material/Check'

export default function WizardLayout({
  title,
  subtitle,
  steps,
  currentStep,
  onNext,
  onPrev,
  onComplete,
  onCancel,
  nextLabel = 'Next',
  prevLabel = 'Back',
  completeLabel = 'Complete',
  cancelLabel = 'Exit',
  nextDisabled = false,
  loading = false,
  children,
}) {
  const progress = ((currentStep + 1) / steps.length) * 100
  const isLastStep = currentStep === steps.length - 1
  const isFirstStep = currentStep === 0

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
          py: 2,
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h5" fontWeight={600}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Container>
      </Box>

      {/* Progress Bar */}
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 4,
          bgcolor: 'action.hover',
          '& .MuiLinearProgress-bar': {
            bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
          },
        }}
      />

      {/* Step Indicators */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Container maxWidth="md">
          <Stack direction="row" spacing={0} sx={{ py: 2 }}>
            {steps.map((step, index) => (
              <Box
                key={step.key}
                sx={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: (theme) => index < currentStep
                      ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
                      : index === currentStep
                        ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
                        : 'action.disabledBackground',
                    color: index <= currentStep ? 'white' : 'text.disabled',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                  }}
                >
                  {index < currentStep ? <CheckIcon sx={{ fontSize: 16 }} /> : index + 1}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="body2"
                    fontWeight={index === currentStep ? 600 : 400}
                    color={index === currentStep ? 'text.primary' : 'text.secondary'}
                  >
                    {step.label}
                  </Typography>
                  {step.description && (
                    <Typography variant="caption" color="text.disabled">
                      {step.description}
                    </Typography>
                  )}
                </Box>
                {index < steps.length - 1 && (
                  <Box
                    sx={{
                      width: 40,
                      height: 2,
                      bgcolor: (theme) => index < currentStep ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : theme.palette.divider,
                      mx: 1,
                    }}
                  />
                )}
              </Box>
            ))}
          </Stack>
        </Container>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, py: 4 }}>
        <Container maxWidth="md">
          <Paper
            elevation={0}
            sx={{
              p: 4,
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,  // Figma spec: 8px
            }}
          >
            {children}
          </Paper>
        </Container>
      </Box>

      {/* Footer Actions */}
      <Box
        sx={{
          borderTop: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
          py: 2,
        }}
      >
        <Container maxWidth="md">
          <Stack direction="row" justifyContent="space-between">
            <Stack direction="row" spacing={1}>
              {onCancel && (
                <Button
                  variant="text"
                  onClick={onCancel}
                  disabled={loading}
                  sx={{ color: 'text.secondary' }}
                >
                  {cancelLabel}
                </Button>
              )}
              <Button
                variant="outlined"
                startIcon={<ArrowBackIcon />}
                onClick={onPrev}
                disabled={isFirstStep || loading}
              >
                {prevLabel}
              </Button>
            </Stack>
            <Button
              variant="contained"
              endIcon={isLastStep ? <CheckIcon /> : <ArrowForwardIcon />}
              onClick={isLastStep ? onComplete : onNext}
              disabled={nextDisabled || loading}
            >
              {isLastStep ? completeLabel : nextLabel}
            </Button>
          </Stack>
        </Container>
      </Box>
    </Box>
  )
}

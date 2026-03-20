/**
 * Workflow Progress Component
 *
 * Displays workflow step progress using MUI Stepper.
 */
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Box,
  Typography,
  Paper,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  CheckCircle as CompleteIcon,
  Error as ErrorIcon,
  RadioButtonUnchecked as PendingIcon,
  HourglassEmpty as InProgressIcon,
} from '@mui/icons-material'
import { StepStatus } from './workflowConstants'
import { useWorkflow } from './WorkflowContracts'

function getStepIcon(status, theme) {
  switch (status) {
    case StepStatus.COMPLETED:
      return <CompleteIcon sx={{ color: 'text.secondary' }} />
    case StepStatus.FAILED:
      return <ErrorIcon sx={{ color: 'text.secondary' }} />
    case StepStatus.IN_PROGRESS:
      return <InProgressIcon sx={{ color: 'text.secondary' }} />
    default:
      return <PendingIcon sx={{ color: theme.palette.text.disabled }} />
  }
}

export default function WorkflowProgressView({ compact = false }) {
  const theme = useTheme()
  const { contract, stepStates, currentStepIndex } = useWorkflow()

  if (!contract) return null

  if (compact) {
    const completedCount = contract.steps.filter(
      (s) => stepStates[s.id]?.status === StepStatus.COMPLETED
    ).length

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {contract.name}:
        </Typography>
        <Typography variant="caption" fontWeight={600}>
          {completedCount}/{contract.steps.length} steps
        </Typography>
      </Box>
    )
  }

  return (
    <Paper
      sx={{
        p: 2,
        bgcolor: alpha(theme.palette.background.paper, 0.8),
        borderRadius: 1,  // Figma spec: 8px
      }}
    >
      <Typography variant="subtitle2" gutterBottom>
        {contract.name}
      </Typography>
      <Stepper activeStep={currentStepIndex} orientation="vertical">
        {contract.steps.map((step) => {
          const stepState = stepStates[step.id]
          return (
            <Step key={step.id} completed={stepState?.status === StepStatus.COMPLETED}>
              <StepLabel
                icon={getStepIcon(stepState?.status, theme)}
                optional={!step.required && (
                  <Typography variant="caption">Optional</Typography>
                )}
              >
                {step.name}
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
                {stepState?.error && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {stepState.error}
                  </Alert>
                )}
              </StepContent>
            </Step>
          )
        })}
      </Stepper>
    </Paper>
  )
}

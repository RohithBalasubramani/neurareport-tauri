import { Typography, Stack, Button, Chip, Alert, Stepper, Step, StepLabel } from '@mui/material'
import SwapHorizIcon from '@mui/icons-material/SwapHoriz'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import StepIndicator from '@/features/setup/components/UploadStepIndicator'

export default function UploadHeader({ verified, format, connection, onChangeConnection }) {
  return (
    <Stack spacing={1}>
      <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }} justifyContent="space-between" spacing={1.5}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Upload & Verify Design</Typography>
          <InfoTooltip content={TOOLTIP_COPY.uploadVerifyTemplate} ariaLabel="How to upload and verify a design" />
        </Stack>
        <Button size="small" variant="outlined" startIcon={<SwapHorizIcon />}
          sx={{ px: 1.5, display: { xs: 'none', sm: 'inline-flex' } }} onClick={onChangeConnection}>
          Change Connection
        </Button>
      </Stack>
      <Stepper activeStep={verified ? 1 : 0} alternativeLabel aria-label="Template onboarding steps"
        sx={{ pb: 0, '& .MuiStep-root': { position: 'relative' }, '& .MuiStepConnector-root': { top: 16 },
          '& .MuiStepLabel-label': { mt: 1 }, '& .MuiStepConnector-line': { borderColor: 'divider' } }}>
        {['Check Preview', 'Map Fields'].map((label, idx) => (
          <Step key={label} completed={idx < (verified ? 2 : 0)}>
            <StepLabel StepIconComponent={StepIndicator}>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Alert severity="info" sx={{ borderRadius: 1 }}>
        Upload a report design, verify the preview, then map fields to your data.
        SQL expressions and AI corrections are optional. Approving saves the design for report runs.
      </Alert>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ xs: 'stretch', sm: 'center' }}
        sx={{ mt: 1, width: { xs: '100%', sm: 'auto' } }}>
        <Chip label={`Auto: ${format || '-'}`} size="small" variant="outlined" />
        <Chip label={connection?.status === 'connected' ? 'Connected' : 'Unknown'} size="small"
          variant={connection?.status === 'connected' ? 'filled' : 'outlined'}
          sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
      </Stack>
    </Stack>
  )
}

import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Box, Typography, Stack, Button, Alert,
} from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import { formatDuration } from '@/hooks/useStepTimingEstimator'

export default function VerifyDetailsDialog({
  open,
  onClose,
  verifying,
  verified,
  verifyStageLabel,
  verifyProgress,
  verifyEtaText,
  verifyLog,
  verifyBtnRef,
}) {
  const handleClose = () => {
    if (!verifying) {
      onClose()
      verifyBtnRef.current?.focus()
    }
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="sm"
      aria-labelledby="verify-dialog-title"
      aria-describedby="verify-dialog-description"
    >
      <DialogTitle id="verify-dialog-title">Design Verification</DialogTitle>
      <DialogContent id="verify-dialog-description">
        <Box sx={{ my: 2 }} aria-live="polite">
          <LoadingState
            label={verifyStageLabel}
            progress={verifyProgress}
            description={verifyEtaText}
          />
          {!!verifyLog.length && (
            <Stack
              component="ol"
              spacing={0.5}
              sx={{
                mt: 2,
                pl: 2.5,
                listStyle: 'decimal',
              }}
            >
              {verifyLog.map((entry, idx) => {
                const baseLabel = entry?.label || entry?.key || `Step ${idx + 1}`
                let suffix = ''
                if (entry?.status === 'complete') {
                  if (entry?.skipped) suffix = ' (skipped)'
                  else if (entry?.elapsedMs != null) suffix = ` (${formatDuration(entry.elapsedMs)})`
                  else suffix = ' (done)'
                } else if (entry?.status === 'error') {
                  suffix = ` (failed${entry?.detail ? `: ${entry.detail}` : ''})`
                } else if (entry?.status === 'started') {
                  suffix = ' (in progress)'
                } else if (entry?.status === 'skipped') {
                  suffix = ' (skipped)'
                }
                const text = `${baseLabel}${suffix}`
                const isActive = Boolean(verifying && entry?.status === 'started')
                const isError = entry?.status === 'error'
                return (
                  <Typography
                    key={`${entry?.key || baseLabel}-${idx}`}
                    component="li"
                    variant="caption"
                    color={isActive ? 'text.primary' : isError ? 'text.secondary' : 'text.secondary'}
                    sx={{ display: 'list-item' }}
                  >
                    {text}
                  </Typography>
                )
              })}
            </Stack>
          )}
        </Box>
        {verified && <Alert severity="success" icon={<CheckCircleOutlineIcon />}>Verification passed</Alert>}
      </DialogContent>
      <DialogActions>
        <Button
          onClick={handleClose}
          disabled={verifying}
          autoFocus
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  )
}

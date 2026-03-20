import { Stack, Button, CircularProgress, Alert } from '@mui/material'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import SchemaIcon from '@mui/icons-material/Schema'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { forwardRef } from 'react'

const VerifyActionButtons = forwardRef(function VerifyActionButtons({
  file, verifying, queueingVerify, canGenerate,
  onVerify, onQueue, onMapping,
  queuedJobId, onNavigateJobs,
  mappingBtnRef,
}, verifyBtnRef) {
  return (
    <>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 2 }}>
        <Button variant="contained" color="primary" disableElevation
          startIcon={verifying ? <CircularProgress size={18} /> : <TaskAltIcon />}
          sx={{ px: 2.5 }} onClick={onVerify} disabled={!file || verifying || queueingVerify} ref={verifyBtnRef}>
          {verifying ? 'Verifying...' : 'Verify Design'}
        </Button>
        <Button variant="outlined" startIcon={queueingVerify ? <CircularProgress size={18} /> : <ScheduleIcon />}
          sx={{ px: 2.5, color: 'text.secondary', borderColor: 'divider' }}
          onClick={onQueue} disabled={!file || verifying || queueingVerify}>
          {queueingVerify ? 'Queueing...' : 'Verify in Background'}
        </Button>
        <Button variant="outlined" startIcon={<SchemaIcon />}
          sx={{ px: 2.5, color: 'text.secondary', borderColor: 'divider' }}
          onClick={onMapping} disabled={!canGenerate || verifying || queueingVerify} ref={mappingBtnRef}>
          Map Fields
        </Button>
      </Stack>
      {queuedJobId && (
        <Alert severity="info" sx={{ mt: 2, alignItems: 'center' }}
          action={<Button size="small" onClick={onNavigateJobs} sx={{ textTransform: 'none' }}>View Jobs</Button>}>
          Verification queued in background. Job ID: {queuedJobId}
        </Alert>
      )}
    </>
  )
})

export default VerifyActionButtons

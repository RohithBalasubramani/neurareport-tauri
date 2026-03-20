import {
  Stack,
  Typography,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormControlLabel,
  Switch,
} from '@mui/material'
import { splitList } from '../hooks/useOpsConsole'

export default function ShareConfigSection({ shareState, busy, toast, runRequest }) {
  const {
    shareAnalysisId, setShareAnalysisId,
    shareAccessLevel, setShareAccessLevel,
    shareExpiresHours, setShareExpiresHours,
    shareAllowedEmails, setShareAllowedEmails,
    sharePasswordProtected, setSharePasswordProtected,
  } = shareState

  return (
    <>
      <Grid item xs={12} md={6}>
        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Share Links</Typography>
          <TextField
            fullWidth
            label="Analysis ID"
            value={shareAnalysisId}
            onChange={(event) => setShareAnalysisId(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            select
            label="Access Level"
            value={shareAccessLevel}
            onChange={(event) => setShareAccessLevel(event.target.value)}
            size="small"
          >
            <MenuItem value="view">View</MenuItem>
            <MenuItem value="comment">Comment</MenuItem>
            <MenuItem value="edit">Edit</MenuItem>
          </TextField>
          <TextField
            fullWidth
            label="Expires in Hours (optional)"
            value={shareExpiresHours}
            onChange={(event) => setShareExpiresHours(event.target.value)}
            size="small"
            type="number"
          />
          <TextField
            fullWidth
            label="Allowed Emails (comma separated)"
            value={shareAllowedEmails}
            onChange={(event) => setShareAllowedEmails(event.target.value)}
            size="small"
          />
          <FormControlLabel
            control={
              <Switch
                checked={sharePasswordProtected}
                onChange={(event) => setSharePasswordProtected(event.target.checked)}
              />
            }
            label="Password Protected"
          />
          <Button
            variant="contained"
            disabled={busy}
            onClick={() => {
              if (!shareAnalysisId) {
                toast.show('Analysis ID is required', 'warning')
                return
              }
              const expires = shareExpiresHours ? Number(shareExpiresHours) : undefined
              runRequest({
                method: 'post',
                url: `/analyze/v2/${encodeURIComponent(shareAnalysisId)}/share`,
                data: {
                  access_level: shareAccessLevel,
                  expires_hours: Number.isFinite(expires) ? expires : undefined,
                  password_protected: sharePasswordProtected,
                  allowed_emails: splitList(shareAllowedEmails),
                },
              })
            }}
          >
            Create Share Link
          </Button>
        </Stack>
      </Grid>
      <Grid item xs={12} md={6}>
        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Config Endpoints</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/industries' })}>Industries</Button>
            <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/export-formats' })}>Export Formats</Button>
            <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/chart-types' })}>Chart Types</Button>
            <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/analyze/v2/config/summary-modes' })}>Summary Modes</Button>
          </Stack>
        </Stack>
      </Grid>
    </>
  )
}

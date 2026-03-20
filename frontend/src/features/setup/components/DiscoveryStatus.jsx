import {
  Typography, Stack, LinearProgress, Alert,
} from '@mui/material'
import { formatCount } from '../utils/templatesPaneUtils'

export default function DiscoveryStatus({ finding, discoverySummary }) {
  if (finding) {
    return (
      <Stack spacing={1.25} sx={{ mt: 1.5 }}>
        <LinearProgress />
        <Typography variant="body2" color="text.secondary">
          Searching data...
        </Typography>
      </Stack>
    )
  }

  if (discoverySummary) {
    return (
      <Alert severity="success" sx={{ mt: 1.5 }}>
        {`${formatCount(discoverySummary.templates)} ${discoverySummary.templates === 1 ? 'template' : 'templates'} \u2022 ${formatCount(discoverySummary.batches)} ${discoverySummary.batches === 1 ? 'batch' : 'batches'} \u2022 ${formatCount(discoverySummary.rows)} rows`}
        <Typography component="span" variant="body2" sx={{ display: 'block', mt: 0.5 }}>
          {discoverySummary.selected > 0
            ? `${formatCount(discoverySummary.selected)} batch${discoverySummary.selected === 1 ? '' : 'es'} selected for run`
            : 'No batches selected yet. Update selections in the discovery panel.'}
        </Typography>
      </Alert>
    )
  }

  return (
    <Alert severity="info" sx={{ mt: 1.5 }}>
      No discovery results yet. Run Find Reports after setting your date range.
    </Alert>
  )
}

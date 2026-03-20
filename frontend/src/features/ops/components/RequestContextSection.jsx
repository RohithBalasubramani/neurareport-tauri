import { Stack, Typography, TextField, Grid, Chip } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'

export default function RequestContextSection({ apiKey, setApiKey, bearerToken, setBearerToken, API_BASE }) {
  return (
    <Surface>
      <SectionHeader
        title="Request Context"
        subtitle="Provide API key or bearer token to authorize protected endpoints."
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Stack spacing={1}>
            <Typography variant="caption" color="text.secondary">
              API Base
            </Typography>
            <Chip label={API_BASE} variant="outlined" />
          </Stack>
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="X-API-Key"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            size="small"
            placeholder="Optional"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Bearer Token"
            value={bearerToken}
            onChange={(event) => setBearerToken(event.target.value)}
            size="small"
            placeholder="Paste access token"
          />
        </Grid>
      </Grid>
    </Surface>
  )
}

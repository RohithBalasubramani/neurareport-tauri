import { Stack, TextField, Button } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'

export default function EnrichmentSection({ enrichmentSourceId, setEnrichmentSourceId, busy, toast, runRequest }) {
  return (
    <Surface>
      <SectionHeader
        title="Enrichment Extras"
        subtitle="Legacy source-type endpoints and source lookups."
      />
      <Stack spacing={1.5}>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/enrichment/source-types' })}>/enrichment/source-types</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/enrichment/sources' })}>/enrichment/sources</Button>
        </Stack>
        <TextField
          fullWidth
          label="Source ID"
          value={enrichmentSourceId}
          onChange={(event) => setEnrichmentSourceId(event.target.value)}
          size="small"
        />
        <Button
          variant="outlined"
          disabled={busy}
          onClick={() => {
            if (!enrichmentSourceId) {
              toast.show('Source ID required', 'warning')
              return
            }
            runRequest({ url: `/enrichment/sources/${encodeURIComponent(enrichmentSourceId)}` })
          }}
        >
          Get Source
        </Button>
      </Stack>
    </Surface>
  )
}

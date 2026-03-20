import { Divider, Grid } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import CompareCommentsSection from './CompareCommentsSection'
import ShareConfigSection from './ShareConfigSection'

export default function AnalyzeExtrasSection({
  analyzeState,
  shareState,
  busy,
  toast,
  runRequest,
}) {
  return (
    <Surface>
      <SectionHeader
        title="Analyze v2 Extras"
        subtitle="Compare analyses, manage comments, create share links, and load config values."
      />
      <Grid container spacing={2}>
        <CompareCommentsSection
          analyzeState={analyzeState}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />
        <Grid item xs={12}>
          <Divider />
        </Grid>
        <ShareConfigSection
          shareState={shareState}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />
      </Grid>
    </Surface>
  )
}

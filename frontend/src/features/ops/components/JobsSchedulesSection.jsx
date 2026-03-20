import { Grid } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import RunJobForm from './RunJobForm'
import ActiveJobsSchedules from './ActiveJobsSchedules'

export default function JobsSchedulesSection({ state, busy, toast, runRequest }) {
  return (
    <Surface>
      <SectionHeader
        title="Jobs & Schedules"
        subtitle="Trigger job runs, inspect active jobs, and manage schedules."
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <RunJobForm state={state} busy={busy} toast={toast} runRequest={runRequest} />
        </Grid>
        <Grid item xs={12} md={6}>
          <ActiveJobsSchedules state={state} busy={busy} toast={toast} runRequest={runRequest} />
        </Grid>
      </Grid>
    </Surface>
  )
}

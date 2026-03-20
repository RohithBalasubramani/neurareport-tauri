import { Box, Stack } from '@mui/material'
import PageHeader from '@/components/layout/PageHeader.jsx'
import {
  useOpsConsole,
  useAuthUsersState,
  useJobsSchedulesState,
  useAnalyzeExtrasState,
  useShareLinksState,
  useEnrichmentState,
  useChartsState,
} from '../hooks/useOpsConsole'
import RequestContextSection from '../components/RequestContextSection'
import AuthUsersSection from '../components/AuthUsersSection'
import HealthOpsSection from '../components/HealthOpsSection'
import JobsSchedulesSection from '../components/JobsSchedulesSection'
import AnalyzeExtrasSection from '../components/AnalyzeExtrasSection'
import EnrichmentSection from '../components/EnrichmentSection'
import ChartsApiSection from '../components/ChartsApiSection'
import ResponseSection from '../components/ResponseSection'

export default function OpsConsolePage() {
  const ops = useOpsConsole()
  const authUsers = useAuthUsersState()
  const jobsSchedules = useJobsSchedulesState()
  const analyzeExtras = useAnalyzeExtrasState()
  const shareLinks = useShareLinksState()
  const enrichment = useEnrichmentState()
  const charts = useChartsState()

  const { toast, busy, lastResponse, apiKey, setApiKey, bearerToken, setBearerToken, runRequest, responseBody, API_BASE } = ops

  return (
    <Box sx={{ py: 3, px: { xs: 2, md: 3 } }}>
      <Stack spacing={3}>
        <PageHeader
          eyebrow="Operations"
          title="Ops Console"
          description="Direct access to health checks, auth, jobs, schedules, and AI utilities that are not surfaced elsewhere."
        />

        <RequestContextSection
          apiKey={apiKey}
          setApiKey={setApiKey}
          bearerToken={bearerToken}
          setBearerToken={setBearerToken}
          API_BASE={API_BASE}
        />

        <AuthUsersSection
          state={authUsers}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
          setBearerToken={setBearerToken}
        />

        <HealthOpsSection busy={busy} runRequest={runRequest} />

        <JobsSchedulesSection
          state={jobsSchedules}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />

        <AnalyzeExtrasSection
          analyzeState={analyzeExtras}
          shareState={shareLinks}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />

        <EnrichmentSection
          enrichmentSourceId={enrichment.enrichmentSourceId}
          setEnrichmentSourceId={enrichment.setEnrichmentSourceId}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />

        <ChartsApiSection
          state={charts}
          busy={busy}
          toast={toast}
          runRequest={runRequest}
        />

        <ResponseSection lastResponse={lastResponse} responseBody={responseBody} />
      </Stack>
    </Box>
  )
}

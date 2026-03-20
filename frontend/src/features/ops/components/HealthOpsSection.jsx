import { Stack, Button } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'

export default function HealthOpsSection({ busy, runRequest }) {
  return (
    <Surface>
      <SectionHeader
        title="Health & Ops"
        subtitle="Run service health checks and diagnostics."
      />
      <Stack spacing={1.5}>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health' })}>/health</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/healthz' })}>/healthz</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/ready' })}>/ready</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/readyz' })}>/readyz</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/detailed' })}>/health/detailed</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/token-usage' })}>/health/token-usage</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/email' })}>/health/email</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/email/test' })}>/health/email/test</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ method: 'post', url: '/health/email/refresh' })}>/health/email/refresh</Button>
          <Button variant="outlined" disabled={busy} onClick={() => runRequest({ url: '/health/scheduler' })}>/health/scheduler</Button>
        </Stack>
      </Stack>
    </Surface>
  )
}

import { Stack, Typography, Chip, Alert } from '@mui/material'
import { useAppStore } from '@/stores'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import HeartbeatBadge from '@/components/HeartbeatBadge.jsx'
import Surface from '@/components/layout/Surface.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'

export default function ConnectDBHeader({
  hbStatus,
  lastLatencyMs,
  heartbeatChipColor,
  showHeartbeatChip,
  lastHeartbeatLabel,
  children,
}) {
  const { connection } = useAppStore()

  return (
    <Surface
      component="section"
      aria-labelledby="connect-db-heading"
      sx={{ p: { xs: 2.5, md: 3 }, display: 'flex', flexDirection: 'column', gap: 2.5 }}
    >
      <SectionHeader
        id="connect-db-heading"
        eyebrow="Step 1"
        title="Connect Data Source"
        subtitle="Connected sources power report designs and report runs."
        helpContent={TOOLTIP_COPY.connectDatabase}
        helpPlacement="left"
        action={
          <Stack
            direction="row"
            alignItems="center"
            spacing={1}
            sx={{ flexWrap: 'wrap', justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}
          >
            <HeartbeatBadge
              status={hbStatus}
              latencyMs={connection.latencyMs ?? lastLatencyMs ?? undefined}
            />
            {showHeartbeatChip ? (
              <Chip
                label="Last heartbeat"
                size="small"
                color={heartbeatChipColor}
                variant={heartbeatChipColor === 'default' ? 'outlined' : 'filled'}
                sx={{ fontWeight: 600 }}
              />
            ) : null}
            <Typography variant="caption" color="text.secondary">
              {lastHeartbeatLabel}
            </Typography>
          </Stack>
        }
      />

      <Alert severity="info" sx={{ borderRadius: 1 }}>
        <Stack spacing={0.5}>
          <Typography variant="subtitle2">Safe defaults</Typography>
          <Typography variant="body2">
            Use a read-only account when possible. Testing only checks connectivity.
            The active connection is used for report runs, and you can switch it anytime.
            Passwords stay hidden after save. Removing a connection only removes it from NeuraReport; it does not change your database.
          </Typography>
        </Stack>
      </Alert>

      {children}
    </Surface>
  )
}

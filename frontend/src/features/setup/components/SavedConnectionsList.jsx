import {
  Box, Stack, Typography, Chip, List, ListItemButton,
  ListItemText,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight'
import { useAppStore } from '@/stores'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import HeartbeatBadge from '@/components/HeartbeatBadge.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { neutral } from '@/app/theme'
import { sanitizeDbType, formatHostPort } from '../constants/connectDB'

export default function SavedConnectionsList({
  listRef,
  detailId,
  setDetailId,
  rowHeartbeat,
}) {
  const { savedConnections, activeConnectionId } = useAppStore()

  return (
    <Surface
      component="section"
      aria-labelledby="saved-connections-heading"
      sx={{ p: { xs: 2.5, md: 3 }, display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <SectionHeader
        id="saved-connections-heading"
        eyebrow="Step 2"
        title="Saved Connections"
        subtitle="Tested connections stay synced for quick reuse."
        helpContent={TOOLTIP_COPY.savedConnections}
        helpPlacement="left"
      />
      {savedConnections.length === 0 ? (
        <EmptyState
          size="medium"
          title="No saved connections yet"
          description="Test and save a connection to reuse it across report runs."
          sx={{ borderStyle: 'solid' }}
        />
      ) : (
        <Stack direction="column" spacing={2} alignItems="stretch">
          <Box
            ref={listRef}
            sx={{
              flex: '1 1 auto',
              maxHeight: { md: 480 },
              overflow: 'hidden',
              p: { xs: 2, md: 2.5 },
              pt: { xs: 0.75, md: 1 },
            }}
          >
            <List
              disablePadding
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 1.5,
                flex: 1,
                pr: 0,
                overflowY: 'auto',
                maxHeight: { md: 432 },
                pt: 0,
              }}
            >
              {savedConnections.map((c) => {
                const isActive = activeConnectionId === c.backend_connection_id || activeConnectionId === c.id
                const isSelected = detailId === c.id
                const heartbeat = rowHeartbeat[c.id]
                const status = heartbeat?.status || (c.status === 'connected' ? 'healthy' : (c.status === 'failed' ? 'unreachable' : 'unknown'))
                const latency = heartbeat?.latencyMs ?? c.lastLatencyMs ?? null
                const lastConnected = c.lastConnected ? new Date(c.lastConnected).toLocaleString() : 'Never connected'
                const typeKey = sanitizeDbType(c.db_type)
                const locationDisplay =
                  typeKey === 'sqlite'
                    ? c.databasePath || c.database || c.summary || '-'
                    : `${formatHostPort(c.host, c.port) || c.host || '-'}${c.database ? `/${c.database}` : ''}`
                const typeLabel = (c.db_type || 'unknown').toUpperCase()
                return (
                  <ListItemButton
                    key={c.id}
                    onClick={() => setDetailId(c.id)}
                    selected={isSelected}
                    sx={{
                      alignItems: 'flex-start',
                      p: 2,
                      borderRadius: 1,  // Figma spec: 8px
                      border: '1px solid',
                      borderColor: isSelected ? 'text.secondary' : 'divider',
                      boxShadow: isSelected ? `0 12px 24px ${alpha(neutral[900], 0.12)}` : 'none',
                      backgroundColor: 'background.paper',
                      transition: 'border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                      '&:hover': {
                        borderColor: 'text.secondary',
                        boxShadow: `0 10px 20px ${alpha(neutral[900], 0.18)}`,
                      },
                    }}
                  >
                    <Stack direction="row" spacing={2} sx={{ width: '100%' }} alignItems="flex-start">
                      <ListItemText
                        primary={
                          <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
                            <Typography variant="subtitle2" noWrap title={c.name}>{c.name}</Typography>
                            {isActive && <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />}
                          </Stack>
                        }
                        secondary={
                          <Stack spacing={0.5} sx={{ mt: 0.25 }}>
                            <Typography variant="body2" color="text.secondary" noWrap title={locationDisplay || '-'}>
                              {locationDisplay || '-'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {typeLabel} - {lastConnected}
                            </Typography>
                          </Stack>
                        }
                        secondaryTypographyProps={{ component: 'div' }}
                        sx={{ my: 0, flex: 1, minWidth: 0 }}
                      />
                      <Stack spacing={0.75} alignItems="flex-end">
                        <HeartbeatBadge
                          size="small"
                          status={status}
                          latencyMs={latency != null ? latency : undefined}
                          tooltip={c.details || c.status || 'unknown'}
                        />
                        <KeyboardArrowRightIcon color="disabled" sx={{ transform: isSelected ? 'translateX(2px)' : 'none', transition: 'transform 0.2s cubic-bezier(0.22, 1, 0.36, 1)' }} />
                      </Stack>
                    </Stack>
                  </ListItemButton>
                )
              })}
            </List>
          </Box>
        </Stack>
      )}
    </Surface>
  )
}

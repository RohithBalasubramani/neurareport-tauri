/**
 * System status, storage, API config, and LLM cards
 */
import {
  Stack,
  Typography,
  Divider,
  Box,
  useTheme,
  alpha,
} from '@mui/material'
import SpeedIcon from '@mui/icons-material/Speed'
import StorageIcon from '@mui/icons-material/Storage'
import SecurityIcon from '@mui/icons-material/Security'
import CloudIcon from '@mui/icons-material/Cloud'
import SettingCard from './SettingCard'
import StatusChip from './StatusChip'
import ConfigRow from './ConfigRow'

export function SystemStatusCard({ health }) {
  const theme = useTheme()

  return (
    <SettingCard icon={SpeedIcon} title="System Status">
      <Stack spacing={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.75 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Overall Status
          </Typography>
          <StatusChip status={health?.status} />
        </Box>
        <ConfigRow label="API Version" value={health?.version || '-'} />
        <ConfigRow label="Response Time" value={health?.response_time_ms ? `${health.response_time_ms}ms` : '-'} />
        {health?.timestamp && (
          <ConfigRow
            label="Last Checked"
            value={new Date(health.timestamp).toLocaleString()}
          />
        )}
      </Stack>
    </SettingCard>
  )
}

export function StorageCard({ uploadsDir, stateDir, memory }) {
  const theme = useTheme()

  return (
    <SettingCard icon={StorageIcon} title="Storage">
      <Stack spacing={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.75 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Uploads Directory
          </Typography>
          <StatusChip status={uploadsDir.status} />
        </Box>
        {uploadsDir.writable !== undefined && (
          <ConfigRow label="Writable" value={uploadsDir.writable ? 'Yes' : 'No'} />
        )}
        <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.08) }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.75 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            State Directory
          </Typography>
          <StatusChip status={stateDir.status} />
        </Box>
        {memory.rss_mb && (
          <>
            <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.08) }} />
            <ConfigRow label="Memory Usage (RSS)" value={`${memory.rss_mb.toFixed(1)} MB`} />
          </>
        )}
      </Stack>
    </SettingCard>
  )
}

export function ApiConfigCard({ config }) {
  return (
    <SettingCard icon={SecurityIcon} title="API Configuration">
      <Stack spacing={1}>
        <ConfigRow
          label="API Key"
          value={config.api_key_configured ? 'Configured' : 'Not Set'}
        />
        <ConfigRow
          label="Rate Limiting"
          value={config.rate_limiting_enabled ? `Enabled (${config.rate_limit})` : 'Disabled'}
        />
        <ConfigRow
          label="Request Timeout"
          value={config.request_timeout ? `${config.request_timeout}s` : '-'}
        />
        <ConfigRow
          label="Max Upload Size"
          value={config.max_upload_size_mb ? `${config.max_upload_size_mb} MB` : '-'}
        />
        <ConfigRow label="Debug Mode" value={config.debug_mode ? 'Enabled' : 'Disabled'} />
      </Stack>
    </SettingCard>
  )
}

export function LlmProviderCard({ llm }) {
  const theme = useTheme()

  return (
    <SettingCard icon={CloudIcon} title="LLM Provider (Claude Code CLI)">
      <Stack spacing={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.75 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Connection Status
          </Typography>
          <StatusChip status={llm.status} />
        </Box>
        {llm.message && (
          <ConfigRow label="Details" value={llm.message} />
        )}
        {llm.model && (
          <ConfigRow label="Model" value={llm.model} />
        )}
      </Stack>
    </SettingCard>
  )
}

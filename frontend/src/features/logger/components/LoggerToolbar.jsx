import {
  Box, CircularProgress, Select, MenuItem,
  InputLabel, FormControl, Button, Tooltip, Chip,
  ToggleButton, ToggleButtonGroup,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import RadarIcon from '@mui/icons-material/Radar'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DashboardIcon from '@mui/icons-material/Dashboard'
import StorageIcon from '@mui/icons-material/Storage'
import { GlassCard } from '@/styles/components'
import { LOGGER_URL } from '../hooks/useLoggerPage'

export default function LoggerToolbar({
  viewMode,
  setViewMode,
  loggerStatus,
  handleRefreshIframe,
  loggerConnections,
  selectedConnectionId,
  handleConnectionSelect,
  discovering,
  handleDiscover,
}) {
  return (
    <GlassCard sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', py: 1.5 }}>
      {/* View toggle */}
      <ToggleButtonGroup
        value={viewMode}
        exclusive
        onChange={(_, v) => v && setViewMode(v)}
        size="small"
      >
        <ToggleButton value="plugin">
          <Tooltip title="Logger Dashboard — full device management UI">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <DashboardIcon sx={{ fontSize: 18 }} />
              <span>Dashboard</span>
            </Box>
          </Tooltip>
        </ToggleButton>
        <ToggleButton value="data">
          <Tooltip title="Data Pipeline — select Logger database for reports & templates">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <StorageIcon sx={{ fontSize: 18 }} />
              <span>Data Pipeline</span>
            </Box>
          </Tooltip>
        </ToggleButton>
      </ToggleButtonGroup>

      {viewMode === 'plugin' && (
        <>
          <Chip
            size="small"
            label={loggerStatus === 'online' ? 'Logger Online' : loggerStatus === 'checking' ? 'Checking...' : 'Logger Offline'}
            color={loggerStatus === 'online' ? 'success' : loggerStatus === 'checking' ? 'default' : 'error'}
            variant="outlined"
          />
          <Button
            variant="text"
            startIcon={<RefreshIcon />}
            onClick={handleRefreshIframe}
            size="small"
            disabled={loggerStatus !== 'online'}
          >
            Refresh
          </Button>
          <Button
            variant="text"
            startIcon={<OpenInNewIcon />}
            onClick={() => window.open(LOGGER_URL, '_blank')}
            size="small"
          >
            Open in New Tab
          </Button>
        </>
      )}

      {viewMode === 'data' && (
        <>
          <FormControl size="small" sx={{ minWidth: 300 }}>
            <InputLabel>Logger Database</InputLabel>
            <Select
              value={selectedConnectionId}
              label="Logger Database"
              onChange={(e) => handleConnectionSelect(e.target.value)}
            >
              {loggerConnections.length === 0 && (
                <MenuItem value="" disabled>No PostgreSQL connections</MenuItem>
              )}
              {loggerConnections.map((c) => (
                <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={discovering ? <CircularProgress size={16} /> : <RadarIcon />}
            onClick={handleDiscover}
            disabled={discovering}
            size="small"
          >
            {discovering ? 'Discovering...' : 'Discover Logger'}
          </Button>
        </>
      )}
    </GlassCard>
  )
}

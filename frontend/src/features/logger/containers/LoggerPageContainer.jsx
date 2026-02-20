import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Box, Tabs, Tab, Alert, CircularProgress, Select, MenuItem,
  InputLabel, FormControl, Button, Typography, alpha, ToggleButton,
  ToggleButtonGroup, Tooltip, Chip,
} from '@mui/material'
import SensorsIcon from '@mui/icons-material/Sensors'
import RefreshIcon from '@mui/icons-material/Refresh'
import RadarIcon from '@mui/icons-material/Radar'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DashboardIcon from '@mui/icons-material/Dashboard'
import StorageIcon from '@mui/icons-material/Storage'
import PageHeader from '@/components/layout/PageHeader'
import { GlassCard } from '@/styles/components'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import {
  discoverLoggerDatabases,
  upsertConnection,
  listConnections,
} from '@/api/client'
import { useAppStore } from '@/stores'

// Logger frontend URL — embedded as iframe plugin
const LOGGER_URL = 'http://localhost:9847?embedded=true'

export default function LoggerPageContainer() {
  const [viewMode, setViewMode] = useState('plugin') // 'plugin' | 'data'
  const [loggerConnections, setLoggerConnections] = useState([])
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [discovering, setDiscovering] = useState(false)
  const [discoveryError, setDiscoveryError] = useState(null)
  const [loggerStatus, setLoggerStatus] = useState('checking') // 'checking' | 'online' | 'offline'
  const iframeRef = useRef(null)

  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)

  // Check if Logger frontend is accessible
  useEffect(() => {
    setLoggerStatus('checking')
    const img = new Image()
    const timeout = setTimeout(() => {
      setLoggerStatus('offline')
    }, 5000)
    // Try fetching the Logger frontend to check if it's up
    fetch(LOGGER_URL, { mode: 'no-cors' })
      .then(() => {
        clearTimeout(timeout)
        setLoggerStatus('online')
      })
      .catch(() => {
        clearTimeout(timeout)
        setLoggerStatus('offline')
      })
    return () => clearTimeout(timeout)
  }, [])

  // Load existing PostgreSQL connections
  useEffect(() => {
    listConnections().then((res) => {
      const conns = (res?.connections || []).filter(
        (c) => c.db_type === 'postgresql' || c.db_type === 'postgres'
      )
      setLoggerConnections(conns)
      if (conns.length > 0 && !selectedConnectionId) {
        setSelectedConnectionId(conns[0].id)
      }
    }).catch(() => {})
  }, [])

  const handleDiscover = useCallback(async () => {
    setDiscovering(true)
    setDiscoveryError(null)
    try {
      const result = await discoverLoggerDatabases()
      const databases = result?.databases || []
      if (databases.length === 0) {
        setDiscoveryError('No Logger databases found on the network.')
        return
      }
      for (const db of databases) {
        try {
          await upsertConnection({
            name: db.name,
            dbType: 'postgresql',
            dbUrl: db.db_url,
            database: db.database,
            status: 'connected',
          })
        } catch {
          // already exists or failed
        }
      }
      const res = await listConnections()
      const conns = (res?.connections || []).filter(
        (c) => c.db_type === 'postgresql' || c.db_type === 'postgres'
      )
      setLoggerConnections(conns)
      if (conns.length > 0 && !selectedConnectionId) {
        setSelectedConnectionId(conns[0].id)
      }
    } catch (err) {
      setDiscoveryError(err?.message || 'Discovery failed')
    } finally {
      setDiscovering(false)
    }
  }, [selectedConnectionId])

  const handleRefreshIframe = useCallback(() => {
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src
    }
  }, [])

  const handleConnectionSelect = useCallback((connId) => {
    setSelectedConnectionId(connId)
    setActiveConnectionId(connId)
  }, [setActiveConnectionId])

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <PageHeader
        title="Logger"
        subtitle="PLC data logger — device management, schemas, and data pipeline"
        icon={<SensorsIcon />}
      />

      <Box sx={{ px: 4, py: 2, maxWidth: 1400, mx: 'auto', width: '100%', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Toolbar */}
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

        {discoveryError && (
          <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }} onClose={() => setDiscoveryError(null)}>
            {discoveryError}
          </Alert>
        )}

        {/* Plugin View — embedded Logger frontend */}
        {viewMode === 'plugin' && (
          <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            {loggerStatus === 'checking' && (
              <GlassCard sx={{ textAlign: 'center', py: 6, flex: 1 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Connecting to Logger...
                </Typography>
              </GlassCard>
            )}
            {loggerStatus === 'offline' && (
              <GlassCard sx={{ textAlign: 'center', py: 6, flex: 1 }}>
                <SensorsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Logger Not Available
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 500, mx: 'auto' }}>
                  The Logger frontend at <strong>{LOGGER_URL}</strong> is not reachable.
                  Make sure the Logger service is running.
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setLoggerStatus('checking')
                    fetch(LOGGER_URL, { mode: 'no-cors' })
                      .then(() => setLoggerStatus('online'))
                      .catch(() => setLoggerStatus('offline'))
                  }}
                >
                  Retry Connection
                </Button>
              </GlassCard>
            )}
            {loggerStatus === 'online' && (
              <Box
                sx={{
                  flex: 1,
                  minHeight: 600,
                  borderRadius: 2,
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <iframe
                  ref={iframeRef}
                  src={LOGGER_URL}
                  title="Logger Dashboard"
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    display: 'block',
                    minHeight: 600,
                  }}
                />
              </Box>
            )}
          </Box>
        )}

        {/* Data Pipeline View — connection-based integration for reports/templates */}
        {viewMode === 'data' && (
          <>
            {!selectedConnectionId ? (
              <GlassCard sx={{ textAlign: 'center', py: 6 }}>
                <SensorsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Logger Database Selected
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Select an existing PostgreSQL connection or click "Discover Logger" to find Logger databases.
                  Once connected, you can use Logger data in templates and reports.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<RadarIcon />}
                  onClick={handleDiscover}
                  disabled={discovering}
                >
                  Discover Logger Databases
                </Button>
              </GlassCard>
            ) : (
              <GlassCard>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                  Data Pipeline Integration
                </Typography>
                <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                  This Logger database is available as a data source throughout NeuraReport.
                  You can select it in the <strong>Reports</strong> page, <strong>Template Creator</strong>,
                  and any feature that uses the Data Source selector.
                </Alert>

                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 2 }}>
                  {loggerConnections.filter(c => c.id === selectedConnectionId).map(c => (
                    <GlassCard key={c.id} sx={{ '&:hover': { transform: 'none' } }}>
                      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
                        {c.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', fontSize: '0.75rem', mb: 1 }}>
                        {c.db_type}
                      </Typography>
                      <Chip
                        size="small"
                        label={c.status || 'connected'}
                        color={c.status === 'connected' || !c.status ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </GlassCard>
                  ))}
                </Box>

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => window.location.href = '/neurareport/reports'}
                    size="small"
                  >
                    Go to Reports
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => window.location.href = '/neurareport/templates/create'}
                    size="small"
                  >
                    Create Template
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => window.location.href = '/neurareport/connections'}
                    size="small"
                  >
                    Manage Connections
                  </Button>
                </Box>
              </GlassCard>
            )}
          </>
        )}
      </Box>
    </Box>
  )
}

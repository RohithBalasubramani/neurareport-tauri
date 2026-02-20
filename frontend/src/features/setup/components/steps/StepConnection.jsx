import { useState, useCallback, useEffect } from 'react'
import {
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  CardActionArea,
  Radio,
  Button,
  Alert,
  Collapse,
  Divider,
  Chip,
  alpha,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import StorageIcon from '@mui/icons-material/Storage'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ScienceIcon from '@mui/icons-material/Science'
import CloudIcon from '@mui/icons-material/Cloud'
import TableChartIcon from '@mui/icons-material/TableChart'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { Drawer } from '@/components/Drawer'
import ConnectionForm from '@/features/connections/components/ConnectionForm'
import * as api from '@/api/client'
import { neutral, secondary, palette } from '@/app/theme'

// Demo connection that doesn't require real credentials
const DEMO_CONNECTION = {
  id: 'demo-connection',
  name: 'Sample Database (Demo)',
  db_type: 'demo',
  database: 'sample_data',
  status: 'connected',
  summary: 'Pre-loaded sample data for testing',
  isDemo: true,
}

export default function StepConnection({ wizardState, updateWizardState, onComplete, setLoading }) {
  const toast = useToast()
  const { execute } = useInteraction()
  const savedConnections = useAppStore((s) => s.savedConnections)
  const setSavedConnections = useAppStore((s) => s.setSavedConnections)
  const addSavedConnection = useAppStore((s) => s.addSavedConnection)
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)
  const activeConnection = useAppStore((s) => s.activeConnection)

  const [selectedId, setSelectedId] = useState(wizardState.connectionId || activeConnection?.id || null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [formLoading, setFormLoading] = useState(false)
  const normalizedConnections = Array.isArray(savedConnections)
    ? savedConnections.filter((conn) => conn && typeof conn === 'object' && conn.id)
    : []

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const state = await api.bootstrapState()
        if (state?.connections) {
          setSavedConnections(state.connections)
        }
      } catch (err) {
        console.error('Failed to fetch connections:', err)
        toast.show('Failed to load saved connections', 'warning')
      }
    }
    if (normalizedConnections.length === 0) {
      fetchConnections()
    }
  }, [normalizedConnections.length, setSavedConnections, toast])

  const handleSelect = useCallback((connectionId) => {
    setSelectedId(connectionId)
    updateWizardState({ connectionId })
    setActiveConnectionId(connectionId)
  }, [updateWizardState, setActiveConnectionId])

  const handleAddConnection = useCallback(() => {
    setDrawerOpen(true)
  }, [])

  const handleSaveConnection = useCallback(async (connectionData) => {
    setFormLoading(true)
    try {
      await execute({
        type: InteractionType.CREATE,
        label: `Add connection "${connectionData?.name || connectionData?.db_url || 'connection'}"`,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: false,
        intent: {
          connectionName: connectionData?.name,
          dbType: connectionData?.db_type,
        },
        action: async () => {
          try {
            const result = await api.testConnection(connectionData)
            if (!result.ok) {
              throw new Error(result.detail || 'Connection test failed')
            }

            const savedConnection = await api.upsertConnection({
              id: result.connection_id,
              name: connectionData.name,
              dbType: connectionData.db_type,
              dbUrl: connectionData.db_url,
              database: connectionData.database,
              status: 'connected',
              latencyMs: result.latency_ms,
            })

            addSavedConnection(savedConnection)
            handleSelect(savedConnection.id)
            toast.show('Connection added', 'success')
            setDrawerOpen(false)
            return savedConnection
          } catch (err) {
            toast.show(err.message || 'Failed to save connection', 'error')
            throw err
          }
        },
      })
    } finally {
      setFormLoading(false)
    }
  }, [addSavedConnection, handleSelect, toast, execute])

  const handleContinue = useCallback(() => {
    if (selectedId) {
      onComplete()
    }
  }, [selectedId, onComplete])

  const handleSelectDemo = useCallback(() => {
    setSelectedId(DEMO_CONNECTION.id)
    updateWizardState({ connectionId: DEMO_CONNECTION.id, isDemo: true })
    // Add demo connection to store temporarily
    if (!normalizedConnections.find(c => c.id === DEMO_CONNECTION.id)) {
      addSavedConnection(DEMO_CONNECTION)
    }
    setActiveConnectionId(DEMO_CONNECTION.id)
    toast.show('Demo mode activated! Using sample data.', 'success')
  }, [updateWizardState, normalizedConnections, addSavedConnection, setActiveConnectionId, toast])

  const handleSkipConnection = useCallback(() => {
    // Allow users to skip if they just want to explore
    updateWizardState({ connectionId: null, skippedConnection: true })
    onComplete()
  }, [updateWizardState, onComplete])

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        Connect Your Data
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Choose where your report data comes from. You can always change this later.
      </Typography>

      {/* Quick Start Options */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="subtitle2" fontWeight={600} color="text.secondary" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
          Quick Start
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Card
            variant="outlined"
            sx={{
              flex: 1,
              border: 2,
              borderColor: selectedId === DEMO_CONNECTION.id ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
              bgcolor: selectedId === DEMO_CONNECTION.id ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
              },
            }}
          >
            <CardActionArea onClick={handleSelectDemo} sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <ScienceIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                <Typography variant="subtitle1" fontWeight={600}>
                  Try Demo Mode
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Explore with sample data — no setup needed
                </Typography>
                <Chip label="Recommended for first-time users" size="small" variant="outlined" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
              </CardContent>
            </CardActionArea>
          </Card>

          <Card
            variant="outlined"
            sx={{
              flex: 1,
              border: 2,
              borderColor: 'divider',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: 'secondary.main',
              },
            }}
          >
            <CardActionArea onClick={handleSkipConnection} sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <CloudIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                <Typography variant="subtitle1" fontWeight={600}>
                  Skip for Now
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Set up data source later and explore templates first
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Stack>
      </Box>

      <Divider sx={{ my: 3 }}>
        <Chip label="Or connect your own data" size="small" />
      </Divider>

      {normalizedConnections.length === 0 || normalizedConnections.every((c) => c.isDemo) ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          No database connections yet. Add one below or try demo mode above.
        </Alert>
      ) : (
        <Stack spacing={2} sx={{ mb: 3 }}>
          {normalizedConnections.map((conn) => (
            <Card
              key={conn.id}
              variant="outlined"
              sx={{
                border: 2,
                borderColor: selectedId === conn.id ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
                transition: 'border-color 0.2s',
              }}
            >
              <CardActionArea onClick={() => handleSelect(conn.id)}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Radio
                    checked={selectedId === conn.id}
                    sx={{ p: 0 }}
                  />
                  <StorageIcon sx={{ color: 'text.secondary' }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" fontWeight={500}>
                      {conn.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {conn.db_type} • {conn.summary || conn.database}
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      size="small"
                      label={conn.status === 'connected' ? 'Connected' : 'Disconnected'}
                      variant="outlined"
                      sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                    />
                    {selectedId === conn.id && (
                      <CheckCircleIcon sx={{ color: 'text.secondary' }} />
                    )}
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Stack>
      )}

      <Divider sx={{ my: 3 }} />

      <Button
        variant="outlined"
        startIcon={<AddIcon />}
        onClick={handleAddConnection}
        fullWidth
        sx={{
          py: 1.5,
          borderStyle: 'dashed',
        }}
      >
        Add New Connection
      </Button>

      {/* Connection Form Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="New Connection"
        subtitle="Configure your database connection"
        width={520}
      >
        <ConnectionForm
          onSave={handleSaveConnection}
          onCancel={() => setDrawerOpen(false)}
          loading={formLoading}
        />
      </Drawer>
    </Box>
  )
}

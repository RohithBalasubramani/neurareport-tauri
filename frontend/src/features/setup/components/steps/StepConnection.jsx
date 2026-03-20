import { useState, useCallback, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Divider,
  Chip,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { Drawer } from '@/components/drawer'
import ConnectionForm from '@/features/connections/components/ConnectionForm'
import * as api from '@/api/client'
import QuickStartCards from './QuickStartCards'
import ConnectionList from './ConnectionList'

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

  const handleSelectDemo = useCallback(() => {
    setSelectedId(DEMO_CONNECTION.id)
    updateWizardState({ connectionId: DEMO_CONNECTION.id, isDemo: true })
    if (!normalizedConnections.find(c => c.id === DEMO_CONNECTION.id)) {
      addSavedConnection(DEMO_CONNECTION)
    }
    setActiveConnectionId(DEMO_CONNECTION.id)
    toast.show('Demo mode activated! Using sample data.', 'success')
  }, [updateWizardState, normalizedConnections, addSavedConnection, setActiveConnectionId, toast])

  const handleSkipConnection = useCallback(() => {
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

      <QuickStartCards
        selectedId={selectedId}
        demoId={DEMO_CONNECTION.id}
        onSelectDemo={handleSelectDemo}
        onSkip={handleSkipConnection}
      />

      <Divider sx={{ my: 3 }}>
        <Chip label="Or connect your own data" size="small" />
      </Divider>

      <ConnectionList
        connections={normalizedConnections}
        selectedId={selectedId}
        onSelect={handleSelect}
      />

      <Divider sx={{ my: 3 }} />

      <Button
        variant="outlined"
        startIcon={<AddIcon />}
        onClick={() => setDrawerOpen(true)}
        fullWidth
        sx={{ py: 1.5, borderStyle: 'dashed' }}
      >
        Add New Connection
      </Button>

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

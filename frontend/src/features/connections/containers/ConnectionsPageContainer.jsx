/**
 * Premium Connections Page
 * Data source management with theme-based styling
 */
import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import {
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Alert,
  Stack,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import StorageIcon from '@mui/icons-material/Storage'
import TableViewIcon from '@mui/icons-material/TableView'
import { DataTable } from '@/components/DataTable'
import { ConfirmModal } from '@/components/Modal'
import { Drawer } from '@/components/Drawer'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import FavoriteButton from '@/features/favorites/components/FavoriteButton.jsx'
import * as api from '@/api/client'
import ConnectionForm from '../components/ConnectionForm'
import ConnectionSchemaDrawer from '../components/ConnectionSchemaDrawer'
// UX Governance - Enforced interaction API
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import { neutral, palette, status as statusColors } from '@/app/theme'
import { fadeInUp } from '@/styles'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1400,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  animation: `${fadeInUp} 0.5s ease-out`,
}))

const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: 8,  // Figma spec: 8px
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.15)}`,
    minWidth: 160,
    animation: `${fadeInUp} 0.2s ease-out`,
  },
}))

const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  borderRadius: 8,
  margin: theme.spacing(0.5, 1),
  padding: theme.spacing(1, 1.5),
  fontSize: '14px',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

const IconContainer = styled(Box)(({ theme }) => ({
  width: 32,
  height: 32,
  borderRadius: 8,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const ActionButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    transform: 'scale(1.05)',
  },
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConnectionsPage() {
  const theme = useTheme()
  const toast = useToast()
  // UX Governance: Enforced interaction API - ALL user actions flow through this
  const { execute } = useInteraction()
  const savedConnections = useAppStore((s) => s.savedConnections)
  const setSavedConnections = useAppStore((s) => s.setSavedConnections)
  const addSavedConnection = useAppStore((s) => s.addSavedConnection)
  const removeSavedConnection = useAppStore((s) => s.removeSavedConnection)
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)
  const activeConnectionId = useAppStore((s) => s.activeConnectionId)

  const [loading, setLoading] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editingConnection, setEditingConnection] = useState(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [deletingConnection, setDeletingConnection] = useState(null)
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [menuConnection, setMenuConnection] = useState(null)
  const [schemaOpen, setSchemaOpen] = useState(false)
  const [schemaConnection, setSchemaConnection] = useState(null)
  const [favorites, setFavorites] = useState(new Set())
  const didLoadFavoritesRef = useRef(false)

  useEffect(() => {
    if (didLoadFavoritesRef.current) return
    didLoadFavoritesRef.current = true
    api.getFavorites()
      .then((data) => {
        const favIds = (data.connections || []).map((c) => c.id)
        setFavorites(new Set(favIds))
      })
      .catch((err) => {
        console.error('Failed to load favorites:', err)
        // Non-critical - don't block UI but log for debugging
      })
  }, [])

  const handleFavoriteToggle = useCallback((connectionId, isFavorite) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      if (isFavorite) {
        next.add(connectionId)
      } else {
        next.delete(connectionId)
      }
      return next
    })
  }, [])

  const handleOpenMenu = useCallback((event, connection) => {
    event.stopPropagation()
    setMenuAnchor(event.currentTarget)
    setMenuConnection(connection)
  }, [])

  const handleCloseMenu = useCallback(() => {
    setMenuAnchor(null)
    setMenuConnection(null)
  }, [])

  const drawerOpenRef = useRef(false)
  const handleAddConnection = useCallback(() => {
    if (drawerOpenRef.current) return // Ref-based guard: prevents double-click opening duplicate drawers
    drawerOpenRef.current = true
    setEditingConnection(null)
    setDrawerOpen(true)
  }, [])

  const handleEditConnection = useCallback(() => {
    setEditingConnection(menuConnection)
    setDrawerOpen(true)
    handleCloseMenu()
  }, [menuConnection, handleCloseMenu])

  const handleDeleteClick = useCallback(() => {
    setDeletingConnection(menuConnection)
    setDeleteConfirmOpen(true)
    handleCloseMenu()
  }, [menuConnection, handleCloseMenu])

  const handleSchemaInspect = useCallback(async () => {
    if (!menuConnection) return
    const connectionToInspect = menuConnection
    handleCloseMenu()

    // UX Governance: Analyze action with tracking
    execute({
      type: InteractionType.ANALYZE,
      label: `Inspect schema for "${connectionToInspect.name}"`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      errorMessage: 'Unable to connect to database. Please verify the connection is active.',
      action: async () => {
        setLoading(true)
        try {
          const result = await api.healthcheckConnection(connectionToInspect.id)
          if (result.status !== 'ok') {
            throw new Error('Connection is unavailable. Please verify connection settings.')
          }
          setSchemaConnection(connectionToInspect)
          setSchemaOpen(true)
        } finally {
          setLoading(false)
        }
      },
    })
  }, [menuConnection, handleCloseMenu, execute])

  const handleDeleteConfirm = useCallback(async () => {
    if (!deletingConnection) return
    const connectionToDelete = deletingConnection
    const connectionData = savedConnections.find((c) => c.id === connectionToDelete.id)

    setDeleteConfirmOpen(false)
    setDeletingConnection(null)

    // UX Governance: Delete action with tracking
    execute({
      type: InteractionType.DELETE,
      label: `Delete data source "${connectionToDelete.name}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: `"${connectionToDelete.name}" removed`,
      errorMessage: 'Failed to delete connection',
      action: async () => {
        // Remove from UI immediately
        removeSavedConnection(connectionToDelete.id)

        // Delete from backend immediately (no delayed timeout)
        try {
          await api.deleteConnection(connectionToDelete.id)
        } catch (err) {
          // If delete fails, restore the connection to UI
          if (connectionData) {
            addSavedConnection(connectionData)
          }
          throw err
        }

        // Show undo toast - undo will re-create the connection
        toast.showWithUndo(
          `"${connectionToDelete.name}" removed`,
          async () => {
            // Undo: re-create the connection via API
            if (connectionData) {
              try {
                const restored = await api.upsertConnection({
                  name: connectionData.name,
                  dbType: connectionData.db_type,
                  dbUrl: connectionData.db_url,
                  database: connectionData.database || connectionData.summary,
                  status: connectionData.status || 'connected',
                  latencyMs: connectionData.latency_ms,
                })
                addSavedConnection(restored)
                toast.show('Data source restored', 'success')
              } catch (restoreErr) {
                console.error('Failed to restore connection:', restoreErr)
                toast.show('Failed to restore connection', 'error')
              }
            }
          },
          { severity: 'info' }
        )
      },
    })
  }, [deletingConnection, savedConnections, removeSavedConnection, setSavedConnections, toast, execute])

  const handleSaveConnection = useCallback(async (connectionData) => {
    const isEditing = !!editingConnection

    // UX Governance: Create/Update action with tracking
    execute({
      type: isEditing ? InteractionType.UPDATE : InteractionType.CREATE,
      label: isEditing ? `Update data source "${connectionData.name}"` : `Add data source "${connectionData.name}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: isEditing ? 'Data source updated' : 'Data source added',
      errorMessage: 'Failed to save connection',
      action: async () => {
        setLoading(true)
        try {
          const result = await api.testConnection(connectionData)
          if (!result.ok) {
            throw new Error(result.detail || 'Connection test failed')
          }

          const savedConnection = await api.upsertConnection({
            id: editingConnection?.id || result.connection_id,
            name: connectionData.name,
            dbType: connectionData.db_type,
            dbUrl: connectionData.db_url,
            database: connectionData.database,
            status: 'connected',
            latencyMs: result.latency_ms,
          })

          addSavedConnection(savedConnection)
          drawerOpenRef.current = false
          setDrawerOpen(false)
        } finally {
          setLoading(false)
        }
      },
    })
  }, [editingConnection, addSavedConnection, execute])

  const handleTestConnection = useCallback(async (connection) => {
    // UX Governance: Execute action with tracking
    execute({
      type: InteractionType.EXECUTE,
      label: `Test connection "${connection.name}"`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      errorMessage: 'Connection test failed',
      action: async () => {
        setLoading(true)
        try {
          const result = await api.healthcheckConnection(connection.id)
          if (result.status === 'ok') {
            toast.show(`Connected (${result.latency_ms}ms)`, 'success')
          } else {
            throw new Error('Connection unavailable')
          }
        } finally {
          setLoading(false)
        }
      },
    })
  }, [toast, execute])

  const handleRowClick = useCallback((row) => {
    setActiveConnectionId(row.id)
    toast.show(`Selected: ${row.name}`, 'info')
  }, [setActiveConnectionId, toast])

  const columns = useMemo(() => [
    {
      field: 'name',
      headerName: 'Name',
      minWidth: 200,
      flex: 1, // Take remaining space but ensure minimum width
      renderCell: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FavoriteButton
            entityType="connections"
            entityId={row.id}
            initialFavorite={favorites.has(row.id)}
            onToggle={(isFav) => handleFavoriteToggle(row.id, isFav)}
          />
          <IconContainer
            sx={{
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            }}
          >
            <StorageIcon sx={{ color: theme.palette.text.secondary, fontSize: 16 }} />
          </IconContainer>
          <Box sx={{ minWidth: 0 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Box data-testid="connection-name" sx={{ fontWeight: 500, fontSize: '14px', color: theme.palette.text.primary }}>
                {value}
              </Box>
              {activeConnectionId === row.id && (
                <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
              )}
            </Stack>
            <Box sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
              {row.summary || row.db_type}
            </Box>
          </Box>
        </Box>
      ),
    },
    {
      field: 'db_type',
      headerName: 'Type',
      width: 120,
      renderCell: (value) => {
        const typeLabels = { sqlite: 'SQLite', postgresql: 'PostgreSQL', postgres: 'PostgreSQL', mysql: 'MySQL', mssql: 'SQL Server', oracle: 'Oracle', csv: 'CSV', excel: 'Excel', json: 'JSON' }
        return (
          <Chip
            label={typeLabels[(value || '').toLowerCase()] || value || 'Unknown'}
            size="small"
            data-testid="connection-db-type"
            sx={{
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              color: theme.palette.text.secondary,
              fontSize: '0.75rem',
              borderRadius: 1,  // Figma spec: 8px
            }}
          />
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (value) => {
        const isConnected = value === 'connected'
        return (
          <Chip
            icon={isConnected
              ? <CheckCircleIcon sx={{ fontSize: 14 }} />
              : <ErrorIcon sx={{ fontSize: 14 }} />
            }
            label={value || 'Unknown'}
            size="small"
            data-testid="connection-status"
            sx={{
              fontSize: '0.75rem',
              textTransform: 'capitalize',
              borderRadius: 1,  // Figma spec: 8px
              bgcolor: isConnected
                ? alpha(statusColors.success, 0.1)
                : alpha(statusColors.destructive, 0.1),
              color: isConnected
                ? statusColors.success
                : statusColors.destructive,
              '& .MuiChip-icon': {
                color: 'inherit',
              },
            }}
          />
        )
      },
    },
    {
      field: 'lastLatencyMs',
      headerName: 'Latency',
      width: 100,
      renderCell: (value) => (
        <Box data-testid="connection-latency" sx={{ color: theme.palette.text.secondary, fontSize: '14px' }}>
          {value ? `${value}ms` : '-'}
        </Box>
      ),
    },
    {
      field: 'lastConnected',
      headerName: 'Last Connected',
      width: 160,
      renderCell: (value) => {
        if (!value) return <Box sx={{ color: theme.palette.text.disabled, fontSize: '14px' }}>-</Box>
        const d = new Date(value)
        const now = new Date()
        const diffMs = now - d
        const diffMin = Math.floor(diffMs / 60000)
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        let relative
        if (diffMin < 1) relative = 'Just now'
        else if (diffMin < 60) relative = `${diffMin}m ago`
        else if (diffHr < 24) relative = `${diffHr}h ago`
        else if (diffDay < 7) relative = `${diffDay}d ago`
        else relative = d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Box data-testid="connection-last-connected" sx={{ color: theme.palette.text.secondary, fontSize: '14px', cursor: 'default' }}>
              {relative}
            </Box>
          </Tooltip>
        )
      },
    },
  ], [favorites, handleFavoriteToggle, theme, activeConnectionId])

  const filters = useMemo(() => [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'connected', label: 'Connected' },
        { value: 'disconnected', label: 'Disconnected' },
        { value: 'error', label: 'Error' },
      ],
    },
    {
      key: 'db_type',
      label: 'Type',
      options: [
        { value: 'sqlite', label: 'SQLite' },
        { value: 'postgresql', label: 'PostgreSQL' },
      ],
    },
  ], [])

  return (
    <PageContainer>
      <Alert severity="info" sx={{ mb: 2, borderRadius: 1 }}>
        Data sources power report runs and AI tools. Use a read-only account when possible. Active sources are labeled
        and can be switched anytime.
      </Alert>
      <DataTable
        title="Data Sources"
        subtitle="Connect to your databases and data files"
        columns={columns}
        data={savedConnections}
        loading={loading}
        searchPlaceholder="Search connections..."
        filters={filters}
        actions={[
          {
            label: 'Add Data Source',
            icon: <AddIcon sx={{ fontSize: 18 }} />,
            variant: 'contained',
            onClick: handleAddConnection,
          },
        ]}
        onRowClick={handleRowClick}
        rowActions={(row) => (
          <Tooltip title="More actions">
            <ActionButton
              size="small"
              onClick={(e) => handleOpenMenu(e, row)}
              aria-label="More actions"
              data-testid="connection-actions-button"
              sx={{ color: theme.palette.text.secondary }}
            >
              <MoreVertIcon sx={{ fontSize: 18 }} />
            </ActionButton>
          </Tooltip>
        )}
        emptyState={{
          icon: StorageIcon,
          title: 'No data sources yet',
          description: 'Connect to a database to start pulling data for your reports.',
          actionLabel: 'Add Data Source',
          onAction: handleAddConnection,
        }}
      />

      {/* Row Actions Menu */}
      <StyledMenu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleCloseMenu}
      >
        <StyledMenuItem
          onClick={() => { handleTestConnection(menuConnection); handleCloseMenu() }}
        >
          <ListItemIcon>
            <RefreshIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
            Test Connection
          </ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleSchemaInspect}>
          <ListItemIcon>
            <TableViewIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
            Inspect Schema
          </ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleEditConnection}>
          <ListItemIcon>
            <EditIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
            Edit
          </ListItemText>
        </StyledMenuItem>
        <StyledMenuItem
          onClick={handleDeleteClick}
          sx={{ color: theme.palette.text.primary }}
        >
          <ListItemIcon>
            <DeleteIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
            Delete
          </ListItemText>
        </StyledMenuItem>
      </StyledMenu>

      {/* Connection Form Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={() => { drawerOpenRef.current = false; setDrawerOpen(false) }}
        title={editingConnection ? 'Edit Data Source' : 'Add Data Source'}
        subtitle="Enter your database details to connect"
        width={520}
      >
        <ConnectionForm
          connection={editingConnection}
          onSave={handleSaveConnection}
          onCancel={() => { drawerOpenRef.current = false; setDrawerOpen(false) }}
          loading={loading}
        />
      </Drawer>

      {/* Delete Confirmation */}
      <ConfirmModal
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Remove Data Source"
        message={`Remove "${deletingConnection?.name}"? This only removes it from NeuraReport and does not change your database. You can undo this within a few seconds.`}
        confirmLabel="Remove"
        severity="error"
        loading={loading}
      />

      <ConnectionSchemaDrawer
        open={schemaOpen}
        onClose={() => setSchemaOpen(false)}
        connection={schemaConnection}
      />
    </PageContainer>
  )
}

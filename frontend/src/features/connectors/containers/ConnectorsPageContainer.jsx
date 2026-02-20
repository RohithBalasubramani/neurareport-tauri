/**
 * Connectors Page Container
 * Database and cloud storage connector management.
 */
import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Tabs,
  Tab,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Storage as DatabaseIcon,
  Cloud as CloudIcon,
  Refresh as RefreshIcon,
  CheckCircle as ConnectedIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Schema as SchemaIcon,
  Code as QueryIcon,
} from '@mui/icons-material'
import useConnectorStore from '@/stores/connectorStore'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { neutral, palette, secondary } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const Content = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
}))

const ConnectorCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: `0 8px 30px ${alpha(theme.palette.text.primary, 0.15)}`,
  },
}))

const ConnectorIcon = styled(Box)(({ theme }) => ({
  width: 48,
  height: 48,
  borderRadius: 8,  // Figma spec: 8px
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
}))

const StatusChip = styled(Chip)(({ theme, status }) => ({
  borderRadius: 6,
  fontWeight: 500,
  ...(status === 'connected' && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    color: theme.palette.text.secondary,
  }),
  ...(status === 'error' && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.secondary,
  }),
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

// =============================================================================
// CONNECTOR CONFIGS
// =============================================================================

const CONNECTOR_CATEGORIES = {
  database: {
    label: 'Databases',
    icon: DatabaseIcon,
    connectors: [
      { id: 'postgresql', name: 'PostgreSQL', color: secondary.slate[600] },
      { id: 'mysql', name: 'MySQL', color: secondary.cyan[700] },
      { id: 'mongodb', name: 'MongoDB', color: secondary.emerald[500] },
      { id: 'sqlserver', name: 'SQL Server', color: secondary.rose[600] },
      { id: 'bigquery', name: 'BigQuery', color: secondary.cyan[500] },
      { id: 'snowflake', name: 'Snowflake', color: secondary.cyan[400] },
    ],
  },
  cloud_storage: {
    label: 'Cloud Storage',
    icon: CloudIcon,
    connectors: [
      { id: 'google_drive', name: 'Google Drive', color: secondary.cyan[500] },
      { id: 'dropbox', name: 'Dropbox', color: secondary.violet[500] },
      { id: 's3', name: 'Amazon S3', color: secondary.fuchsia[500] },
      { id: 'azure_blob', name: 'Azure Blob', color: secondary.teal[500] },
      { id: 'onedrive', name: 'OneDrive', color: secondary.slate[500] },
    ],
  },
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConnectorsPage() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const addSavedConnection = useAppStore((s) => s.addSavedConnection)
  const setSavedConnections = useAppStore((s) => s.setSavedConnections)
  const removeSavedConnection = useAppStore((s) => s.removeSavedConnection)
  const {
    connectorTypes,
    connections,
    currentConnection,
    schema,
    queryResult,
    loading,
    testing,
    querying,
    error,
    fetchConnectorTypes,
    fetchConnections,
    testConnection,
    createConnection,
    deleteConnection,
    checkHealth,
    fetchSchema,
    executeQuery,
    reset,
  } = useConnectorStore()

  const [activeTab, setActiveTab] = useState(0)
  const [connectDialogOpen, setConnectDialogOpen] = useState(false)
  const [selectedConnector, setSelectedConnector] = useState(null)
  const [connectionName, setConnectionName] = useState('')
  const [connectionConfig, setConnectionConfig] = useState({})
  const [queryDialogOpen, setQueryDialogOpen] = useState(false)
  const [queryText, setQueryText] = useState('')
  const [schemaDialogOpen, setSchemaDialogOpen] = useState(false)

  useEffect(() => {
    fetchConnectorTypes()
    fetchConnections().then(() => {
      // Sync to global app store so other pages see the connections
      const connectorConnections = useConnectorStore.getState().connections
      if (connectorConnections?.length > 0 && setSavedConnections) {
        setSavedConnections(connectorConnections)
      }
    })
    return () => reset()
  }, [fetchConnectorTypes, fetchConnections, reset, setSavedConnections])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'connectors', ...intent },
      action,
    })
  }, [execute])

  const handleOpenConnect = useCallback((connector) => {
    return executeUI('Open connector setup', () => {
      setSelectedConnector(connector)
      setConnectionName('')
      setConnectionConfig({})
      setConnectDialogOpen(true)
    }, { connectorId: connector?.id })
  }, [executeUI])

  const handleCloseConnect = useCallback(() => {
    return executeUI('Close connector setup', () => setConnectDialogOpen(false))
  }, [executeUI])

  const handleTestConnection = useCallback(() => {
    if (!selectedConnector) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Test connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'connectors', connectorId: selectedConnector.id },
      action: async () => {
        const result = await testConnection(selectedConnector.id, connectionConfig)
        if (result?.success) {
          toast.show('Connection successful!', 'success')
        } else {
          toast.show(`Connection failed: ${result?.error || 'Unknown error'}`, 'error')
        }
        return result
      },
    })
  }, [connectionConfig, execute, selectedConnector, testConnection, toast])

  const handleCreateConnection = useCallback(() => {
    if (!selectedConnector || !connectionName) return undefined
    return execute({
      type: InteractionType.CREATE,
      label: 'Create connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'connectors', connectorId: selectedConnector.id, name: connectionName },
      action: async () => {
        const connection = await createConnection(
          selectedConnector.id,
          connectionName,
          connectionConfig
        )
        if (connection) {
          // Sync to global app store so other pages see the new connection
          if (addSavedConnection) {
            addSavedConnection(connection)
          }
          setConnectDialogOpen(false)
          setSelectedConnector(null)
          toast.show('Connection created successfully', 'success')
        }
        return connection
      },
    })
  }, [addSavedConnection, connectionConfig, connectionName, createConnection, execute, selectedConnector, toast])

  const handleDeleteConnection = useCallback((connectionId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'connectors', connectionId },
      action: async () => {
        const success = await deleteConnection(connectionId)
        if (success) {
          // Sync deletion to global app store so other pages reflect the change
          if (removeSavedConnection) {
            removeSavedConnection(connectionId)
          }
          toast.show('Connection deleted', 'success')
        }
        return success
      },
    })
  }, [deleteConnection, execute, removeSavedConnection, toast])

  const handleCheckHealth = useCallback((connectionId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Check connection health',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'connectors', connectionId },
      action: async () => {
        const result = await checkHealth(connectionId)
        if (result?.success) {
          toast.show('Connection is healthy', 'success')
        } else {
          toast.show(`Health check failed: ${result?.error}`, 'error')
        }
        return result
      },
    })
  }, [checkHealth, execute, toast])

  const handleViewSchema = useCallback((connectionId) => {
    return executeUI('View schema', async () => {
      await fetchSchema(connectionId)
      setSchemaDialogOpen(true)
    }, { connectionId })
  }, [executeUI, fetchSchema])

  const handleCloseSchema = useCallback(() => {
    return executeUI('Close schema', () => setSchemaDialogOpen(false))
  }, [executeUI])

  const handleOpenQuery = useCallback((connection) => {
    return executeUI('Open query runner', () => {
      setSelectedConnector(connection)
      setQueryText('')
      setQueryDialogOpen(true)
    }, { connectionId: connection?.id })
  }, [executeUI])

  const handleCloseQuery = useCallback(() => {
    return executeUI('Close query runner', () => setQueryDialogOpen(false))
  }, [executeUI])

  const handleExecuteQuery = useCallback(() => {
    if (!selectedConnector || !queryText) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Execute query',
      reversibility: Reversibility.IRREVERSIBLE,
      requiresConfirmation: false,
      blocksNavigation: true,
      intent: { source: 'connectors', connectionId: selectedConnector.id },
      action: async () => {
        const result = await executeQuery(selectedConnector.id, queryText)
        if (result?.error) {
          toast.show(`Query error: ${result.error}`, 'error')
        } else {
          toast.show(`Query executed: ${result?.row_count || 0} rows`, 'success')
        }
        return result
      },
    })
  }, [execute, executeQuery, queryText, selectedConnector, toast])

  const handleTabChange = useCallback((value) => {
    return executeUI('Switch connector tab', () => setActiveTab(value), { tab: value })
  }, [executeUI])

  const handleDismissError = useCallback(() => {
    return executeUI('Dismiss connector error', () => reset())
  }, [executeUI, reset])

  const categoryKeys = Object.keys(CONNECTOR_CATEGORIES)

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Data Connectors
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Connect to databases and cloud storage services
            </Typography>
          </Box>
          <Chip
            label={`${connections.length} connections`}
            variant="outlined"
            sx={{ borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'text.secondary' }}
          />
        </Box>

        <Tabs
          value={activeTab}
          onChange={(e, v) => handleTabChange(v)}
          sx={{ mt: 2 }}
        >
          <Tab label="Available Connectors" />
          <Tab label={`My Connections (${connections.length})`} />
        </Tabs>
      </Header>

      <Content>
        {activeTab === 0 ? (
          // Available Connectors
          <Box>
            {categoryKeys.map((catKey) => {
              const category = CONNECTOR_CATEGORIES[catKey]
              const CategoryIcon = category.icon
              return (
                <Box key={catKey} sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <CategoryIcon color="inherit" sx={{ color: 'text.secondary' }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {category.label}
                    </Typography>
                  </Box>
                  <Grid container spacing={2}>
                    {category.connectors.map((connector) => (
                      <Grid item xs={12} sm={6} md={4} lg={3} key={connector.id}>
                        <ConnectorCard variant="outlined">
                          <CardContent>
                            <ConnectorIcon
                              sx={{ bgcolor: alpha(connector.color, 0.1) }}
                            >
                              {catKey === 'database' ? (
                                <DatabaseIcon sx={{ color: connector.color }} />
                              ) : (
                                <CloudIcon sx={{ color: connector.color }} />
                              )}
                            </ConnectorIcon>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                              {connector.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {catKey === 'database' ? 'Database' : 'Cloud Storage'}
                            </Typography>
                          </CardContent>
                          <CardActions sx={{ mt: 'auto', p: 2, pt: 0 }}>
                            <ActionButton
                              fullWidth
                              variant="outlined"
                              size="small"
                              onClick={() => handleOpenConnect(connector)}
                              data-testid="connector-connect-button"
                            >
                              Connect
                            </ActionButton>
                          </CardActions>
                        </ConnectorCard>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )
            })}
          </Box>
        ) : (
          // My Connections
          <Box>
            {connections.length > 0 ? (
              <Grid container spacing={2}>
                {connections.map((conn) => (
                  <Grid item xs={12} sm={6} md={4} key={conn.id}>
                    <ConnectorCard>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                          <Box>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                              {conn.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {conn.connector_type}
                            </Typography>
                          </Box>
                          <StatusChip
                            size="small"
                            status={conn.status}
                            label={conn.status}
                            icon={conn.status === 'connected' ? <ConnectedIcon /> : <ErrorIcon />}
                          />
                        </Box>
                        {conn.latency_ms && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Latency: {conn.latency_ms.toFixed(0)}ms
                          </Typography>
                        )}
                      </CardContent>
                      <CardActions sx={{ p: 2, pt: 0, gap: 1 }}>
                        <Tooltip title="Test connection">
                          <IconButton
                            size="small"
                            onClick={() => handleCheckHealth(conn.id)}
                          >
                            <RefreshIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View schema">
                          <IconButton
                            size="small"
                            onClick={() => handleViewSchema(conn.id)}
                          >
                            <SchemaIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Run query">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenQuery(conn)}
                          >
                            <QueryIcon />
                          </IconButton>
                        </Tooltip>
                        <Box sx={{ flex: 1 }} />
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            sx={{ color: 'text.secondary' }}
                            onClick={() => handleDeleteConnection(conn.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </ConnectorCard>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <DatabaseIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  No connections yet
                </Typography>
                <Typography color="text.secondary" sx={{ mb: 3 }}>
                  Connect to a database or cloud storage to get started.
                </Typography>
                <ActionButton
                  variant="contained"
                  onClick={() => handleTabChange(0)}
                >
                  Browse Connectors
                </ActionButton>
              </Box>
            )}
          </Box>
        )}
      </Content>

      {/* Connect Dialog */}
      <Dialog
        open={connectDialogOpen}
        onClose={handleCloseConnect}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Connect to {selectedConnector?.name}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Connection Name"
            value={connectionName}
            onChange={(e) => setConnectionName(e.target.value)}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            label="Host"
            value={connectionConfig.host || ''}
            onChange={(e) => setConnectionConfig({ ...connectionConfig, host: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Port"
            type="number"
            value={connectionConfig.port || ''}
            onChange={(e) => setConnectionConfig({ ...connectionConfig, port: parseInt(e.target.value) })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Database"
            value={connectionConfig.database || ''}
            onChange={(e) => setConnectionConfig({ ...connectionConfig, database: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Username"
            value={connectionConfig.username || ''}
            onChange={(e) => setConnectionConfig({ ...connectionConfig, username: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={connectionConfig.password || ''}
            onChange={(e) => setConnectionConfig({ ...connectionConfig, password: e.target.value })}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseConnect}>Cancel</Button>
          <Button
            variant="outlined"
            onClick={handleTestConnection}
            disabled={testing}
            startIcon={testing ? <CircularProgress size={16} /> : <PlayArrowIcon />}
          >
            Test
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateConnection}
            disabled={!connectionName || loading}
            data-testid="connector-create-button"
          >
            Connect
          </Button>
        </DialogActions>
      </Dialog>

      {/* Query Dialog */}
      <Dialog
        open={queryDialogOpen}
        onClose={handleCloseQuery}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Run Query</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="SQL Query"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="SELECT * FROM table_name LIMIT 100"
            sx={{ mt: 2 }}
          />
          {queryResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Results ({queryResult.row_count} rows, {queryResult.execution_time_ms?.toFixed(0)}ms)
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, maxHeight: 300, overflow: 'auto' }}>
                {queryResult.columns?.length > 0 ? (
                  <Box component="pre" sx={{ fontSize: 12, m: 0 }}>
                    {JSON.stringify(queryResult.rows?.slice(0, 10), null, 2)}
                  </Box>
                ) : (
                  <Typography color="text.secondary">No results</Typography>
                )}
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseQuery}>Close</Button>
          <Button
            variant="contained"
            onClick={handleExecuteQuery}
            disabled={!queryText || querying}
            startIcon={querying ? <CircularProgress size={16} /> : <PlayArrowIcon />}
          >
            Execute
          </Button>
        </DialogActions>
      </Dialog>

      {/* Schema Dialog */}
      <Dialog
        open={schemaDialogOpen}
        onClose={handleCloseSchema}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Database Schema</DialogTitle>
        <DialogContent>
          {schema?.tables?.length > 0 ? (
            <Box sx={{ mt: 2 }}>
              {schema.tables.map((table) => (
                <Paper key={table.name} variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    {table.name}
                    {table.row_count && (
                      <Chip size="small" label={`${table.row_count} rows`} sx={{ ml: 1 }} />
                    )}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {table.columns?.map((col) => (
                      <Chip
                        key={col.name}
                        size="small"
                        variant="outlined"
                        label={`${col.name}: ${col.data_type}`}
                      />
                    ))}
                  </Box>
                </Paper>
              ))}
            </Box>
          ) : (
            <Typography color="text.secondary" sx={{ mt: 2 }}>
              No schema information available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSchema}>Close</Button>
        </DialogActions>
      </Dialog>

      {error && (
        <Alert
          severity="error"
          onClose={handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}


/**
 * Custom hook for connectors page state and actions.
 */
import { useState, useEffect, useCallback } from 'react'
import useConnectorStore from '@/stores/connectorStore'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useConnectorsPage() {
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

  return {
    // Store state
    connections,
    schema,
    queryResult,
    loading,
    testing,
    querying,
    error,

    // Local state
    activeTab,
    connectDialogOpen,
    selectedConnector,
    connectionName,
    setConnectionName,
    connectionConfig,
    setConnectionConfig,
    queryDialogOpen,
    queryText,
    setQueryText,
    schemaDialogOpen,

    // Handlers
    handleOpenConnect,
    handleCloseConnect,
    handleTestConnection,
    handleCreateConnection,
    handleDeleteConnection,
    handleCheckHealth,
    handleViewSchema,
    handleCloseSchema,
    handleOpenQuery,
    handleCloseQuery,
    handleExecuteQuery,
    handleTabChange,
    handleDismissError,
  }
}

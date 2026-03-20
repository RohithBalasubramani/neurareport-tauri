/**
 * Custom hook for schema builder state and operations
 */
import { useState, useEffect, useCallback } from 'react'
import useFederationStore from '@/stores/federationStore'
import { useConnectionStore } from '@/stores'
import { getWriteOperation } from '@/utils/sqlSafety'
import { useConfirmedAction, useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import useCrossPageActions from '@/hooks/useCrossPageActions'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'

export function useSchemaBuilder() {
  const {
    schemas,
    currentSchema,
    joinSuggestions,
    queryResult,
    loading,
    error,
    fetchSchemas,
    createSchema,
    deleteSchema,
    suggestJoins,
    executeQuery,
    setCurrentSchema,
    reset,
  } = useFederationStore()

  const { connections, fetchConnections } = useConnectionStore()
  const confirmWriteQuery = useConfirmedAction('EXECUTE_WRITE_QUERY')
  const { execute } = useInteraction()
  const { registerOutput } = useCrossPageActions(FeatureKey.FEDERATION)

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newSchemaName, setNewSchemaName] = useState('')
  const [newSchemaDescription, setNewSchemaDescription] = useState('')
  const [selectedConnections, setSelectedConnections] = useState([])
  const [queryInput, setQueryInput] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState({ open: false, schemaId: null, schemaName: '' })
  const [initialLoading, setInitialLoading] = useState(true)

  const writeOperation = getWriteOperation(queryInput)

  useEffect(() => {
    const init = async () => {
      setInitialLoading(true)
      await Promise.all([fetchSchemas(), fetchConnections()])
      setInitialLoading(false)
    }
    init()
    return () => reset()
  }, [fetchSchemas, fetchConnections, reset])

  const handleCreateSchema = async () => {
    if (!newSchemaName || selectedConnections.length < 2) return
    await execute({
      type: InteractionType.CREATE,
      label: 'Create federation schema',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionIds: selectedConnections,
        action: 'create_federation_schema',
      },
      action: async () => {
        const result = await createSchema({
          name: newSchemaName,
          connectionIds: selectedConnections,
          description: newSchemaDescription,
        })
        if (!result) throw new Error('Create schema failed')
        setCreateDialogOpen(false)
        setNewSchemaName('')
        setNewSchemaDescription('')
        setSelectedConnections([])
        return result
      },
    })
  }

  const handleSuggestJoins = async () => {
    if (!currentSchema) return
    await execute({
      type: InteractionType.GENERATE,
      label: 'Suggest joins',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { schemaId: currentSchema.id, action: 'suggest_joins' },
      action: async () => {
        const result = await suggestJoins()
        if (!result) throw new Error('Suggest joins failed')
        return result
      },
    })
  }

  const runExecuteQuery = useCallback(async () => {
    if (!currentSchema || !queryInput.trim()) return
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Run federated query',
      reversibility: writeOperation ? Reversibility.IRREVERSIBLE : Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        schemaId: currentSchema.id,
        action: 'execute_federation_query',
        writeOperation,
      },
      action: async () => {
        const result = await executeQuery(currentSchema.id, queryInput)
        if (!result) throw new Error('Query execution failed')
        const rows = result.rows || []
        const columns = rows.length > 0 ? Object.keys(rows[0]).map((k) => ({ name: k })) : []
        registerOutput({
          type: OutputType.TABLE,
          title: `Federation: ${currentSchema.name || 'Query'} (${rows.length} rows)`,
          summary: queryInput.slice(0, 100),
          data: { columns, rows },
          format: 'table',
        })
        return result
      },
    })
  }, [currentSchema, executeQuery, queryInput, execute, writeOperation, registerOutput])

  const handleExecuteQuery = useCallback(async () => {
    if (!currentSchema || !queryInput.trim()) return
    if (writeOperation) {
      confirmWriteQuery(currentSchema.name || currentSchema.id || 'selected schema', runExecuteQuery)
      return
    }
    await runExecuteQuery()
  }, [confirmWriteQuery, currentSchema, queryInput, runExecuteQuery, writeOperation])

  const handleDeleteRequest = useCallback((schema) => {
    setDeleteConfirm({
      open: true,
      schemaId: schema?.id || null,
      schemaName: schema?.name || 'this schema',
    })
  }, [])

  const handleDeleteSchemaConfirm = async () => {
    const schemaId = deleteConfirm.schemaId
    const schemaName = deleteConfirm.schemaName
    setDeleteConfirm({ open: false, schemaId: null, schemaName: '' })
    if (!schemaId) return
    await execute({
      type: InteractionType.DELETE,
      label: 'Delete federation schema',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { schemaId, schemaName, action: 'delete_federation_schema' },
      action: async () => {
        const result = await deleteSchema(schemaId)
        if (!result) throw new Error('Delete schema failed')
        return result
      },
    })
  }

  const toggleConnection = (connId) => {
    setSelectedConnections((prev) =>
      prev.includes(connId) ? prev.filter((id) => id !== connId) : [...prev, connId]
    )
  }

  return {
    // Store state
    schemas,
    currentSchema,
    joinSuggestions,
    queryResult,
    loading,
    error,
    connections,
    setCurrentSchema,
    reset,
    // Local state
    createDialogOpen,
    setCreateDialogOpen,
    newSchemaName,
    setNewSchemaName,
    newSchemaDescription,
    setNewSchemaDescription,
    selectedConnections,
    queryInput,
    setQueryInput,
    deleteConfirm,
    setDeleteConfirm,
    initialLoading,
    writeOperation,
    // Actions
    handleCreateSchema,
    handleSuggestJoins,
    handleExecuteQuery,
    handleDeleteRequest,
    handleDeleteSchemaConfirm,
    toggleConnection,
  }
}

/**
 * Custom hook: all Query Builder page state, effects, and handlers.
 * Hook files are exempt from the 200-line limit.
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useAppStore } from '@/stores'
import useQueryStore from '@/stores/queryStore'
import * as nl2sqlApi from '@/api/nl2sql'
import * as api from '@/api/client'
import { getWriteOperation } from '@/utils/sqlSafety'
import useCrossPageActions from '@/hooks/useCrossPageActions'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'
import {
  useInteraction,
  InteractionType,
  Reversibility,
  useConfirmedAction,
} from '@/components/ux/governance'

export function useQueryBuilderState() {
  const toast = useToast()
  const { execute } = useInteraction()
  const confirmWriteQuery = useConfirmedAction('EXECUTE_WRITE_QUERY')
  const { registerOutput } = useCrossPageActions(FeatureKey.QUERY)
  const connections = useAppStore((s) => s.savedConnections)
  const {
    currentQuestion,
    generatedSQL,
    explanation,
    confidence,
    warnings,
    results,
    columns,
    totalCount,
    executionTimeMs,
    includeTotal,
    isGenerating,
    isExecuting,
    error,
    selectedConnectionId,
    savedQueries,
    queryHistory,
    setCurrentQuestion,
    setGeneratedSQL,
    setSelectedConnection,
    setGenerationResult,
    setExecutionResult,
    setError,
    setIsGenerating,
    setIsExecuting,
    clearResults,
    clearAll,
    setSavedQueries,
    addSavedQuery,
    removeSavedQuery,
    setIncludeTotal,
    setQueryHistory,
    loadSavedQuery,
  } = useQueryStore()

  // Local UI state
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [saveDescription, setSaveDescription] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [showSaved, setShowSaved] = useState(false)
  const [schema, setSchema] = useState(null)
  const [deleteSavedConfirm, setDeleteSavedConfirm] = useState({ open: false, queryId: null, queryName: '' })
  const [deleteHistoryConfirm, setDeleteHistoryConfirm] = useState({ open: false, entryId: null, question: '' })
  const schemaRequestIdRef = useRef(0)
  const writeOperation = getWriteOperation(generatedSQL)
  const selectedConnectionLabel = connections.find((conn) => conn.id === selectedConnectionId)?.name
    || (selectedConnectionId ? 'Selected connection' : 'No connection selected')

  // ---------------------------------------------------------------------------
  // Effects: fetch connections, schema, saved queries, history
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const { connections: conns } = await api.listConnections()
        useAppStore.getState().setSavedConnections(conns || [])
      } catch (err) {
        console.error('Failed to fetch connections:', err)
        toast.show('Failed to load connections. Please refresh the page.', 'error')
      }
    }
    fetchConnections()
  }, [toast])

  useEffect(() => {
    if (!selectedConnectionId) {
      setSchema(null)
      return
    }
    const requestId = ++schemaRequestIdRef.current
    const fetchSchema = async () => {
      try {
        const result = await api.getConnectionSchema(selectedConnectionId)
        if (requestId === schemaRequestIdRef.current) {
          setSchema(result)
        }
      } catch (err) {
        if (requestId === schemaRequestIdRef.current) {
          console.error('Failed to fetch schema:', err)
          toast.show('Failed to load database schema', 'warning')
        }
      }
    }
    fetchSchema()
  }, [selectedConnectionId, toast])

  useEffect(() => {
    const fetchSaved = async () => {
      try {
        const { queries } = await nl2sqlApi.listSavedQueries()
        setSavedQueries(queries || [])
      } catch (err) {
        console.error('Failed to fetch saved queries:', err)
      }
    }
    fetchSaved()
  }, [setSavedQueries])

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const { history } = await nl2sqlApi.getQueryHistory({ limit: 50 })
        setQueryHistory(history || [])
      } catch (err) {
        console.error('Failed to fetch history:', err)
      }
    }
    fetchHistory()
  }, [setQueryHistory])

  // ---------------------------------------------------------------------------
  // Handlers
  // ---------------------------------------------------------------------------
  const handleGenerate = useCallback(() => {
    if (!currentQuestion.trim() || !selectedConnectionId) return

    execute({
      type: InteractionType.GENERATE,
      label: 'Generate SQL query',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      action: async () => {
        setIsGenerating(true)
        setError(null)
        clearResults()

        try {
          const result = await nl2sqlApi.generateSQL({
            question: currentQuestion,
            connectionId: selectedConnectionId,
          })

          setGenerationResult({
            sql: result.sql,
            explanation: result.explanation,
            confidence: result.confidence,
            warnings: result.warnings,
            originalQuestion: result.original_question,
          })
        } catch (err) {
          const errorMsg = err.response?.data?.message || err.message || 'Failed to generate SQL'
          setError(errorMsg)
          throw new Error(errorMsg)
        } finally {
          setIsGenerating(false)
        }
      },
    })
  }, [currentQuestion, selectedConnectionId, setIsGenerating, setError, clearResults, setGenerationResult, execute])

  const runExecute = useCallback(() => {
    execute({
      type: InteractionType.EXECUTE,
      label: 'Execute SQL query',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      successMessage: 'Query executed successfully',
      action: async () => {
        setIsExecuting(true)
        setError(null)

        try {
          const result = await nl2sqlApi.executeQuery({
            sql: generatedSQL,
            connectionId: selectedConnectionId,
            limit: 100,
            includeTotal,
          })

          setExecutionResult({
            columns: result.columns,
            rows: result.rows,
            rowCount: result.row_count,
            totalCount: result.total_count,
            executionTimeMs: result.execution_time_ms,
            truncated: result.truncated,
          })
          registerOutput({
            type: OutputType.TABLE,
            title: `Query: ${currentQuestion.substring(0, 60)}`,
            summary: `${result.row_count} rows, ${result.columns?.length || 0} columns`,
            data: { columns: result.columns, rows: result.rows },
            format: 'table',
          })
          toast.show(`Query returned ${result.row_count} rows`, 'success')
        } catch (err) {
          const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to execute query'
          setError(errorMsg)
          throw new Error(errorMsg)
        } finally {
          setIsExecuting(false)
        }
      },
    })
  }, [execute, generatedSQL, includeTotal, selectedConnectionId, setError, setExecutionResult, setIsExecuting, toast])

  const handleExecute = useCallback(() => {
    if (!generatedSQL.trim() || !selectedConnectionId) return

    if (writeOperation) {
      const selectedConnection = connections.find((conn) => conn.id === selectedConnectionId)
      const targetLabel = selectedConnection?.name || selectedConnectionId || 'selected connection'
      confirmWriteQuery(targetLabel, runExecute)
      return
    }

    runExecute()
  }, [confirmWriteQuery, connections, generatedSQL, runExecute, selectedConnectionId, writeOperation])

  const handleSave = useCallback(() => {
    if (!saveName.trim() || !generatedSQL.trim() || !selectedConnectionId) return

    execute({
      type: InteractionType.CREATE,
      label: `Save query "${saveName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Query saved successfully',
      errorMessage: 'Failed to save query',
      action: async () => {
        const result = await nl2sqlApi.saveQuery({
          name: saveName,
          sql: generatedSQL,
          connectionId: selectedConnectionId,
          description: saveDescription || undefined,
          originalQuestion: currentQuestion || undefined,
        })

        addSavedQuery(result.query)
        setShowSaveDialog(false)
        setSaveName('')
        setSaveDescription('')
      },
    })
  }, [saveName, saveDescription, generatedSQL, selectedConnectionId, currentQuestion, addSavedQuery, execute])

  const handleDeleteSaved = useCallback(
    (queryId) => {
      execute({
        type: InteractionType.DELETE,
        label: 'Delete saved query',
        reversibility: Reversibility.IRREVERSIBLE,
        successMessage: 'Query deleted',
        errorMessage: 'Failed to delete query',
        action: async () => {
          await nl2sqlApi.deleteSavedQuery(queryId)
          removeSavedQuery(queryId)
        },
      })
    },
    [removeSavedQuery, execute]
  )

  const handleDeleteHistory = useCallback(
    (entryId) => {
      if (!entryId) return
      execute({
        type: InteractionType.DELETE,
        label: 'Delete history entry',
        reversibility: Reversibility.IRREVERSIBLE,
        successMessage: 'History entry deleted',
        errorMessage: 'Failed to delete history entry',
        action: async () => {
          await nl2sqlApi.deleteQueryHistoryEntry(entryId)
          const current = useQueryStore.getState().queryHistory
          setQueryHistory(current.filter((entry) => entry.id !== entryId))
        },
      })
    },
    [setQueryHistory, execute]
  )

  const handleCopySQL = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(generatedSQL)
      toast.show('SQL copied to clipboard', 'success')
    } catch (err) {
      toast.show('Failed to copy to clipboard', 'error')
    }
  }, [generatedSQL, toast])

  // ---------------------------------------------------------------------------
  // Derived values
  // ---------------------------------------------------------------------------
  const tableColumns = columns.map((col) => ({
    field: col,
    header: col,
    sortable: true,
  }))

  const executeDisabledReason = !generatedSQL.trim()
    ? 'Generate SQL before executing'
    : !selectedConnectionId
      ? 'Select a connection first'
      : null

  return {
    // Store state
    currentQuestion, generatedSQL, explanation, confidence, warnings,
    results, columns, totalCount, executionTimeMs, includeTotal,
    isGenerating, isExecuting, error, selectedConnectionId,
    savedQueries, queryHistory,
    setCurrentQuestion, setGeneratedSQL, setSelectedConnection,
    setError, setIncludeTotal, loadSavedQuery,
    // Local UI state
    showSaveDialog, setShowSaveDialog,
    saveName, setSaveName,
    saveDescription, setSaveDescription,
    showHistory, setShowHistory,
    showSaved, setShowSaved,
    schema,
    deleteSavedConfirm, setDeleteSavedConfirm,
    deleteHistoryConfirm, setDeleteHistoryConfirm,
    // Derived
    writeOperation, selectedConnectionLabel, tableColumns, executeDisabledReason,
    connections,
    // Handlers
    handleGenerate, handleExecute, handleSave,
    handleDeleteSaved, handleDeleteHistory, handleCopySQL,
  }
}

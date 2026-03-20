import { useCallback, useEffect, useMemo, useState } from 'react'
import * as api from '@/api/client'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useSchemaDrawer({ open, connection }) {
  const { execute } = useInteraction()
  const [schema, setSchema] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')
  const [previewState, setPreviewState] = useState({})

  const fetchSchema = useCallback(async () => {
    if (!connection?.id) return
    setLoading(true)
    setError(null)
    try {
      const result = await api.getConnectionSchema(connection.id, {
        includeRowCounts: true,
        includeForeignKeys: true,
      })
      setSchema(result)
    } catch (err) {
      setError(err.message || 'Failed to load schema')
    } finally {
      setLoading(false)
    }
  }, [connection?.id])

  useEffect(() => {
    if (open) {
      fetchSchema()
    }
  }, [open, fetchSchema])

  const filteredTables = useMemo(() => {
    const tables = schema?.tables || []
    const query = filter.trim().toLowerCase()
    if (!query) return tables
    return tables.filter((table) => table.name.toLowerCase().includes(query))
  }, [schema, filter])

  const handlePreview = useCallback((tableName) => {
    if (!connection?.id || !tableName) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: `Preview ${tableName}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { connectionId: connection.id, table: tableName },
      action: async () => {
        setPreviewState((prev) => ({
          ...prev,
          [tableName]: { ...(prev[tableName] || {}), loading: true, error: null },
        }))
        try {
          const result = await api.getConnectionTablePreview(connection.id, {
            table: tableName,
            limit: 6,
          })
          setPreviewState((prev) => ({
            ...prev,
            [tableName]: {
              loading: false,
              error: null,
              columns: result.columns || [],
              rows: result.rows || [],
            },
          }))
        } catch (err) {
          setPreviewState((prev) => ({
            ...prev,
            [tableName]: { ...(prev[tableName] || {}), loading: false, error: err.message || 'Preview failed' },
          }))
        }
      },
    })
  }, [connection?.id, execute])

  const handleRefreshSchema = useCallback(() => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Refresh schema',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { connectionId: connection?.id },
      action: fetchSchema,
    })
  }, [connection?.id, execute, fetchSchema])

  return {
    schema,
    loading,
    error,
    filter,
    setFilter,
    previewState,
    filteredTables,
    handlePreview,
    handleRefreshSchema,
  }
}

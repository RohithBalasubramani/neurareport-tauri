/**
 * Custom hook for Connections Page state and actions.
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import * as api from '@/api/client'

export function useConnectionsPage() {
  const toast = useToast()
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
  const drawerOpenRef = useRef(false)

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

  const handleAddConnection = useCallback(() => {
    if (drawerOpenRef.current) return
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

    execute({
      type: InteractionType.DELETE,
      label: `Delete data source "${connectionToDelete.name}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: `"${connectionToDelete.name}" removed`,
      errorMessage: 'Failed to delete connection',
      action: async () => {
        removeSavedConnection(connectionToDelete.id)

        try {
          await api.deleteConnection(connectionToDelete.id)
        } catch (err) {
          if (connectionData) {
            addSavedConnection(connectionData)
          }
          throw err
        }

        toast.showWithUndo(
          `"${connectionToDelete.name}" removed`,
          async () => {
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
  }, [deletingConnection, savedConnections, removeSavedConnection, setSavedConnections, toast, execute, addSavedConnection])

  const handleSaveConnection = useCallback(async (connectionData) => {
    const isEditing = !!editingConnection

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

  const handleCloseDrawer = useCallback(() => {
    drawerOpenRef.current = false
    setDrawerOpen(false)
  }, [])

  return {
    // Store state
    savedConnections,
    activeConnectionId,
    // Local state
    loading,
    drawerOpen,
    editingConnection,
    deleteConfirmOpen,
    setDeleteConfirmOpen,
    deletingConnection,
    menuAnchor,
    menuConnection,
    schemaOpen,
    setSchemaOpen,
    schemaConnection,
    favorites,
    // Handlers
    handleFavoriteToggle,
    handleOpenMenu,
    handleCloseMenu,
    handleAddConnection,
    handleEditConnection,
    handleDeleteClick,
    handleSchemaInspect,
    handleDeleteConfirm,
    handleSaveConnection,
    handleTestConnection,
    handleRowClick,
    handleCloseDrawer,
  }
}

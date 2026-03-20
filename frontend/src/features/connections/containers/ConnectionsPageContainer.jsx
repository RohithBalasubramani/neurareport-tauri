/**
 * Premium Connections Page
 * Data source management with theme-based styling
 */
import React from 'react'
import {
  Alert,
  Tooltip,
  useTheme,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import StorageIcon from '@mui/icons-material/Storage'
import { DataTable } from '@/components/data-table'
import { ConfirmModal } from '@/components/modal'
import { Drawer } from '@/components/drawer'
import ConnectionForm from '../components/ConnectionForm'
import ConnectionSchemaDrawer from '../components/ConnectionSchemaDrawer'
import ConnectionActionsMenu from '../components/ConnectionActionsMenu'
import { useConnectionsPage } from '../hooks/useConnectionsPage'
import { useConnectionColumns } from '../components/useConnectionColumns'
import { PageContainer, ActionButton } from '../components/ConnectionsStyledComponents'

export default function ConnectionsPage() {
  const theme = useTheme()
  const {
    savedConnections,
    activeConnectionId,
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
  } = useConnectionsPage()

  const { columns, filters } = useConnectionColumns({
    favorites,
    handleFavoriteToggle,
    activeConnectionId,
  })

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
      <ConnectionActionsMenu
        menuAnchor={menuAnchor}
        menuConnection={menuConnection}
        onClose={handleCloseMenu}
        onTestConnection={handleTestConnection}
        onSchemaInspect={handleSchemaInspect}
        onEditConnection={handleEditConnection}
        onDeleteClick={handleDeleteClick}
      />

      {/* Connection Form Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={handleCloseDrawer}
        title={editingConnection ? 'Edit Data Source' : 'Add Data Source'}
        subtitle="Enter your database details to connect"
        width={520}
      >
        <ConnectionForm
          connection={editingConnection}
          onSave={handleSaveConnection}
          onCancel={handleCloseDrawer}
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

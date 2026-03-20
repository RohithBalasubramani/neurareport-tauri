/**
 * Cross-Database Federation Schema Builder Page
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material'
import {
  Add as AddIcon,
  JoinInner as JoinIcon,
} from '@mui/icons-material'
import ConfirmModal from '@/components/modal/ConfirmModal'
import AiUsageNotice from '@/components/ai/AiUsageNotice'
import { useSchemaBuilder } from '../hooks/useSchemaBuilder'
import SchemaListPanel from '../components/SchemaListPanel'
import SchemaDetailPanel from '../components/SchemaDetailPanel'
import CreateSchemaDialog from '../components/CreateSchemaDialog'

export default function SchemaBuilderPage() {
  const {
    schemas,
    currentSchema,
    joinSuggestions,
    queryResult,
    loading,
    error,
    connections,
    setCurrentSchema,
    reset,
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
    handleCreateSchema,
    handleSuggestJoins,
    handleExecuteQuery,
    handleDeleteRequest,
    handleDeleteSchemaConfirm,
    toggleConnection,
  } = useSchemaBuilder()

  if (initialLoading) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <JoinIcon />
          <Typography variant="h5">Cross-Database Federation</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <CircularProgress />
        </Box>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <JoinIcon /> Cross-Database Federation
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create virtual schemas to query across multiple databases
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          New Virtual Schema
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => reset()}>
          {error}
        </Alert>
      )}

      <AiUsageNotice
        title="AI join suggestions"
        description="Join suggestions are generated from schema metadata. Review before running cross-database queries."
        chips={[
          { label: 'Source: Selected schemas', variant: 'outlined' },
          { label: 'Confidence: Provided per suggestion', variant: 'outlined' },
          { label: 'Read-only recommended', variant: 'outlined' },
        ]}
        dense
        sx={{ mb: 2 }}
      />

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <SchemaListPanel
            schemas={schemas}
            currentSchema={currentSchema}
            onSelectSchema={setCurrentSchema}
            onDeleteRequest={handleDeleteRequest}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <SchemaDetailPanel
            currentSchema={currentSchema}
            joinSuggestions={joinSuggestions}
            queryResult={queryResult}
            loading={loading}
            queryInput={queryInput}
            setQueryInput={setQueryInput}
            writeOperation={writeOperation}
            onSuggestJoins={handleSuggestJoins}
            onExecuteQuery={handleExecuteQuery}
          />
        </Grid>
      </Grid>

      <CreateSchemaDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        connections={connections}
        newSchemaName={newSchemaName}
        setNewSchemaName={setNewSchemaName}
        newSchemaDescription={newSchemaDescription}
        setNewSchemaDescription={setNewSchemaDescription}
        selectedConnections={selectedConnections}
        onToggleConnection={toggleConnection}
        onCreateSchema={handleCreateSchema}
      />

      <ConfirmModal
        open={deleteConfirm.open}
        onClose={() => setDeleteConfirm({ open: false, schemaId: null, schemaName: '' })}
        onConfirm={handleDeleteSchemaConfirm}
        title="Delete Virtual Schema"
        message={`Delete "${deleteConfirm.schemaName}"? This will remove the virtual schema and its saved join logic.`}
        confirmLabel="Delete"
        severity="error"
      />
    </Box>
  )
}

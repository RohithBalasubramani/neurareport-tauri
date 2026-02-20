/**
 * Cross-Database Federation Schema Builder Page
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Link as LinkIcon,
  Storage as DatabaseIcon,
  AutoAwesome as AIIcon,
  PlayArrow as RunIcon,
  JoinInner as JoinIcon,
} from '@mui/icons-material';
import useFederationStore from '@/stores/federationStore';
import { useConnectionStore } from '@/stores';
import ConfirmModal from '@/components/Modal/ConfirmModal';
import { getWriteOperation } from '@/utils/sqlSafety';
import { useConfirmedAction, useInteraction, InteractionType, Reversibility } from '@/components/ux/governance';
import AiUsageNotice from '@/components/ai/AiUsageNotice';
import { neutral, palette } from '@/app/theme';
import useCrossPageActions from '@/hooks/useCrossPageActions';
import SendToMenu from '@/components/common/SendToMenu';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';

export default function SchemaBuilderPage() {
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
  } = useFederationStore();

  const { connections, fetchConnections } = useConnectionStore();
  const confirmWriteQuery = useConfirmedAction('EXECUTE_WRITE_QUERY');
  const { execute } = useInteraction();
  const { registerOutput } = useCrossPageActions(FeatureKey.FEDERATION);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSchemaName, setNewSchemaName] = useState('');
  const [newSchemaDescription, setNewSchemaDescription] = useState('');
  const [selectedConnections, setSelectedConnections] = useState([]);
  const [queryInput, setQueryInput] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState({ open: false, schemaId: null, schemaName: '' });

  const [initialLoading, setInitialLoading] = useState(true);
  const writeOperation = getWriteOperation(queryInput);

  useEffect(() => {
    const init = async () => {
      setInitialLoading(true);
      await Promise.all([fetchSchemas(), fetchConnections()]);
      setInitialLoading(false);
    };
    init();
    return () => reset();
  }, [fetchSchemas, fetchConnections, reset]);

  const handleCreateSchema = async () => {
    if (!newSchemaName || selectedConnections.length < 2) return;
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
        });
        if (!result) {
          throw new Error('Create schema failed');
        }
        setCreateDialogOpen(false);
        setNewSchemaName('');
        setNewSchemaDescription('');
        setSelectedConnections([]);
        return result;
      },
    });
  };

  const handleSuggestJoins = async () => {
    if (!currentSchema) return;
    await execute({
      type: InteractionType.GENERATE,
      label: 'Suggest joins',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        schemaId: currentSchema.id,
        action: 'suggest_joins',
      },
      action: async () => {
        const result = await suggestJoins(); // Store gets connections from currentSchema
        if (!result) {
          throw new Error('Suggest joins failed');
        }
        return result;
      },
    });
  };

  const runExecuteQuery = useCallback(async () => {
    if (!currentSchema || !queryInput.trim()) return;
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
        const result = await executeQuery(currentSchema.id, queryInput);
        if (!result) {
          throw new Error('Query execution failed');
        }
        // Register query result for cross-page use
        const rows = result.rows || [];
        const columns = rows.length > 0 ? Object.keys(rows[0]).map((k) => ({ name: k })) : [];
        registerOutput({
          type: OutputType.TABLE,
          title: `Federation: ${currentSchema.name || 'Query'} (${rows.length} rows)`,
          summary: queryInput.slice(0, 100),
          data: { columns, rows },
          format: 'table',
        });
        return result;
      },
    });
  }, [currentSchema, executeQuery, queryInput, execute, writeOperation, registerOutput]);

  const handleExecuteQuery = useCallback(async () => {
    if (!currentSchema || !queryInput.trim()) return;
    if (writeOperation) {
      confirmWriteQuery(currentSchema.name || currentSchema.id || 'selected schema', runExecuteQuery);
      return;
    }
    await runExecuteQuery();
  }, [confirmWriteQuery, currentSchema, queryInput, runExecuteQuery, writeOperation]);

  const handleDeleteRequest = useCallback((schema) => {
    setDeleteConfirm({
      open: true,
      schemaId: schema?.id || null,
      schemaName: schema?.name || 'this schema',
    });
  }, []);

  const handleDeleteSchemaConfirm = async () => {
    const schemaId = deleteConfirm.schemaId;
    const schemaName = deleteConfirm.schemaName;
    setDeleteConfirm({ open: false, schemaId: null, schemaName: '' });
    if (!schemaId) return;
    await execute({
      type: InteractionType.DELETE,
      label: 'Delete federation schema',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        schemaId,
        schemaName,
        action: 'delete_federation_schema',
      },
      action: async () => {
        const result = await deleteSchema(schemaId);
        if (!result) {
          throw new Error('Delete schema failed');
        }
        return result;
      },
    });
  };

  const toggleConnection = (connId) => {
    setSelectedConnections(prev =>
      prev.includes(connId)
        ? prev.filter(id => id !== connId)
        : [...prev, connId]
    );
  };

  // Show loading during initial fetch
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
    );
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
        {/* Schema List */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Virtual Schemas
            </Typography>
            {schemas.length === 0 ? (
              <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                No virtual schemas yet. Create one to get started.
              </Typography>
            ) : (
              <List>
                {schemas.map((schema) => (
                  <ListItem
                    key={schema.id}
                    button
                    selected={currentSchema?.id === schema.id}
                    onClick={() => setCurrentSchema(schema)}
                    secondaryAction={
                      <Tooltip title="Delete schema">
                        <IconButton
                          edge="end"
                          aria-label={`Delete ${schema.name}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteRequest(schema);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    }
                  >
                    <ListItemIcon>
                      <DatabaseIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={schema.name}
                      secondary={`${schema.connections?.length || 0} databases`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        {/* Schema Details & Query */}
        <Grid size={{ xs: 12, md: 8 }}>
          {currentSchema ? (
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">{currentSchema.name}</Typography>
                <Button
                  variant="outlined"
                  startIcon={loading ? <CircularProgress size={20} /> : <AIIcon />}
                  onClick={handleSuggestJoins}
                  disabled={loading}
                >
                  AI Join Suggestions
                </Button>
              </Box>

              {currentSchema.description && (
                <Typography color="text.secondary" sx={{ mb: 2 }}>
                  {currentSchema.description}
                </Typography>
              )}

              <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
                {(currentSchema.connections || []).map((conn, idx) => (
                  <Chip
                    key={idx}
                    icon={<DatabaseIcon />}
                    label={conn.name || conn}
                    variant="outlined"
                  />
                ))}
              </Box>

              {/* Join Suggestions */}
              {joinSuggestions.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Suggested Joins
                  </Typography>
                  <Grid container spacing={2}>
                    {joinSuggestions.map((suggestion, idx) => (
                      <Grid size={{ xs: 12, sm: 6 }} key={idx}>
                        <Card variant="outlined">
                          <CardContent sx={{ py: 1.5 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <LinkIcon sx={{ color: 'text.secondary' }} />
                              <Typography variant="subtitle2">
                                {suggestion.left_table} ↔ {suggestion.right_table}
                              </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              {suggestion.left_column} = {suggestion.right_column}
                            </Typography>
                            {suggestion.reason && (
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                {suggestion.reason}
                              </Typography>
                            )}
                            <Chip
                              size="small"
                              label={`${Math.round((suggestion.confidence || 0) * 100)}% confidence`}
                              sx={{ mt: 1, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                            />
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Query Input */}
              <Typography variant="subtitle1" gutterBottom>
                Federated Query
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                placeholder="SELECT * FROM db1.users u JOIN db2.orders o ON u.id = o.user_id"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                sx={{ mb: 2, fontFamily: 'monospace' }}
              />
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                <Chip
                  size="small"
                  label="Read-only recommended"
                  variant="outlined"
                  sx={{ fontSize: '12px' }}
                />
                {writeOperation && (
                  <Chip
                    size="small"
                    label={`${writeOperation.toUpperCase()} detected`}
                    sx={{ fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                  />
                )}
              </Box>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <RunIcon />}
                onClick={handleExecuteQuery}
                disabled={!queryInput.trim() || loading}
              >
                Execute Query
              </Button>
              {writeOperation && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Write queries can modify data and may not be reversible. You will be asked to confirm before execution.
                </Alert>
              )}

              {/* Query Results */}
              {queryResult && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Results ({queryResult.rows?.length || 0} rows)
                  </Typography>
                  <Box sx={{ overflowX: 'auto' }}>
                    <pre style={{ fontSize: 12, margin: 0 }}>
                      {JSON.stringify(queryResult, null, 2)}
                    </pre>
                  </Box>
                </Box>
              )}
            </Paper>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <DatabaseIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography color="text.secondary">
                Select a virtual schema or create a new one to get started
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Create Schema Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Virtual Schema</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Schema Name"
            value={newSchemaName}
            onChange={(e) => setNewSchemaName(e.target.value)}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            label="Description"
            value={newSchemaDescription}
            onChange={(e) => setNewSchemaDescription(e.target.value)}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          <Typography variant="subtitle2" gutterBottom>
            Select Databases (minimum 2)
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {connections.map((conn) => (
              <Card
                key={conn.id}
                variant="outlined"
                sx={{
                  cursor: 'pointer',
                  borderColor: selectedConnections.includes(conn.id) ? 'text.secondary' : 'divider',
                  bgcolor: selectedConnections.includes(conn.id) ? 'action.selected' : 'background.paper',
                }}
                onClick={() => toggleConnection(conn.id)}
              >
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <DatabaseIcon />
                      <Typography>{conn.name}</Typography>
                    </Box>
                    {selectedConnections.includes(conn.id) && (
                      <Chip label="Selected" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                    )}
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateSchema}
            disabled={!newSchemaName || selectedConnections.length < 2}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

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
  );
}

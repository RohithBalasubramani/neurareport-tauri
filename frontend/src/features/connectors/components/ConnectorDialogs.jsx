/**
 * Dialogs for connector operations: connect, query, schema.
 */
import React from 'react'
import { Box, Typography, Button, TextField, Chip, Paper, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress } from '@mui/material'
import { PlayArrow as PlayArrowIcon } from '@mui/icons-material'

export function ConnectDialog({ open, onClose, selectedConnector, connectionName, setConnectionName, connectionConfig, setConnectionConfig, onTest, onCreate, testing, loading }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
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
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="outlined"
          onClick={onTest}
          disabled={testing}
          startIcon={testing ? <CircularProgress size={16} /> : <PlayArrowIcon />}
        >
          Test
        </Button>
        <Button
          variant="contained"
          onClick={onCreate}
          disabled={!connectionName || loading}
          data-testid="connector-create-button"
        >
          Connect
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export function QueryDialog({
  open,
  onClose,
  queryText,
  setQueryText,
  queryResult,
  onExecute,
  querying,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
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
        <Button onClick={onClose}>Close</Button>
        <Button
          variant="contained"
          onClick={onExecute}
          disabled={!queryText || querying}
          startIcon={querying ? <CircularProgress size={16} /> : <PlayArrowIcon />}
        >
          Execute
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export function SchemaDialog({
  open,
  onClose,
  schema,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
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
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

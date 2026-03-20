/**
 * Schema detail panel with joins, query input, and results
 */
import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Divider,
  alpha,
} from '@mui/material'
import {
  Link as LinkIcon,
  Storage as DatabaseIcon,
  AutoAwesome as AIIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'

export default function SchemaDetailPanel({
  currentSchema,
  joinSuggestions,
  queryResult,
  loading,
  queryInput,
  setQueryInput,
  writeOperation,
  onSuggestJoins,
  onExecuteQuery,
}) {
  if (!currentSchema) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <DatabaseIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography color="text.secondary">
          Select a virtual schema or create a new one to get started
        </Typography>
      </Paper>
    )
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{currentSchema.name}</Typography>
        <Button
          variant="outlined"
          startIcon={loading ? <CircularProgress size={20} /> : <AIIcon />}
          onClick={onSuggestJoins}
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
          <Chip key={idx} icon={<DatabaseIcon />} label={conn.name || conn} variant="outlined" />
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
        <Chip size="small" label="Read-only recommended" variant="outlined" sx={{ fontSize: '12px' }} />
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
        onClick={onExecuteQuery}
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
  )
}

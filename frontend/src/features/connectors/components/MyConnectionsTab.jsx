/**
 * My connections tab showing existing connections.
 */
import React from 'react'
import {
  Box,
  Typography,
  Grid,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Storage as DatabaseIcon,
  Refresh as RefreshIcon,
  Schema as SchemaIcon,
  Code as QueryIcon,
} from '@mui/icons-material'

export default function MyConnectionsTab({
  connections,
  handleCheckHealth,
  handleViewSchema,
  handleOpenQuery,
  handleDeleteConnection,
  handleTabChange,
  ConnectorCard,
  StatusChip,
  ActionButton,
  ConnectedIcon,
  ErrorIcon,
}) {
  if (connections.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <DatabaseIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" sx={{ mb: 1 }}>
          No connections yet
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          Connect to a database or cloud storage to get started.
        </Typography>
        <ActionButton
          variant="contained"
          onClick={() => handleTabChange(0)}
        >
          Browse Connectors
        </ActionButton>
      </Box>
    )
  }

  return (
    <Box>
      <Grid container spacing={2}>
        {connections.map((conn) => (
          <Grid item xs={12} sm={6} md={4} key={conn.id}>
            <ConnectorCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {conn.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {conn.connector_type}
                    </Typography>
                  </Box>
                  <StatusChip
                    size="small"
                    status={conn.status}
                    label={conn.status}
                    icon={conn.status === 'connected' ? <ConnectedIcon /> : <ErrorIcon />}
                  />
                </Box>
                {conn.latency_ms && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Latency: {conn.latency_ms.toFixed(0)}ms
                  </Typography>
                )}
              </CardContent>
              <CardActions sx={{ p: 2, pt: 0, gap: 1 }}>
                <Tooltip title="Test connection">
                  <IconButton
                    size="small"
                    onClick={() => handleCheckHealth(conn.id)}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View schema">
                  <IconButton
                    size="small"
                    onClick={() => handleViewSchema(conn.id)}
                  >
                    <SchemaIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Run query">
                  <IconButton
                    size="small"
                    onClick={() => handleOpenQuery(conn)}
                  >
                    <QueryIcon />
                  </IconButton>
                </Tooltip>
                <Box sx={{ flex: 1 }} />
                <Tooltip title="Delete">
                  <IconButton
                    size="small"
                    sx={{ color: 'text.secondary' }}
                    onClick={() => handleDeleteConnection(conn.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </ConnectorCard>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

/**
 * Schema list panel showing virtual schemas
 */
import React from 'react'
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Storage as DatabaseIcon,
} from '@mui/icons-material'

export default function SchemaListPanel({
  schemas,
  currentSchema,
  onSelectSchema,
  onDeleteRequest,
}) {
  return (
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
              onClick={() => onSelectSchema(schema)}
              secondaryAction={
                <Tooltip title="Delete schema">
                  <IconButton
                    edge="end"
                    aria-label={`Delete ${schema.name}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteRequest(schema)
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
  )
}

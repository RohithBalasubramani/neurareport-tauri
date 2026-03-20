/**
 * Sessions sidebar list for SynthesisPage
 */
import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Merge as MergeIcon,
} from '@mui/icons-material';

export default function SessionsList({
  sessions,
  currentSession,
  onSelectSession,
  onDeleteSession,
}) {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Sessions
      </Typography>
      {sessions.length === 0 ? (
        <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
          No sessions yet
        </Typography>
      ) : (
        <List dense>
          {sessions.map((session) => (
            <ListItem
              key={session.id}
              button
              selected={currentSession?.id === session.id}
              onClick={() => onSelectSession(session.id)}
            >
              <ListItemIcon>
                <MergeIcon />
              </ListItemIcon>
              <ListItemText
                primary={session.name}
                secondary={`${session.documents?.length || 0} docs`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session);
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
}

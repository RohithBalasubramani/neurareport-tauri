/**
 * Folder Watcher panel for the Ingestion page.
 */
import React from 'react'
import {
  Box,
  Typography,
  Chip,
  IconButton,
} from '@mui/material'
import {
  Folder as FolderIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  FolderOpen as WatcherIcon,
} from '@mui/icons-material'
import { WatcherCard, ActionButton } from './IngestionStyledComponents'

export default function WatcherPanel({
  watchers,
  onToggleWatcher,
  onDeleteWatcher,
  onOpenCreateWatcher,
}) {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Folder Watchers
        </Typography>
        <ActionButton
          variant="contained"
          size="small"
          startIcon={<WatcherIcon />}
          onClick={onOpenCreateWatcher}
        >
          Add Watcher
        </ActionButton>
      </Box>
      {watchers.length > 0 ? (
        watchers.map((watcher) => (
          <WatcherCard key={watcher.id} isRunning={watcher.status === 'running'}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <FolderIcon color={watcher.status === 'running' ? 'success' : 'action'} />
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {watcher.folder_path}
                  </Typography>
                  <Chip
                    size="small"
                    label={watcher.status}
                    color={watcher.status === 'running' ? 'success' : 'default'}
                  />
                </Box>
              </Box>
              <Box>
                <IconButton onClick={() => onToggleWatcher(watcher)}>
                  {watcher.status === 'running' ? <StopIcon /> : <StartIcon />}
                </IconButton>
                <IconButton onClick={() => onDeleteWatcher(watcher.id)}>
                  <DeleteIcon />
                </IconButton>
              </Box>
            </Box>
          </WatcherCard>
        ))
      ) : (
        <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
          No folder watchers configured
        </Typography>
      )}
    </Box>
  )
}

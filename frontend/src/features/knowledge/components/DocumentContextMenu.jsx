/**
 * Context menu for document actions (auto-tag, find related, delete).
 */
import React from 'react'
import { Menu, MenuItem, ListItemIcon, ListItemText, Divider } from '@mui/material'
import {
  AutoAwesome as AIIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'

export default function DocumentContextMenu({
  anchorEl, selectedDoc, onClose,
  onAutoTag, onFindRelated, onDelete,
}) {
  return (
    <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={onClose}>
      <MenuItem onClick={() => { onAutoTag(selectedDoc?.id); onClose() }}>
        <ListItemIcon><AIIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Auto-tag</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => { onFindRelated(selectedDoc?.id); onClose() }}>
        <ListItemIcon><SearchIcon fontSize="small" /></ListItemIcon>
        <ListItemText>Find Related</ListItemText>
      </MenuItem>
      <Divider />
      <MenuItem onClick={() => { onDelete(selectedDoc?.id); onClose() }}>
        <ListItemIcon><DeleteIcon fontSize="small" sx={{ color: 'text.secondary' }} /></ListItemIcon>
        <ListItemText>Delete</ListItemText>
      </MenuItem>
    </Menu>
  )
}

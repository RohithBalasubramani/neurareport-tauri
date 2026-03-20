/**
 * Row actions menu for the Connections table.
 */
import React from 'react'
import {
  ListItemIcon,
  ListItemText,
  useTheme,
} from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import RefreshIcon from '@mui/icons-material/Refresh'
import TableViewIcon from '@mui/icons-material/TableView'
import { StyledMenu, StyledMenuItem } from './ConnectionsStyledComponents'

export default function ConnectionActionsMenu({
  menuAnchor,
  menuConnection,
  onClose,
  onTestConnection,
  onSchemaInspect,
  onEditConnection,
  onDeleteClick,
}) {
  const theme = useTheme()

  return (
    <StyledMenu
      anchorEl={menuAnchor}
      open={Boolean(menuAnchor)}
      onClose={onClose}
    >
      <StyledMenuItem
        onClick={() => { onTestConnection(menuConnection); onClose() }}
      >
        <ListItemIcon>
          <RefreshIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
        </ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
          Test Connection
        </ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={onSchemaInspect}>
        <ListItemIcon>
          <TableViewIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
        </ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
          Inspect Schema
        </ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={onEditConnection}>
        <ListItemIcon>
          <EditIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
        </ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
          Edit
        </ListItemText>
      </StyledMenuItem>
      <StyledMenuItem
        onClick={onDeleteClick}
        sx={{ color: theme.palette.text.primary }}
      >
        <ListItemIcon>
          <DeleteIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
        </ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
          Delete
        </ListItemText>
      </StyledMenuItem>
    </StyledMenu>
  )
}

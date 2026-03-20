/**
 * Row actions context menu for templates
 */
import { ListItemIcon, ListItemText } from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import SettingsIcon from '@mui/icons-material/Settings'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import { StyledMenu, StyledMenuItem } from './TemplateStyledComponents'

export default function TemplateRowActionsMenu({
  menuAnchor,
  handleCloseMenu,
  handleEditTemplate,
  handleEditMetadata,
  handleExport,
  handleDuplicate,
  duplicating,
  handleViewSimilar,
  handleDeleteClick,
}) {
  return (
    <StyledMenu
      anchorEl={menuAnchor}
      open={Boolean(menuAnchor)}
      onClose={handleCloseMenu}
    >
      <StyledMenuItem onClick={handleEditTemplate}>
        <ListItemIcon><EditIcon sx={{ fontSize: 16 }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Edit</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={handleEditMetadata}>
        <ListItemIcon><SettingsIcon sx={{ fontSize: 16 }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Edit Details</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={handleExport}>
        <ListItemIcon><DownloadIcon sx={{ fontSize: 16 }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Export</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={handleDuplicate} disabled={duplicating}>
        <ListItemIcon><ContentCopyIcon sx={{ fontSize: 16 }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>{duplicating ? 'Duplicating...' : 'Duplicate'}</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={handleViewSimilar}>
        <ListItemIcon><AutoAwesomeIcon sx={{ fontSize: 16 }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>View Similar</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={handleDeleteClick} sx={{ color: 'text.primary' }}>
        <ListItemIcon><DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} /></ListItemIcon>
        <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Delete</ListItemText>
      </StyledMenuItem>
    </StyledMenu>
  )
}

/**
 * Context menu for schedule row actions.
 */
import { Fade, ListItemIcon, ListItemText } from '@mui/material'
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
} from '@mui/icons-material'
import { StyledMenu, StyledMenuItem } from './ScheduleStyles'

export default function ScheduleActionMenu({
  anchorEl, onClose,
  menuScheduleActive,
  onRunNow, onEdit, onToggleEnabled, onDelete,
}) {
  return (
    <StyledMenu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={onClose} TransitionComponent={Fade}>
      <StyledMenuItem onClick={onRunNow}>
        <ListItemIcon>
          <PlayArrowIcon fontSize="small" sx={{ color: 'primary.main' }} />
        </ListItemIcon>
        <ListItemText>Run Now</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={onEdit}>
        <ListItemIcon>
          <EditIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>Edit</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={onToggleEnabled}>
        <ListItemIcon>
          {menuScheduleActive ? <PauseIcon fontSize="small" /> : <PlayArrowIcon fontSize="small" />}
        </ListItemIcon>
        <ListItemText>{menuScheduleActive ? 'Pause' : 'Enable'}</ListItemText>
      </StyledMenuItem>
      <StyledMenuItem onClick={onDelete} sx={{ color: 'error.main' }}>
        <ListItemIcon>
          <DeleteIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        </ListItemIcon>
        <ListItemText>Delete</ListItemText>
      </StyledMenuItem>
    </StyledMenu>
  )
}

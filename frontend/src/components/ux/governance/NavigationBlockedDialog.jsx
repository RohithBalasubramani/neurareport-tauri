/**
 * Navigation Blocked Dialog
 *
 * Shows when navigation is attempted while blockers are active.
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Typography,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Warning as WarningIcon,
  HourglassEmpty as PendingIcon,
  Edit as UnsavedIcon,
} from '@mui/icons-material'
import { BlockerType } from './navigationConstants'

export default function NavigationBlockedDialog({
  open,
  activeBlockers,
  onCancel,
  onForceNavigate,
}) {
  const theme = useTheme()

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: alpha(theme.palette.background.paper, 0.95),
          backdropFilter: 'blur(10px)',
          borderRadius: 1,  // Figma spec: 8px
        },
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <WarningIcon sx={{ color: 'text.secondary' }} />
        <Typography variant="h6" fontWeight={600}>
          Wait! You have unsaved work
        </Typography>
      </DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          Leaving this page will interrupt the following:
        </DialogContentText>
        <List dense>
          {activeBlockers.map((blocker) => (
            <ListItem key={blocker.id}>
              <ListItemIcon>
                {blocker.type === BlockerType.OPERATION_IN_PROGRESS ? (
                  <CircularProgress size={20} />
                ) : blocker.type === BlockerType.UNSAVED_CHANGES ? (
                  <UnsavedIcon sx={{ color: 'text.secondary' }} />
                ) : (
                  <PendingIcon sx={{ color: 'text.secondary' }} />
                )}
              </ListItemIcon>
              <ListItemText
                primary={blocker.label}
                secondary={blocker.description}
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onCancel} variant="contained">
          Stay on this page
        </Button>
        <Button onClick={onForceNavigate} sx={{ color: 'text.secondary' }}>
          Leave anyway
        </Button>
      </DialogActions>
    </Dialog>
  )
}

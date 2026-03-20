/**
 * TopNav keyboard shortcuts and help dialogs
 */
import {
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  Button,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import { StyledDialog, ShortcutChip, HelpCard } from './TopNavStyles'
import { getShortcutDisplay, SHORTCUTS } from '../../hooks/useKeyboardShortcuts'

const shortcutItems = [
  { label: 'Command Palette', keys: getShortcutDisplay(SHORTCUTS.COMMAND_PALETTE).join(' + ') },
  { label: 'Close dialogs', keys: getShortcutDisplay(SHORTCUTS.CLOSE).join(' + ') },
]

const helpActions = [
  { label: 'Open Setup Wizard', description: 'Connect a data source and upload templates.', path: '/setup/wizard' },
  { label: 'Manage Templates', description: 'Edit, duplicate, or export templates.', path: '/templates' },
  { label: 'Generate Reports', description: 'Run report jobs and download outputs.', path: '/reports' },
  { label: 'Analyze Documents', description: 'Extract tables and charts from files.', path: '/analyze' },
  { label: 'System Settings', description: 'View health checks and preferences.', path: '/settings' },
]

export function ShortcutsDialog({ open, onClose }) {
  const theme = useTheme()

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      TransitionComponent={Fade}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Keyboard Shortcuts</DialogTitle>
      <DialogContent dividers sx={{ borderColor: alpha(theme.palette.divider, 0.1) }}>
        <Stack spacing={2}>
          {shortcutItems.map((item) => (
            <Box
              key={item.label}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            >
              <Typography sx={{ fontSize: '0.875rem' }}>
                {item.label}
              </Typography>
              <ShortcutChip label={item.keys} size="small" />
            </Box>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions sx={{ borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`, p: 2 }}>
        <Button
          onClick={onClose}
          sx={{ borderRadius: 1, textTransform: 'none', fontWeight: 500 }}
        >
          Close
        </Button>
      </DialogActions>
    </StyledDialog>
  )
}

export function HelpDialog({ open, onClose, onNavigate }) {
  const theme = useTheme()

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      TransitionComponent={Fade}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Help Center</DialogTitle>
      <DialogContent dividers sx={{ borderColor: alpha(theme.palette.divider, 0.1) }}>
        <Typography sx={{ fontSize: '0.875rem', color: 'text.secondary', mb: 3 }}>
          Jump to common workflows or explore system settings.
        </Typography>
        <Stack spacing={1.5}>
          {helpActions.map((action) => (
            <HelpCard key={action.label}>
              <Box sx={{ minWidth: 0 }}>
                <Typography sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 0.25 }}>
                  {action.label}
                </Typography>
                <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                  {action.description}
                </Typography>
              </Box>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {
                  onClose()
                  onNavigate(action.path, `Open ${action.label}`)
                }}
                sx={{
                  borderRadius: 1,  // Figma spec: 8px
                  textTransform: 'none',
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                  minWidth: 64,
                }}
              >
                Open
              </Button>
            </HelpCard>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions sx={{ borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`, p: 2 }}>
        <Button
          onClick={onClose}
          sx={{ borderRadius: 1, textTransform: 'none', fontWeight: 500 }}
        >
          Close
        </Button>
      </DialogActions>
    </StyledDialog>
  )
}

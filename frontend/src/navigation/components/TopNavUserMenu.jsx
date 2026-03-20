/**
 * TopNav user menu dropdown
 */
import {
  ListItemIcon,
  ListItemText,
  Divider,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { StyledMenu, StyledMenuItem } from './TopNavStyles'

export default function TopNavUserMenu({ anchorEl, onClose, onNavigate, onSignOut }) {
  const theme = useTheme()

  return (
    <StyledMenu
      anchorEl={anchorEl}
      open={Boolean(anchorEl)}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      TransitionComponent={Fade}
    >
      <StyledMenuItem onClick={() => onNavigate('/settings')}>
        <ListItemIcon>
          <SettingsIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
        </ListItemIcon>
        <ListItemText
          primary="Settings"
          primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: 500 }}
        />
      </StyledMenuItem>
      <Divider sx={{ my: 0.5, mx: 1, borderColor: alpha(theme.palette.divider, 0.1) }} />
      <StyledMenuItem onClick={onSignOut}>
        <ListItemIcon>
          <LogoutIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
        </ListItemIcon>
        <ListItemText
          primary="Sign Out"
          primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: 500 }}
        />
      </StyledMenuItem>
    </StyledMenu>
  )
}

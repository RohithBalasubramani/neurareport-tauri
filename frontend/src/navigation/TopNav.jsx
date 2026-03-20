/**
 * Premium Top Navigation
 * Sophisticated header with glassmorphism, animations, and refined interactions
 */
import {
  Box,
  Stack,
  Tooltip,
  Zoom,
  useTheme,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  PersonOutline as PersonOutlineIcon,
  Keyboard as KeyboardIcon,
  HelpOutline as HelpOutlineIcon,
  Work as WorkIcon,
} from '@mui/icons-material'
import Breadcrumbs from './Breadcrumbs'
import GlobalSearch from './GlobalSearch'
import { getShortcutDisplay, SHORTCUTS } from '../hooks/useKeyboardShortcuts'
import {
  useTopNavInteractions,
  useTopNavMenus,
  useTopNavDialogs,
  useTopNavSignOut,
  useTopNavNotificationData,
} from './hooks/useTopNav'
import {
  StyledAppBar,
  StyledToolbar,
  NavIconButton,
  ConnectionChip,
  StatusDot,
  StyledBadge,
} from './components/TopNavStyles'
import TopNavUserMenu from './components/TopNavUserMenu'
import TopNavNotificationsMenu from './components/TopNavNotificationsMenu'
import { ShortcutsDialog, HelpDialog } from './components/TopNavDialogs'

export default function TopNav({ onMenuClick, showMenuButton, connection }) {
  const theme = useTheme()
  const { execute, executeUI, handleNavigate, handleMenuButtonClick, handleOpenCommandPalette } = useTopNavInteractions(onMenuClick)
  const menus = useTopNavMenus(executeUI, handleNavigate)
  const dialogs = useTopNavDialogs(executeUI)
  const { handleSignOut } = useTopNavSignOut(execute, menus.closeMenu)
  const { jobNotifications, downloadNotifications, notificationsCount } = useTopNavNotificationData()

  const isConnected = connection?.status === 'connected'

  return (
    <StyledAppBar position="sticky" elevation={0}>
      <StyledToolbar>
        {/* Menu Button (Mobile) */}
        {showMenuButton && (
          <NavIconButton edge="start" onClick={handleMenuButtonClick} aria-label="Open menu" data-testid="mobile-menu-button">
            <MenuIcon sx={{ fontSize: 20 }} />
          </NavIconButton>
        )}

        {/* Breadcrumbs + Global Search */}
        <Box sx={{ flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 2 }} data-testid="topnav-breadcrumb-search-container">
          <Box sx={{ flex: 1, minWidth: 0 }} data-testid="topnav-breadcrumb-wrapper">
            <Breadcrumbs />
          </Box>
          <Box sx={{ display: { xs: 'none', md: 'block' } }} data-testid="topnav-global-search-wrapper">
            <GlobalSearch variant="compact" enableShortcut={false} showShortcutHint={false} />
          </Box>
        </Box>

        {/* Connection Status */}
        {connection && (
          <Tooltip title={isConnected ? 'Database connected' : 'Connection issue'} arrow TransitionComponent={Zoom}>
            <ConnectionChip
              connected={isConnected}
              icon={<StatusDot connected={isConnected} data-testid="connection-status-dot" />}
              label={connection.name || (isConnected ? 'Connected' : 'Disconnected')}
              size="small"
              data-testid="connection-status-chip"
            />
          </Tooltip>
        )}

        {/* Actions */}
        <Stack direction="row" spacing={0.5} alignItems="center" data-testid="topnav-actions-container">
          <Tooltip title={`Search (${getShortcutDisplay(SHORTCUTS.COMMAND_PALETTE).join(' + ')})`} arrow TransitionComponent={Zoom}>
            <NavIconButton size="small" onClick={handleOpenCommandPalette} aria-label="Open search" data-testid="search-button">
              <SearchIcon sx={{ fontSize: 18 }} />
            </NavIconButton>
          </Tooltip>

          <Tooltip title="Keyboard Shortcuts" arrow TransitionComponent={Zoom}>
            <NavIconButton size="small" onClick={dialogs.handleOpenShortcuts} aria-label="View shortcuts" data-testid="keyboard-shortcuts-button">
              <KeyboardIcon sx={{ fontSize: 18 }} />
            </NavIconButton>
          </Tooltip>

          <Tooltip title="Jobs & downloads" arrow TransitionComponent={Zoom}>
            <NavIconButton size="small" onClick={menus.handleOpenNotifications} aria-label="View notifications" data-testid="notifications-button">
              <StyledBadge badgeContent={notificationsCount} invisible={!notificationsCount}>
                <WorkIcon sx={{ fontSize: 18 }} />
              </StyledBadge>
            </NavIconButton>
          </Tooltip>

          <Tooltip title="Help" arrow TransitionComponent={Zoom}>
            <NavIconButton size="small" onClick={dialogs.handleOpenHelp} aria-label="Open help" data-testid="help-button">
              <HelpOutlineIcon sx={{ fontSize: 18 }} />
            </NavIconButton>
          </Tooltip>

          <NavIconButton size="small" onClick={menus.handleOpenMenu} aria-label="User menu" data-testid="user-menu-button" sx={{ ml: 0.5 }}>
            <PersonOutlineIcon sx={{ fontSize: 18 }} />
          </NavIconButton>
        </Stack>

        {/* User Menu */}
        <TopNavUserMenu
          anchorEl={menus.anchorEl}
          onClose={menus.handleCloseMenu}
          onNavigate={menus.handleNavigateAndClose}
          onSignOut={handleSignOut}
        />

        {/* Notifications Menu */}
        <TopNavNotificationsMenu
          anchorEl={menus.notificationsAnchorEl}
          onClose={menus.handleCloseNotifications}
          jobNotifications={jobNotifications}
          downloadNotifications={downloadNotifications}
          onNavigate={menus.handleNavigateAndClose}
          onCloseNotifications={menus.handleCloseNotifications}
          onOpenJobsPanel={menus.handleOpenJobsPanel}
          onOpenDownload={menus.handleOpenDownload}
        />

        {/* Dialogs */}
        <ShortcutsDialog open={dialogs.shortcutsOpen} onClose={dialogs.handleCloseShortcuts} />
        <HelpDialog open={dialogs.helpOpen} onClose={dialogs.handleCloseHelp} onNavigate={menus.handleNavigateAndClose} />
      </StyledToolbar>
    </StyledAppBar>
  )
}

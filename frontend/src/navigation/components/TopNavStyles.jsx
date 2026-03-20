/**
 * TopNav bar styled components
 */
import {
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Badge,
  Box,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { neutral } from '@/app/theme'

// =============================================================================
// ANIMATIONS
// =============================================================================

export const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
`

export const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
`

export const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? neutral[900] : 'rgba(255, 255, 255, 0.85)',
  backdropFilter: 'blur(12px)',
  borderBottom: `1px solid ${theme.palette.mode === 'dark' ? neutral[700] : neutral[200]}`,
  boxShadow: 'none',
}))

export const StyledToolbar = styled(Toolbar)(({ theme }) => ({
  gap: theme.spacing(2),
  minHeight: 60,
  padding: theme.spacing(0, 3),
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(0, 2),
  },
}))

export const NavIconButton = styled(IconButton)(({ theme }) => ({
  width: 36,
  height: 36,
  borderRadius: 8,
  color: theme.palette.mode === 'dark' ? neutral[500] : neutral[300],
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : neutral[100],
    color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
  },
  '&:active': {
    transform: 'none',
  },
}))

export const ConnectionChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'connected',
})(({ theme, connected }) => ({
  height: 30,
  borderRadius: 8,
  flexShrink: 1,
  minWidth: 0,
  maxWidth: 240,
  [theme.breakpoints.down('sm')]: {
    maxWidth: 140,
  },
  backgroundColor: connected
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100])
    : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[50]),
  border: `1px solid ${connected
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200])
    : alpha(theme.palette.divider, 0.2)}`,
  color: theme.palette.text.secondary,
  fontWeight: 500,
  fontSize: '0.75rem',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '& .MuiChip-icon': {
    marginLeft: 6,
  },
  '& .MuiChip-label': {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    maxWidth: '100%',
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
  },
}))

export const StatusDot = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'connected',
})(({ theme, connected }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: connected
    ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
    : (theme.palette.mode === 'dark' ? neutral[300] : neutral[500]),
  boxShadow: connected
    ? `0 0 0 3px ${theme.palette.mode === 'dark' ? alpha(neutral[500], 0.2) : alpha(neutral[700], 0.2)}`
    : 'none',
  animation: connected ? `${pulse} 2s infinite ease-in-out` : 'none',
}))

export const StyledBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[400],
    color: 'common.white',
    fontSize: '10px',
    fontWeight: 600,
    minWidth: 18,
    height: 18,
    borderRadius: 9,
    boxShadow: 'none',
    animation: `${fadeIn} 0.3s ease-out`,
  },
}))

// Re-export menu styles for backward compat
export {
  StyledMenu,
  StyledMenuItem,
  MenuHeader,
  MenuLabel,
  ShortcutChip,
  HelpCard,
  StyledDialog,
} from './TopNavMenuStyles'

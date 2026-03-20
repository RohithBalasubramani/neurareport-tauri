/**
 * TopNav menu and dialog styled components
 */
import {
  Chip,
  Box,
  Dialog,
  Menu,
  MenuItem,
  Typography,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'

export const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 14,
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 12px 40px ${alpha(theme.palette.common.black, 0.15)}`,
    marginTop: theme.spacing(1),
    minWidth: 200,
  },
}))

export const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  borderRadius: 8,
  margin: theme.spacing(0.5, 1),
  padding: theme.spacing(1, 1.5),
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const MenuHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5, 2, 1),
}))

export const MenuLabel = styled(Typography)(({ theme }) => ({
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: theme.palette.text.disabled,
}))

export const ShortcutChip = styled(Chip)(({ theme }) => ({
  height: 24,
  fontSize: '12px',
  fontFamily: 'var(--font-mono, monospace)',
  fontWeight: 500,
  backgroundColor: alpha(theme.palette.text.primary, 0.06),
  color: theme.palette.text.secondary,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  borderRadius: 6,
}))

export const HelpCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  gap: theme.spacing(2),
  padding: theme.spacing(2),
  borderRadius: 8,  // Figma spec: 8px
  backgroundColor: alpha(theme.palette.background.paper, 0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
  },
}))

export const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 8,  // Figma spec: 8px
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  },
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.5),
    backdropFilter: 'blur(4px)',
  },
}))

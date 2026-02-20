/**
 * Shared Styled Components
 * Reusable MUI styled components used across feature containers.
 */

import { styled } from '@mui/material/styles'
import { Card, FormControl, IconButton, Button, alpha } from '@mui/material'
import { neutral } from '@/app/theme'

// ---------------------------------------------------------------------------
// GLASS CARD
// ---------------------------------------------------------------------------

export const GlassCard = styled(Card)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(20px)',
  border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
  borderRadius: 8,
  padding: theme.spacing(3),
  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 12px 48px ${alpha(theme.palette.common.black, 0.12)}`,
    transform: 'translateY(-2px)',
  },
}))

// ---------------------------------------------------------------------------
// STYLED FORM CONTROL
// ---------------------------------------------------------------------------

export const StyledFormControl = styled(FormControl)(({ theme }) => ({
  minWidth: 160,
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    backdropFilter: 'blur(8px)',
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    '&:hover': {
      backgroundColor: alpha(theme.palette.background.paper, 0.8),
    },
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
      boxShadow: `0 0 0 3px ${alpha(theme.palette.text.primary, 0.08)}`,
    },
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: alpha(theme.palette.divider, 0.15),
    },
  },
  '& .MuiInputLabel-root': {
    color: theme.palette.text.secondary,
  },
}))

// ---------------------------------------------------------------------------
// REFRESH BUTTON
// ---------------------------------------------------------------------------

export const RefreshButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 12,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.text.primary, 0.1)
      : neutral[100],
    transform: 'rotate(180deg)',
  },
}))

// ---------------------------------------------------------------------------
// EXPORT BUTTON
// ---------------------------------------------------------------------------

export const ExportButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 500,
  borderColor: alpha(theme.palette.divider, 0.2),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.text.primary, 0.08)
      : neutral[100],
  },
}))

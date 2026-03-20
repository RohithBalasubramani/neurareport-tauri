/**
 * Shared styled components for query builder feature
 */
import { styled, alpha, Button, TextField } from '@mui/material'
import { neutral } from '@/app/theme'

export const HeaderButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 500,
  borderColor: alpha(theme.palette.divider, 0.2),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const PrimaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 600,
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-1px)',
  },
  '&:active': { transform: 'translateY(0)' },
  '&:disabled': {
    background: alpha(theme.palette.text.disabled, 0.2),
    color: theme.palette.text.disabled,
    boxShadow: 'none',
  },
}))

export const ExecuteButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 600,
  background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-1px)',
  },
  '&:disabled': {
    background: alpha(theme.palette.text.disabled, 0.2),
    color: theme.palette.text.disabled,
    boxShadow: 'none',
  },
}))

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    backgroundColor: alpha(theme.palette.background.default, 0.5),
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    '&:hover': {
      backgroundColor: alpha(theme.palette.background.default, 0.7),
    },
    '&.Mui-focused': {
      backgroundColor: alpha(theme.palette.background.default, 0.9),
      boxShadow: `0 0 0 3px ${alpha(theme.palette.text.primary, 0.08)}`,
    },
  },
}))

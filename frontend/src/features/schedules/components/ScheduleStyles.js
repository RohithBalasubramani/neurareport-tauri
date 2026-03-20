/**
 * Styled components, constants, and helpers for the Schedules page.
 */
import {
  Box, Typography, Chip, Button, TextField, Switch,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Menu, MenuItem,
  styled, alpha,
} from '@mui/material'
import { fadeInUp } from '@/styles'
import { neutral } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  animation: `${fadeInUp} 0.4s ease-out`,
}))

export const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 8,  // Figma spec: 8px
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 24px 48px ${alpha(theme.palette.common.black, 0.2)}`,
  },
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.5),
    backdropFilter: 'blur(4px)',
  },
}))

export const DialogHeader = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const DialogIconContainer = styled(Box)(({ theme }) => ({
  width: 48,
  height: 48,
  borderRadius: 14,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  '& svg': {
    fontSize: 24,
    color: theme.palette.text.secondary,
  },
}))

export const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(3),
}))

export const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  gap: theme.spacing(1),
}))

export const SectionLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.75rem',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: theme.palette.text.disabled,
  marginBottom: theme.spacing(2),
  marginTop: theme.spacing(3),
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  '&:first-of-type': {
    marginTop: 0,
  },
}))

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[300],
    },
    '&.Mui-focused': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
        borderWidth: 2,
      },
    },
  },
}))

export const StatusChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({
  borderRadius: 8,
  fontWeight: 500,
  fontSize: '0.75rem',
  backgroundColor: active
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100])
    : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[50]),
  color: theme.palette.text.secondary,
  border: `1px solid ${active
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200])
    : alpha(theme.palette.divider, 0.2)}`,
}))

export const FrequencyChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  fontWeight: 500,
  fontSize: '0.75rem',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  color: theme.palette.text.secondary,
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200]}`,
}))

export const StyledSwitch = styled(Switch)(({ theme }) => ({
  '& .MuiSwitch-switchBase.Mui-checked': {
    color: theme.palette.mode === 'dark' ? neutral[400] : neutral[400],
    '& + .MuiSwitch-track': {
      backgroundColor: theme.palette.mode === 'dark' ? neutral[400] : neutral[400],
    },
  },
}))

export const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 12,
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.15)}`,
    minWidth: 180,
  },
}))

export const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  borderRadius: 8,
  margin: theme.spacing(0.5, 1),
  padding: theme.spacing(1, 1.5),
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
  },
}))

export const SchedulerStatusBanner = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'status',
})(({ theme, status }) => {
  const neutralColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
  const neutralBg = theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]
  const colors = {
    ok: { bg: neutralBg, border: neutralColor, text: neutralColor },
    warning: { bg: neutralBg, border: neutralColor, text: neutralColor },
    disabled: { bg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[50], border: alpha(theme.palette.divider, 0.3), text: theme.palette.text.secondary },
    error: { bg: neutralBg, border: neutralColor, text: neutralColor },
  }
  const colorScheme = colors[status] || colors.warning
  return {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1.5),
    padding: theme.spacing(1.5, 2),
    marginBottom: theme.spacing(2),
    borderRadius: 8,
    backgroundColor: colorScheme.bg,
    border: `1px solid ${colorScheme.border}`,
    color: colorScheme.text,
  }
})

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 10,
  textTransform: 'none',
  fontWeight: 500,
  padding: theme.spacing(1, 2.5),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

export const PrimaryButton = styled(ActionButton)(({ theme }) => ({
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-1px)',
  },
  '&:disabled': {
    background: alpha(theme.palette.text.primary, 0.1),
    color: alpha(theme.palette.text.primary, 0.4),
    boxShadow: 'none',
  },
}))

// =============================================================================
// CONSTANTS
// =============================================================================

export const FREQUENCY_OPTIONS = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
]

export const FREQUENCY_INTERVALS = {
  daily: 1440,
  weekly: 10080,
  monthly: 43200,
}

// =============================================================================
// HELPERS
// =============================================================================

export const extractDateOnly = (value) => {
  if (!value) return ''
  const match = String(value).match(/^(\d{4}-\d{2}-\d{2})/)
  return match ? match[1] : ''
}

export const buildDateTime = (dateValue, endOfDay = false) => {
  if (!dateValue) return ''
  const time = endOfDay ? '23:59:59' : '00:00:00'
  return `${dateValue} ${time}`
}

export const parseEmailList = (raw) => {
  if (!raw) return []
  return raw.split(/[;,]/).map((entry) => entry.trim()).filter(Boolean)
}

export const formatEmailList = (list) => {
  if (!Array.isArray(list)) return ''
  return list.filter(Boolean).join(', ')
}

export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const isSchedulableTemplate = (template) => {
  if (!template || typeof template !== 'object') return false
  const status = String(template.status || '').toLowerCase()
  return status === 'approved' || status === 'active'
}

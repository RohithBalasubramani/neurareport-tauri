/**
 * Styled components and helpers for CommentsPanel.
 */
import {
  Box,
  Paper,
  TextField,
  Button,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'

export const PanelContainer = styled(Box)(({ theme }) => ({
  width: 320,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

export const CommentComposer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

export const CommentCard = styled(Paper, {
  shouldForwardProp: (prop) => !['isResolved', 'isHighlighted'].includes(prop),
})(({ theme, isResolved, isHighlighted }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${
    isHighlighted
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
      : isResolved
      ? alpha(theme.palette.divider, 0.3)
      : alpha(theme.palette.divider, 0.1)
  }`,
  backgroundColor: isResolved
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50])
    : isHighlighted
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50])
    : 'transparent',
  opacity: isResolved ? 0.7 : 1,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
}))

export const ReplyCard = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1.5),
  paddingTop: theme.spacing(1.5),
  paddingLeft: theme.spacing(2),
  borderLeft: `2px solid ${alpha(theme.palette.divider, 0.3)}`,
}))

export const QuotedText = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderLeft: `3px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[300]}`,
  borderRadius: '0 4px 4px 0',
  fontSize: '0.75rem',
  fontStyle: 'italic',
  color: theme.palette.text.secondary,
}))

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.75rem',
}))

export const CompactTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,
    fontSize: '0.875rem',
  },
}))

// =============================================================================
// HELPERS
// =============================================================================

export const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

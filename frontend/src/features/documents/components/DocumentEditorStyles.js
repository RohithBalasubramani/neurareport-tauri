/**
 * Styled components for the Document Editor page.
 */
import { Box, Paper, Button, styled, alpha } from '@mui/material'
import { neutral } from '@/app/theme'

export const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

export const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(10px)',
  gap: theme.spacing(2),
}))

export const EditorArea = styled(Box)(() => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

export const EditorPane = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
}))

export const DocumentsList = styled(Box)(({ theme }) => ({
  width: 300,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.5),
  display: 'flex',
  flexDirection: 'column',
}))

export const DocumentsHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}))

export const DocumentsContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(1),
}))

export const DocumentItem = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isActive',
})(({ theme, isActive }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  cursor: 'pointer',
  border: `1px solid ${isActive ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'transparent'}`,
  backgroundColor: isActive ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50]) : 'transparent',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    borderColor: alpha(theme.palette.divider, 0.3),
  },
}))

export const ActionButton = styled(Button)(() => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
}))

export const EmptyState = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}))

export const AIResultCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.spacing(2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  borderRadius: 8,  // Figma spec: 8px
}))

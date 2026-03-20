/**
 * Styled components for WorkflowBuilderPage
 */
import {
  Box,
  Paper,
  Card,
  Button,
  alpha,
  styled,
} from '@mui/material'
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
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

export const WorkflowArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

export const NodePalette = styled(Box)(({ theme }) => ({
  width: 260,
  flexShrink: 0,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  padding: theme.spacing(2),
  overflow: 'auto',
}))

export const Canvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
  backgroundColor: theme.palette.background.default,
  backgroundImage: `radial-gradient(${alpha(theme.palette.divider, 0.15)} 1px, transparent 1px)`,
  backgroundSize: '20px 20px',
}))

export const SidebarContainer = styled(Box)(({ theme }) => ({
  width: 300,
  flexShrink: 0,
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  display: 'flex',
  flexDirection: 'column',
}))

export const NodeCard = styled(Card)(({ theme }) => ({
  cursor: 'grab',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  marginBottom: theme.spacing(1),
  '&:hover': {
    transform: 'translateX(4px)',
    boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

export const WorkflowNode = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  minWidth: 200,
  borderRadius: 8,  // Figma spec: 8px
  border: `2px solid ${alpha(theme.palette.divider, 0.3)}`,
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

export const ExecutionCard = styled(Paper)(({ theme, status }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1),
  borderLeft: `4px solid ${
    status === 'completed'
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
      : status === 'running'
      ? (theme.palette.mode === 'dark' ? neutral[300] : neutral[500])
      : status === 'failed'
      ? theme.palette.text.secondary
      : neutral[400]
  }`,
}))

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
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

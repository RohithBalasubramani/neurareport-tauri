/**
 * Shared styled components and constants for Dashboard Builder.
 */
import { Box, Button, Paper, ListItemButton, styled, alpha } from '@mui/material'
import { neutral } from '@/app/theme'

export const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

export const Sidebar = styled(Box)(({ theme }) => ({
  width: 300,
  display: 'flex',
  flexDirection: 'column',
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
}))

export const SidebarSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const SidebarContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

export const MainContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}))

export const ToolbarContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

export const Canvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(2),
  overflow: 'auto',
  backgroundColor: theme.palette.background.default,
}))

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
}))

export const DashboardListItem = styled(ListItemButton, {
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  backgroundColor: active ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]) : 'transparent',
  '&:hover': {
    backgroundColor: active
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[100])
      : alpha(theme.palette.action.hover, 0.05),
  },
}))

export const EmptyCanvas = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: `2px dashed ${alpha(theme.palette.divider, 0.3)}`,
  borderRadius: 8,  // Figma spec: 8px
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

export const InsightCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]}`,
}))

export const SAMPLE_CHART_DATA = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    { label: 'Revenue', data: [12000, 19000, 15000, 25000, 22000, 30000] },
    { label: 'Expenses', data: [8000, 12000, 10000, 14000, 13000, 16000] },
  ],
}

export const SAMPLE_SPARKLINE = [65, 70, 68, 75, 82, 78, 85, 90, 88, 95]

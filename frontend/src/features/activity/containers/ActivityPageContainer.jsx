/**
 * Premium Activity Page
 * Beautiful activity log with animations and theme-based styling
 */
import React from 'react'
import {
  Box,
  Typography,
  Stack,
  Button,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  useTheme,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import DeleteIcon from '@mui/icons-material/Delete'
import HistoryIcon from '@mui/icons-material/History'
import DashboardIcon from '@mui/icons-material/Dashboard'
import { ConfirmModal } from '@/components/modal'
import { StyledFormControl, RefreshButton } from '@/styles'
import { useActivity } from '../hooks/useActivity'
import ActivityItem from '../components/ActivityItem'
import {
  PageContainer,
  HeaderContainer,
  FilterContainer,
  ActivityListContainer,
  DeleteButton,
  EmptyStateContainer,
} from '../components/ActivityStyledComponents'

export default function ActivityPage() {
  const theme = useTheme()
  const {
    activities, loading,
    entityTypeFilter, setEntityTypeFilter,
    actionFilter, setActionFilter,
    clearConfirmOpen, setClearConfirmOpen,
    clearing, fetchActivities,
    handleClearLog, handleNavigate,
  } = useActivity()

  return (
    <PageContainer>
      <HeaderContainer direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h5" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
            Activity Log
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Track actions and events in your workspace
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <RefreshButton onClick={fetchActivities} disabled={loading} data-testid="refresh-activity-button" aria-label="Refresh activities" sx={{ color: theme.palette.text.secondary }}>
            {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          </RefreshButton>
          <DeleteButton onClick={() => setClearConfirmOpen(true)} disabled={activities.length === 0} data-testid="clear-activity-button" aria-label="Clear all activities" sx={{ color: theme.palette.text.secondary }}>
            <DeleteIcon />
          </DeleteButton>
        </Stack>
      </HeaderContainer>

      <FilterContainer direction="row" spacing={2}>
        <StyledFormControl size="small">
          <InputLabel>Entity Type</InputLabel>
          <Select value={entityTypeFilter} onChange={(e) => setEntityTypeFilter(e.target.value)} label="Entity Type" data-testid="entity-type-filter">
            <MenuItem value="">All</MenuItem>
            <MenuItem value="template">Template</MenuItem>
            <MenuItem value="connection">Connection</MenuItem>
            <MenuItem value="job">Job</MenuItem>
            <MenuItem value="schedule">Schedule</MenuItem>
          </Select>
        </StyledFormControl>
        <StyledFormControl size="small">
          <InputLabel>Action</InputLabel>
          <Select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)} label="Action" data-testid="action-filter">
            <MenuItem value="">All</MenuItem>
            <MenuItem value="favorite_added">Favorite added</MenuItem>
            <MenuItem value="favorite_removed">Favorite removed</MenuItem>
            <MenuItem value="template_deleted">Template deleted</MenuItem>
            <MenuItem value="job_cancelled">Job cancelled</MenuItem>
          </Select>
        </StyledFormControl>
      </FilterContainer>

      <ActivityListContainer>
        {loading ? (
          <Box sx={{ py: 4, textAlign: 'center' }}><CircularProgress size={32} /></Box>
        ) : activities.length === 0 ? (
          <EmptyStateContainer>
            <HistoryIcon sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 2 }} />
            <Typography sx={{ fontSize: '0.875rem', color: theme.palette.text.secondary }}>No activity recorded yet</Typography>
            <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.disabled, mt: 0.5, mb: 2 }}>Actions like creating templates, running jobs, and more will appear here</Typography>
            <Button variant="contained" startIcon={<DashboardIcon />} onClick={() => handleNavigate('/', 'Go to Dashboard', { action: 'empty-state-cta' })} sx={{ textTransform: 'none' }}>
              Go to Dashboard
            </Button>
          </EmptyStateContainer>
        ) : (
          activities.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} onNavigate={(route) => handleNavigate(route, 'Open activity item', { route, activityId: activity.id })} />
          ))
        )}
      </ActivityListContainer>

      <ConfirmModal
        open={clearConfirmOpen}
        onClose={() => setClearConfirmOpen(false)}
        onConfirm={handleClearLog}
        title="Clear Activity Log"
        message="Are you sure you want to clear all activity log entries? This action cannot be undone."
        confirmLabel="Clear All"
        severity="warning"
        loading={clearing}
      />
    </PageContainer>
  )
}

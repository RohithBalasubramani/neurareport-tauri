/**
 * Premium Activity Page
 * Beautiful activity log with animations and theme-based styling
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import {
  Box,
  Typography,
  Stack,
  Button,
  IconButton,
  Chip,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import DeleteIcon from '@mui/icons-material/Delete'
import HistoryIcon from '@mui/icons-material/History'
import DescriptionIcon from '@mui/icons-material/Description'
import StorageIcon from '@mui/icons-material/Storage'
import WorkIcon from '@mui/icons-material/Work'
import ScheduleIcon from '@mui/icons-material/Schedule'
import StarIcon from '@mui/icons-material/Star'
import SettingsIcon from '@mui/icons-material/Settings'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DashboardIcon from '@mui/icons-material/Dashboard'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { ConfirmModal } from '@/components/Modal'
import * as api from '@/api/client'
import { neutral, palette } from '@/app/theme'
import { fadeInUp, pulse, StyledFormControl, RefreshButton } from '@/styles'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1000,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

const HeaderContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

const FilterContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out 0.1s both`,
}))

const ActivityListContainer = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(20px)',
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  padding: theme.spacing(2),
  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  animation: `${fadeInUp} 0.5s ease-out 0.2s both`,
}))

const DeleteButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.primary,
  },
}))

const EmptyStateContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(6),
  textAlign: 'center',
  animation: `${fadeInUp} 0.5s ease-out`,
}))

// =============================================================================
// HELPERS
// =============================================================================

// Map entity types to their navigation routes
const ENTITY_ROUTES = {
  template: (id) => `/templates/${id}/edit`,
  connection: () => '/connections',
  job: () => '/jobs',
  schedule: () => '/schedules',
}

const ACTION_ICONS = {
  template: DescriptionIcon,
  connection: StorageIcon,
  job: WorkIcon,
  schedule: ScheduleIcon,
  favorite: StarIcon,
  settings: SettingsIcon,
  default: HistoryIcon,
}

const getActionConfig = (theme, action) => {
  const configs = {
    created: { color: theme.palette.text.secondary },
    deleted: { color: theme.palette.text.secondary },
    updated: { color: theme.palette.text.secondary },
    completed: { color: theme.palette.text.secondary },
    failed: { color: theme.palette.text.secondary },
    started: { color: theme.palette.text.secondary },
    favorite_added: { color: theme.palette.text.secondary },
    favorite_removed: { color: theme.palette.text.secondary },
    default: { color: theme.palette.text.secondary },
  }
  return configs[action] || configs.default
}

function formatRelativeTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
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

function formatAction(action) {
  return (action || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// =============================================================================
// ACTIVITY ITEM COMPONENT
// =============================================================================

function ActivityItem({ activity, onNavigate }) {
  const theme = useTheme()
  const entityTypeRaw = activity.entity_type || 'default'
  const entityType = String(entityTypeRaw).toLowerCase().replace(/s$/, '')
  const action = activity.action || ''
  const actionKey = String(action).toLowerCase()
  const Icon = ACTION_ICONS[entityType] || ACTION_ICONS.default
  const actionConfig = getActionConfig(theme, action)
  const accentColor = actionConfig.color

  // Determine if this item is navigable (not deleted items)
  const fallbackUrl = activity.details?.url || null
  const routeFn = ENTITY_ROUTES[entityType]
  const isNavigable = !actionKey.includes('deleted') && (routeFn || fallbackUrl)

  const handleClick = () => {
    if (isNavigable && onNavigate) {
      const route = routeFn ? routeFn(activity.entity_id) : fallbackUrl
      if (route) {
        onNavigate(route)
      }
    }
  }

  return (
    <Box
      onClick={handleClick}
      sx={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 2,
        py: 2,
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.06)}`,
        '&:last-child': { borderBottom: 'none' },
        cursor: isNavigable ? 'pointer' : 'default',
        borderRadius: 1,  // Figma spec: 8px
        mx: -1,
        px: 1,
        transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
        '&:hover': isNavigable ? {
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
          transform: 'translateX(4px)',
        } : {},
      }}
    >
      <Box
        sx={{
          width: 36,
          height: 36,
          borderRadius: 1,  // Figma spec: 8px
          bgcolor: alpha(accentColor, 0.15),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          transition: 'transform 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
          '.MuiBox-root:hover > &': isNavigable ? {
            animation: `${pulse} 0.5s cubic-bezier(0.22, 1, 0.36, 1)`,
          } : {},
        }}
      >
        <Icon sx={{ fontSize: 16, color: accentColor }} />
      </Box>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
          <Typography
            sx={{
              fontSize: '14px',
              fontWeight: 500,
              color: theme.palette.text.primary,
            }}
          >
            {formatAction(action)}
          </Typography>
          <Chip
            label={entityType}
            size="small"
            sx={{
              height: 18,
              fontSize: '0.625rem',
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              color: theme.palette.text.secondary,
              borderRadius: 1,
            }}
          />
        </Stack>
        {activity.entity_name && (
          <Typography
            sx={{
              fontSize: '14px',
              color: theme.palette.text.secondary,
              mb: 0.5,
            }}
          >
            {activity.entity_name}
          </Typography>
        )}
        {activity.entity_id && !activity.entity_name && (
          <Typography
            sx={{
              fontSize: '0.75rem',
              color: theme.palette.text.disabled,
              fontFamily: 'monospace',
              mb: 0.5,
            }}
          >
            {activity.entity_id.slice(0, 20)}...
          </Typography>
        )}
        <Typography
          sx={{
            fontSize: '12px',
            color: theme.palette.text.disabled,
          }}
        >
          {formatRelativeTime(activity.timestamp)}
        </Typography>
      </Box>
      {isNavigable && (
        <OpenInNewIcon
          sx={{
            fontSize: 14,
            color: theme.palette.text.disabled,
            opacity: 0,
            transition: 'opacity 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
            '.MuiBox-root:hover > &': { opacity: 1 },
          }}
        />
      )}
    </Box>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ActivityPage() {
  const theme = useTheme()
  const toast = useToast()
  const navigate = useNavigateInteraction()
  const { execute } = useInteraction()
  const didLoadRef = useRef(false)
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'activity', ...intent } }),
    [navigate]
  )

  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [entityTypeFilter, setEntityTypeFilter] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false)
  const [clearing, setClearing] = useState(false)

  const fetchActivities = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getActivityLog({
        limit: 100,
        entityType: entityTypeFilter || undefined,
        action: actionFilter || undefined,
      })
      setActivities(data?.activities || [])
    } catch (err) {
      toast.show(err.message || 'Failed to load activity log', 'error')
    } finally {
      setLoading(false)
    }
  }, [entityTypeFilter, actionFilter, toast])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchActivities()
  }, [fetchActivities])

  useEffect(() => {
    if (!didLoadRef.current) return
    fetchActivities()
  }, [entityTypeFilter, actionFilter, fetchActivities])

  const handleClearLog = useCallback(async () => {
    await execute({
      type: InteractionType.DELETE,
      label: 'Clear activity log',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        action: 'clear_activity_log',
      },
      action: async () => {
        setClearing(true)
        try {
          const result = await api.clearActivityLog()
          setActivities([])
          toast.show(`Cleared ${result.cleared} activity entries`, 'success')
          return result
        } catch (err) {
          toast.show(err.message || 'Failed to clear activity log', 'error')
          throw err
        } finally {
          setClearing(false)
          setClearConfirmOpen(false)
        }
      },
    })
  }, [toast, execute])

  return (
    <PageContainer>
      {/* Header */}
      <HeaderContainer direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography
            variant="h5"
            fontWeight={600}
            sx={{ color: theme.palette.text.primary }}
          >
            Activity Log
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Track actions and events in your workspace
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <RefreshButton
            onClick={fetchActivities}
            disabled={loading}
            data-testid="refresh-activity-button"
            aria-label="Refresh activities"
            sx={{ color: theme.palette.text.secondary }}
          >
            {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          </RefreshButton>
          <DeleteButton
            onClick={() => setClearConfirmOpen(true)}
            disabled={activities.length === 0}
            data-testid="clear-activity-button"
            aria-label="Clear all activities"
            sx={{ color: theme.palette.text.secondary }}
          >
            <DeleteIcon />
          </DeleteButton>
        </Stack>
      </HeaderContainer>

      {/* Filters */}
      <FilterContainer direction="row" spacing={2}>
        <StyledFormControl size="small">
          <InputLabel>Entity Type</InputLabel>
          <Select
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value)}
            label="Entity Type"
            data-testid="entity-type-filter"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="template">Template</MenuItem>
            <MenuItem value="connection">Connection</MenuItem>
            <MenuItem value="job">Job</MenuItem>
            <MenuItem value="schedule">Schedule</MenuItem>
          </Select>
        </StyledFormControl>
        <StyledFormControl size="small">
          <InputLabel>Action</InputLabel>
          <Select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            label="Action"
            data-testid="action-filter"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="favorite_added">Favorite added</MenuItem>
            <MenuItem value="favorite_removed">Favorite removed</MenuItem>
            <MenuItem value="template_deleted">Template deleted</MenuItem>
            <MenuItem value="job_cancelled">Job cancelled</MenuItem>
          </Select>
        </StyledFormControl>
      </FilterContainer>

      {/* Activity List */}
      <ActivityListContainer>
        {loading ? (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <CircularProgress size={32} />
          </Box>
        ) : activities.length === 0 ? (
          <EmptyStateContainer>
            <HistoryIcon
              sx={{
                fontSize: 48,
                color: theme.palette.text.disabled,
                mb: 2,
              }}
            />
            <Typography sx={{ fontSize: '0.875rem', color: theme.palette.text.secondary }}>
              No activity recorded yet
            </Typography>
            <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.disabled, mt: 0.5, mb: 2 }}>
              Actions like creating templates, running jobs, and more will appear here
            </Typography>
            <Button
              variant="contained"
              startIcon={<DashboardIcon />}
              onClick={() => handleNavigate('/', 'Go to Dashboard', { action: 'empty-state-cta' })}
              sx={{ textTransform: 'none' }}
            >
              Go to Dashboard
            </Button>
          </EmptyStateContainer>
        ) : (
          activities.map((activity) => (
            <ActivityItem
              key={activity.id}
              activity={activity}
              onNavigate={(route) =>
                handleNavigate(route, 'Open activity item', { route, activityId: activity.id })
              }
            />
          ))
        )}
      </ActivityListContainer>

      {/* Clear Confirmation */}
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

/**
 * Single activity item row
 */
import React from 'react'
import {
  Box,
  Typography,
  Stack,
  Chip,
  useTheme,
  alpha,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import StorageIcon from '@mui/icons-material/Storage'
import WorkIcon from '@mui/icons-material/Work'
import ScheduleIcon from '@mui/icons-material/Schedule'
import StarIcon from '@mui/icons-material/Star'
import SettingsIcon from '@mui/icons-material/Settings'
import HistoryIcon from '@mui/icons-material/History'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import { neutral } from '@/app/theme'
import { pulse } from '@/styles'

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

export default function ActivityItem({ activity, onNavigate }) {
  const theme = useTheme()
  const entityTypeRaw = activity.entity_type || 'default'
  const entityType = String(entityTypeRaw).toLowerCase().replace(/s$/, '')
  const action = activity.action || ''
  const actionKey = String(action).toLowerCase()
  const Icon = ACTION_ICONS[entityType] || ACTION_ICONS.default
  const actionConfig = getActionConfig(theme, action)
  const accentColor = actionConfig.color

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
        borderRadius: 1,
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
          borderRadius: 1,
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
          <Typography sx={{ fontSize: '14px', fontWeight: 500, color: theme.palette.text.primary }}>
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
          <Typography sx={{ fontSize: '14px', color: theme.palette.text.secondary, mb: 0.5 }}>
            {activity.entity_name}
          </Typography>
        )}
        {activity.entity_id && !activity.entity_name && (
          <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.disabled, fontFamily: 'monospace', mb: 0.5 }}>
            {activity.entity_id.slice(0, 20)}...
          </Typography>
        )}
        <Typography sx={{ fontSize: '12px', color: theme.palette.text.disabled }}>
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

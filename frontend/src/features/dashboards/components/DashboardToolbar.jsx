/**
 * Dashboard Builder Toolbar - actions for the active dashboard.
 */
import React from 'react'
import { Box, Typography, Chip, alpha } from '@mui/material'
import {
  Save as SaveIcon, Refresh as RefreshIcon, AutoAwesome as AIIcon,
  CameraAlt as SnapshotIcon, Code as EmbedIcon,
} from '@mui/icons-material'
import { ToolbarContainer, ActionButton } from './DashboardBuilderStyles'
import { neutral } from '@/app/theme'

export default function DashboardToolbar({
  currentDashboard, widgetCount, hasUnsavedChanges,
  saving, refreshing,
  onRefresh, onOpenAiMenu, onSnapshot, onEmbed, onSave,
}) {
  return (
    <ToolbarContainer>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {currentDashboard.name}
        </Typography>
        <Chip
          size="small"
          label={`${widgetCount} widgets`}
          sx={{ borderRadius: 1, height: 20, fontSize: '12px' }}
        />
        {hasUnsavedChanges && (
          <Chip
            size="small"
            label="Unsaved"
            sx={{ borderRadius: 1, height: 20, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <ActionButton size="small" startIcon={<RefreshIcon />} onClick={onRefresh} disabled={refreshing}>
          Refresh
        </ActionButton>
        <ActionButton size="small" startIcon={<AIIcon />} onClick={onOpenAiMenu}>
          AI Analytics
        </ActionButton>
        <ActionButton size="small" startIcon={<SnapshotIcon />} onClick={onSnapshot}>
          Snapshot
        </ActionButton>
        <ActionButton size="small" startIcon={<EmbedIcon />} onClick={onEmbed}>
          Embed
        </ActionButton>
        <ActionButton
          variant="contained" size="small" startIcon={<SaveIcon />}
          onClick={onSave} disabled={saving || !hasUnsavedChanges}
        >
          {saving ? 'Saving...' : 'Save'}
        </ActionButton>
      </Box>
    </ToolbarContainer>
  )
}

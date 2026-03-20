/**
 * Dashboard Builder Sidebar - dashboard list, widget palette, AI suggestions, insights.
 */
import React from 'react'
import {
  Box, Typography, IconButton, Tooltip, List, ListItemIcon, ListItemText,
  CircularProgress,
} from '@mui/material'
import { Add as AddIcon, Dashboard as DashboardIcon } from '@mui/icons-material'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { FeatureKey } from '@/utils/crossPageTypes'
import WidgetPalette from './WidgetPalette'
import AIWidgetSuggestion from './AIWidgetSuggestion'
import {
  Sidebar, SidebarSection, SidebarContent,
  DashboardListItem, InsightCard,
} from './DashboardBuilderStyles'

export default function DashboardSidebar({
  dashboards, currentDashboard, loading, insights,
  onOpenCreateDialog, onSelectDashboard,
  onAddWidgetFromPalette, onImportWidget, onAddAIWidgets,
}) {
  return (
    <Sidebar>
      <SidebarSection>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Dashboards
          </Typography>
          <Tooltip title="New Dashboard">
            <IconButton size="small" onClick={onOpenCreateDialog}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <Box sx={{ mt: 1 }}>
          {loading && dashboards.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress size={20} />
            </Box>
          ) : dashboards.length === 0 ? (
            <Typography variant="caption" color="text.secondary">
              No dashboards yet
            </Typography>
          ) : (
            <List disablePadding dense>
              {dashboards.slice(0, 5).map((db) => (
                <DashboardListItem
                  key={db.id}
                  active={currentDashboard?.id === db.id}
                  onClick={() => onSelectDashboard(db.id)}
                  dense
                >
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <DashboardIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={db.name}
                    primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                  />
                </DashboardListItem>
              ))}
            </List>
          )}
        </Box>
      </SidebarSection>

      {currentDashboard && (
        <SidebarContent>
          <ImportFromMenu
            currentFeature={FeatureKey.DASHBOARDS}
            onImport={onImportWidget}
            label="Import Widget"
          />
          <Box sx={{ mt: 1 }} />
          <WidgetPalette onAddWidget={onAddWidgetFromPalette} />

          <AIWidgetSuggestion
            onAddSingleWidget={(scenario, variant) => {
              onAddWidgetFromPalette(scenario, scenario, variant)
            }}
            onAddWidgets={onAddAIWidgets}
          />

          {insights.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                AI INSIGHTS
              </Typography>
              {insights.map((insight, idx) => (
                <InsightCard key={idx} elevation={0}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>
                    {insight.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {insight.description}
                  </Typography>
                </InsightCard>
              ))}
            </Box>
          )}
        </SidebarContent>
      )}
    </Sidebar>
  )
}

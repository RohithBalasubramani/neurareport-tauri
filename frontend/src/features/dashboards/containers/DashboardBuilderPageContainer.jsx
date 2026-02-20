/**
 * Dashboard Builder Page Container
 * Drag-and-drop dashboard builder with react-grid-layout and ECharts.
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Paper,
  List,
  ListItem,
  ListItemButton,
  CircularProgress,
  Select,
  FormControl,
  InputLabel,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Dashboard as DashboardIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon,
  Code as EmbedIcon,
  AutoAwesome as AIIcon,
  TrendingUp as TrendIcon,
  Warning as AnomalyIcon,
  CameraAlt as SnapshotIcon,
  Fullscreen as FullscreenIcon,
  Edit as EditIcon,
  ContentCopy as DuplicateIcon,
} from '@mui/icons-material'
import useDashboardStore from '@/stores/dashboardStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import DashboardGridLayout, { generateWidgetId, DEFAULT_WIDGET_SIZES } from '../components/DashboardGridLayout'
import ChartWidget, { CHART_TYPES } from '../components/ChartWidget'
import MetricWidget, { METRIC_FORMATS } from '../components/MetricWidget'
import WidgetPalette, { parseWidgetType } from '../components/WidgetPalette'
import WidgetRenderer, { isScenarioWidget } from '../components/WidgetRenderer'
import AIWidgetSuggestion from '../components/AIWidgetSuggestion'
import { DEFAULT_VARIANTS, SCENARIO_VARIANTS, VARIANT_CONFIG, getVariantDefaultSize } from '../constants/widgetVariants'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Sidebar = styled(Box)(({ theme }) => ({
  width: 300,
  display: 'flex',
  flexDirection: 'column',
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
}))

const SidebarSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const SidebarContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const MainContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}))

const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const Canvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(2),
  overflow: 'auto',
  backgroundColor: theme.palette.background.default,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
}))

const DashboardListItem = styled(ListItemButton, {
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

const EmptyCanvas = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: `2px dashed ${alpha(theme.palette.divider, 0.3)}`,
  borderRadius: 8,  // Figma spec: 8px
}))

const EmptyState = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}))

const InsightCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]}`,
}))

// =============================================================================
// SAMPLE DATA FOR WIDGETS
// =============================================================================

const SAMPLE_CHART_DATA = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    { label: 'Revenue', data: [12000, 19000, 15000, 25000, 22000, 30000] },
    { label: 'Expenses', data: [8000, 12000, 10000, 14000, 13000, 16000] },
  ],
}

const SAMPLE_SPARKLINE = [65, 70, 68, 75, 82, 78, 85, 90, 88, 95]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DashboardBuilderPage() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    dashboards,
    currentDashboard,
    widgets,
    insights,
    loading,
    saving,
    refreshing,
    error,
    fetchDashboards,
    createDashboard,
    getDashboard,
    updateDashboard,
    deleteDashboard,
    addWidget,
    updateWidget,
    deleteWidget,
    refreshDashboard,
    generateInsights,
    predictTrends,
    detectAnomalies,
    createSnapshot,
    generateEmbedToken,
    reset,
  } = useDashboardStore()

  const { connections, templates, activeConnectionId } = useSharedData()
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId)

  // Cross-page: accept diagrams/data from other features (Visualization, Query)
  useIncomingTransfer(FeatureKey.DASHBOARDS, {
    [TransferAction.ADD_TO]: async (payload) => {
      if (currentDashboard) {
        await addWidget(currentDashboard.id, {
          type: payload.data?.svg ? 'html' : 'chart',
          title: payload.title || 'Imported Widget',
          config: payload.data || {},
        })
      }
    },
  })

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newDashboardName, setNewDashboardName] = useState('')
  const [addWidgetDialogOpen, setAddWidgetDialogOpen] = useState(false)
  const [pendingWidgetType, setPendingWidgetType] = useState(null)
  const [widgetTitle, setWidgetTitle] = useState('')
  const [widgetChartType, setWidgetChartType] = useState('bar')
  const [aiMenuAnchor, setAiMenuAnchor] = useState(null)
  const [localLayout, setLocalLayout] = useState([])
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  useEffect(() => {
    fetchDashboards()
    return () => reset()
  }, [fetchDashboards, reset])

  // Sync layout from widgets
  useEffect(() => {
    if (widgets.length > 0) {
      const layout = widgets.map((w) => ({
        i: w.id,
        x: w.x ?? 0,
        y: w.y ?? 0,
        w: w.w ?? 4,
        h: w.h ?? 3,
        minW: w.minW ?? 2,
        minH: w.minH ?? 2,
      }))
      setLocalLayout(layout)
    } else {
      setLocalLayout([])
    }
  }, [widgets])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboards', ...intent },
      action,
    })
  }, [execute])

  const handleOpenCreateDialog = useCallback(() => {
    return executeUI('Open create dashboard', () => setCreateDialogOpen(true))
  }, [executeUI])

  const handleCloseCreateDialog = useCallback(() => {
    return executeUI('Close create dashboard', () => {
      setCreateDialogOpen(false)
      setNewDashboardName('')
    })
  }, [executeUI])

  const handleSelectDashboard = useCallback((dashboardId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Open dashboard',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId },
      action: async () => {
        await getDashboard(dashboardId)
        setHasUnsavedChanges(false)
      },
    })
  }, [execute, getDashboard])

  const handleCreateDashboard = useCallback(() => {
    if (!newDashboardName) return undefined
    return execute({
      type: InteractionType.CREATE,
      label: 'Create dashboard',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', name: newDashboardName },
      action: async () => {
        const dashboard = await createDashboard({
          name: newDashboardName,
          connectionId: selectedConnectionId || undefined,
          widgets: [],
          filters: [],
        })
        if (dashboard) {
          setCreateDialogOpen(false)
          setNewDashboardName('')
          toast.show('Dashboard created', 'success')
        }
        return dashboard
      },
    })
  }, [createDashboard, execute, newDashboardName, toast])

  const handleDeleteDashboard = useCallback((dashboardId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete dashboard',
      reversibility: Reversibility.REQUIRES_CONFIRMATION,
      intent: { source: 'dashboards', dashboardId },
      action: async () => {
        const success = await deleteDashboard(dashboardId)
        if (success) {
          toast.show('Dashboard deleted', 'success')
        }
        return success
      },
    })
  }, [deleteDashboard, execute, toast])

  const [pendingVariant, setPendingVariant] = useState(null)

  // Add widget from palette
  const handleAddWidgetFromPalette = useCallback((widgetType, label, variant) => {
    setPendingWidgetType(widgetType)
    setWidgetTitle(label || '')
    setPendingVariant(variant || DEFAULT_VARIANTS[widgetType] || null)
    const { category, subtype } = parseWidgetType(widgetType)
    if (category === 'chart') {
      setWidgetChartType(subtype)
    }
    setAddWidgetDialogOpen(true)
  }, [])

  const handleCloseAddWidgetDialog = useCallback(() => {
    return executeUI('Close add widget', () => {
      setAddWidgetDialogOpen(false)
      setPendingWidgetType(null)
      setPendingVariant(null)
      setWidgetTitle('')
    })
  }, [executeUI])

  const handleConfirmAddWidget = useCallback(() => {
    if (!currentDashboard || !pendingWidgetType || !widgetTitle) return undefined

    const { category, subtype } = parseWidgetType(pendingWidgetType)
    const isScenario = isScenarioWidget(pendingWidgetType)

    // Use variant-aware sizing for scenario widgets, legacy sizing otherwise
    let sizes
    if (isScenario && pendingVariant) {
      const vs = getVariantDefaultSize(pendingVariant, pendingWidgetType)
      sizes = { w: vs.w, h: vs.h, minW: 2, minH: 2 }
    } else {
      sizes = DEFAULT_WIDGET_SIZES[category] || { w: 4, h: 3, minW: 2, minH: 2 }
    }

    return execute({
      type: InteractionType.UPDATE,
      label: 'Add widget',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, widgetType: pendingWidgetType },
      action: async () => {
        const connectionId = selectedConnectionId || currentDashboard?.connectionId || undefined

        const widgetConfig = isScenario
          ? {
              type: pendingWidgetType,
              scenario: pendingWidgetType,
              variant: pendingVariant || DEFAULT_VARIANTS[pendingWidgetType],
              title: widgetTitle,
              data_source: connectionId,
            }
          : {
              type: category,
              subtype: subtype,
              chartType: category === 'chart' ? widgetChartType : undefined,
              title: widgetTitle,
              data: category === 'chart' ? SAMPLE_CHART_DATA : undefined,
              value: category === 'metric' ? 12500 : undefined,
              previousValue: category === 'metric' ? 10000 : undefined,
              sparklineData: category === 'metric' ? SAMPLE_SPARKLINE : undefined,
              format: category === 'metric' ? 'currency' : undefined,
              data_source: connectionId,
            }

        const widget = await addWidget(currentDashboard.id, {
          config: widgetConfig,
          x: 0,
          y: widgets.length * 4,
          ...sizes,
        })
        if (widget) {
          setAddWidgetDialogOpen(false)
          setPendingWidgetType(null)
          setPendingVariant(null)
          setWidgetTitle('')
          setHasUnsavedChanges(true)
          toast.show('Widget added', 'success')
        }
        return widget
      },
    })
  }, [addWidget, currentDashboard, execute, pendingWidgetType, pendingVariant, toast, widgetChartType, widgetTitle, widgets.length, selectedConnectionId])

  const handleDeleteWidget = useCallback((widgetId) => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.DELETE,
      label: 'Remove widget',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, widgetId },
      action: async () => {
        await deleteWidget(currentDashboard.id, widgetId)
        setHasUnsavedChanges(true)
        toast.show('Widget removed', 'success')
      },
    })
  }, [currentDashboard, deleteWidget, execute, toast])

  const handleLayoutChange = useCallback((layout) => {
    setLocalLayout(layout)
    setHasUnsavedChanges(true)
  }, [])

  const handleSave = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Save dashboard',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        // Update widget positions from layout
        const updatedWidgets = widgets.map((w) => {
          const layoutItem = localLayout.find((l) => l.i === w.id)
          if (layoutItem) {
            return { ...w, x: layoutItem.x, y: layoutItem.y, w: layoutItem.w, h: layoutItem.h }
          }
          return w
        })
        await updateDashboard(currentDashboard.id, { widgets: updatedWidgets })
        setHasUnsavedChanges(false)
        toast.show('Dashboard saved', 'success')
      },
    })
  }, [currentDashboard, execute, localLayout, toast, updateDashboard, widgets])

  const handleRefresh = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Refresh dashboard',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        await refreshDashboard(currentDashboard.id)
        toast.show('Dashboard refreshed', 'success')
      },
    })
  }, [currentDashboard, execute, refreshDashboard, toast])

  const handleOpenAiMenu = useCallback((event) => {
    const anchor = event.currentTarget
    return executeUI('Open AI analytics', () => setAiMenuAnchor(anchor))
  }, [executeUI])

  const handleCloseAiMenu = useCallback(() => {
    return executeUI('Close AI analytics', () => setAiMenuAnchor(null))
  }, [executeUI])

  const handleAIAction = useCallback((action) => {
    handleCloseAiMenu()
    if (!currentDashboard) return undefined

    const sampleData = [{ x: 1, y: 10 }, { x: 2, y: 20 }, { x: 3, y: 15 }, { x: 4, y: 25 }]
    const labelMap = {
      insights: 'Generate insights',
      trends: 'Predict trends',
      anomalies: 'Detect anomalies',
    }

    return execute({
      type: InteractionType.ANALYZE,
      label: labelMap[action] || 'Run AI analytics',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, action },
      action: async () => {
        switch (action) {
          case 'insights':
            await generateInsights(sampleData)
            toast.show('Insights generated', 'success')
            break
          case 'trends':
            await predictTrends(sampleData, 'x', 'y', 6)
            toast.show('Trends predicted', 'success')
            break
          case 'anomalies':
            await detectAnomalies(sampleData, ['y'])
            toast.show('Anomalies detected', 'success')
            break
        }
      },
    })
  }, [currentDashboard, detectAnomalies, execute, generateInsights, handleCloseAiMenu, predictTrends, toast])

  const handleSnapshot = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.DOWNLOAD,
      label: 'Create snapshot',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        const result = await createSnapshot(currentDashboard.id, 'png')
        if (result) {
          toast.show('Snapshot created', 'success')
        }
        return result
      },
    })
  }, [createSnapshot, currentDashboard, execute, toast])

  const handleEmbed = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Generate embed link',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        const result = await generateEmbedToken(currentDashboard.id)
        if (result) {
          navigator.clipboard.writeText(result.embed_url)
          toast.show('Embed URL copied to clipboard', 'success')
        }
        return result
      },
    })
  }, [currentDashboard, execute, generateEmbedToken, toast])

  const handleDismissError = useCallback(() => {
    return executeUI('Dismiss dashboard error', () => reset())
  }, [executeUI, reset])

  // Render widget by type
  const renderWidget = useCallback((widget) => {
    const widgetType = widget.config?.type || 'chart'

    // Scenario-based intelligent widgets
    if (isScenarioWidget(widgetType)) {
      return (
        <WidgetRenderer
          key={widget.id}
          scenario={widget.config?.scenario || widgetType}
          variant={widget.config?.variant}
          data={widget.config?.data || widget.data}
          config={widget.config}
          connectionId={widget.config?.data_source || selectedConnectionId || currentDashboard?.connectionId}
          id={widget.id}
          editable
          onDelete={handleDeleteWidget}
        />
      )
    }

    const { category } = parseWidgetType(widgetType)

    if (category === 'chart' || widget.config?.type === 'chart') {
      return (
        <ChartWidget
          key={widget.id}
          id={widget.id}
          title={widget.config?.title}
          chartType={widget.config?.chartType || widget.config?.subtype || 'bar'}
          data={widget.config?.data || SAMPLE_CHART_DATA}
          onDelete={handleDeleteWidget}
          onRefresh={() => {}}
          editable
        />
      )
    }

    if (category === 'metric' || widget.config?.type === 'metric') {
      return (
        <MetricWidget
          key={widget.id}
          id={widget.id}
          title={widget.config?.title}
          value={widget.config?.value || 0}
          previousValue={widget.config?.previousValue}
          format={widget.config?.format || 'number'}
          sparklineData={widget.config?.sparklineData || []}
          onDelete={handleDeleteWidget}
          editable
        />
      )
    }

    // Default placeholder for other widget types
    return (
      <Paper
        key={widget.id}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          p: 2,
          borderRadius: 1,  // Figma spec: 8px
        }}
        variant="outlined"
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {widget.config?.title || 'Widget'}
        </Typography>
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'text.secondary',
          }}
        >
          <Typography variant="caption">
            {widget.config?.type} widget coming soon
          </Typography>
        </Box>
      </Paper>
    )
  }, [handleDeleteWidget])

  return (
    <PageContainer>
      {/* Sidebar */}
      <Sidebar>
        <SidebarSection>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Dashboards
            </Typography>
            <Tooltip title="New Dashboard">
              <IconButton size="small" onClick={handleOpenCreateDialog}>
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
                    onClick={() => handleSelectDashboard(db.id)}
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
              onImport={async (output) => {
                if (currentDashboard) {
                  await addWidget(currentDashboard.id, {
                    type: output.data?.svg ? 'html' : 'chart',
                    title: output.title || 'Imported Widget',
                    config: output.data || {},
                  })
                  toast.show(`Added "${output.title}" as widget`, 'success')
                }
              }}
              label="Import Widget"
            />
            <Box sx={{ mt: 1 }} />
            <WidgetPalette onAddWidget={handleAddWidgetFromPalette} />

            <AIWidgetSuggestion
              onAddSingleWidget={(scenario, variant) => {
                handleAddWidgetFromPalette(scenario, scenario, variant)
              }}
              onAddWidgets={(widgets, layout) => {
                if (!currentDashboard) return
                const cells = layout?.cells || []
                widgets.forEach((w, i) => {
                  const cell = cells[i]
                  addWidget(currentDashboard.id, {
                    config: {
                      type: w.scenario,
                      title: w.question || w.scenario,
                      variant: w.variant,
                      scenario: w.scenario,
                    },
                    x: cell ? cell.col_start - 1 : 0,
                    y: cell ? cell.row_start - 1 : i * 3,
                    w: cell ? cell.col_end - cell.col_start : 4,
                    h: cell ? cell.row_end - cell.row_start : 3,
                  })
                })
                toast.show(`Added ${widgets.length} AI-suggested widgets`, 'success')
              }}
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

      {/* Main Content */}
      <MainContent>
        {currentDashboard ? (
          <>
            {/* Toolbar */}
            <Toolbar>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {currentDashboard.name}
                </Typography>
                <Chip
                  size="small"
                  label={`${widgets.length} widgets`}
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
                <ActionButton
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={handleRefresh}
                  disabled={refreshing}
                >
                  Refresh
                </ActionButton>
                <ActionButton
                  size="small"
                  startIcon={<AIIcon />}
                  onClick={handleOpenAiMenu}
                >
                  AI Analytics
                </ActionButton>
                <ActionButton
                  size="small"
                  startIcon={<SnapshotIcon />}
                  onClick={handleSnapshot}
                >
                  Snapshot
                </ActionButton>
                <ActionButton
                  size="small"
                  startIcon={<EmbedIcon />}
                  onClick={handleEmbed}
                >
                  Embed
                </ActionButton>
                <ActionButton
                  variant="contained"
                  size="small"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={saving || !hasUnsavedChanges}
                >
                  {saving ? 'Saving...' : 'Save'}
                </ActionButton>
              </Box>
            </Toolbar>

            {/* Canvas */}
            <Canvas>
              {widgets.length > 0 ? (
                <DashboardGridLayout
                  widgets={widgets}
                  layout={localLayout}
                  onLayoutChange={handleLayoutChange}
                  editable
                >
                  {widgets.map((widget) => (
                    <div key={widget.id}>
                      {renderWidget(widget)}
                    </div>
                  ))}
                </DashboardGridLayout>
              ) : (
                <EmptyCanvas>
                  <Typography color="text.secondary">
                    Add widgets from the palette to build your dashboard
                  </Typography>
                </EmptyCanvas>
              )}
            </Canvas>
          </>
        ) : (
          <EmptyState>
            <DashboardIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              No Dashboard Selected
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Create a new dashboard or select one from the sidebar.
            </Typography>
            <ActionButton
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
            >
              Create Dashboard
            </ActionButton>
          </EmptyState>
        )}
      </MainContent>

      {/* AI Menu */}
      <Menu
        anchorEl={aiMenuAnchor}
        open={Boolean(aiMenuAnchor)}
        onClose={handleCloseAiMenu}
      >
        <MenuItem onClick={() => handleAIAction('insights')}>
          <ListItemIcon><AIIcon /></ListItemIcon>
          <ListItemText>Generate Insights</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('trends')}>
          <ListItemIcon><TrendIcon /></ListItemIcon>
          <ListItemText>Predict Trends</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('anomalies')}>
          <ListItemIcon><AnomalyIcon /></ListItemIcon>
          <ListItemText>Detect Anomalies</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create Dashboard Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={handleCloseCreateDialog}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Create New Dashboard</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Dashboard Name"
            value={newDashboardName}
            onChange={(e) => setNewDashboardName(e.target.value)}
            sx={{ mt: 2 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newDashboardName) {
                handleCreateDashboard()
              }
            }}
          />
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={setSelectedConnectionId}
            label="Data Source (optional)"
            showStatus
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateDashboard}
            disabled={!newDashboardName || loading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Widget Dialog */}
      <Dialog
        open={addWidgetDialogOpen}
        onClose={handleCloseAddWidgetDialog}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Add Widget</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Widget Title"
            value={widgetTitle}
            onChange={(e) => setWidgetTitle(e.target.value)}
            sx={{ mt: 2 }}
          />
          {pendingWidgetType?.startsWith('chart') && (
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Chart Type</InputLabel>
              <Select
                value={widgetChartType}
                label="Chart Type"
                onChange={(e) => setWidgetChartType(e.target.value)}
              >
                {CHART_TYPES.map((ct) => (
                  <MenuItem key={ct.type} value={ct.type}>
                    {ct.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
          {isScenarioWidget(pendingWidgetType) && SCENARIO_VARIANTS[pendingWidgetType]?.length > 1 && (
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Variant</InputLabel>
              <Select
                value={pendingVariant || DEFAULT_VARIANTS[pendingWidgetType] || ''}
                label="Variant"
                onChange={(e) => setPendingVariant(e.target.value)}
              >
                {(SCENARIO_VARIANTS[pendingWidgetType] || []).map((v) => {
                  const vc = VARIANT_CONFIG[v]
                  return (
                    <MenuItem key={v} value={v}>
                      {vc?.label || v}
                    </MenuItem>
                  )
                })}
              </Select>
            </FormControl>
          )}
          {!currentDashboard?.connectionId && (
            <ConnectionSelector
              value={selectedConnectionId}
              onChange={setSelectedConnectionId}
              label="Widget Data Source"
              showStatus
              sx={{ mt: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddWidgetDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleConfirmAddWidget}
            disabled={!widgetTitle}
          >
            Add Widget
          </Button>
        </DialogActions>
      </Dialog>

      {error && (
        <Alert
          severity="error"
          onClose={handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}

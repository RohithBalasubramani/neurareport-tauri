/**
 * Custom hook: all state, effects, and handlers for Dashboard Builder.
 */
import { useState, useEffect, useCallback } from 'react'
import useDashboardStore from '@/stores/dashboardStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { parseWidgetType } from '../components/WidgetPalette'
import { isScenarioWidget } from '../components/WidgetRenderer'
import { DEFAULT_WIDGET_SIZES } from '../components/DashboardGridLayout'
import { DEFAULT_VARIANTS, VARIANT_CONFIG, SCENARIO_VARIANTS, getVariantDefaultSize } from '../constants/widgetVariants'
import { SAMPLE_CHART_DATA, SAMPLE_SPARKLINE } from '../components/DashboardBuilderStyles'

export function useDashboardBuilder() {
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    dashboards, currentDashboard, widgets, insights,
    loading, saving, refreshing, error,
    fetchDashboards, createDashboard, getDashboard, updateDashboard, deleteDashboard,
    addWidget, updateWidget, deleteWidget,
    refreshDashboard, generateInsights, predictTrends, detectAnomalies,
    createSnapshot, generateEmbedToken, reset,
  } = useDashboardStore()

  const { connections, templates, activeConnectionId } = useSharedData()
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId)

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
  const [pendingVariant, setPendingVariant] = useState(null)

  useEffect(() => {
    fetchDashboards()
    return () => reset()
  }, [fetchDashboards, reset])

  useEffect(() => {
    if (widgets.length > 0) {
      const layout = widgets.map((w) => ({
        i: w.id, x: w.x ?? 0, y: w.y ?? 0, w: w.w ?? 4, h: w.h ?? 3,
        minW: w.minW ?? 2, minH: w.minH ?? 2,
      }))
      setLocalLayout(layout)
    } else {
      setLocalLayout([])
    }
  }, [widgets])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE, label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true, suppressErrorToast: true,
      intent: { source: 'dashboards', ...intent }, action,
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
      type: InteractionType.EXECUTE, label: 'Open dashboard',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true, suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId },
      action: async () => { await getDashboard(dashboardId); setHasUnsavedChanges(false) },
    })
  }, [execute, getDashboard])

  const handleCreateDashboard = useCallback(() => {
    if (!newDashboardName) return undefined
    return execute({
      type: InteractionType.CREATE, label: 'Create dashboard',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', name: newDashboardName },
      action: async () => {
        const dashboard = await createDashboard({
          name: newDashboardName, connectionId: selectedConnectionId || undefined,
          widgets: [], filters: [],
        })
        if (dashboard) {
          setCreateDialogOpen(false); setNewDashboardName('')
          toast.show('Dashboard created', 'success')
        }
        return dashboard
      },
    })
  }, [createDashboard, execute, newDashboardName, selectedConnectionId, toast])

  const handleDeleteDashboard = useCallback((dashboardId) => {
    return execute({
      type: InteractionType.DELETE, label: 'Delete dashboard',
      reversibility: Reversibility.REQUIRES_CONFIRMATION,
      intent: { source: 'dashboards', dashboardId },
      action: async () => {
        const success = await deleteDashboard(dashboardId)
        if (success) toast.show('Dashboard deleted', 'success')
        return success
      },
    })
  }, [deleteDashboard, execute, toast])

  const handleAddWidgetFromPalette = useCallback((widgetType, label, variant) => {
    setPendingWidgetType(widgetType)
    setWidgetTitle(label || '')
    setPendingVariant(variant || DEFAULT_VARIANTS[widgetType] || null)
    const { category, subtype } = parseWidgetType(widgetType)
    if (category === 'chart') setWidgetChartType(subtype)
    setAddWidgetDialogOpen(true)
  }, [])

  const handleCloseAddWidgetDialog = useCallback(() => {
    return executeUI('Close add widget', () => {
      setAddWidgetDialogOpen(false); setPendingWidgetType(null)
      setPendingVariant(null); setWidgetTitle('')
    })
  }, [executeUI])

  const handleConfirmAddWidget = useCallback(() => {
    if (!currentDashboard || !pendingWidgetType || !widgetTitle) return undefined
    const { category, subtype } = parseWidgetType(pendingWidgetType)
    const isScenario = isScenarioWidget(pendingWidgetType)
    let sizes
    if (isScenario && pendingVariant) {
      const vs = getVariantDefaultSize(pendingVariant, pendingWidgetType)
      sizes = { w: vs.w, h: vs.h, minW: 2, minH: 2 }
    } else {
      sizes = DEFAULT_WIDGET_SIZES[category] || { w: 4, h: 3, minW: 2, minH: 2 }
    }
    return execute({
      type: InteractionType.UPDATE, label: 'Add widget',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, widgetType: pendingWidgetType },
      action: async () => {
        const connectionId = selectedConnectionId || currentDashboard?.connectionId || undefined
        const widgetConfig = isScenario
          ? { type: pendingWidgetType, scenario: pendingWidgetType,
              variant: pendingVariant || DEFAULT_VARIANTS[pendingWidgetType],
              title: widgetTitle, data_source: connectionId }
          : { type: category, subtype, chartType: category === 'chart' ? widgetChartType : undefined,
              title: widgetTitle, data: category === 'chart' ? SAMPLE_CHART_DATA : undefined,
              value: category === 'metric' ? 12500 : undefined,
              previousValue: category === 'metric' ? 10000 : undefined,
              sparklineData: category === 'metric' ? SAMPLE_SPARKLINE : undefined,
              format: category === 'metric' ? 'currency' : undefined, data_source: connectionId }
        const widget = await addWidget(currentDashboard.id, {
          config: widgetConfig, x: 0, y: widgets.length * 4, ...sizes,
        })
        if (widget) {
          setAddWidgetDialogOpen(false); setPendingWidgetType(null)
          setPendingVariant(null); setWidgetTitle('')
          setHasUnsavedChanges(true); toast.show('Widget added', 'success')
        }
        return widget
      },
    })
  }, [addWidget, currentDashboard, execute, pendingWidgetType, pendingVariant, toast, widgetChartType, widgetTitle, widgets.length, selectedConnectionId])

  const handleDeleteWidget = useCallback((widgetId) => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.DELETE, label: 'Remove widget',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, widgetId },
      action: async () => {
        await deleteWidget(currentDashboard.id, widgetId)
        setHasUnsavedChanges(true); toast.show('Widget removed', 'success')
      },
    })
  }, [currentDashboard, deleteWidget, execute, toast])

  const handleLayoutChange = useCallback((layout) => {
    setLocalLayout(layout); setHasUnsavedChanges(true)
  }, [])

  const handleSave = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.UPDATE, label: 'Save dashboard',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        const updatedWidgets = widgets.map((w) => {
          const layoutItem = localLayout.find((l) => l.i === w.id)
          if (layoutItem) return { ...w, x: layoutItem.x, y: layoutItem.y, w: layoutItem.w, h: layoutItem.h }
          return w
        })
        await updateDashboard(currentDashboard.id, { widgets: updatedWidgets })
        setHasUnsavedChanges(false); toast.show('Dashboard saved', 'success')
      },
    })
  }, [currentDashboard, execute, localLayout, toast, updateDashboard, widgets])

  const handleRefresh = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.EXECUTE, label: 'Refresh dashboard',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true, suppressErrorToast: true,
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
    const labelMap = { insights: 'Generate insights', trends: 'Predict trends', anomalies: 'Detect anomalies' }
    return execute({
      type: InteractionType.ANALYZE, label: labelMap[action] || 'Run AI analytics',
      reversibility: Reversibility.FULLY_REVERSIBLE, blocksNavigation: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id, action },
      action: async () => {
        switch (action) {
          case 'insights': await generateInsights(sampleData); toast.show('Insights generated', 'success'); break
          case 'trends': await predictTrends(sampleData, 'x', 'y', 6); toast.show('Trends predicted', 'success'); break
          case 'anomalies': await detectAnomalies(sampleData, ['y']); toast.show('Anomalies detected', 'success'); break
        }
      },
    })
  }, [currentDashboard, detectAnomalies, execute, generateInsights, handleCloseAiMenu, predictTrends, toast])

  const handleSnapshot = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.DOWNLOAD, label: 'Create snapshot',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true, suppressErrorToast: true,
      intent: { source: 'dashboards', dashboardId: currentDashboard.id },
      action: async () => {
        const result = await createSnapshot(currentDashboard.id, 'png')
        if (result) toast.show('Snapshot created', 'success')
        return result
      },
    })
  }, [createSnapshot, currentDashboard, execute, toast])

  const handleEmbed = useCallback(() => {
    if (!currentDashboard) return undefined
    return execute({
      type: InteractionType.EXECUTE, label: 'Generate embed link',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true, suppressErrorToast: true,
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

  const handleImportWidget = useCallback(async (output) => {
    if (currentDashboard) {
      await addWidget(currentDashboard.id, {
        type: output.data?.svg ? 'html' : 'chart',
        title: output.title || 'Imported Widget',
        config: output.data || {},
      })
      toast.show(`Added "${output.title}" as widget`, 'success')
    }
  }, [addWidget, currentDashboard, toast])

  const handleAddAIWidgets = useCallback((aiWidgets, layout) => {
    if (!currentDashboard) return
    const cells = layout?.cells || []
    aiWidgets.forEach((w, i) => {
      const cell = cells[i]
      addWidget(currentDashboard.id, {
        config: {
          type: w.scenario, title: w.question || w.scenario,
          variant: w.variant, scenario: w.scenario,
        },
        x: cell ? cell.col_start - 1 : 0,
        y: cell ? cell.row_start - 1 : i * 3,
        w: cell ? cell.col_end - cell.col_start : 4,
        h: cell ? cell.row_end - cell.row_start : 3,
      })
    })
    toast.show(`Added ${aiWidgets.length} AI-suggested widgets`, 'success')
  }, [addWidget, currentDashboard, toast])

  return {
    // Store state
    dashboards, currentDashboard, widgets, insights,
    loading, saving, refreshing, error,
    // Local state
    createDialogOpen, newDashboardName, setNewDashboardName,
    addWidgetDialogOpen, pendingWidgetType, widgetTitle, setWidgetTitle,
    widgetChartType, setWidgetChartType, pendingVariant, setPendingVariant,
    aiMenuAnchor, localLayout, hasUnsavedChanges,
    selectedConnectionId, setSelectedConnectionId,
    // Handlers
    handleOpenCreateDialog, handleCloseCreateDialog,
    handleSelectDashboard, handleCreateDashboard, handleDeleteDashboard,
    handleAddWidgetFromPalette, handleCloseAddWidgetDialog, handleConfirmAddWidget,
    handleDeleteWidget, handleLayoutChange, handleSave, handleRefresh,
    handleOpenAiMenu, handleCloseAiMenu, handleAIAction,
    handleSnapshot, handleEmbed, handleDismissError,
    handleImportWidget, handleAddAIWidgets,
    // Store actions (for sidebar import)
    addWidget,
  }
}

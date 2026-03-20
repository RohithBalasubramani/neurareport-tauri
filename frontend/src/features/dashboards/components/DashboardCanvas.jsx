/**
 * Dashboard Canvas - grid layout with widget rendering.
 */
import React, { useCallback } from 'react'
import { Box, Typography, Paper } from '@mui/material'
import DashboardGridLayout from './DashboardGridLayout'
import ChartWidget from './ChartWidget'
import MetricWidget from './MetricWidget'
import WidgetRenderer, { isScenarioWidget } from './WidgetRenderer'
import { parseWidgetType } from './WidgetPalette'
import { Canvas, EmptyCanvas, SAMPLE_CHART_DATA } from './DashboardBuilderStyles'

export default function DashboardCanvas({
  widgets, localLayout, onLayoutChange, onDeleteWidget,
  selectedConnectionId, currentDashboard,
}) {
  const renderWidget = useCallback((widget) => {
    const widgetType = widget.config?.type || 'chart'

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
          onDelete={onDeleteWidget}
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
          onDelete={onDeleteWidget}
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
          onDelete={onDeleteWidget}
          editable
        />
      )
    }

    return (
      <Paper
        key={widget.id}
        sx={{
          height: '100%', display: 'flex', flexDirection: 'column',
          p: 2, borderRadius: 1,
        }}
        variant="outlined"
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {widget.config?.title || 'Widget'}
        </Typography>
        <Box
          sx={{
            flex: 1, display: 'flex', alignItems: 'center',
            justifyContent: 'center', color: 'text.secondary',
          }}
        >
          <Typography variant="caption">
            {widget.config?.type} widget coming soon
          </Typography>
        </Box>
      </Paper>
    )
  }, [onDeleteWidget, selectedConnectionId, currentDashboard?.connectionId])

  return (
    <Canvas>
      {widgets.length > 0 ? (
        <DashboardGridLayout
          widgets={widgets}
          layout={localLayout}
          onLayoutChange={onLayoutChange}
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
  )
}

/**
 * Add Widget Dialog - configure widget type, title, variant before adding.
 */
import React from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, FormControl, InputLabel, Select, MenuItem,
} from '@mui/material'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { CHART_TYPES } from './ChartWidget'
import { isScenarioWidget } from './WidgetRenderer'
import { SCENARIO_VARIANTS, DEFAULT_VARIANTS, VARIANT_CONFIG } from '../constants/widgetVariants'

export default function AddWidgetDialog({
  open, onClose,
  pendingWidgetType, widgetTitle, onTitleChange,
  widgetChartType, onChartTypeChange,
  pendingVariant, onVariantChange,
  selectedConnectionId, onConnectionChange,
  currentDashboard, onConfirm,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Add Widget</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Widget Title"
          value={widgetTitle}
          onChange={(e) => onTitleChange(e.target.value)}
          sx={{ mt: 2 }}
        />
        {pendingWidgetType?.startsWith('chart') && (
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Chart Type</InputLabel>
            <Select
              value={widgetChartType}
              label="Chart Type"
              onChange={(e) => onChartTypeChange(e.target.value)}
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
              onChange={(e) => onVariantChange(e.target.value)}
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
            onChange={onConnectionChange}
            label="Widget Data Source"
            showStatus
            sx={{ mt: 2 }}
          />
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onConfirm} disabled={!widgetTitle}>
          Add Widget
        </Button>
      </DialogActions>
    </Dialog>
  )
}

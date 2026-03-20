/**
 * Hook for managing PivotTableBuilder state and actions.
 */
import { useState, useCallback, useMemo } from 'react'

export const AGGREGATIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'average', label: 'Average' },
  { value: 'min', label: 'Min' },
  { value: 'max', label: 'Max' },
  { value: 'countDistinct', label: 'Count Distinct' },
  { value: 'product', label: 'Product' },
  { value: 'stdev', label: 'Std Dev' },
  { value: 'variance', label: 'Variance' },
]

export const SORT_OPTIONS = [
  { value: 'none', label: 'No Sort' },
  { value: 'asc', label: 'A to Z' },
  { value: 'desc', label: 'Z to A' },
  { value: 'value_asc', label: 'Value (Low to High)' },
  { value: 'value_desc', label: 'Value (High to Low)' },
]

export function usePivotTableBuilder({ config, onConfigChange }) {
  const [draggedField, setDraggedField] = useState(null)
  const [dragOverZone, setDragOverZone] = useState(null)
  const [settingsDialog, setSettingsDialog] = useState({ open: false, field: null, zone: null })
  const [expandedZones, setExpandedZones] = useState(['rows', 'columns', 'values', 'filters'])

  const toggleZone = useCallback((zone) => {
    setExpandedZones((prev) =>
      prev.includes(zone) ? prev.filter((z) => z !== zone) : [...prev, zone]
    )
  }, [])

  const handleDragStart = useCallback((field, sourceZone = null) => {
    setDraggedField({ ...field, sourceZone })
  }, [])

  const handleDragOver = useCallback((e, zone) => {
    e.preventDefault()
    setDragOverZone(zone)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOverZone(null)
  }, [])

  const handleDrop = useCallback((e, targetZone) => {
    e.preventDefault()
    setDragOverZone(null)

    if (!draggedField) return

    const newConfig = { ...config }

    if (draggedField.sourceZone) {
      newConfig[draggedField.sourceZone] = newConfig[draggedField.sourceZone].filter(
        (f) => f.name !== draggedField.name
      )
    }

    const fieldToAdd = {
      name: draggedField.name,
      type: draggedField.type,
      aggregation: targetZone === 'values' ? 'sum' : undefined,
    }

    const existsInTarget = newConfig[targetZone].some((f) => f.name === draggedField.name)
    if (!existsInTarget) {
      newConfig[targetZone] = [...newConfig[targetZone], fieldToAdd]
    }

    onConfigChange?.(newConfig)
    setDraggedField(null)
  }, [draggedField, config, onConfigChange])

  const handleRemoveField = useCallback((zone, fieldName) => {
    const newConfig = { ...config }
    newConfig[zone] = newConfig[zone].filter((f) => f.name !== fieldName)
    onConfigChange?.(newConfig)
  }, [config, onConfigChange])

  const handleOpenSettings = useCallback((field, zone) => {
    setSettingsDialog({ open: true, field, zone })
  }, [])

  const handleSaveSettings = useCallback((updatedField) => {
    const { zone } = settingsDialog
    const newConfig = { ...config }
    newConfig[zone] = newConfig[zone].map((f) =>
      f.name === updatedField.name ? updatedField : f
    )
    onConfigChange?.(newConfig)
    setSettingsDialog({ open: false, field: null, zone: null })
  }, [settingsDialog, config, onConfigChange])

  const previewData = useMemo(() => {
    if (config.rows.length === 0 && config.columns.length === 0) return []
    return [
      { rowLabel: 'Category A', col1: 1234, col2: 5678, total: 6912 },
      { rowLabel: 'Category B', col1: 2345, col2: 6789, total: 9134 },
      { rowLabel: 'Category C', col1: 3456, col2: 7890, total: 11346 },
      { rowLabel: 'Grand Total', col1: 7035, col2: 20357, total: 27392 },
    ]
  }, [config])

  return {
    dragOverZone,
    settingsDialog,
    expandedZones,
    previewData,
    setSettingsDialog,
    toggleZone,
    handleDragStart,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleRemoveField,
    handleOpenSettings,
    handleSaveSettings,
  }
}

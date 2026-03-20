/**
 * Hook for managing data validation state and actions.
 */
import { useState, useCallback } from 'react'

// Validation types and conditions (shared constants)
export const VALIDATION_TYPES = [
  { value: 'any', label: 'Any Value', icon: 'InfoIcon' },
  { value: 'whole_number', label: 'Whole Number', icon: 'NumberIcon' },
  { value: 'decimal', label: 'Decimal', icon: 'NumberIcon' },
  { value: 'list', label: 'List', icon: 'ListIcon' },
  { value: 'date', label: 'Date', icon: 'DateIcon' },
  { value: 'time', label: 'Time', icon: 'DateIcon' },
  { value: 'text_length', label: 'Text Length', icon: 'TextIcon' },
  { value: 'custom', label: 'Custom Formula', icon: 'FormulaIcon' },
]

export const NUMBER_CONDITIONS = [
  { value: 'between', label: 'between' },
  { value: 'not_between', label: 'not between' },
  { value: 'equal', label: 'equal to' },
  { value: 'not_equal', label: 'not equal to' },
  { value: 'greater', label: 'greater than' },
  { value: 'less', label: 'less than' },
  { value: 'greater_equal', label: 'greater than or equal to' },
  { value: 'less_equal', label: 'less than or equal to' },
]

export const DATE_CONDITIONS = [
  { value: 'between', label: 'between' },
  { value: 'not_between', label: 'not between' },
  { value: 'equal', label: 'equal to' },
  { value: 'before', label: 'before' },
  { value: 'after', label: 'after' },
]

export const ERROR_STYLES = [
  { value: 'stop', label: 'Stop', icon: 'ErrorIcon', color: 'error' },
  { value: 'warning', label: 'Warning', icon: 'WarningIcon', color: 'warning' },
  { value: 'info', label: 'Information', icon: 'InfoIcon', color: 'info' },
]

export function getValidationDescription(validation) {
  const type = VALIDATION_TYPES.find((t) => t.value === validation.type)
  if (validation.type === 'any') return 'Any value allowed'
  if (validation.type === 'list') {
    const count = validation.listValues?.length || 0
    return `List: ${count} items`
  }
  if (validation.type === 'custom') return 'Custom formula'

  const conditions = ['date', 'time'].includes(validation.type) ? DATE_CONDITIONS : NUMBER_CONDITIONS
  const cond = conditions.find((c) => c.value === validation.condition)

  if (['between', 'not_between'].includes(validation.condition)) {
    return `${type?.label} ${cond?.label} ${validation.value1} and ${validation.value2}`
  }
  return `${type?.label} ${cond?.label} ${validation.value1}`
}

export function useDataValidation({ validations, onValidationsChange }) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingValidation, setEditingValidation] = useState(null)

  const handleAddValidation = useCallback(() => {
    setEditingValidation(null)
    setDialogOpen(true)
  }, [])

  const handleEditValidation = useCallback((validation) => {
    setEditingValidation(validation)
    setDialogOpen(true)
  }, [])

  const handleSaveValidation = useCallback((validation) => {
    if (validation.id) {
      onValidationsChange?.(validations.map((v) => (v.id === validation.id ? validation : v)))
    } else {
      onValidationsChange?.([...validations, { ...validation, id: `validation_${Date.now()}` }])
    }
    setDialogOpen(false)
  }, [validations, onValidationsChange])

  const handleDeleteValidation = useCallback((validationId) => {
    onValidationsChange?.(validations.filter((v) => v.id !== validationId))
  }, [validations, onValidationsChange])

  return {
    dialogOpen,
    editingValidation,
    setDialogOpen,
    handleAddValidation,
    handleEditValidation,
    handleSaveValidation,
    handleDeleteValidation,
  }
}

import { useState, useCallback, useMemo } from 'react'

/**
 * Custom hook for FormBuilder state and field operations.
 */
export function useFormBuilder({ fields, onFieldsChange }) {
  const [selectedFieldId, setSelectedFieldId] = useState(null)
  const [expandedCategories, setExpandedCategories] = useState(['basic', 'choice'])
  const [previewOpen, setPreviewOpen] = useState(false)

  const selectedField = useMemo(
    () => fields.find((f) => f.id === selectedFieldId),
    [fields, selectedFieldId]
  )

  const toggleCategory = useCallback((categoryId) => {
    setExpandedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((c) => c !== categoryId)
        : [...prev, categoryId]
    )
  }, [])

  const handleAddField = useCallback((fieldType) => {
    const newField = {
      id: `field_${Date.now()}`,
      type: fieldType.type,
      label: `New ${fieldType.label}`,
      name: `field_${Date.now()}`,
      required: false,
      options: ['radio', 'select', 'multiselect'].includes(fieldType.type)
        ? ['Option 1', 'Option 2']
        : undefined,
    }
    onFieldsChange?.([...fields, newField])
    setSelectedFieldId(newField.id)
  }, [fields, onFieldsChange])

  const handleUpdateField = useCallback((updatedField) => {
    onFieldsChange?.(
      fields.map((f) => (f.id === updatedField.id ? updatedField : f))
    )
  }, [fields, onFieldsChange])

  const handleDeleteField = useCallback((fieldId) => {
    onFieldsChange?.(fields.filter((f) => f.id !== fieldId))
    if (selectedFieldId === fieldId) {
      setSelectedFieldId(null)
    }
  }, [fields, onFieldsChange, selectedFieldId])

  const handleDuplicateField = useCallback((fieldId) => {
    const field = fields.find((f) => f.id === fieldId)
    if (field) {
      const newField = {
        ...field,
        id: `field_${Date.now()}`,
        name: `${field.name}_copy`,
        label: `${field.label} (Copy)`,
      }
      const index = fields.findIndex((f) => f.id === fieldId)
      const newFields = [...fields]
      newFields.splice(index + 1, 0, newField)
      onFieldsChange?.(newFields)
      setSelectedFieldId(newField.id)
    }
  }, [fields, onFieldsChange])

  return {
    selectedFieldId,
    setSelectedFieldId,
    selectedField,
    expandedCategories,
    toggleCategory,
    previewOpen,
    setPreviewOpen,
    handleAddField,
    handleUpdateField,
    handleDeleteField,
    handleDuplicateField,
  }
}

import { useState, useCallback, useEffect, useRef } from 'react'
import { FORMULA_FUNCTIONS } from '../components/formulaFunctions'

export function useFormulaBar({ value = '', formula = null, onChange, onApply, onCancel }) {
  const inputRef = useRef(null)
  const [localValue, setLocalValue] = useState(value)
  const [isEditing, setIsEditing] = useState(false)
  const [functionMenuAnchor, setFunctionMenuAnchor] = useState(null)
  const [autocompleteAnchor, setAutocompleteAnchor] = useState(null)
  const [filteredFunctions, setFilteredFunctions] = useState([])

  useEffect(() => {
    setLocalValue(formula || value)
  }, [value, formula])

  const handleChange = useCallback((e) => {
    const newValue = e.target.value
    setLocalValue(newValue)
    setIsEditing(true)
    onChange?.(newValue)

    if (newValue.startsWith('=')) {
      const match = newValue.match(/=([A-Z]+)$/i)
      if (match) {
        const searchTerm = match[1].toUpperCase()
        const matches = FORMULA_FUNCTIONS.filter((f) =>
          f.name.startsWith(searchTerm)
        )
        if (matches.length > 0) {
          setFilteredFunctions(matches)
          setAutocompleteAnchor(inputRef.current)
        } else {
          setAutocompleteAnchor(null)
        }
      } else {
        setAutocompleteAnchor(null)
      }
    } else {
      setAutocompleteAnchor(null)
    }
  }, [onChange])

  const handleApply = useCallback(() => {
    setIsEditing(false)
    setAutocompleteAnchor(null)
    onApply?.(localValue)
  }, [localValue, onApply])

  const handleCancel = useCallback(() => {
    setLocalValue(formula || value)
    setIsEditing(false)
    setAutocompleteAnchor(null)
    onCancel?.()
  }, [formula, onCancel, value])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      handleApply()
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }, [handleApply, handleCancel])

  const handleInsertFunction = useCallback((func) => {
    const currentValue = localValue
    const match = currentValue.match(/=([A-Z]+)$/i)
    if (match) {
      const newValue = currentValue.slice(0, -match[1].length) + func.name + '('
      setLocalValue(newValue)
      onChange?.(newValue)
    }
    setAutocompleteAnchor(null)
    inputRef.current?.focus()
  }, [localValue, onChange])

  const handleSelectFunction = useCallback((func) => {
    const newValue = `=${func.name}(`
    setLocalValue(newValue)
    onChange?.(newValue)
    setFunctionMenuAnchor(null)
    inputRef.current?.focus()
  }, [onChange])

  return {
    inputRef,
    localValue,
    isEditing,
    setIsEditing,
    functionMenuAnchor,
    setFunctionMenuAnchor,
    autocompleteAnchor,
    setAutocompleteAnchor,
    filteredFunctions,
    handleChange,
    handleApply,
    handleCancel,
    handleKeyDown,
    handleInsertFunction,
    handleSelectFunction,
  }
}

/**
 * Custom hook: manages filter state for ToolbarSearchAndFilters
 */
import { useState, useCallback } from 'react'

export function useToolbarFilters({ onFiltersChange }) {
  const [filterAnchor, setFilterAnchor] = useState(null)
  const [activeFilters, setActiveFilters] = useState({})

  const handleFilterClick = useCallback((event) => {
    setFilterAnchor(event.currentTarget)
  }, [])

  const handleFilterClose = useCallback(() => {
    setFilterAnchor(null)
  }, [])

  const handleFilterSelect = useCallback((filterKey, value) => {
    setActiveFilters((prev) => {
      const next = { ...prev, [filterKey]: value }
      onFiltersChange?.(next)
      return next
    })
    handleFilterClose()
  }, [handleFilterClose, onFiltersChange])

  const handleClearFilter = useCallback((filterKey) => {
    setActiveFilters((prev) => {
      const next = { ...prev }
      delete next[filterKey]
      onFiltersChange?.(next)
      return next
    })
  }, [onFiltersChange])

  const handleClearAllFilters = useCallback(() => {
    setActiveFilters({})
    onFiltersChange?.({})
  }, [onFiltersChange])

  const activeFilterCount = Object.keys(activeFilters).length

  return {
    filterAnchor,
    activeFilters,
    activeFilterCount,
    handleFilterClick,
    handleFilterClose,
    handleFilterSelect,
    handleClearFilter,
    handleClearAllFilters,
  }
}

/**
 * Custom hook for search state and operations
 */
import { useState, useEffect, useCallback } from 'react'
import useSearchStore from '@/stores/searchStore'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useSearch() {
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    results,
    totalResults,
    facets,
    savedSearches,
    searchHistory,
    loading,
    searching,
    error,
    search,
    semanticSearch,
    regexSearch,
    booleanSearch,
    saveSearch,
    fetchSavedSearches,
    deleteSavedSearch,
    runSavedSearch,
    clearResults,
    reset,
  } = useSearchStore()

  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('fulltext')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({})
  const [selectedConnectionId, setSelectedConnectionId] = useState('')

  useEffect(() => {
    fetchSavedSearches()
    return () => reset()
  }, [fetchSavedSearches, reset])

  const handleSearch = useCallback(async (overrideQuery) => {
    const searchQuery = (overrideQuery ?? query).trim()
    if (!searchQuery) return

    const searchFilters = selectedConnectionId
      ? { ...filters, connectionId: selectedConnectionId }
      : filters

    const searchAction = async () => {
      let searchResult = null
      switch (searchType) {
        case 'semantic':
          searchResult = await semanticSearch(searchQuery, { filters: searchFilters })
          break
        case 'regex':
          searchResult = await regexSearch(searchQuery, { filters: searchFilters })
          break
        case 'boolean':
          searchResult = await booleanSearch(searchQuery, { filters: searchFilters })
          break
        default:
          searchResult = await search(searchQuery, { searchType: 'fulltext', filters: searchFilters })
      }
      return searchResult
    }

    return execute({
      type: InteractionType.EXECUTE,
      label: 'Search documents',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { source: 'search', query: searchQuery, searchType },
      action: searchAction,
    })
  }, [booleanSearch, execute, filters, query, regexSearch, search, searchType, selectedConnectionId, semanticSearch])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }, [handleSearch])

  const handleSaveSearch = useCallback(async (searchName) => {
    if (!searchName.trim() || !query.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Save search',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'search', name: searchName },
      action: async () => {
        await saveSearch(searchName, query, { searchType, filters })
        toast.show('Search saved', 'success')
      },
    })
  }, [execute, filters, query, saveSearch, searchType, toast])

  const handleRunSavedSearch = useCallback(async (savedSearch) => {
    setQuery(savedSearch.query)
    setSearchType(savedSearch.search_type || 'fulltext')
    await runSavedSearch(savedSearch.id)
  }, [runSavedSearch])

  const handleClearSearch = useCallback(() => {
    setQuery('')
    clearResults()
  }, [clearResults])

  return {
    // State
    query,
    setQuery,
    searchType,
    setSearchType,
    showFilters,
    setShowFilters,
    filters,
    setFilters,
    selectedConnectionId,
    setSelectedConnectionId,
    // Store state
    results,
    totalResults,
    facets,
    savedSearches,
    searchHistory,
    loading,
    searching,
    error,
    // Actions
    handleSearch,
    handleKeyDown,
    handleSaveSearch,
    handleRunSavedSearch,
    handleClearSearch,
  }
}

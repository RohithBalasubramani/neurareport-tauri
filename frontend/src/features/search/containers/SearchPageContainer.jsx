/**
 * Search Page Container
 * Advanced search and discovery interface.
 */
import React, { useState, useCallback } from 'react'
import { Box, Alert, alpha, styled } from '@mui/material'
import { useSearch } from '../hooks/useSearch'
import SearchHeaderSection from '../components/SearchHeaderSection'
import SearchResultsPanel from '../components/SearchResultsPanel'
import SearchSidebar from '../components/SearchSidebar'

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

export default function SearchPageContainer() {
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [searchName, setSearchName] = useState('')

  const {
    query, setQuery,
    searchType, setSearchType,
    showFilters, setShowFilters,
    filters, setFilters,
    selectedConnectionId, setSelectedConnectionId,
    results, totalResults, facets,
    savedSearches, searchHistory,
    searching, error,
    handleSearch, handleKeyDown,
    handleSaveSearch, handleRunSavedSearch,
    handleClearSearch,
  } = useSearch()

  const onSaveClick = useCallback(() => setSaveDialogOpen(true), [])

  const onExampleClick = useCallback((example) => {
    setQuery(example.query)
    setSearchType(example.type)
  }, [setQuery, setSearchType])

  const onHistoryClick = useCallback((item) => {
    setQuery(item.query)
    handleSearch(item.query)
  }, [setQuery, handleSearch])

  return (
    <PageContainer>
      <SearchHeaderSection
        query={query}
        setQuery={setQuery}
        searchType={searchType}
        setSearchType={setSearchType}
        showFilters={showFilters}
        setShowFilters={setShowFilters}
        filters={filters}
        setFilters={setFilters}
        selectedConnectionId={selectedConnectionId}
        setSelectedConnectionId={setSelectedConnectionId}
        searching={searching}
        onSearch={handleSearch}
        onKeyDown={handleKeyDown}
        onClear={handleClearSearch}
      />

      <ContentArea>
        <SearchResultsPanel
          results={results}
          totalResults={totalResults}
          searching={searching}
          onSaveClick={onSaveClick}
          onExampleClick={onExampleClick}
        />

        <SearchSidebar
          savedSearches={savedSearches}
          searchHistory={searchHistory}
          facets={facets}
          onRunSavedSearch={handleRunSavedSearch}
          onHistoryClick={onHistoryClick}
        />
      </ContentArea>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}

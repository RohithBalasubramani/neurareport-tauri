/**
 * Search Page Container
 * Advanced search and discovery interface.
 */
import React, { useState, useEffect, useCallback } from 'react'
import { sanitizeHighlight } from '@/utils/sanitize'
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Collapse,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  History as HistoryIcon,
  BookmarkBorder as SaveIcon,
  Bookmark as SavedIcon,
  Description as DocIcon,
  Folder as FolderIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Clear as ClearIcon,
  Code as RegexIcon,
  Psychology as SemanticIcon,
  DataObject as BooleanIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'
import useSearchStore from '@/stores/searchStore'
import useSharedData from '@/hooks/useSharedData'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const SearchHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

const MainPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

const Sidebar = styled(Box)(({ theme }) => ({
  width: 280,
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  display: 'flex',
  flexDirection: 'column',
}))

const SearchInput = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    // Figma spec: Background #F1F0EF, Border 1px solid #E2E1DE, Border-radius 8px
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.6) : neutral[100],
    borderRadius: 8,  // Figma spec: 8px
    '& fieldset': {
      borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    },
    '&:hover': {
      '& fieldset': {
        borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.2) : neutral[300],
      },
    },
    '&.Mui-focused': {
      '& fieldset': {
        borderColor: theme.palette.mode === 'dark' ? theme.palette.text.secondary : neutral[500],
        borderWidth: 1,
      },
    },
  },
}))

const ResultCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const FacetSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

// =============================================================================
// SEARCH TYPES
// =============================================================================

const SEARCH_TYPES = [
  { type: 'fulltext', label: 'Full Text', icon: SearchIcon },
  { type: 'semantic', label: 'Semantic', icon: SemanticIcon },
  { type: 'regex', label: 'Regex', icon: RegexIcon },
  { type: 'boolean', label: 'Boolean', icon: BooleanIcon },
]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function SearchPageContainer() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const { connections, activeConnectionId } = useSharedData()
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
  const [showHistory, setShowHistory] = useState(false)
  const [saveDialogOpen, setSaveDialogOpen] = useState(false)
  const [searchName, setSearchName] = useState('')

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

  const handleSaveSearch = useCallback(async () => {
    if (!searchName.trim() || !query.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Save search',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'search', name: searchName },
      action: async () => {
        await saveSearch(searchName, query, { searchType, filters })
        toast.show('Search saved', 'success')
        setSearchName('')
        setSaveDialogOpen(false)
      },
    })
  }, [execute, filters, query, saveSearch, searchName, searchType, toast])

  const handleRunSavedSearch = useCallback(async (savedSearch) => {
    setQuery(savedSearch.query)
    setSearchType(savedSearch.search_type || 'fulltext')
    await runSavedSearch(savedSearch.id)
  }, [runSavedSearch])

  const handleClearSearch = useCallback(() => {
    setQuery('')
    clearResults()
  }, [clearResults])

  return (
    <PageContainer>
      {/* Search Header */}
      <SearchHeader>
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
            Search & Discovery
          </Typography>

          {/* Search Type Tabs */}
          <Tabs
            value={searchType}
            onChange={(_, v) => setSearchType(v)}
            sx={{ mb: 2 }}
          >
            {SEARCH_TYPES.map((st) => (
              <Tab
                key={st.type}
                value={st.type}
                label={st.label}
                icon={<st.icon fontSize="small" />}
                iconPosition="start"
              />
            ))}
          </Tabs>

          {/* Search Input */}
          <SearchInput
            fullWidth
            placeholder={
              searchType === 'regex'
                ? 'Enter regex pattern...'
                : searchType === 'boolean'
                ? 'e.g., (revenue AND growth) OR profit'
                : searchType === 'semantic'
                ? 'Describe what you\'re looking for...'
                : 'Search documents...'
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            inputProps={{ 'aria-label': 'Search query' }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  {query && (
                    <IconButton size="small" onClick={handleClearSearch}>
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  )}
                  <IconButton
                    onClick={() => setShowFilters(!showFilters)}
                    color={showFilters ? 'primary' : 'default'}
                  >
                    <FilterIcon />
                  </IconButton>
                  <ActionButton
                    variant="contained"
                    onClick={handleSearch}
                    disabled={!query.trim() || searching}
                    sx={{ ml: 1 }}
                  >
                    {searching ? <CircularProgress size={20} /> : 'Search'}
                  </ActionButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Filters */}
          <Collapse in={showFilters}>
            <Paper sx={{ mt: 2, p: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <ConnectionSelector
                    value={selectedConnectionId}
                    onChange={setSelectedConnectionId}
                    label="Data Source"
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Document Type</InputLabel>
                    <Select
                      value={filters.documentType || ''}
                      label="Document Type"
                      onChange={(e) => setFilters({ ...filters, documentType: e.target.value })}
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="pdf">PDF</MenuItem>
                      <MenuItem value="docx">Word</MenuItem>
                      <MenuItem value="xlsx">Excel</MenuItem>
                      <MenuItem value="txt">Text</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Date From"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={filters.dateFrom || ''}
                    onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Date To"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={filters.dateTo || ''}
                    onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Collapse>
        </Box>
      </SearchHeader>

      <ContentArea>
        {/* Results */}
        <MainPanel>
          {results.length > 0 ? (
            <>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="subtitle1">
                  {totalResults} results found
                </Typography>
                <ActionButton
                  size="small"
                  startIcon={<SaveIcon />}
                  onClick={() => setSaveDialogOpen(true)}
                >
                  Save Search
                </ActionButton>
              </Box>

              {results.map((result, index) => (
                <ResultCard key={result.id || index} variant="outlined">
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <DocIcon color="inherit" />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {result.title || result.filename || 'Untitled'}
                      </Typography>
                      {result.highlight && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mt: 0.5 }}
                          dangerouslySetInnerHTML={{ __html: sanitizeHighlight(result.highlight) }}
                        />
                      )}
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        {result.score && (
                          <Chip size="small" label={`Score: ${(result.score * 100).toFixed(0)}%`} />
                        )}
                        {result.type && (
                          <Chip size="small" label={result.type.toUpperCase()} variant="outlined" />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </ResultCard>
              ))}
            </>
          ) : !searching ? (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                maxWidth: 500,
                mx: 'auto',
              }}
            >
              <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Search Your Documents
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Find what you need across all your documents using different search modes.
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, width: '100%', maxWidth: 300 }}>
                <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'left', mb: 0.5 }}>
                  Try these example searches:
                </Typography>
                {[
                  { query: 'quarterly revenue', type: 'fulltext', label: 'Full Text' },
                  { query: 'documents about marketing strategy', type: 'semantic', label: 'Semantic' },
                  { query: '(budget AND 2024) OR forecast', type: 'boolean', label: 'Boolean' },
                ].map((example) => (
                  <Button
                    key={example.query}
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      setQuery(example.query)
                      setSearchType(example.type)
                    }}
                    sx={{ justifyContent: 'flex-start', textTransform: 'none', textAlign: 'left' }}
                  >
                    <Chip size="small" label={example.label} sx={{ mr: 1, pointerEvents: 'none' }} />
                    <Typography variant="body2" noWrap>{example.query}</Typography>
                  </Button>
                ))}
              </Box>
            </Box>
          ) : null}
        </MainPanel>

        {/* Sidebar */}
        <Sidebar>
          {/* Saved Searches */}
          <FacetSection>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Saved Searches
              </Typography>
              <SavedIcon fontSize="small" color="action" />
            </Box>
            <List dense>
              {savedSearches.slice(0, 5).map((saved) => (
                <ListItem
                  key={saved.id}
                  button
                  onClick={() => handleRunSavedSearch(saved)}
                  sx={{ borderRadius: 1 }}
                >
                  <ListItemText
                    primary={saved.name}
                    secondary={saved.query}
                    primaryTypographyProps={{ variant: 'body2' }}
                    secondaryTypographyProps={{ noWrap: true }}
                  />
                </ListItem>
              ))}
              {savedSearches.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                  No saved searches
                </Typography>
              )}
            </List>
          </FacetSection>

          {/* Recent Searches */}
          <FacetSection>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Recent Searches
              </Typography>
              <HistoryIcon fontSize="small" color="action" />
            </Box>
            <List dense>
              {searchHistory.slice(0, 5).map((item, index) => (
                <ListItem
                  key={index}
                  button
                  onClick={() => {
                    setQuery(item.query)
                    handleSearch(item.query)
                  }}
                  sx={{ borderRadius: 1 }}
                >
                  <ListItemText
                    primary={item.query}
                    secondary={`${item.resultCount} results`}
                    primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                  />
                </ListItem>
              ))}
              {searchHistory.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                  No recent searches
                </Typography>
              )}
            </List>
          </FacetSection>

          {/* Facets */}
          {Object.keys(facets).length > 0 && (
            <FacetSection>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Refine Results
              </Typography>
              {Object.entries(facets).map(([facetName, facetValues]) => (
                <Box key={facetName} sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    {facetName.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  {Object.entries(facetValues).slice(0, 5).map(([value, count]) => (
                    <FormControlLabel
                      key={value}
                      control={<Checkbox size="small" />}
                      label={
                        <Typography variant="body2">
                          {value} ({count})
                        </Typography>
                      }
                    />
                  ))}
                </Box>
              ))}
            </FacetSection>
          )}
        </Sidebar>
      </ContentArea>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}

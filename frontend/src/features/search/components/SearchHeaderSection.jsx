/**
 * Search header with tabs, input, and filters
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  Collapse,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  alpha,
  styled,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Code as RegexIcon,
  Psychology as SemanticIcon,
  DataObject as BooleanIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import ConnectionSelector from '@/components/common/ConnectionSelector'

const SearchHeaderBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const SearchInput = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.6) : neutral[100],
    borderRadius: 8,
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

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

const SEARCH_TYPES = [
  { type: 'fulltext', label: 'Full Text', icon: SearchIcon },
  { type: 'semantic', label: 'Semantic', icon: SemanticIcon },
  { type: 'regex', label: 'Regex', icon: RegexIcon },
  { type: 'boolean', label: 'Boolean', icon: BooleanIcon },
]

export default function SearchHeaderSection({
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
  searching,
  onSearch,
  onKeyDown,
  onClear,
}) {
  return (
    <SearchHeaderBox>
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Search & Discovery
        </Typography>

        <Tabs value={searchType} onChange={(_, v) => setSearchType(v)} sx={{ mb: 2 }}>
          {SEARCH_TYPES.map((st) => (
            <Tab key={st.type} value={st.type} label={st.label} icon={<st.icon fontSize="small" />} iconPosition="start" />
          ))}
        </Tabs>

        <SearchInput
          fullWidth
          placeholder={
            searchType === 'regex' ? 'Enter regex pattern...'
              : searchType === 'boolean' ? 'e.g., (revenue AND growth) OR profit'
              : searchType === 'semantic' ? 'Describe what you\'re looking for...'
              : 'Search documents...'
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
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
                  <IconButton size="small" onClick={onClear}>
                    <ClearIcon fontSize="small" />
                  </IconButton>
                )}
                <IconButton onClick={() => setShowFilters(!showFilters)} color={showFilters ? 'primary' : 'default'}>
                  <FilterIcon />
                </IconButton>
                <ActionButton variant="contained" onClick={onSearch} disabled={!query.trim() || searching} sx={{ ml: 1 }}>
                  {searching ? <CircularProgress size={20} /> : 'Search'}
                </ActionButton>
              </InputAdornment>
            ),
          }}
        />

        <Collapse in={showFilters}>
          <Paper sx={{ mt: 2, p: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <ConnectionSelector value={selectedConnectionId} onChange={setSelectedConnectionId} label="Data Source" size="small" />
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Document Type</InputLabel>
                  <Select value={filters.documentType || ''} label="Document Type" onChange={(e) => setFilters({ ...filters, documentType: e.target.value })}>
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="pdf">PDF</MenuItem>
                    <MenuItem value="docx">Word</MenuItem>
                    <MenuItem value="xlsx">Excel</MenuItem>
                    <MenuItem value="txt">Text</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Date From" type="date" InputLabelProps={{ shrink: true }} value={filters.dateFrom || ''} onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })} />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Date To" type="date" InputLabelProps={{ shrink: true }} value={filters.dateTo || ''} onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })} />
              </Grid>
            </Grid>
          </Paper>
        </Collapse>
      </Box>
    </SearchHeaderBox>
  )
}

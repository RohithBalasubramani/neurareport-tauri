/**
 * Filter Bar Component
 * Dashboard filter controls with date range, dropdowns, and search.
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Chip,
  Popover,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Divider,
  Badge,
  InputAdornment,
  Collapse,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  FilterList as FilterIcon,
  Search as SearchIcon,
  CalendarToday as CalendarIcon,
  Clear as ClearIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Check as CheckIcon,
  Save as SaveIcon,
  Bookmark as BookmarkIcon,
  ArrowDropDown as DropdownIcon,
} from '@mui/icons-material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const FilterBarContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: theme.spacing(1.5),
  padding: theme.spacing(1.5, 2),
  backgroundColor: theme.palette.background.paper,
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const FilterChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  fontWeight: 500,
  '& .MuiChip-deleteIcon': {
    fontSize: 16,
  },
}))

const DateRangeButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderColor: 'transparent',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const QuickFilterButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  minWidth: 'auto',
  padding: theme.spacing(0.5, 1.5),
}))

const FilterPopover = styled(Paper)(({ theme }) => ({
  width: 280,
  maxHeight: 400,
  overflow: 'auto',
  borderRadius: 8,
  boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.15)}`,
}))

const SavedFilterItem = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 4,
  margin: theme.spacing(0.5, 1),
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

// =============================================================================
// PRESET DATE RANGES
// =============================================================================

const DATE_PRESETS = [
  { label: 'Today', getValue: () => ({ start: new Date(), end: new Date() }) },
  { label: 'Yesterday', getValue: () => {
    const d = new Date()
    d.setDate(d.getDate() - 1)
    return { start: d, end: d }
  }},
  { label: 'Last 7 Days', getValue: () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 7)
    return { start, end }
  }},
  { label: 'Last 30 Days', getValue: () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 30)
    return { start, end }
  }},
  { label: 'This Month', getValue: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    return { start, end }
  }},
  { label: 'Last Month', getValue: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const end = new Date(now.getFullYear(), now.getMonth(), 0)
    return { start, end }
  }},
  { label: 'This Quarter', getValue: () => {
    const now = new Date()
    const quarter = Math.floor(now.getMonth() / 3)
    const start = new Date(now.getFullYear(), quarter * 3, 1)
    const end = new Date(now.getFullYear(), (quarter + 1) * 3, 0)
    return { start, end }
  }},
  { label: 'This Year', getValue: () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), 0, 1)
    const end = new Date(now.getFullYear(), 11, 31)
    return { start, end }
  }},
]

// =============================================================================
// DATE RANGE PICKER
// =============================================================================

function DateRangePicker({ startDate, endDate, onChange, onClose }) {
  const [localStart, setLocalStart] = useState(startDate)
  const [localEnd, setLocalEnd] = useState(endDate)

  const handlePresetClick = (preset) => {
    const { start, end } = preset.getValue()
    setLocalStart(start)
    setLocalEnd(end)
  }

  const handleApply = () => {
    onChange?.({ start: localStart, end: localEnd })
    onClose?.()
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 2, width: 320 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
          Date Range
        </Typography>

        <Stack spacing={2}>
          <DatePicker
            label="Start Date"
            value={localStart}
            onChange={setLocalStart}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
          <DatePicker
            label="End Date"
            value={localEnd}
            onChange={setLocalEnd}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Stack>

        <Divider sx={{ my: 2 }} />

        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
          Quick Select
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
          {DATE_PRESETS.map((preset) => (
            <QuickFilterButton
              key={preset.label}
              size="small"
              variant="outlined"
              onClick={() => handlePresetClick(preset)}
            >
              {preset.label}
            </QuickFilterButton>
          ))}
        </Box>

        <Divider sx={{ my: 2 }} />

        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button size="small" onClick={onClose}>
            Cancel
          </Button>
          <Button size="small" variant="contained" onClick={handleApply}>
            Apply
          </Button>
        </Stack>
      </Box>
    </LocalizationProvider>
  )
}

// =============================================================================
// MULTI-SELECT FILTER
// =============================================================================

function MultiSelectFilter({ label, options, selected, onChange, onClose }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [localSelected, setLocalSelected] = useState(selected || [])

  const filteredOptions = useMemo(() =>
    options.filter((opt) =>
      opt.label.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [options, searchTerm]
  )

  const handleToggle = (value) => {
    setLocalSelected((prev) =>
      prev.includes(value)
        ? prev.filter((v) => v !== value)
        : [...prev, value]
    )
  }

  const handleSelectAll = () => {
    setLocalSelected(options.map((opt) => opt.value))
  }

  const handleClearAll = () => {
    setLocalSelected([])
  }

  const handleApply = () => {
    onChange?.(localSelected)
    onClose?.()
  }

  return (
    <FilterPopover>
      <Box sx={{ p: 1.5 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
          {label}
        </Typography>

        <TextField
          size="small"
          fullWidth
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 1 }}
        />

        <Stack direction="row" spacing={1} mb={1}>
          <Button size="small" onClick={handleSelectAll}>
            Select All
          </Button>
          <Button size="small" onClick={handleClearAll}>
            Clear
          </Button>
        </Stack>
      </Box>

      <List dense sx={{ maxHeight: 200, overflow: 'auto', py: 0 }}>
        {filteredOptions.map((option) => (
          <ListItem key={option.value} disablePadding>
            <ListItemButton
              onClick={() => handleToggle(option.value)}
              dense
              sx={{ py: 0.25 }}
            >
              <Checkbox
                checked={localSelected.includes(option.value)}
                size="small"
                sx={{ py: 0 }}
              />
              <ListItemText
                primary={option.label}
                primaryTypographyProps={{ variant: 'body2' }}
              />
              {option.count !== undefined && (
                <Typography variant="caption" color="text.secondary">
                  ({option.count})
                </Typography>
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      <Box sx={{ p: 1.5 }}>
        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button size="small" onClick={onClose}>
            Cancel
          </Button>
          <Button size="small" variant="contained" onClick={handleApply}>
            Apply ({localSelected.length})
          </Button>
        </Stack>
      </Box>
    </FilterPopover>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function FilterBar({
  filters = [],
  activeFilters = {},
  dateRange = { start: null, end: null },
  searchQuery = '',
  savedFilters = [],
  onFilterChange,
  onDateRangeChange,
  onSearchChange,
  onClearAll,
  onSaveFilter,
  onLoadSavedFilter,
  onRefresh,
  showSearch = true,
  showDateRange = true,
  compact = false,
}) {
  const theme = useTheme()
  const [datePickerAnchor, setDatePickerAnchor] = useState(null)
  const [filterAnchors, setFilterAnchors] = useState({})
  const [savedFiltersAnchor, setSavedFiltersAnchor] = useState(null)
  const [expanded, setExpanded] = useState(!compact)

  // Count active filters
  const activeFilterCount = useMemo(() =>
    Object.values(activeFilters).reduce(
      (count, values) => count + (Array.isArray(values) ? values.length : values ? 1 : 0),
      0
    ) + (dateRange.start || dateRange.end ? 1 : 0) + (searchQuery ? 1 : 0),
    [activeFilters, dateRange, searchQuery]
  )

  // Format date range label
  const dateRangeLabel = useMemo(() => {
    if (!dateRange.start && !dateRange.end) return 'Select Date Range'
    if (dateRange.start && dateRange.end) {
      const start = dateRange.start.toLocaleDateString()
      const end = dateRange.end.toLocaleDateString()
      return start === end ? start : `${start} - ${end}`
    }
    return dateRange.start?.toLocaleDateString() || dateRange.end?.toLocaleDateString()
  }, [dateRange])

  // Handle filter popover
  const handleOpenFilter = useCallback((filterId, event) => {
    setFilterAnchors((prev) => ({ ...prev, [filterId]: event.currentTarget }))
  }, [])

  const handleCloseFilter = useCallback((filterId) => {
    setFilterAnchors((prev) => ({ ...prev, [filterId]: null }))
  }, [])

  // Handle filter change
  const handleFilterChange = useCallback((filterId, values) => {
    onFilterChange?.({ ...activeFilters, [filterId]: values })
    handleCloseFilter(filterId)
  }, [activeFilters, onFilterChange])

  // Clear single filter
  const handleClearFilter = useCallback((filterId) => {
    const newFilters = { ...activeFilters }
    delete newFilters[filterId]
    onFilterChange?.(newFilters)
  }, [activeFilters, onFilterChange])

  return (
    <FilterBarContainer>
      {/* Collapse/Expand for compact mode */}
      {compact && (
        <Tooltip title={expanded ? 'Collapse filters' : 'Expand filters'}>
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
          >
            <Badge badgeContent={activeFilterCount} sx={{ '& .MuiBadge-badge': { bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' } }}>
              <FilterIcon />
            </Badge>
          </IconButton>
        </Tooltip>
      )}

      <Collapse in={expanded || !compact} orientation="horizontal" sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
        {/* Search */}
        {showSearch && (
          <TextField
            size="small"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => onSearchChange?.(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: searchQuery && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => onSearchChange?.('')}>
                    <ClearIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ width: 200 }}
          />
        )}

        {/* Date Range */}
        {showDateRange && (
          <>
            <DateRangeButton
              variant="outlined"
              startIcon={<CalendarIcon />}
              endIcon={<DropdownIcon />}
              onClick={(e) => setDatePickerAnchor(e.currentTarget)}
            >
              {dateRangeLabel}
            </DateRangeButton>
            <Popover
              open={Boolean(datePickerAnchor)}
              anchorEl={datePickerAnchor}
              onClose={() => setDatePickerAnchor(null)}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            >
              <DateRangePicker
                startDate={dateRange.start}
                endDate={dateRange.end}
                onChange={onDateRangeChange}
                onClose={() => setDatePickerAnchor(null)}
              />
            </Popover>
          </>
        )}

        {/* Dynamic Filters */}
        {filters.map((filter) => {
          const selectedValues = activeFilters[filter.id] || []
          const hasSelection = selectedValues.length > 0

          return (
            <Box key={filter.id}>
              <Button
                variant="outlined"
                size="small"
                endIcon={<DropdownIcon />}
                onClick={(e) => handleOpenFilter(filter.id, e)}
                sx={{
                  borderRadius: 1,  // Figma spec: 8px
                  textTransform: 'none',
                  borderColor: hasSelection ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : undefined,
                  backgroundColor: hasSelection ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : undefined,
                }}
              >
                {filter.label}
                {hasSelection && (
                  <Chip
                    label={selectedValues.length}
                    size="small"
                    sx={{ ml: 0.5, height: 18, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                  />
                )}
              </Button>
              <Popover
                open={Boolean(filterAnchors[filter.id])}
                anchorEl={filterAnchors[filter.id]}
                onClose={() => handleCloseFilter(filter.id)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
              >
                <MultiSelectFilter
                  label={filter.label}
                  options={filter.options}
                  selected={selectedValues}
                  onChange={(values) => handleFilterChange(filter.id, values)}
                  onClose={() => handleCloseFilter(filter.id)}
                />
              </Popover>
            </Box>
          )
        })}

        {/* Active Filter Chips */}
        {Object.entries(activeFilters).map(([filterId, values]) => {
          if (!values || values.length === 0) return null
          const filter = filters.find((f) => f.id === filterId)
          if (!filter) return null

          return values.map((value) => {
            const option = filter.options.find((o) => o.value === value)
            return (
              <FilterChip
                key={`${filterId}-${value}`}
                label={`${filter.label}: ${option?.label || value}`}
                size="small"
                onDelete={() => {
                  const newValues = values.filter((v) => v !== value)
                  handleFilterChange(filterId, newValues.length > 0 ? newValues : undefined)
                }}
              />
            )
          })
        })}
      </Collapse>

      {/* Actions */}
      <Box sx={{ flex: 1 }} />

      <Stack direction="row" spacing={0.5}>
        {/* Saved Filters */}
        {savedFilters.length > 0 && (
          <>
            <Tooltip title="Saved filters">
              <IconButton
                size="small"
                onClick={(e) => setSavedFiltersAnchor(e.currentTarget)}
              >
                <BookmarkIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Popover
              open={Boolean(savedFiltersAnchor)}
              anchorEl={savedFiltersAnchor}
              onClose={() => setSavedFiltersAnchor(null)}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
              <FilterPopover>
                <Box sx={{ p: 1.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Saved Filters
                  </Typography>
                </Box>
                <List dense>
                  {savedFilters.map((saved) => (
                    <SavedFilterItem
                      key={saved.id}
                      onClick={() => {
                        onLoadSavedFilter?.(saved)
                        setSavedFiltersAnchor(null)
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <BookmarkIcon sx={{ fontSize: 18 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={saved.name}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </SavedFilterItem>
                  ))}
                </List>
              </FilterPopover>
            </Popover>
          </>
        )}

        {/* Save Current Filter */}
        {activeFilterCount > 0 && onSaveFilter && (
          <Tooltip title="Save filter">
            <IconButton size="small" onClick={onSaveFilter}>
              <SaveIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}

        {/* Clear All */}
        {activeFilterCount > 0 && (
          <Tooltip title="Clear all filters">
            <IconButton size="small" onClick={onClearAll}>
              <ClearIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}

        {/* Refresh */}
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={onRefresh}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
    </FilterBarContainer>
  )
}

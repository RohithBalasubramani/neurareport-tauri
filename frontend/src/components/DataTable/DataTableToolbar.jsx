/**
 * Premium Data Table Toolbar
 * Sophisticated search, filters, and actions with glassmorphism effects
 */
import { useState, useCallback } from 'react'
import {
  Box,
  TextField,
  InputAdornment,
  Button,
  Stack,
  Typography,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Menu,
  MenuItem,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  Fade,
  Zoom,
  useTheme,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Archive as ArchiveIcon,
  Label as LabelIcon,
  Download as DownloadIcon,
  ViewColumn as ColumnsIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  KeyboardArrowDown as ArrowDownIcon,
} from '@mui/icons-material'

// =============================================================================
// ANIMATIONS
// =============================================================================

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const ToolbarContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5, 3),
  backgroundColor: alpha(theme.palette.background.paper, 0.4),
  backdropFilter: 'blur(10px)',
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

const HeaderRow = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}))

const TitleSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(0.25),
}))

const Title = styled(Typography)(({ theme }) => ({
  fontSize: '1.125rem',
  fontWeight: 600,
  color: theme.palette.text.primary,
  letterSpacing: '-0.01em',
}))

const Subtitle = styled(Typography)(({ theme }) => ({
  fontSize: '14px',
  color: theme.palette.text.secondary,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
  padding: theme.spacing(0.75, 2),
  transition: 'all 0.2s ease',
  '&.MuiButton-outlined': {
    borderColor: alpha(theme.palette.divider, 0.2),
    '&:hover': {
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    },
  },
  '&.MuiButton-contained': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
      transform: 'translateY(-1px)',
    },
  },
}))

const SelectionBar = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  padding: theme.spacing(1.5, 2),
  background: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  borderRadius: 8,  // Figma spec: 8px
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  animation: `${slideIn} 0.3s ease-out`,
}))

const SelectionText = styled(Typography)(({ theme }) => ({
  fontSize: '14px',
  fontWeight: 500,
  color: theme.palette.text.primary,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}))

const SelectionBadge = styled(Box)(({ theme }) => ({
  width: 24,
  height: 24,
  borderRadius: 8,
  backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.75rem',
  fontWeight: 600,
}))

const SelectionAction = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontSize: '0.75rem',
  fontWeight: 500,
  padding: theme.spacing(0.5, 1.5),
  minWidth: 'auto',
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.text.primary, 0.1),
  '&:hover': {
    borderColor: alpha(theme.palette.text.primary, 0.2),
    backgroundColor: alpha(theme.palette.text.primary, 0.04),
  },
}))

const DeleteAction = styled(SelectionAction)(({ theme }) => ({
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.3),
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

const SearchField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,  // Figma spec: 8px
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    transition: 'all 0.2s ease',
    '& fieldset': {
      borderColor: alpha(theme.palette.divider, 0.1),
      transition: 'all 0.2s ease',
    },
    '&:hover fieldset': {
      borderColor: alpha(theme.palette.divider, 0.3),
    },
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
      boxShadow: `0 0 0 3px ${alpha(theme.palette.divider, 0.1)}`,
      '& fieldset': {
        borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      },
    },
  },
  '& .MuiInputBase-input': {
    fontSize: '0.875rem',
    padding: theme.spacing(1, 1.5),
    '&::placeholder': {
      color: theme.palette.text.disabled,
      opacity: 1,
    },
  },
}))

const FilterButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
  padding: theme.spacing(0.75, 1.5),
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.2),
  '&:hover': {
    borderColor: alpha(theme.palette.divider, 0.3),
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  },
  '&.active': {
    color: theme.palette.text.primary,
    borderColor: alpha(theme.palette.divider, 0.5),
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

const FilterChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  height: 28,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  color: theme.palette.text.secondary,
  fontWeight: 500,
  fontSize: '0.75rem',
  animation: `${slideIn} 0.2s ease-out`,
  '& .MuiChip-deleteIcon': {
    color: theme.palette.text.disabled,
    fontSize: 16,
    '&:hover': {
      color: theme.palette.text.secondary,
    },
  },
}))

const IconButtonStyled = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  color: theme.palette.text.secondary,
  transition: 'all 0.2s ease',
  '&:hover': {
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 8,  // Figma spec: 8px
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.12)}`,
    minWidth: 200,
    marginTop: theme.spacing(0.5),
  },
}))

const MenuSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 0),
}))

const MenuLabel = styled(Typography)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: theme.palette.text.disabled,
}))

const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  fontSize: '14px',
  padding: theme.spacing(1, 2),
  borderRadius: 6,
  margin: theme.spacing(0, 1),
  transition: 'all 0.15s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    color: theme.palette.text.primary,
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.16) : neutral[200],
    },
  },
}))

const FilterBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    color: theme.palette.common.white,
    fontSize: '10px',
    fontWeight: 600,
    minWidth: 16,
    height: 16,
    borderRadius: 6,
    padding: '0 4px',
  },
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DataTableToolbar({
  title,
  subtitle,
  searchPlaceholder = 'Search...',
  onSearch,
  filters = [],
  actions = [],
  numSelected = 0,
  onRefresh,
  onBulkDelete,
  bulkActions = [],
  onFiltersChange,
  columns = [],
  hiddenColumns = [],
  onToggleColumn,
  onResetColumns,
  onExportCsv,
  onExportJson,
  exportCsvDisabled = false,
  exportJsonDisabled = false,
}) {
  const theme = useTheme()
  const [searchValue, setSearchValue] = useState('')
  const [filterAnchor, setFilterAnchor] = useState(null)
  const [activeFilters, setActiveFilters] = useState({})
  const [moreAnchor, setMoreAnchor] = useState(null)
  const [columnSettingsOpen, setColumnSettingsOpen] = useState(false)

  const visibleColumnCount = columns.filter(
    (column) => column?.field && !hiddenColumns.includes(column.field)
  ).length
  const canConfigureColumns = columns.some((column) => column?.field) && typeof onToggleColumn === 'function'

  const handleSearchChange = useCallback((e) => {
    const value = e.target.value
    setSearchValue(value)
    onSearch?.(value)
  }, [onSearch])

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

  const handleMoreClick = useCallback((event) => {
    setMoreAnchor(event.currentTarget)
  }, [])

  const handleMoreClose = useCallback(() => {
    setMoreAnchor(null)
  }, [])

  const handleOpenColumnSettings = useCallback(() => {
    if (!canConfigureColumns) return
    setColumnSettingsOpen(true)
    handleMoreClose()
  }, [canConfigureColumns, handleMoreClose])

  const handleCloseColumnSettings = useCallback(() => {
    setColumnSettingsOpen(false)
  }, [])

  const handleExportCsv = useCallback(() => {
    if (exportCsvDisabled || !onExportCsv) return
    onExportCsv()
    handleMoreClose()
  }, [exportCsvDisabled, onExportCsv, handleMoreClose])

  const handleExportJson = useCallback(() => {
    if (exportJsonDisabled || !onExportJson) return
    onExportJson()
    handleMoreClose()
  }, [exportJsonDisabled, onExportJson, handleMoreClose])

  const activeFilterCount = Object.keys(activeFilters).length

  return (
    <ToolbarContainer>
      {/* Header Row */}
      <HeaderRow
        direction={{ xs: 'column', sm: 'row' }}
        alignItems={{ xs: 'stretch', sm: 'center' }}
        justifyContent="space-between"
        spacing={2}
      >
        <TitleSection>
          {title && <Title>{title}</Title>}
          {subtitle && <Subtitle>{subtitle}</Subtitle>}
        </TitleSection>

        <Stack direction="row" spacing={1}>
          {actions.map((action, index) => (
            <ActionButton
              key={index}
              variant={action.variant || 'outlined'}
              color={action.color || 'primary'}
              size="small"
              startIcon={action.icon}
              onClick={action.onClick}
              disabled={action.disabled}
            >
              {action.label}
            </ActionButton>
          ))}
        </Stack>
      </HeaderRow>

      {/* Selection Bar */}
      {numSelected > 0 && (
        <Fade in>
          <SelectionBar>
            <SelectionText>
              <SelectionBadge>{numSelected}</SelectionBadge>
              item{numSelected > 1 ? 's' : ''} selected
            </SelectionText>
            <Stack direction="row" spacing={1}>
              {bulkActions.map((action, index) => (
                <SelectionAction
                  key={index}
                  variant="outlined"
                  size="small"
                  startIcon={action.icon}
                  onClick={action.onClick}
                  disabled={action.disabled}
                >
                  {action.label}
                </SelectionAction>
              ))}
              {onBulkDelete && (
                <DeleteAction
                  variant="outlined"
                  size="small"
                  startIcon={<DeleteIcon sx={{ fontSize: 16 }} />}
                  onClick={onBulkDelete}
                >
                  Delete
                </DeleteAction>
              )}
            </Stack>
          </SelectionBar>
        </Fade>
      )}

      {/* Search and Filters Row */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={2}
        alignItems={{ xs: 'stretch', sm: 'center' }}
      >
        <SearchField
          size="small"
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
              </InputAdornment>
            ),
            endAdornment: searchValue && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={() => {
                    setSearchValue('')
                    onSearch?.('')
                  }}
                  sx={{ p: 0.5 }}
                >
                  <CloseIcon sx={{ fontSize: 16 }} />
                </IconButton>
              </InputAdornment>
            ),
          }}
          sx={{ width: { xs: '100%', sm: 280 } }}
        />

        <Stack
          direction="row"
          spacing={1}
          sx={{ flex: 1, flexWrap: 'wrap', gap: 1 }}
          alignItems="center"
        >
          {filters.length > 0 && (
            <>
              <FilterBadge badgeContent={activeFilterCount} invisible={activeFilterCount === 0}>
                <FilterButton
                  variant="outlined"
                  size="small"
                  startIcon={<FilterListIcon sx={{ fontSize: 16 }} />}
                  endIcon={<ArrowDownIcon sx={{ fontSize: 16 }} />}
                  onClick={handleFilterClick}
                  className={activeFilterCount > 0 ? 'active' : ''}
                >
                  Filters
                </FilterButton>
              </FilterBadge>

              <StyledMenu
                anchorEl={filterAnchor}
                open={Boolean(filterAnchor)}
                onClose={handleFilterClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                transformOrigin={{ vertical: 'top', horizontal: 'left' }}
              >
                {filters.map((filter, idx) => (
                  <MenuSection key={filter.key}>
                    <MenuLabel>{filter.label}</MenuLabel>
                    {filter.options.map((option) => (
                      <StyledMenuItem
                        key={option.value}
                        selected={activeFilters[filter.key] === option.value}
                        onClick={() => handleFilterSelect(filter.key, option.value)}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                          {option.label}
                          {activeFilters[filter.key] === option.value && (
                            <CheckIcon sx={{ fontSize: 16, color: 'text.primary', ml: 1 }} />
                          )}
                        </Box>
                      </StyledMenuItem>
                    ))}
                    {idx < filters.length - 1 && (
                      <Divider sx={{ my: 1, mx: 2, borderColor: alpha(theme.palette.divider, 0.1) }} />
                    )}
                  </MenuSection>
                ))}
                {activeFilterCount > 0 && (
                  <>
                    <Divider sx={{ my: 1, mx: 2, borderColor: alpha(theme.palette.divider, 0.1) }} />
                    <Box sx={{ px: 2, pb: 1 }}>
                      <Button
                        size="small"
                        onClick={handleClearAllFilters}
                        sx={{ fontSize: '0.75rem', textTransform: 'none' }}
                      >
                        Clear all filters
                      </Button>
                    </Box>
                  </>
                )}
              </StyledMenu>
            </>
          )}

          {/* Active Filter Chips */}
          {Object.entries(activeFilters).map(([key, value]) => {
            const filter = filters.find((f) => f.key === key)
            const option = filter?.options.find((o) => o.value === value)
            return (
              <FilterChip
                key={key}
                label={`${filter?.label}: ${option?.label}`}
                size="small"
                onDelete={() => handleClearFilter(key)}
              />
            )
          })}
        </Stack>

        <Stack direction="row" spacing={0.5}>
          {onRefresh && (
            <Tooltip title="Refresh data" arrow>
              <IconButtonStyled size="small" onClick={onRefresh} aria-label="Refresh data">
                <RefreshIcon sx={{ fontSize: 18 }} />
              </IconButtonStyled>
            </Tooltip>
          )}
          <Tooltip title="More options" arrow>
            <IconButtonStyled size="small" onClick={handleMoreClick} aria-label="More options">
              <MoreVertIcon sx={{ fontSize: 18 }} />
            </IconButtonStyled>
          </Tooltip>
        </Stack>

        <StyledMenu
          anchorEl={moreAnchor}
          open={Boolean(moreAnchor)}
          onClose={handleMoreClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MenuSection>
            <MenuLabel>Export</MenuLabel>
            <StyledMenuItem
              onClick={handleExportCsv}
              disabled={exportCsvDisabled || !onExportCsv}
            >
              <DownloadIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
              Export as CSV
            </StyledMenuItem>
            <StyledMenuItem
              onClick={handleExportJson}
              disabled={exportJsonDisabled || !onExportJson}
            >
              <DownloadIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
              Export as JSON
            </StyledMenuItem>
          </MenuSection>
          <Divider sx={{ my: 1, mx: 2, borderColor: alpha(theme.palette.divider, 0.1) }} />
          <MenuSection>
            <MenuLabel>View</MenuLabel>
            <StyledMenuItem onClick={handleOpenColumnSettings} disabled={!canConfigureColumns}>
              <ColumnsIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
              Column Settings
            </StyledMenuItem>
          </MenuSection>
        </StyledMenu>
      </Stack>

      <Dialog open={columnSettingsOpen} onClose={handleCloseColumnSettings} maxWidth="xs" fullWidth>
        <DialogTitle>Column Settings</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={1.5}>
            <Typography variant="body2" color="text.secondary">
              Choose which columns are visible in the table.
            </Typography>
            <FormGroup>
              {columns.map((column) => {
                if (!column?.field) return null
                const isVisible = !hiddenColumns.includes(column.field)
                const disableToggle = isVisible && visibleColumnCount <= 1
                return (
                  <FormControlLabel
                    key={column.field}
                    control={
                      <Checkbox
                        checked={isVisible}
                        onChange={() => onToggleColumn?.(column.field)}
                        disabled={disableToggle}
                      />
                    }
                    label={column.headerName || column.field}
                  />
                )
              })}
            </FormGroup>
            {visibleColumnCount <= 1 && (
              <Typography variant="caption" color="text.secondary">
                At least one column must remain visible.
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => onResetColumns?.()} disabled={!hiddenColumns.length || !onResetColumns}>
            Reset
          </Button>
          <Button onClick={handleCloseColumnSettings} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </ToolbarContainer>
  )
}

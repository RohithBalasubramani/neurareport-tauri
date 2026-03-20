/**
 * Search field, filter menu, and active filter chips for DataTableToolbar
 */
import { useState, useCallback } from 'react'
import {
  Box,
  InputAdornment,
  Button,
  Stack,
  IconButton,
  Tooltip,
  Divider,
  alpha,
  useTheme,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  KeyboardArrowDown as ArrowDownIcon,
} from '@mui/icons-material'
import {
  SearchField,
  FilterButton,
  FilterChip,
  FilterBadge,
  IconButtonStyled,
  StyledMenu,
  MenuSection,
  MenuLabel,
  StyledMenuItem,
} from './DataTableToolbarStyled'
import { useToolbarFilters } from './hooks/useToolbarFilters'

export default function ToolbarSearchAndFilters({
  searchPlaceholder,
  onSearch,
  filters,
  onFiltersChange,
  onRefresh,
  onMoreClick,
}) {
  const theme = useTheme()
  const [searchValue, setSearchValue] = useState('')
  const {
    filterAnchor, activeFilters, activeFilterCount,
    handleFilterClick, handleFilterClose, handleFilterSelect,
    handleClearFilter, handleClearAllFilters,
  } = useToolbarFilters({ onFiltersChange })

  const handleSearchChange = useCallback((e) => {
    const value = e.target.value
    setSearchValue(value)
    onSearch?.(value)
  }, [onSearch])

  return (
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
                onClick={() => { setSearchValue(''); onSearch?.('') }}
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
          <IconButtonStyled size="small" onClick={onMoreClick} aria-label="More options">
            <MoreVertIcon sx={{ fontSize: 18 }} />
          </IconButtonStyled>
        </Tooltip>
      </Stack>
    </Stack>
  )
}

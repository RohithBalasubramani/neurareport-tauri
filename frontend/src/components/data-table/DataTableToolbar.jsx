/**
 * Premium Data Table Toolbar
 * Sophisticated search, filters, and actions with glassmorphism effects
 */
import { useState, useCallback } from 'react'
import { Stack } from '@mui/material'
import ToolbarSelectionBar from './ToolbarSelectionBar'
import ToolbarSearchAndFilters from './ToolbarSearchAndFilters'
import ToolbarMoreMenu from './ToolbarMoreMenu'
import {
  ToolbarContainer,
  HeaderRow,
  TitleSection,
  Title,
  Subtitle,
  ActionButton,
} from './DataTableToolbarStyled'

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
  const [moreAnchor, setMoreAnchor] = useState(null)

  const visibleColumnCount = columns.filter(
    (column) => column?.field && !hiddenColumns.includes(column.field)
  ).length
  const canConfigureColumns = columns.some((column) => column?.field) && typeof onToggleColumn === 'function'

  const handleMoreClick = useCallback((event) => {
    setMoreAnchor(event.currentTarget)
  }, [])

  const handleMoreClose = useCallback(() => {
    setMoreAnchor(null)
  }, [])

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
      <ToolbarSelectionBar
        numSelected={numSelected}
        bulkActions={bulkActions}
        onBulkDelete={onBulkDelete}
      />

      {/* Search and Filters Row */}
      <ToolbarSearchAndFilters
        searchPlaceholder={searchPlaceholder}
        onSearch={onSearch}
        filters={filters}
        onFiltersChange={onFiltersChange}
        onRefresh={onRefresh}
        onMoreClick={handleMoreClick}
      />

      {/* More Options Menu + Column Settings Dialog */}
      <ToolbarMoreMenu
        moreAnchor={moreAnchor}
        onMoreClose={handleMoreClose}
        columns={columns}
        hiddenColumns={hiddenColumns}
        visibleColumnCount={visibleColumnCount}
        canConfigureColumns={canConfigureColumns}
        onToggleColumn={onToggleColumn}
        onResetColumns={onResetColumns}
        onExportCsv={onExportCsv}
        onExportJson={onExportJson}
        exportCsvDisabled={exportCsvDisabled}
        exportJsonDisabled={exportJsonDisabled}
      />
    </ToolbarContainer>
  )
}

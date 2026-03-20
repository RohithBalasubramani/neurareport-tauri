/**
 * Premium Data Table Component
 * Sophisticated table with glassmorphism, animations, and advanced interactions
 */
import { Table, useTheme, useMediaQuery } from '@mui/material'
import DataTableToolbar from './DataTableToolbar'
import DataTableEmptyState from './DataTableEmptyState'
import DataTableHead from './DataTableHead'
import DataTableBodyContent from './DataTableBodyContent'
import { useDataTableState } from './hooks/useDataTableState'
import { useDataTableExport } from './hooks/useDataTableExport'
import {
  TableWrapper,
  StyledTableContainer,
  StyledPagination,
} from './DataTableStyledComponents'

export default function DataTable({
  columns,
  data = [],
  loading = false,
  selectable = false,
  expandable = false,
  renderExpandedRow,
  onRowClick,
  onSelectionChange,
  rowActions,
  emptyState,
  filters,
  searchPlaceholder = 'Search...',
  onSearch,
  actions,
  bulkActions = [],
  onBulkDelete,
  title,
  subtitle,
  pagination = null,
  defaultSortField,
  defaultSortOrder = 'asc',
  pageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  stickyHeader = false,
  persistKey = null,
  rowHeight = 'medium',
}) {
  const theme = useTheme()
  const isNarrow = useMediaQuery(theme.breakpoints.down('lg'))

  const state = useDataTableState({
    columns,
    data,
    selectable,
    defaultSortField,
    defaultSortOrder,
    pageSize,
    persistKey,
    onSearch,
    onSelectionChange,
    onRowClick,
    pagination,
  })

  const {
    exportColumns, exportRows, handleExportCsv, handleExportJson,
  } = useDataTableExport({
    visibleColumns: state.visibleColumns,
    sortedData: state.sortedData,
    title,
  })

  const cellPadding = { compact: 1, medium: 1.5, comfortable: 2 }[rowHeight] || 1.5

  const toolbarProps = {
    title,
    subtitle,
    searchPlaceholder,
    onSearch: state.handleSearch,
    filters,
    bulkActions,
    onBulkDelete,
    numSelected: state.numSelected,
    onFiltersChange: state.setActiveFilters,
    columns,
    hiddenColumns: state.hiddenColumns,
    onToggleColumn: state.handleToggleColumn,
    onResetColumns: state.handleResetColumns,
    onExportCsv: handleExportCsv,
    onExportJson: handleExportJson,
    exportCsvDisabled: !exportColumns.length || !exportRows.length,
    exportJsonDisabled: !exportColumns.length || !exportRows.length,
  }

  // Empty state
  if (!loading && data.length === 0 && emptyState) {
    const emptyActionLabel = emptyState?.actionLabel
    const actionsForEmpty =
      emptyActionLabel && Array.isArray(actions)
        ? actions.filter((action) => action?.label !== emptyActionLabel)
        : actions

    return (
      <TableWrapper>
        <DataTableToolbar {...toolbarProps} actions={actionsForEmpty} />
        <DataTableEmptyState {...emptyState} />
      </TableWrapper>
    )
  }

  return (
    <TableWrapper>
      <DataTableToolbar {...toolbarProps} actions={actions} />

      <StyledTableContainer sx={{ maxHeight: stickyHeader ? 600 : 'none' }}>
        <Table
          stickyHeader={stickyHeader}
          size={rowHeight === 'compact' ? 'small' : 'medium'}
          sx={{ width: '100%', tableLayout: 'auto' }}
        >
          <DataTableHead
            visibleColumns={state.visibleColumns}
            expandable={expandable}
            selectable={selectable}
            rowActions={rowActions}
            orderBy={state.orderBy}
            order={state.order}
            numSelected={state.numSelected}
            pageRowCount={state.pageRowCount}
            onRequestSort={state.handleRequestSort}
            onSelectAll={state.handleSelectAll}
            isNarrow={isNarrow}
          />
          <DataTableBodyContent
            loading={loading}
            paginatedData={state.paginatedData}
            visibleColumns={state.visibleColumns}
            expandable={expandable}
            selectable={selectable}
            rowActions={rowActions}
            renderExpandedRow={renderExpandedRow}
            onRowClick={onRowClick}
            onRowKeyDown={state.handleRowKeyDown}
            isSelected={state.isSelected}
            expandedRows={state.expandedRows}
            handleToggleExpand={state.handleToggleExpand}
            handleSelect={state.handleSelect}
            cellPadding={cellPadding}
            rowsPerPage={state.rowsPerPage}
            isNarrow={isNarrow}
          />
        </Table>
      </StyledTableContainer>

      <StyledPagination
        rowsPerPageOptions={pageSizeOptions}
        component="div"
        count={state.rowCount}
        rowsPerPage={state.effectiveRowsPerPage}
        page={state.effectivePage}
        onPageChange={state.handleChangePage}
        onRowsPerPageChange={state.handleChangeRowsPerPage}
        labelRowsPerPage="Rows per page:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count}`}
      />
    </TableWrapper>
  )
}

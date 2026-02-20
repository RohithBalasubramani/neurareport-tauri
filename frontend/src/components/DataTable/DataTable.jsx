/**
 * Premium Data Table Component
 * Sophisticated table with glassmorphism, animations, and advanced interactions
 */
import { Fragment, useState, useMemo, useCallback, useEffect, useRef } from 'react'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TablePagination,
  Checkbox,
  IconButton,
  Typography,
  Skeleton,
  Tooltip,
  Fade,
  Collapse,
  useTheme,
  useMediaQuery,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import {
  MoreVert as MoreVertIcon,
  KeyboardArrowDown as ExpandIcon,
  KeyboardArrowUp as CollapseIcon,
  ArrowUpward as SortAscIcon,
  ArrowDownward as SortDescIcon,
} from '@mui/icons-material'
import DataTableToolbar from './DataTableToolbar'
import DataTableEmptyState from './DataTableEmptyState'

// Import design tokens
import {
  neutral,
  figmaComponents,
  fontFamilyBody,
} from '@/app/theme'
import { shimmer, slideIn } from '@/styles'

// =============================================================================
// FIGMA DATA TABLE CONSTANTS (EXACT from Figma specs)
// =============================================================================
const FIGMA_TABLE = {
  headerHeight: figmaComponents.dataTable.headerHeight,  // 60px
  rowHeight: figmaComponents.dataTable.rowHeight,        // 60px
  cellPadding: figmaComponents.dataTable.cellPadding,    // 16px
}

// =============================================================================
// ANIMATIONS (local — differ from shared versions)
// =============================================================================

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const TableWrapper = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.25)}`,
  overflow: 'hidden',
  // In flex layouts, allow the table wrapper to shrink so wide tables don't force horizontal page scroll.
  minWidth: 0,
  maxWidth: '100%',
  boxShadow: `0 4px 24px ${alpha(theme.palette.common.black, 0.06)}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  overflowX: 'auto',
  '&::-webkit-scrollbar': {
    width: 8,
    height: 8,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    borderRadius: 4,
    '&:hover': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

// FIGMA STYLED TABLE HEAD (EXACT from Figma: 60px height, 16px padding)
const StyledTableHead = styled(TableHead)(({ theme }) => ({
  '& .MuiTableCell-head': {
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.background.paper, 0.5)
      : neutral[50],  // #F9F9F8 from Figma
    fontFamily: fontFamilyBody,  // Lato from Figma
    fontWeight: 500,
    fontSize: '14px',
    textTransform: 'none',  // No uppercase per Figma
    letterSpacing: 'normal',
    color: theme.palette.mode === 'dark' ? theme.palette.text.secondary : neutral[700],  // #63635E
    borderBottom: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.divider, 0.08) : neutral[200]}`,
    height: FIGMA_TABLE.headerHeight,  // 60px from Figma
    padding: `0 ${FIGMA_TABLE.cellPadding}px`,  // 16px from Figma
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[100],
    },
  },
}))

// FIGMA STYLED TABLE ROW (EXACT from Figma: 60px height)
const StyledTableRow = styled(TableRow, {
  shouldForwardProp: (prop) => !['rowIndex', 'isClickable'].includes(prop),
})(({ theme, rowIndex, isClickable }) => ({
  height: FIGMA_TABLE.rowHeight,  // 60px from Figma
  animation: `${fadeInUp} 0.4s ease-out`,
  animationDelay: `${rowIndex * 0.03}s`,
  animationFillMode: 'both',
  transition: 'all 0.2s ease',
  cursor: isClickable ? 'pointer' : 'default',
  '& .MuiTableCell-body': {
    fontFamily: fontFamilyBody,  // Lato from Figma
    borderBottom: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.divider, 0.05) : neutral[200]}`,
    padding: `0 ${FIGMA_TABLE.cellPadding}px`,  // 16px from Figma
    height: FIGMA_TABLE.rowHeight,  // 60px from Figma
    fontSize: '14px',
    color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[900],  // #21201C
    transition: 'all 0.2s ease',
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : alpha(neutral[100], 0.5),
    '& .MuiTableCell-body': {
      color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[900],
    },
    '& .row-actions': {
      opacity: 1,
      transform: 'translateX(0)',
    },
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    },
  },
  '&:last-child .MuiTableCell-body': {
    borderBottom: 'none',
  },
}))

const RowActionsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  gap: theme.spacing(0.5),
  opacity: 0.5,
  transform: 'translateX(4px)',
  transition: 'all 0.2s ease',
}))

const StyledCheckbox = styled(Checkbox)(({ theme }) => ({
  color: alpha(theme.palette.text.primary, 0.3),
  padding: theme.spacing(0.5),
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  },
  '&.Mui-checked': {
    color: theme.palette.text.primary,
  },
  '&.MuiCheckbox-indeterminate': {
    color: theme.palette.text.primary,
  },
}))

const StyledTableSortLabel = styled(TableSortLabel)(({ theme }) => ({
  color: theme.palette.text.secondary,
  '&:hover': {
    color: theme.palette.text.primary,
  },
  '&.Mui-active': {
    color: theme.palette.text.primary,
    '& .MuiTableSortLabel-icon': {
      color: theme.palette.text.primary,
    },
  },
  '& .MuiTableSortLabel-icon': {
    fontSize: 16,
    transition: 'all 0.2s ease',
  },
}))

const SkeletonRow = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(1.5, 2),
  gap: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  animation: `${pulse} 1.5s infinite ease-in-out`,
}))

const ShimmerSkeleton = styled(Skeleton)(({ theme }) => ({
  background: `linear-gradient(
    90deg,
    ${alpha(theme.palette.text.primary, 0.06)} 0%,
    ${alpha(theme.palette.text.primary, 0.12)} 50%,
    ${alpha(theme.palette.text.primary, 0.06)} 100%
  )`,
  backgroundSize: '200% 100%',
  animation: `${shimmer} 1.5s infinite`,
  borderRadius: 6,
}))

const StyledPagination = styled(TablePagination)(({ theme }) => ({
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  '& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows': {
    fontSize: 14,
    color: theme.palette.text.secondary,
  },
  '& .MuiTablePagination-select': {
    borderRadius: 8,
    fontSize: 14,
  },
  '& .MuiTablePagination-actions': {
    '& .MuiIconButton-root': {
      color: theme.palette.text.secondary,
      '&:hover': {
        backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        color: theme.palette.text.primary,
      },
      '&.Mui-disabled': {
        color: alpha(theme.palette.text.primary, 0.2),
      },
    },
  },
}))

const ExpandableRow = styled(TableRow)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  '& .MuiTableCell-body': {
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  },
}))

// =============================================================================
// HELPERS
// =============================================================================

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) return -1
  if (b[orderBy] > a[orderBy]) return 1
  return 0
}

function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy)
}

const STORAGE_PREFIX = 'neurareport_table_'

function loadPersistedState(key) {
  if (!key) return null
  try {
    const stored = localStorage.getItem(`${STORAGE_PREFIX}${key}`)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

function savePersistedState(key, state) {
  if (!key) return
  try {
    localStorage.setItem(`${STORAGE_PREFIX}${key}`, JSON.stringify(state))
  } catch {
    // Ignore storage errors
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

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
  rowHeight = 'medium', // 'compact', 'medium', 'comfortable'
}) {
  const theme = useTheme()
  // Enable a responsive table layout for phones + tablets (and smaller laptops) to avoid page-level horizontal scrolling.
  const isNarrow = useMediaQuery(theme.breakpoints.down('lg'))
  const persisted = loadPersistedState(persistKey)

  const [order, setOrder] = useState(persisted?.order || defaultSortOrder)
  const [orderBy, setOrderBy] = useState(persisted?.orderBy || defaultSortField || columns[0]?.field)
  const [selected, setSelected] = useState([])
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(persisted?.rowsPerPage || pageSize)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilters, setActiveFilters] = useState(persisted?.filters || {})
  const [expandedRows, setExpandedRows] = useState(new Set())
  const [hiddenColumns, setHiddenColumns] = useState(persisted?.hiddenColumns || [])

  const visibleColumns = useMemo(() => (
    columns.filter((column) => column?.field && !hiddenColumns.includes(column.field))
  ), [columns, hiddenColumns])

  // Persist state
  useEffect(() => {
    if (!persistKey) return
    savePersistedState(persistKey, {
      order,
      orderBy,
      rowsPerPage,
      filters: activeFilters,
      hiddenColumns,
    })
  }, [persistKey, order, orderBy, rowsPerPage, activeFilters, hiddenColumns])

  useEffect(() => {
    setHiddenColumns((prev) => prev.filter((field) => columns.some((col) => col.field === field)))
  }, [columns])

  useEffect(() => {
    if (!visibleColumns.length) return
    if (!visibleColumns.some((column) => column.field === orderBy)) {
      setOrderBy(visibleColumns[0].field)
    }
  }, [visibleColumns, orderBy])

  const handleRequestSort = useCallback((property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }, [order, orderBy])

  const handleSelect = useCallback((id) => {
    const selectedIndex = selected.indexOf(id)
    let newSelected = []

    if (selectedIndex === -1) {
      newSelected = [...selected, id]
    } else {
      newSelected = selected.filter((item) => item !== id)
    }

    setSelected(newSelected)
    onSelectionChangeRef.current?.(newSelected)
  }, [selected])

  const handleToggleExpand = useCallback((id) => {
    setExpandedRows((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const handleToggleColumn = useCallback((field) => {
    if (!field) return
    setHiddenColumns((prev) => {
      const next = new Set(prev)
      if (next.has(field)) {
        next.delete(field)
        return Array.from(next)
      }
      const visibleCount = columns.filter((column) =>
        column?.field && !next.has(column.field)
      ).length
      if (visibleCount <= 1) return prev
      next.add(field)
      return Array.from(next)
    })
  }, [columns])

  const handleResetColumns = useCallback(() => {
    setHiddenColumns([])
  }, [])

  const onSelectionChangeRef = useRef(onSelectionChange)
  onSelectionChangeRef.current = onSelectionChange

  useEffect(() => {
    if (!selectable) return
    const idSet = new Set(data.map((row) => row?.id).filter(Boolean))
    const nextSelected = selected.filter((id) => idSet.has(id))
    if (nextSelected.length !== selected.length) {
      setSelected(nextSelected)
      onSelectionChangeRef.current?.(nextSelected)
    }
  }, [data, selectable, selected])

  const handleChangePage = useCallback((_, newPage) => {
    if (pagination?.onPageChange) {
      pagination.onPageChange(newPage)
      return
    }
    setPage(newPage)
  }, [pagination])

  const handleChangeRowsPerPage = useCallback((event) => {
    const nextValue = parseInt(event.target.value, 10)
    if (pagination?.onRowsPerPageChange) {
      pagination.onRowsPerPageChange(nextValue)
      return
    }
    setRowsPerPage(nextValue)
    setPage(0)
  }, [pagination])

  const handleSearch = useCallback((query) => {
    setSearchQuery(query)
    if (pagination?.onPageChange) {
      pagination.onPageChange(0)
    } else {
      setPage(0)
    }
    onSearch?.(query)
  }, [onSearch, pagination])

  const handleRowKeyDown = useCallback((event, row, rowIndex) => {
    if (event.key === 'Enter' && onRowClick) {
      event.preventDefault()
      onRowClick(row)
      return
    }
    if ((event.key === ' ' || event.key === 'Spacebar') && selectable) {
      event.preventDefault()
      handleSelect(row.id)
      return
    }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      const dir = event.key === 'ArrowDown' ? 1 : -1
      const rows = event.currentTarget.parentElement?.querySelectorAll('tr[data-row-index]')
      const next = rows?.[rowIndex + dir]
      if (next?.focus) next.focus()
    }
  }, [onRowClick, selectable, handleSelect])

  const filteredData = useMemo(() => {
    const filterEntries = Object.entries(activeFilters)
    const baseData = filterEntries.length
      ? data.filter((row) =>
          filterEntries.every(([key, filterValue]) => {
            const cellValue = row[key]
            if (cellValue == null) return false
            if (Array.isArray(cellValue)) return cellValue.includes(filterValue)
            if (typeof cellValue === 'string') {
              return cellValue.toLowerCase() === String(filterValue).toLowerCase()
            }
            return cellValue === filterValue
          })
        )
      : data

    if (!searchQuery) return baseData
    const searchColumns = visibleColumns.length ? visibleColumns : columns
    return baseData.filter((row) =>
      searchColumns.some((col) => {
        const value = row[col.field]
        if (value == null) return false
        return String(value).toLowerCase().includes(searchQuery.toLowerCase())
      })
    )
  }, [data, searchQuery, columns, activeFilters, visibleColumns])

  const sortedData = useMemo(() => {
    return [...filteredData].sort(getComparator(order, orderBy))
  }, [filteredData, order, orderBy])

  const paginatedData = useMemo(() => {
    if (pagination) return sortedData
    return sortedData.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
  }, [sortedData, page, rowsPerPage, pagination])

  const handleSelectAll = useCallback((event) => {
    if (event.target.checked) {
      const newSelected = paginatedData.map((row) => row.id)
      setSelected(newSelected)
      onSelectionChangeRef.current?.(newSelected)
      return
    }
    setSelected([])
    onSelectionChangeRef.current?.([])
  }, [paginatedData])

  const isSelected = (id) => selected.includes(id)
  const numSelected = selected.length
  const rowCount = pagination?.total ?? filteredData.length
  const pageRowCount = useMemo(() =>
    pagination ? paginatedData.length : rowCount,
    [pagination, paginatedData, rowCount]
  )
  const effectivePage = pagination?.page ?? page
  const effectiveRowsPerPage = pagination?.rowsPerPage ?? rowsPerPage

  const exportColumns = useMemo(
    () => visibleColumns.filter((column) => column?.exportable !== false && column?.field),
    [visibleColumns],
  )

  const exportRows = useMemo(() => sortedData, [sortedData])

  const getExportValue = useCallback((row, column) => {
    if (typeof column.exportValue === 'function') {
      return column.exportValue(row[column.field], row)
    }
    if (typeof column.valueGetter === 'function') {
      return column.valueGetter(row)
    }
    return row[column.field]
  }, [])

  const formatCsvValue = useCallback((value) => {
    if (value === null || value === undefined) return ''
    if (value instanceof Date) return value.toISOString()
    const text = typeof value === 'string' ? value : JSON.stringify(value)
    const escaped = text.replace(/"/g, '""')
    if (/[",\n\r]/.test(escaped)) {
      return `"${escaped}"`
    }
    return escaped
  }, [])

  const buildExportFileName = useCallback((extension) => {
    const base = String(title || 'table-export').trim().toLowerCase()
    const safeBase = base.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'table-export'
    return `${safeBase}.${extension}`
  }, [title])

  const downloadFile = useCallback((content, filename, type) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.rel = 'noopener'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }, [])

  const handleExportCsv = useCallback(() => {
    if (!exportColumns.length || !exportRows.length) return
    const headers = exportColumns.map((column) => column.headerName || column.field)
    const rows = exportRows.map((row) =>
      exportColumns.map((column) => formatCsvValue(getExportValue(row, column)))
    )
    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n')
    downloadFile(csv, buildExportFileName('csv'), 'text/csv;charset=utf-8;')
  }, [exportColumns, exportRows, formatCsvValue, getExportValue, downloadFile, buildExportFileName])

  const handleExportJson = useCallback(() => {
    if (!exportColumns.length || !exportRows.length) return
    const records = exportRows.map((row) => {
      const record = {}
      exportColumns.forEach((column) => {
        const key = column.field || column.headerName
        record[key] = getExportValue(row, column) ?? null
      })
      return record
    })
    const json = JSON.stringify(records, null, 2)
    downloadFile(json, buildExportFileName('json'), 'application/json;charset=utf-8;')
  }, [exportColumns, exportRows, getExportValue, downloadFile, buildExportFileName])

  const cellPadding = {
    compact: 1,
    medium: 1.5,
    comfortable: 2,
  }[rowHeight] || 1.5

  // Empty state
  if (!loading && data.length === 0 && emptyState) {
    // Avoid rendering duplicate CTAs when both toolbar actions and emptyState define the same label.
    // This commonly happens during first-load (empty list before data arrives) and creates confusing UX
    // + strict-mode selector collisions in e2e.
    const emptyActionLabel = emptyState?.actionLabel
    const actionsForEmpty =
      emptyActionLabel && Array.isArray(actions)
        ? actions.filter((action) => action?.label !== emptyActionLabel)
        : actions

    return (
      <TableWrapper>
        <DataTableToolbar
          title={title}
          subtitle={subtitle}
          searchPlaceholder={searchPlaceholder}
          onSearch={handleSearch}
          filters={filters}
          actions={actionsForEmpty}
          bulkActions={bulkActions}
          onBulkDelete={onBulkDelete}
          numSelected={numSelected}
          onFiltersChange={setActiveFilters}
          columns={columns}
          hiddenColumns={hiddenColumns}
          onToggleColumn={handleToggleColumn}
          onResetColumns={handleResetColumns}
          onExportCsv={handleExportCsv}
          onExportJson={handleExportJson}
          exportCsvDisabled={!exportColumns.length || !exportRows.length}
          exportJsonDisabled={!exportColumns.length || !exportRows.length}
        />
        <DataTableEmptyState {...emptyState} />
      </TableWrapper>
    )
  }

  return (
    <TableWrapper>
      <DataTableToolbar
        title={title}
        subtitle={subtitle}
        searchPlaceholder={searchPlaceholder}
        onSearch={handleSearch}
        filters={filters}
        actions={actions}
        bulkActions={bulkActions}
        onBulkDelete={onBulkDelete}
        numSelected={numSelected}
        onFiltersChange={setActiveFilters}
        columns={columns}
        hiddenColumns={hiddenColumns}
        onToggleColumn={handleToggleColumn}
        onResetColumns={handleResetColumns}
        onExportCsv={handleExportCsv}
        onExportJson={handleExportJson}
        exportCsvDisabled={!exportColumns.length || !exportRows.length}
        exportJsonDisabled={!exportColumns.length || !exportRows.length}
      />

      <StyledTableContainer sx={{ maxHeight: stickyHeader ? 600 : 'none' }}>
        <Table
          stickyHeader={stickyHeader}
          size={rowHeight === 'compact' ? 'small' : 'medium'}
          sx={{
            width: '100%',
            tableLayout: 'auto',
          }}
        >
          <StyledTableHead>
            <TableRow>
              {expandable && <TableCell sx={{ width: 48 }} />}
              {selectable && (
                <TableCell padding="checkbox" sx={{ width: 48 }}>
                  <StyledCheckbox
                    indeterminate={numSelected > 0 && numSelected < pageRowCount}
                    checked={pageRowCount > 0 && numSelected === pageRowCount}
                    onChange={handleSelectAll}
                    inputProps={{ 'aria-label': 'Select all rows' }}
                  />
                </TableCell>
              )}
              {visibleColumns.map((column) => (
                <TableCell
                  key={column.field}
                  align={column.align || 'left'}
                  sx={{
                    width: column.width,
                    minWidth: isNarrow ? (column.minWidth || column.width || 80) : column.minWidth,
                    whiteSpace: 'nowrap',
                  }}
                  sortDirection={orderBy === column.field ? order : false}
                >
                  {column.sortable !== false ? (
                    <StyledTableSortLabel
                      active={orderBy === column.field}
                      direction={orderBy === column.field ? order : 'asc'}
                      onClick={() => handleRequestSort(column.field)}
                    >
                      {column.headerName}
                    </StyledTableSortLabel>
                  ) : (
                    column.headerName
                  )}
                </TableCell>
              ))}
              {rowActions && <TableCell align="right" sx={{ width: 80 }} />}
            </TableRow>
          </StyledTableHead>

          <TableBody>
            {loading ? (
              // Loading skeleton
              Array.from({ length: rowsPerPage }).map((_, index) => (
                <TableRow key={index}>
                  {expandable && (
                    <TableCell sx={{ p: cellPadding }}>
                      <ShimmerSkeleton variant="circular" width={24} height={24} />
                    </TableCell>
                  )}
                  {selectable && (
                    <TableCell padding="checkbox">
                      <ShimmerSkeleton variant="rectangular" width={18} height={18} sx={{ borderRadius: 0.5 }} />
                    </TableCell>
                  )}
                  {visibleColumns.map((column) => (
                    <TableCell
                      key={column.field}
                      sx={{
                        p: cellPadding,
                        ...(isNarrow ? { whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 0 } : null),
                      }}
                    >
                      <ShimmerSkeleton
                        variant="text"
                        width={column.width || '80%'}
                        height={20}
                      />
                    </TableCell>
                  ))}
                  {rowActions && (
                    <TableCell sx={{ p: cellPadding }}>
                      <ShimmerSkeleton variant="circular" width={24} height={24} />
                    </TableCell>
                  )}
                </TableRow>
              ))
            ) : (
              paginatedData.map((row, rowIndex) => {
                const isItemSelected = isSelected(row.id)
                const isExpanded = expandedRows.has(row.id)
                const rowKey = row.id ?? rowIndex

                return (
                  <Fragment key={rowKey}>
                    <StyledTableRow
                      hover
                      onClick={() => onRowClick?.(row)}
                      onKeyDown={(event) => handleRowKeyDown(event, row, rowIndex)}
                      selected={isItemSelected}
                      data-row-index={rowIndex}
                      data-testid={`table-row-${rowIndex}`}
                      rowIndex={rowIndex}
                      isClickable={!!onRowClick}
                      tabIndex={onRowClick || selectable ? 0 : -1}
                      role={onRowClick ? 'button' : undefined}
                      aria-selected={selectable ? isItemSelected : undefined}
                    >
                      {expandable && (
                        <TableCell sx={{ p: cellPadding }}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleToggleExpand(row.id)
                            }}
                            sx={{
                              transition: 'all 0.2s ease',
                              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                              color: isExpanded ? 'text.primary' : 'text.secondary',
                            }}
                          >
                            <ExpandIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      )}
                      {selectable && (
                        <TableCell padding="checkbox">
                          <StyledCheckbox
                            checked={isItemSelected}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleSelect(row.id)
                            }}
                            inputProps={{ 'aria-label': `Select row ${row.id}` }}
                          />
                        </TableCell>
                      )}
                      {visibleColumns.map((column) => (
                        <TableCell
                          key={column.field}
                          align={column.align || 'left'}
                          data-testid={`table-cell-${column.field}`}
                          sx={{
                            p: cellPadding,
                            ...(isNarrow ? { whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 0 } : null),
                          }}
                        >
                          {column.renderCell
                            ? column.renderCell(row[column.field], row)
                            : row[column.field]}
                        </TableCell>
                      ))}
                      {rowActions && (
                        <TableCell align="right" onClick={(e) => e.stopPropagation()} sx={{ p: cellPadding }}>
                          <RowActionsContainer className="row-actions">
                            {rowActions(row)}
                          </RowActionsContainer>
                        </TableCell>
                      )}
                    </StyledTableRow>

                    {/* Expandable row content */}
                    {expandable && renderExpandedRow && (
                      <ExpandableRow>
                        <TableCell
                          colSpan={visibleColumns.length + (selectable ? 2 : 1) + (rowActions ? 1 : 0)}
                          sx={{ p: 0 }}
                        >
                          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                            <Box sx={{ p: 3 }}>{renderExpandedRow(row)}</Box>
                          </Collapse>
                        </TableCell>
                      </ExpandableRow>
                    )}
                  </Fragment>
                )
              })
            )}
          </TableBody>
        </Table>
      </StyledTableContainer>

      <StyledPagination
        rowsPerPageOptions={pageSizeOptions}
        component="div"
        count={rowCount}
        rowsPerPage={effectiveRowsPerPage}
        page={effectivePage}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Rows per page:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count}`}
      />
    </TableWrapper>
  )
}

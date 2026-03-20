/**
 * Custom hook: manages DataTable state — sorting, selection, pagination,
 * filtering, search, column visibility, expanded rows, and persistence.
 */
import { useState, useMemo, useCallback, useEffect, useRef } from 'react'
import { loadPersistedState, savePersistedState, getComparator } from '../DataTableStyledComponents'

export function useDataTableState({
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
}) {
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

  const onSelectionChangeRef = useRef(onSelectionChange)
  onSelectionChangeRef.current = onSelectionChange

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

  // Sync selection with data changes
  useEffect(() => {
    if (!selectable) return
    const idSet = new Set(data.map((row) => row?.id).filter(Boolean))
    const nextSelected = selected.filter((id) => idSet.has(id))
    if (nextSelected.length !== selected.length) {
      setSelected(nextSelected)
      onSelectionChangeRef.current?.(nextSelected)
    }
  }, [data, selectable, selected])

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

  const onRowClickRef = useRef(onRowClick)
  onRowClickRef.current = onRowClick

  const handleRowKeyDown = useCallback((event, row, rowIndex) => {
    if (event.key === 'Enter' && onRowClickRef.current) {
      event.preventDefault()
      onRowClickRef.current(row)
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
  }, [selectable, handleSelect])

  // Derived data
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
  const pageRowCount = pagination ? paginatedData.length : rowCount
  const effectivePage = pagination?.page ?? page
  const effectiveRowsPerPage = pagination?.rowsPerPage ?? rowsPerPage

  return {
    order,
    orderBy,
    selected,
    page,
    rowsPerPage,
    searchQuery,
    activeFilters,
    expandedRows,
    hiddenColumns,
    visibleColumns,
    filteredData,
    sortedData,
    paginatedData,
    numSelected,
    rowCount,
    pageRowCount,
    effectivePage,
    effectiveRowsPerPage,
    isSelected,
    handleRequestSort,
    handleSelect,
    handleSelectAll,
    handleToggleExpand,
    handleToggleColumn,
    handleResetColumns,
    handleChangePage,
    handleChangeRowsPerPage,
    handleSearch,
    handleRowKeyDown,
    setActiveFilters,
  }
}

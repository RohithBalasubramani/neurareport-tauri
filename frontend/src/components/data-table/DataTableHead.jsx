/**
 * DataTable header row with sort labels and checkboxes
 */
import { TableRow, TableCell } from '@mui/material'
import {
  StyledTableHead,
  StyledTableSortLabel,
  StyledCheckbox,
} from './DataTableStyledComponents'

export default function DataTableHead({
  visibleColumns,
  expandable,
  selectable,
  rowActions,
  orderBy,
  order,
  numSelected,
  pageRowCount,
  onRequestSort,
  onSelectAll,
  isNarrow,
}) {
  return (
    <StyledTableHead>
      <TableRow>
        {expandable && <TableCell sx={{ width: 48 }} />}
        {selectable && (
          <TableCell padding="checkbox" sx={{ width: 48 }}>
            <StyledCheckbox
              indeterminate={numSelected > 0 && numSelected < pageRowCount}
              checked={pageRowCount > 0 && numSelected === pageRowCount}
              onChange={onSelectAll}
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
                onClick={() => onRequestSort(column.field)}
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
  )
}

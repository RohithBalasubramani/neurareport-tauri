/**
 * DataTable body: loading skeleton and data rows
 */
import { Fragment } from 'react'
import {
  TableBody,
  TableCell,
  TableRow,
  IconButton,
  Collapse,
  Box,
} from '@mui/material'
import { KeyboardArrowDown as ExpandIcon } from '@mui/icons-material'
import {
  StyledTableRow,
  StyledCheckbox,
  RowActionsContainer,
  ShimmerSkeleton,
  ExpandableRow,
} from './DataTableStyledComponents'

export default function DataTableBodyContent({
  loading,
  paginatedData,
  visibleColumns,
  expandable,
  selectable,
  rowActions,
  renderExpandedRow,
  onRowClick,
  onRowKeyDown,
  isSelected,
  expandedRows,
  handleToggleExpand,
  handleSelect,
  cellPadding,
  rowsPerPage,
  isNarrow,
}) {
  if (loading) {
    return (
      <TableBody>
        {Array.from({ length: rowsPerPage }).map((_, index) => (
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
        ))}
      </TableBody>
    )
  }

  return (
    <TableBody>
      {paginatedData.map((row, rowIndex) => {
        const isItemSelected = isSelected(row.id)
        const isExpanded = expandedRows.has(row.id)
        const rowKey = row.id ?? rowIndex

        return (
          <Fragment key={rowKey}>
            <StyledTableRow
              hover
              onClick={() => onRowClick?.(row)}
              onKeyDown={(event) => onRowKeyDown(event, row, rowIndex)}
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
      })}
    </TableBody>
  )
}

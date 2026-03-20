/**
 * Table section for HistoryPage (loading, empty, or data table)
 */
import React from 'react'
import {
  Typography,
  CircularProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { DataTable } from '@/components/data-table'
import {
  TableContainer,
  EmptyStateContainer,
  EmptyIcon,
  SecondaryButton,
} from './HistoryStyledComponents'

export default function HistoryTableSection({
  history,
  loading,
  columns,
  onRowClick,
  onSelectionChange,
  bulkActions,
  page,
  rowsPerPage,
  total,
  onPageChange,
  onRowsPerPageChange,
  onNavigateToReports,
}) {
  return (
    <TableContainer>
      {loading && history.length === 0 ? (
        <EmptyStateContainer>
          <CircularProgress size={40} />
          <Typography sx={{ mt: 2, fontSize: '0.875rem', color: 'text.secondary' }}>
            Loading history...
          </Typography>
        </EmptyStateContainer>
      ) : history.length === 0 ? (
        <EmptyStateContainer>
          <EmptyIcon />
          <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.secondary' }}>
            No report history found
          </Typography>
          <Typography sx={{ fontSize: '0.875rem', color: 'text.disabled', mt: 0.5 }}>
            Generate reports to see them here
          </Typography>
          <SecondaryButton
            variant="outlined"
            onClick={onNavigateToReports}
            sx={{ mt: 3 }}
            startIcon={<AddIcon />}
          >
            Generate Report
          </SecondaryButton>
        </EmptyStateContainer>
      ) : (
        <DataTable
          columns={columns}
          data={history}
          loading={loading}
          searchPlaceholder="Search reports..."
          onRowClick={onRowClick}
          selectable
          onSelectionChange={onSelectionChange}
          bulkActions={bulkActions}
          pagination={{
            page,
            rowsPerPage,
            total,
            onPageChange,
            onRowsPerPageChange,
          }}
        />
      )}
    </TableContainer>
  )
}

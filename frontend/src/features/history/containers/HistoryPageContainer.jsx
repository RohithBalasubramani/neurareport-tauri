/**
 * Premium History Page
 * Sophisticated report history with glassmorphism and animations
 */
import React, { useMemo } from 'react'
import {
  Box,
  Typography,
  Stack,
  CircularProgress,
  Alert,
  Tooltip,
  useTheme,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import { ConfirmModal } from '@/components/modal'
import { RefreshButton } from '@/styles'
import { useHistoryPageState } from '../hooks/useHistoryPageState'
import { PageContainer, PageHeader, PageTitle, PrimaryButton } from '../components/HistoryStyledComponents'
import { getHistoryColumns } from '../components/HistoryColumns'
import HistoryFilters from '../components/HistoryFilters'
import HistoryTableSection from '../components/HistoryTableSection'

export default function HistoryPage() {
  const theme = useTheme()
  const state = useHistoryPageState()

  const columns = useMemo(
    () => getHistoryColumns(theme, state.handleDownloadClick),
    [theme, state.handleDownloadClick]
  )

  const bulkActions = useMemo(() => [
    {
      label: 'Delete Selected',
      icon: <DeleteIcon sx={{ fontSize: 16 }} />,
      color: 'error',
      onClick: state.handleBulkDeleteOpen,
    },
  ], [state.handleBulkDeleteOpen])

  return (
    <PageContainer>
      {/* Header */}
      <PageHeader>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <PageTitle>Report History</PageTitle>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              View and download previously generated reports
            </Typography>
          </Box>
          <Stack direction="row" spacing={1.5}>
            <Tooltip title="Refresh history">
              <span>
                <RefreshButton
                  onClick={state.handleRefresh}
                  disabled={state.loading}
                  aria-label="Refresh history"
                >
                  {state.loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                </RefreshButton>
              </span>
            </Tooltip>
            <PrimaryButton
              onClick={() => state.handleNavigate('/reports', 'Open reports')}
              startIcon={<AddIcon />}
            >
              Generate New
            </PrimaryButton>
          </Stack>
        </Stack>
      </PageHeader>

      <Alert severity="info" sx={{ mb: 2, borderRadius: 1 }}>
        History lists completed report outputs. Deleting a history record only removes the entry here; downloaded files
        are not affected.
      </Alert>

      <HistoryFilters
        statusFilter={state.statusFilter}
        onStatusFilterChange={state.handleStatusFilterChange}
        templateFilter={state.templateFilter}
        onTemplateFilterChange={state.handleTemplateFilterChange}
        templates={state.templates}
      />

      <HistoryTableSection
        history={state.history}
        loading={state.loading}
        columns={columns}
        onRowClick={state.handleRowClick}
        onSelectionChange={state.handleSelectionChange}
        bulkActions={bulkActions}
        page={state.page}
        rowsPerPage={state.rowsPerPage}
        total={state.total}
        onPageChange={state.handlePageChange}
        onRowsPerPageChange={state.handleRowsPerPageChange}
        onNavigateToReports={() => state.handleNavigate('/reports', 'Open reports')}
      />

      <ConfirmModal
        open={state.bulkDeleteOpen}
        onClose={state.handleBulkDeleteClose}
        onConfirm={state.handleBulkDeleteConfirm}
        title="Delete History Records"
        message={`Remove ${state.selectedIds.length} history record${state.selectedIds.length !== 1 ? 's' : ''}? You can undo within a few seconds. Downloaded files are not affected.`}
        confirmLabel="Delete"
        severity="error"
        loading={state.bulkDeleting}
      />
    </PageContainer>
  )
}

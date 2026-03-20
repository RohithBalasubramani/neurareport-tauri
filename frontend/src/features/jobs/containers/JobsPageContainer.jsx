/**
 * Premium Jobs Page
 * Sophisticated job progress tracking with glassmorphism and animations
 */
import { Alert, Tooltip } from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import WorkIcon from '@mui/icons-material/Work'
import { DataTable } from '@/components/data-table'
import { useJobsData } from '../hooks/useJobsData.jsx'
import { PageContainer, MoreActionsButton } from '../components/JobsStyledComponents'
import JobActionsMenu from '../components/JobActionsMenu'
import JobDetailsDialog from '../components/JobDetailsDialog'

export default function JobsPage() {
  const {
    jobs,
    loading,
    cancelConfirmOpen,
    menuAnchor,
    menuJob,
    detailsDialogOpen,
    detailsJob,
    retrying,
    selectedIds,
    bulkCancelOpen,
    bulkDeleteOpen,
    bulkActionLoading,
    columns,
    filters,
    activeSelectedCount,
    bulkActions,
    activeJobsCount,
    handleNavigate,
    handleOpenMenu,
    handleCloseMenu,
    handleRefresh,
    handleCancelClick,
    handleCancelConfirm,
    handleDownload,
    handleViewDetails,
    handleRowClick,
    handleRetry,
    handleBulkCancelConfirm,
    handleBulkDeleteOpen,
    handleSelectionChange,
    handleCancelConfirmClose,
    handleBulkCancelClose,
    handleBulkDeleteClose,
    handleDetailsClose,
    handleDetailsDownload,
    handleDetailsRetry,
    handleBulkDeleteConfirm,
  } = useJobsData()

  return (
    <PageContainer>
      <Alert severity="info" sx={{ mb: 2, borderRadius: 1 }}>
        Jobs track background report runs. Removing a job only clears it from this list; downloaded files remain in
        History.
      </Alert>
      <DataTable
        title="Report Progress"
        subtitle={activeJobsCount > 0 ? `${activeJobsCount} report${activeJobsCount > 1 ? 's' : ''} generating` : 'All reports complete'}
        columns={columns}
        data={jobs}
        loading={loading}
        searchPlaceholder="Search reports..."
        filters={filters}
        selectable
        onSelectionChange={handleSelectionChange}
        onRowClick={handleRowClick}
        bulkActions={bulkActions}
        onBulkDelete={handleBulkDeleteOpen}
        actions={[
          {
            label: 'Refresh',
            icon: <RefreshIcon sx={{ fontSize: 18 }} />,
            variant: 'outlined',
            onClick: handleRefresh,
          },
        ]}
        onRefresh={handleRefresh}
        rowActions={(row) => (
          <Tooltip title="More actions">
            <MoreActionsButton
              size="small"
              onClick={(e) => handleOpenMenu(e, row)}
              aria-label="More actions"
            >
              <MoreVertIcon sx={{ fontSize: 18 }} />
            </MoreActionsButton>
          </Tooltip>
        )}
        emptyState={{
          icon: WorkIcon,
          title: 'No reports in progress',
          description: 'When you create a report, you can track its progress here.',
          actionLabel: 'Create Report',
          onAction: () => handleNavigate('/reports', 'Open reports'),
        }}
      />

      <JobActionsMenu
        menuAnchor={menuAnchor}
        menuJob={menuJob}
        retrying={retrying}
        cancelConfirmOpen={cancelConfirmOpen}
        bulkCancelOpen={bulkCancelOpen}
        bulkDeleteOpen={bulkDeleteOpen}
        bulkActionLoading={bulkActionLoading}
        activeSelectedCount={activeSelectedCount}
        selectedIds={selectedIds}
        jobs={jobs}
        onCloseMenu={handleCloseMenu}
        onViewDetails={handleViewDetails}
        onDownload={handleDownload}
        onRetry={handleRetry}
        onCancelClick={handleCancelClick}
        onCancelConfirm={handleCancelConfirm}
        onCancelConfirmClose={handleCancelConfirmClose}
        onBulkCancelConfirm={handleBulkCancelConfirm}
        onBulkCancelClose={handleBulkCancelClose}
        onBulkDeleteConfirm={handleBulkDeleteConfirm}
        onBulkDeleteClose={handleBulkDeleteClose}
      />

      <JobDetailsDialog
        open={detailsDialogOpen}
        detailsJob={detailsJob}
        retrying={retrying}
        onClose={handleDetailsClose}
        onDownload={handleDetailsDownload}
        onRetry={handleDetailsRetry}
      />
    </PageContainer>
  )
}

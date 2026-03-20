/**
 * Job Actions Menu & Confirm Modals
 */
import { ListItemIcon, ListItemText } from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import DownloadIcon from '@mui/icons-material/Download'
import ReplayIcon from '@mui/icons-material/Replay'
import CancelIcon from '@mui/icons-material/Cancel'
import { canRetryJob, canCancelJob, JobStatus } from '@/utils/jobStatus'
import { ConfirmModal } from '@/components/modal'
import { StyledMenu, StyledMenuItem } from './JobsStyledComponents'

export default function JobActionsMenu({
  menuAnchor,
  menuJob,
  retrying,
  cancelConfirmOpen,
  bulkCancelOpen,
  bulkDeleteOpen,
  bulkActionLoading,
  activeSelectedCount,
  selectedIds,
  jobs,
  onCloseMenu,
  onViewDetails,
  onDownload,
  onRetry,
  onCancelClick,
  onCancelConfirm,
  onCancelConfirmClose,
  onBulkCancelConfirm,
  onBulkCancelClose,
  onBulkDeleteConfirm,
  onBulkDeleteClose,
}) {
  return (
    <>
      <StyledMenu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={onCloseMenu}
      >
        <StyledMenuItem onClick={onViewDetails}>
          <ListItemIcon><VisibilityIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>View Details</ListItemText>
        </StyledMenuItem>
        {menuJob?.status === JobStatus.COMPLETED && menuJob?.artifacts?.html_url && (
          <StyledMenuItem onClick={onDownload}>
            <ListItemIcon><DownloadIcon sx={{ fontSize: 16 }} /></ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Download</ListItemText>
          </StyledMenuItem>
        )}
        {canRetryJob(menuJob?.status) && (
          <StyledMenuItem onClick={onRetry} disabled={retrying}>
            <ListItemIcon><ReplayIcon sx={{ fontSize: 16 }} /></ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>
              {retrying ? 'Retrying...' : 'Retry'}
            </ListItemText>
          </StyledMenuItem>
        )}
        {canCancelJob(menuJob?.status) && (
          <StyledMenuItem onClick={onCancelClick} sx={{ color: 'text.secondary' }}>
            <ListItemIcon><CancelIcon sx={{ fontSize: 16, color: 'text.secondary' }} /></ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Cancel</ListItemText>
          </StyledMenuItem>
        )}
      </StyledMenu>

      <ConfirmModal
        open={cancelConfirmOpen}
        onClose={onCancelConfirmClose}
        onConfirm={onCancelConfirm}
        title="Cancel Job"
        message="Are you sure you want to cancel this job? This action cannot be undone."
        confirmLabel="Cancel Job"
        severity="warning"
      />

      <ConfirmModal
        open={bulkCancelOpen}
        onClose={onBulkCancelClose}
        onConfirm={onBulkCancelConfirm}
        title="Cancel Jobs"
        message={`Cancel ${activeSelectedCount} running job${activeSelectedCount !== 1 ? 's' : ''}?`}
        confirmLabel="Cancel Jobs"
        severity="warning"
        loading={bulkActionLoading}
      />

      <ConfirmModal
        open={bulkDeleteOpen}
        onClose={onBulkDeleteClose}
        onConfirm={onBulkDeleteConfirm}
        title="Delete Jobs"
        message={(() => {
          const selectedJobs = jobs.filter((j) => selectedIds.includes(j.id))
          const names = selectedJobs.slice(0, 3).map((j) => j.templateName || j.id?.slice(0, 8) || 'Unknown')
          const namesList = names.join(', ')
          const remaining = selectedIds.length - 3
          const suffix = remaining > 0 ? ` and ${remaining} more` : ''
          return `Remove ${selectedIds.length} job${selectedIds.length !== 1 ? 's' : ''} (${namesList}${suffix}) from history? You can undo within a few seconds. Downloaded files are not affected.`
        })()}
        confirmLabel="Delete Jobs"
        severity="error"
        loading={bulkActionLoading}
      />
    </>
  )
}

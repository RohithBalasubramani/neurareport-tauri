/**
 * Premium Schedules Page
 * Slim orchestrator that delegates to hooks and sub-components.
 */
import {
  Container, IconButton, Tooltip, Alert, Zoom,
} from '@mui/material'
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material'
import { DataTable } from '@/components/data-table'
import { ConfirmModal } from '@/components/modal'
import { PageContainer } from '../components/ScheduleStyles'
import ScheduleDialog from '../components/ScheduleDialog'
import ScheduleActionMenu from '../components/ScheduleActionMenu'
import SchedulerStatusBannerView from '../components/SchedulerStatusBannerView'
import { useSchedules } from '../hooks/useSchedules'

export default function SchedulesPage() {
  const s = useSchedules()

  return (
    <PageContainer>
      <Container maxWidth="xl">
        <SchedulerStatusBannerView schedulerStatus={s.schedulerStatus} />
        <Alert severity="info" sx={{ mb: 2, borderRadius: 1 }}>
          Schedules create future report runs. Progress appears in Jobs and finished reports show up in History.
        </Alert>
        <DataTable
          title="Scheduled Reports"
          subtitle="Automate report generation on a schedule"
          columns={s.columns}
          data={s.schedules}
          loading={s.loading}
          searchPlaceholder="Search schedules..."
          filters={s.filters}
          actions={[
            {
              label: 'Create Schedule',
              icon: <AddIcon />,
              variant: 'contained',
              onClick: s.handleAddSchedule,
              disabled: !s.canCreateSchedule,
            },
          ]}
          rowActions={(row) => (
            <Tooltip title="More actions" arrow TransitionComponent={Zoom}>
              <IconButton size="small" onClick={(e) => s.handleOpenMenu(e, row)} aria-label="More actions">
                <MoreVertIcon />
              </IconButton>
            </Tooltip>
          )}
          emptyState={{
            icon: ScheduleIcon,
            title: 'No schedules yet',
            description: 'Create a schedule to automatically generate reports on a recurring basis.',
            actionLabel: 'Create Schedule',
            onAction: s.handleAddSchedule,
          }}
        />

        <ScheduleActionMenu
          anchorEl={s.menuAnchor}
          onClose={s.handleCloseMenu}
          menuScheduleActive={s.menuScheduleActive}
          onRunNow={s.handleRunNow}
          onEdit={s.handleEditSchedule}
          onToggleEnabled={s.handleToggleEnabled}
          onDelete={s.handleDeleteClick}
        />

        <ScheduleDialog
          open={s.dialogOpen}
          onClose={() => s.setDialogOpen(false)}
          schedule={s.editingSchedule}
          templates={s.schedulableTemplates}
          connections={s.savedConnections}
          defaultTemplateId={s.defaultTemplateId}
          defaultConnectionId={s.defaultConnectionId}
          onSave={s.handleSaveSchedule}
          onError={(msg) => s.toast.show(msg, 'error')}
        />

        <ConfirmModal
          open={s.deleteConfirmOpen}
          onClose={() => s.setDeleteConfirmOpen(false)}
          onConfirm={s.handleDeleteConfirm}
          title="Delete Schedule"
          message={`Remove "${s.deletingSchedule?.name || s.deletingSchedule?.id}"? You can undo within a few seconds. This stops future runs; past downloads remain in History.`}
          confirmLabel="Delete"
          severity="error"
        />
      </Container>
    </PageContainer>
  )
}

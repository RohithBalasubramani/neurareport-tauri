import {
  Typography, Stack, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { SCHEDULE_FREQUENCY_OPTIONS } from '../utils/templatesPaneUtils'

export default function ScheduleDialogs({
  editingSchedule,
  editScheduleFields,
  setEditScheduleFields,
  scheduleUpdating,
  handleCloseEditSchedule,
  handleUpdateSchedule,
  deleteScheduleConfirmOpen,
  setDeleteScheduleConfirmOpen,
  scheduleToDelete,
  setScheduleToDelete,
  deletingScheduleId,
  handleDeleteScheduleConfirm,
}) {
  return (
    <>
      {/* Edit Schedule Dialog */}
      <Dialog open={Boolean(editingSchedule)} onClose={handleCloseEditSchedule} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Schedule</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Schedule name"
              value={editScheduleFields.name || ''}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
              size="small"
            />
            <TextField
              select
              label="Frequency"
              value={editScheduleFields.frequency || 'daily'}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, frequency: e.target.value }))}
              fullWidth
              size="small"
            >
              {SCHEDULE_FREQUENCY_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={editScheduleFields.active !== false ? 'active' : 'paused'}
              onChange={(e) => setEditScheduleFields((prev) => ({ ...prev, active: e.target.value === 'active' }))}
              fullWidth
              size="small"
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="paused">Paused</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditSchedule} disabled={scheduleUpdating}>
            Cancel
          </Button>
          <Button onClick={handleUpdateSchedule} variant="contained" disabled={scheduleUpdating}>
            {scheduleUpdating ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={deleteScheduleConfirmOpen}
        onClose={() => {
          setDeleteScheduleConfirmOpen(false)
          setScheduleToDelete(null)
        }}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Delete Schedule</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Delete "{scheduleToDelete?.name || scheduleToDelete?.template_name || scheduleToDelete?.template_id}"?
            You can undo within a few seconds. This stops future runs; past downloads remain in History.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setDeleteScheduleConfirmOpen(false)
              setScheduleToDelete(null)
            }}
            disabled={Boolean(deletingScheduleId)}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleDeleteScheduleConfirm}
            disabled={Boolean(deletingScheduleId)}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

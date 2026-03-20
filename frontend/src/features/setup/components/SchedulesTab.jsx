import {
  Box, Typography, Stack, Button, TextField, Chip, LinearProgress,
  MenuItem, Paper, Alert, alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import {
  SCHEDULE_FREQUENCY_OPTIONS,
  formatScheduleDate,
} from '../utils/templatesPaneUtils'

export default function SchedulesTab({
  schedules,
  schedulesLoading,
  scheduleSaving,
  deletingScheduleId,
  scheduleName,
  setScheduleName,
  scheduleFrequency,
  setScheduleFrequency,
  canSchedule,
  onCreateSchedule,
  handleDeleteScheduleRequest,
  handleOpenEditSchedule,
}) {
  return (
    <Box sx={{ px: 2, pb: 2 }}>
      <Stack spacing={2}>
        <Alert severity="info" sx={{ borderRadius: 1 }}>
          Schedules create future report runs. Deleting a schedule stops future runs and does not remove past downloads.
        </Alert>
        {/* Create Schedule */}
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Create New Schedule
          </Typography>
          <Stack spacing={2}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems={{ md: 'flex-end' }}>
              <TextField
                label="Schedule name (optional)"
                value={scheduleName}
                onChange={(e) => setScheduleName(e.target.value)}
                size="small"
                sx={{ flex: 1 }}
              />
              <TextField
                select
                label="Frequency"
                value={scheduleFrequency}
                onChange={(e) => setScheduleFrequency(e.target.value)}
                size="small"
                sx={{ minWidth: 150 }}
              >
                {SCHEDULE_FREQUENCY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
              <Button
                variant="contained"
                onClick={onCreateSchedule}
                disabled={!canSchedule || scheduleSaving}
                sx={{ whiteSpace: 'nowrap', bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
              >
                {scheduleSaving ? 'Creating...' : 'Create Schedule'}
              </Button>
            </Stack>
            {!canSchedule && (
              <Typography variant="caption" color="text.secondary">
                Select exactly one design, set a date range, and connect to a database to create a schedule.
              </Typography>
            )}
          </Stack>
        </Paper>

        {/* Existing Schedules */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <Typography variant="subtitle2" fontWeight={600}>Existing Schedules</Typography>
            {schedulesLoading && <LinearProgress sx={{ flex: 1, height: 4, borderRadius: 2 }} />}
          </Stack>

          {!schedulesLoading && schedules.length === 0 && (
            <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No schedules yet. Create one above.
              </Typography>
            </Paper>
          )}

          {!schedulesLoading && schedules.length > 0 && (
            <Stack spacing={1}>
              {schedules.map((schedule) => (
                <Paper
                  key={schedule.id}
                  variant="outlined"
                  sx={{ p: 1.5, borderRadius: 1.5 }}
                >
                  <Stack direction={{ xs: 'column', md: 'row' }} alignItems={{ md: 'center' }} spacing={1.5} justifyContent="space-between">
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography variant="subtitle2" noWrap>
                          {schedule.name || schedule.template_name || schedule.template_id}
                        </Typography>
                        {schedule.active === false && (
                          <Chip size="small" label="Paused" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                        )}
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        {schedule.frequency || 'custom'} {'\u2022'} Next: {formatScheduleDate(schedule.next_run_at)}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleOpenEditSchedule(schedule)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleDeleteScheduleRequest(schedule)}
                        disabled={deletingScheduleId === schedule.id}
                        sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3) }}
                      >
                        {deletingScheduleId === schedule.id ? '...' : 'Delete'}
                      </Button>
                    </Stack>
                  </Stack>
                </Paper>
              ))}
            </Stack>
          )}
        </Box>
      </Stack>
    </Box>
  )
}

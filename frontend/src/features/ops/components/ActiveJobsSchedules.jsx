import { Stack, Typography, TextField, Button, Divider } from '@mui/material'

export default function ActiveJobsSchedules({ state, busy, toast, runRequest }) {
  const { jobLimit, setJobLimit, scheduleId, setScheduleId } = state

  return (
    <Stack spacing={1.5}>
      <Typography variant="subtitle2">Active Jobs</Typography>
      <TextField
        fullWidth
        label="Limit"
        type="number"
        value={jobLimit}
        onChange={(event) => setJobLimit(Number(event.target.value) || 0)}
        size="small"
        inputProps={{ min: 1, max: 200 }}
      />
      <Button
        variant="outlined"
        disabled={busy}
        onClick={() => {
          const limit = jobLimit > 0 ? jobLimit : 20
          runRequest({ url: `/jobs/active?limit=${limit}` })
        }}
      >
        List Active Jobs
      </Button>
      <Divider />
      <Typography variant="subtitle2">Schedule Controls</Typography>
      <TextField
        fullWidth
        label="Schedule ID"
        value={scheduleId}
        onChange={(event) => setScheduleId(event.target.value)}
        size="small"
      />
      <Stack direction="row" spacing={1} flexWrap="wrap">
        <Button
          variant="outlined"
          disabled={busy}
          onClick={() => {
            if (!scheduleId) {
              toast.show('Schedule ID required', 'warning')
              return
            }
            runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/trigger` })
          }}
        >
          Trigger
        </Button>
        <Button
          variant="outlined"
          disabled={busy}
          onClick={() => {
            if (!scheduleId) {
              toast.show('Schedule ID required', 'warning')
              return
            }
            runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/pause` })
          }}
        >
          Pause
        </Button>
        <Button
          variant="outlined"
          disabled={busy}
          onClick={() => {
            if (!scheduleId) {
              toast.show('Schedule ID required', 'warning')
              return
            }
            runRequest({ method: 'post', url: `/reports/schedules/${encodeURIComponent(scheduleId)}/resume` })
          }}
        >
          Resume
        </Button>
      </Stack>
    </Stack>
  )
}

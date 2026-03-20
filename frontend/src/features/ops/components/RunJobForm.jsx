import {
  Stack,
  Typography,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Switch,
} from '@mui/material'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import { parseJsonInput, splitList } from '../hooks/useOpsConsole'

export default function RunJobForm({ state, busy, toast, runRequest }) {
  const {
    jobTemplateId, setJobTemplateId,
    jobConnectionId, setJobConnectionId,
    jobStartDate, setJobStartDate,
    jobEndDate, setJobEndDate,
    jobDocx, setJobDocx,
    jobXlsx, setJobXlsx,
    jobKeyValues, setJobKeyValues,
    jobBatchIds, setJobBatchIds,
  } = state

  return (
    <Stack spacing={1.5}>
      <Typography variant="subtitle2">Run Report Job</Typography>
      <TemplateSelector
        value={jobTemplateId}
        onChange={setJobTemplateId}
        label="Template"
        size="small"
        fullWidth
        showAll
      />
      <ConnectionSelector
        value={jobConnectionId}
        onChange={setJobConnectionId}
        label="Connection (optional)"
        size="small"
        fullWidth
        showStatus
      />
      <Grid container spacing={1}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Start Date"
            value={jobStartDate}
            onChange={(event) => setJobStartDate(event.target.value)}
            size="small"
            placeholder="YYYY-MM-DD"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="End Date"
            value={jobEndDate}
            onChange={(event) => setJobEndDate(event.target.value)}
            size="small"
            placeholder="YYYY-MM-DD"
          />
        </Grid>
      </Grid>
      <Stack direction="row" spacing={2}>
        <FormControlLabel
          control={<Switch checked={jobDocx} onChange={(event) => setJobDocx(event.target.checked)} />}
          label="DOCX"
        />
        <FormControlLabel
          control={<Switch checked={jobXlsx} onChange={(event) => setJobXlsx(event.target.checked)} />}
          label="XLSX"
        />
      </Stack>
      <TextField
        fullWidth
        label="Key Values (JSON)"
        value={jobKeyValues}
        onChange={(event) => setJobKeyValues(event.target.value)}
        size="small"
        multiline
        minRows={3}
        placeholder='{"PARAM:region":"US"}'
      />
      <TextField
        fullWidth
        label="Batch IDs (comma separated)"
        value={jobBatchIds}
        onChange={(event) => setJobBatchIds(event.target.value)}
        size="small"
      />
      <Button
        variant="contained"
        disabled={busy}
        onClick={() => {
          if (!jobTemplateId || !jobStartDate || !jobEndDate) {
            toast.show('Template ID, start date, and end date are required', 'warning')
            return
          }
          const keyValues = parseJsonInput(jobKeyValues, toast, 'key values')
          if (keyValues === null) return
          const payload = {
            template_id: jobTemplateId,
            connection_id: jobConnectionId || undefined,
            start_date: jobStartDate,
            end_date: jobEndDate,
            docx: jobDocx,
            xlsx: jobXlsx,
            key_values: keyValues,
            batch_ids: splitList(jobBatchIds),
          }
          runRequest({ method: 'post', url: '/jobs/run-report', data: payload })
        }}
      >
        Queue Job
      </Button>
    </Stack>
  )
}

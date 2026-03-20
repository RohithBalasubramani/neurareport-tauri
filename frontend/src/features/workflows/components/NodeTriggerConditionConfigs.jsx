import {
  Stack, TextField, Select, MenuItem, FormControl, InputLabel,
  IconButton, InputAdornment,
} from '@mui/material'
import { ContentCopy as CopyIcon } from '@mui/icons-material'
import { CodeEditor } from './NodeConfigPanel.styles'

export function ConditionConfig({ config, onChange }) {
  return (
    <Stack spacing={2}>
      <CodeEditor
        label="Expression"
        size="small"
        fullWidth
        multiline
        rows={3}
        value={config.expression || ''}
        onChange={(e) => onChange({ ...config, expression: e.target.value })}
        placeholder="{{input.value}} > 100"
        helperText="JavaScript expression that evaluates to true or false"
      />

      <TextField
        label="True Branch Label"
        size="small"
        value={config.trueBranch || 'Yes'}
        onChange={(e) => onChange({ ...config, trueBranch: e.target.value })}
      />

      <TextField
        label="False Branch Label"
        size="small"
        value={config.falseBranch || 'No'}
        onChange={(e) => onChange({ ...config, falseBranch: e.target.value })}
      />
    </Stack>
  )
}

export function TriggerConfig({ config, onChange }) {
  return (
    <Stack spacing={2}>
      <FormControl size="small" fullWidth>
        <InputLabel>Trigger Type</InputLabel>
        <Select
          value={config.type || 'manual'}
          label="Trigger Type"
          onChange={(e) => onChange({ ...config, type: e.target.value })}
        >
          <MenuItem value="manual">Manual</MenuItem>
          <MenuItem value="schedule">Schedule (Cron)</MenuItem>
          <MenuItem value="webhook">Webhook</MenuItem>
          <MenuItem value="event">Event</MenuItem>
        </Select>
      </FormControl>

      {config.type === 'schedule' && (
        <>
          <TextField
            label="Cron Expression"
            size="small"
            fullWidth
            value={config.cron || ''}
            onChange={(e) => onChange({ ...config, cron: e.target.value })}
            placeholder="0 9 * * 1-5"
            helperText="Run at 9 AM Monday-Friday"
          />
          <TextField
            label="Timezone"
            size="small"
            fullWidth
            value={config.timezone || 'UTC'}
            onChange={(e) => onChange({ ...config, timezone: e.target.value })}
          />
        </>
      )}

      {config.type === 'webhook' && (
        <>
          <TextField
            label="Webhook URL"
            size="small"
            fullWidth
            value={config.webhookUrl || 'Generated on save'}
            disabled
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => navigator.clipboard.writeText(config.webhookUrl)}>
                    <CopyIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <TextField
            label="Secret Key"
            size="small"
            fullWidth
            type="password"
            value={config.secret || ''}
            onChange={(e) => onChange({ ...config, secret: e.target.value })}
            helperText="For webhook signature verification"
          />
        </>
      )}
    </Stack>
  )
}

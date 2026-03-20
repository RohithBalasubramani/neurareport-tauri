import {
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import { ExpandMore as ExpandIcon } from '@mui/icons-material'
import { ConfigAccordion } from './NodeConfigPanel.styles'

export default function NodeErrorHandling({
  node,
  expanded,
  onToggle,
  handleChange,
}) {
  return (
    <ConfigAccordion
      expanded={expanded}
      onChange={onToggle}
    >
      <AccordionSummary expandIcon={<ExpandIcon />}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          Error Handling
        </Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={2}>
          <FormControl size="small" fullWidth>
            <InputLabel>On Error</InputLabel>
            <Select
              value={node.onError || 'stop'}
              label="On Error"
              onChange={(e) => handleChange('onError', e.target.value)}
            >
              <MenuItem value="stop">Stop Workflow</MenuItem>
              <MenuItem value="continue">Continue</MenuItem>
              <MenuItem value="retry">Retry</MenuItem>
            </Select>
          </FormControl>

          {node.onError === 'retry' && (
            <>
              <TextField
                label="Max Retries"
                size="small"
                type="number"
                value={node.maxRetries || 3}
                onChange={(e) => handleChange('maxRetries', parseInt(e.target.value))}
              />
              <TextField
                label="Retry Delay (ms)"
                size="small"
                type="number"
                value={node.retryDelay || 1000}
                onChange={(e) => handleChange('retryDelay', parseInt(e.target.value))}
              />
            </>
          )}

          <TextField
            label="Timeout (ms)"
            size="small"
            type="number"
            value={node.timeout || 30000}
            onChange={(e) => handleChange('timeout', parseInt(e.target.value))}
          />
        </Stack>
      </AccordionDetails>
    </ConfigAccordion>
  )
}

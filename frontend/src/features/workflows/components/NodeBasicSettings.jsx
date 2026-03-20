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

export default function NodeBasicSettings({
  node,
  expanded,
  onToggle,
  handleChange,
  handleConfigChange,
}) {
  return (
    <ConfigAccordion
      expanded={expanded}
      onChange={onToggle}
      sx={{ mb: 1.5 }}
    >
      <AccordionSummary expandIcon={<ExpandIcon />}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          Basic Settings
        </Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={2}>
          <TextField
            label="Name"
            size="small"
            fullWidth
            value={node.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="Enter node name"
          />
          <TextField
            label="Description"
            size="small"
            fullWidth
            multiline
            rows={2}
            value={node.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
          />
          {node.type === 'action' && (
            <FormControl size="small" fullWidth>
              <InputLabel>Action Type</InputLabel>
              <Select
                value={node.config?.actionType || ''}
                label="Action Type"
                onChange={(e) => handleConfigChange({ ...node.config, actionType: e.target.value })}
              >
                <MenuItem value="http">HTTP Request</MenuItem>
                <MenuItem value="email">Send Email</MenuItem>
                <MenuItem value="database">Database Query</MenuItem>
                <MenuItem value="transform">Transform Data</MenuItem>
                <MenuItem value="script">Run Script</MenuItem>
              </Select>
            </FormControl>
          )}
        </Stack>
      </AccordionDetails>
    </ConfigAccordion>
  )
}

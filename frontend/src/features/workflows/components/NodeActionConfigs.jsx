/**
 * Action-specific configuration forms for workflow nodes.
 */
import {
  Stack, TextField, Select, MenuItem, FormControl, InputLabel,
  Switch, FormControlLabel, Alert,
} from '@mui/material'
import { CodeEditor } from './NodeConfigPanel.styles'
import { ConditionConfig, TriggerConfig } from './NodeTriggerConditionConfigs'

export function HttpActionConfig({ config, onChange }) {
  return (
    <Stack spacing={2}>
      <FormControl size="small" fullWidth>
        <InputLabel>Method</InputLabel>
        <Select
          value={config.method || 'GET'}
          label="Method"
          onChange={(e) => onChange({ ...config, method: e.target.value })}
        >
          <MenuItem value="GET">GET</MenuItem>
          <MenuItem value="POST">POST</MenuItem>
          <MenuItem value="PUT">PUT</MenuItem>
          <MenuItem value="PATCH">PATCH</MenuItem>
          <MenuItem value="DELETE">DELETE</MenuItem>
        </Select>
      </FormControl>
      <TextField
        label="URL"
        size="small"
        fullWidth
        value={config.url || ''}
        onChange={(e) => onChange({ ...config, url: e.target.value })}
        placeholder="https://api.example.com/endpoint"
      />
      <TextField
        label="Headers (JSON)"
        size="small"
        fullWidth
        multiline
        rows={2}
        value={config.headers || ''}
        onChange={(e) => onChange({ ...config, headers: e.target.value })}
        placeholder='{"Authorization": "Bearer {{env.API_KEY}}"}'
      />
      {['POST', 'PUT', 'PATCH'].includes(config.method) && (
        <TextField
          label="Body"
          size="small"
          fullWidth
          multiline
          rows={4}
          value={config.body || ''}
          onChange={(e) => onChange({ ...config, body: e.target.value })}
          placeholder='{"key": "{{input.value}}"}'
        />
      )}
      <FormControlLabel
        control={
          <Switch
            checked={config.parseJson ?? true}
            onChange={(e) => onChange({ ...config, parseJson: e.target.checked })}
            size="small"
          />
        }
        label="Parse JSON response"
      />
    </Stack>
  )
}

export function EmailActionConfig({ config, onChange }) {
  return (
    <Stack spacing={2}>
      <TextField
        label="To"
        size="small"
        fullWidth
        value={config.to || ''}
        onChange={(e) => onChange({ ...config, to: e.target.value })}
        placeholder="recipient@example.com"
      />
      <TextField
        label="Subject"
        size="small"
        fullWidth
        value={config.subject || ''}
        onChange={(e) => onChange({ ...config, subject: e.target.value })}
        placeholder="Workflow Notification: {{workflow.name}}"
      />
      <TextField
        label="Body"
        size="small"
        fullWidth
        multiline
        rows={6}
        value={config.body || ''}
        onChange={(e) => onChange({ ...config, body: e.target.value })}
        placeholder="Hello,\n\nThis is an automated notification..."
      />
      <FormControlLabel
        control={
          <Switch
            checked={config.html ?? false}
            onChange={(e) => onChange({ ...config, html: e.target.checked })}
            size="small"
          />
        }
        label="HTML email"
      />
    </Stack>
  )
}

export function TransformConfig({ config, onChange }) {
  return (
    <Stack spacing={2}>
      <FormControl size="small" fullWidth>
        <InputLabel>Transform Type</InputLabel>
        <Select
          value={config.type || 'jq'}
          label="Transform Type"
          onChange={(e) => onChange({ ...config, type: e.target.value })}
        >
          <MenuItem value="jq">JQ Expression</MenuItem>
          <MenuItem value="javascript">JavaScript</MenuItem>
          <MenuItem value="mapping">Field Mapping</MenuItem>
        </Select>
      </FormControl>
      {config.type === 'javascript' ? (
        <CodeEditor
          label="JavaScript Code"
          size="small"
          fullWidth
          multiline
          rows={8}
          value={config.code || ''}
          onChange={(e) => onChange({ ...config, code: e.target.value })}
          placeholder="// Transform the input data\nreturn {\n  ...input,\n  processed: true\n}"
        />
      ) : (
        <CodeEditor
          label="JQ Expression"
          size="small"
          fullWidth
          multiline
          rows={4}
          value={config.expression || ''}
          onChange={(e) => onChange({ ...config, expression: e.target.value })}
          placeholder=".data | map({id: .id, name: .name})"
        />
      )}
    </Stack>
  )
}

/**
 * Renders the appropriate config form based on the node type and action type.
 */
export function renderNodeConfigForm(node, handleConfigChange) {
  if (!node) return null
  const actionType = node.config?.actionType || node.actionType
  switch (actionType) {
    case 'http':
      return <HttpActionConfig config={node.config || {}} onChange={handleConfigChange} />
    case 'email':
      return <EmailActionConfig config={node.config || {}} onChange={handleConfigChange} />
    case 'transform':
      return <TransformConfig config={node.config || {}} onChange={handleConfigChange} />
    default:
      if (node.type === 'condition') {
        return <ConditionConfig config={node.config || {}} onChange={handleConfigChange} />
      }
      if (node.type === 'trigger') {
        return <TriggerConfig config={node.config || {}} onChange={handleConfigChange} />
      }
      return (
        <Alert severity="info">
          Select an action type to configure this node.
        </Alert>
      )
  }
}

/**
 * Node Configuration Panel Component
 * Settings panel for configuring workflow nodes (actions, conditions, triggers).
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Divider,
  Chip,
  Switch,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Collapse,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandIcon,
  Code as CodeIcon,
  Webhook as WebhookIcon,
  Email as EmailIcon,
  Storage as DatabaseIcon,
  Api as ApiIcon,
  Schedule as ScheduleIcon,
  Sync as SyncIcon,
  CheckCircle as ApprovalIcon,
  HelpOutline as HelpIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 360,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const PanelFooter = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const NodeTypeChip = styled(Chip)(({ theme }) => ({
  borderRadius: 4,
  fontWeight: 600,
  fontSize: '12px',
}))

const CodeEditor = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    fontFamily: 'monospace',
    fontSize: '14px',
    backgroundColor: alpha(theme.palette.common.black, 0.02),
  },
}))

const VariableChip = styled(Chip)(({ theme }) => ({
  height: 24,
  fontSize: '12px',
  fontFamily: 'monospace',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],
  },
}))

const ConfigAccordion = styled(Accordion)(({ theme }) => ({
  boxShadow: 'none',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  borderRadius: 8,
  '&:before': { display: 'none' },
  '&.Mui-expanded': {
    margin: 0,
  },
}))

// =============================================================================
// NODE TYPES CONFIGURATION
// =============================================================================

const NODE_TYPES = {
  trigger: {
    label: 'Trigger',
    color: 'success',
    icon: PlayIcon,
    configs: ['schedule', 'webhook', 'manual'],
  },
  action: {
    label: 'Action',
    color: 'primary',
    icon: SyncIcon,
    configs: ['http', 'email', 'database', 'transform', 'script'],
  },
  condition: {
    label: 'Condition',
    color: 'warning',
    icon: CodeIcon,
    configs: ['expression', 'switch'],
  },
  approval: {
    label: 'Approval',
    color: 'info',
    icon: ApprovalIcon,
    configs: ['manual', 'timeout', 'parallel'],
  },
  loop: {
    label: 'Loop',
    color: 'secondary',
    icon: SyncIcon,
    configs: ['foreach', 'while'],
  },
}

const AVAILABLE_VARIABLES = [
  { name: 'input', description: 'Input data from previous node' },
  { name: 'env', description: 'Environment variables' },
  { name: 'workflow', description: 'Workflow metadata' },
  { name: 'timestamp', description: 'Current timestamp' },
  { name: 'user', description: 'Current user info' },
]

// =============================================================================
// ACTION CONFIGURATIONS
// =============================================================================

function HttpActionConfig({ config, onChange }) {
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

function EmailActionConfig({ config, onChange }) {
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

function ConditionConfig({ config, onChange }) {
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

function TransformConfig({ config, onChange }) {
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

function TriggerConfig({ config, onChange }) {
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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function NodeConfigPanel({
  node = null,
  onChange,
  onDelete,
  onTest,
  onClose,
}) {
  const theme = useTheme()
  const [expandedSections, setExpandedSections] = useState(['basic', 'config'])

  const nodeTypeInfo = useMemo(() =>
    node ? NODE_TYPES[node.type] || NODE_TYPES.action : null,
    [node]
  )

  const handleChange = useCallback((key, value) => {
    onChange?.({ ...node, [key]: value })
  }, [node, onChange])

  const handleConfigChange = useCallback((config) => {
    onChange?.({ ...node, config })
  }, [node, onChange])

  const toggleSection = useCallback((section) => {
    setExpandedSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section]
    )
  }, [])

  const insertVariable = useCallback((varName) => {
    // This would insert at cursor position in the active field
    navigator.clipboard.writeText(`{{${varName}}}`)
  }, [])

  // Render config form based on action type
  const renderConfigForm = () => {
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

  if (!node) {
    return (
      <PanelContainer>
        <PanelHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Node Configuration
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </PanelHeader>
        <PanelContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <SettingsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              Select a node to configure
            </Typography>
          </Box>
        </PanelContent>
      </PanelContainer>
    )
  }

  const NodeIcon = nodeTypeInfo?.icon || SettingsIcon

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <NodeIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Configure Node
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </PanelHeader>

      <PanelContent>
        {/* Node Type Badge */}
        <Stack direction="row" spacing={1} mb={2}>
          <NodeTypeChip
            label={nodeTypeInfo?.label || node.type}
            size="small"
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
          <Chip label={`ID: ${node.id}`} size="small" variant="outlined" />
        </Stack>

        {/* Basic Settings */}
        <ConfigAccordion
          expanded={expandedSections.includes('basic')}
          onChange={() => toggleSection('basic')}
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

        {/* Action Configuration */}
        <ConfigAccordion
          expanded={expandedSections.includes('config')}
          onChange={() => toggleSection('config')}
          sx={{ mb: 1.5 }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              Configuration
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {renderConfigForm()}
          </AccordionDetails>
        </ConfigAccordion>

        {/* Available Variables */}
        <ConfigAccordion
          expanded={expandedSections.includes('variables')}
          onChange={() => toggleSection('variables')}
          sx={{ mb: 1.5 }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              Available Variables
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Click to copy variable syntax
            </Typography>
            <Stack spacing={0.5}>
              {AVAILABLE_VARIABLES.map((v) => (
                <Stack
                  key={v.name}
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                >
                  <VariableChip
                    label={`{{${v.name}}}`}
                    size="small"
                    onClick={() => insertVariable(v.name)}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {v.description}
                  </Typography>
                </Stack>
              ))}
            </Stack>
          </AccordionDetails>
        </ConfigAccordion>

        {/* Error Handling */}
        <ConfigAccordion
          expanded={expandedSections.includes('errors')}
          onChange={() => toggleSection('errors')}
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
      </PanelContent>

      <PanelFooter>
        <Stack direction="row" spacing={1} justifyContent="space-between">
          <Button
            variant="outlined"
            size="small"
            startIcon={<DeleteIcon />}
            onClick={onDelete}
            sx={{ color: 'text.secondary' }}
          >
            Delete
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<PlayIcon />}
            onClick={onTest}
          >
            Test Node
          </Button>
        </Stack>
      </PanelFooter>
    </PanelContainer>
  )
}

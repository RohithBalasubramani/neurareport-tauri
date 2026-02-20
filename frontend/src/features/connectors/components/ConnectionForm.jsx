/**
 * Connection Form Component
 * Dynamic form for database and cloud connector configuration.
 */
import { useState, useMemo } from 'react'
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material'
import {
  ExpandMore as ExpandIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material'
import OAuthButton, { isOAuthProvider } from './OAuthButton'

// =============================================================================
// FIELD CONFIGS BY CONNECTOR TYPE
// =============================================================================

const CONNECTOR_FIELDS = {
  // Databases
  postgresql: {
    name: 'PostgreSQL',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 5432 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'ssl', label: 'Use SSL', type: 'boolean', default: true },
    ],
    advanced: [
      { name: 'sslmode', label: 'SSL Mode', type: 'select', options: ['disable', 'require', 'verify-ca', 'verify-full'], default: 'require' },
      { name: 'connect_timeout', label: 'Connection Timeout (s)', type: 'number', default: 10 },
    ],
  },
  mysql: {
    name: 'MySQL',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 3306 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'ssl', label: 'Use SSL', type: 'boolean', default: false },
    ],
    advanced: [
      { name: 'charset', label: 'Charset', type: 'text', default: 'utf8mb4' },
      { name: 'connect_timeout', label: 'Connection Timeout (s)', type: 'number', default: 10 },
    ],
  },
  mongodb: {
    name: 'MongoDB',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true, default: 'localhost' },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 27017 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text' },
      { name: 'password', label: 'Password', type: 'password' },
      { name: 'auth_source', label: 'Auth Source', type: 'text', default: 'admin' },
    ],
    advanced: [
      { name: 'replica_set', label: 'Replica Set', type: 'text' },
      { name: 'tls', label: 'Use TLS', type: 'boolean', default: false },
    ],
  },
  sqlserver: {
    name: 'SQL Server',
    fields: [
      { name: 'host', label: 'Host', type: 'text', required: true },
      { name: 'port', label: 'Port', type: 'number', required: true, default: 1433 },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'encrypt', label: 'Encrypt Connection', type: 'boolean', default: true },
    ],
    advanced: [
      { name: 'trust_server_certificate', label: 'Trust Server Certificate', type: 'boolean', default: false },
    ],
  },
  bigquery: {
    name: 'BigQuery',
    fields: [
      { name: 'project_id', label: 'Project ID', type: 'text', required: true },
      { name: 'dataset', label: 'Dataset', type: 'text' },
      { name: 'credentials_json', label: 'Service Account JSON', type: 'textarea', required: true },
    ],
    advanced: [
      { name: 'location', label: 'Location', type: 'text', default: 'US' },
    ],
  },
  snowflake: {
    name: 'Snowflake',
    fields: [
      { name: 'account', label: 'Account Identifier', type: 'text', required: true },
      { name: 'username', label: 'Username', type: 'text', required: true },
      { name: 'password', label: 'Password', type: 'password', required: true },
      { name: 'database', label: 'Database', type: 'text', required: true },
      { name: 'warehouse', label: 'Warehouse', type: 'text', required: true },
      { name: 'schema', label: 'Schema', type: 'text', default: 'PUBLIC' },
    ],
    advanced: [
      { name: 'role', label: 'Role', type: 'text' },
    ],
  },
  // Cloud Storage
  google_drive: {
    name: 'Google Drive',
    oauth: true,
    fields: [
      { name: 'folder_id', label: 'Folder ID (optional)', type: 'text', helpText: 'Leave empty to access entire drive' },
    ],
  },
  dropbox: {
    name: 'Dropbox',
    oauth: true,
    fields: [
      { name: 'root_path', label: 'Root Path', type: 'text', default: '/', helpText: 'Start path for file browsing' },
    ],
  },
  s3: {
    name: 'Amazon S3',
    fields: [
      { name: 'bucket', label: 'Bucket Name', type: 'text', required: true },
      { name: 'region', label: 'Region', type: 'select', required: true, options: [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-west-2', 'eu-central-1',
        'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
      ], default: 'us-east-1' },
      { name: 'access_key_id', label: 'Access Key ID', type: 'text', required: true },
      { name: 'secret_access_key', label: 'Secret Access Key', type: 'password', required: true },
    ],
    advanced: [
      { name: 'prefix', label: 'Key Prefix', type: 'text', helpText: 'Filter objects by prefix' },
      { name: 'endpoint_url', label: 'Custom Endpoint URL', type: 'text', helpText: 'For S3-compatible services' },
    ],
  },
  azure_blob: {
    name: 'Azure Blob Storage',
    fields: [
      { name: 'account_name', label: 'Storage Account Name', type: 'text', required: true },
      { name: 'container', label: 'Container Name', type: 'text', required: true },
      { name: 'connection_string', label: 'Connection String', type: 'password', required: true },
    ],
    advanced: [
      { name: 'prefix', label: 'Blob Prefix', type: 'text' },
    ],
  },
  onedrive: {
    name: 'OneDrive',
    oauth: true,
    fields: [
      { name: 'drive_id', label: 'Drive ID (optional)', type: 'text', helpText: 'Leave empty for default drive' },
    ],
  },
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConnectionForm({
  connectorType,
  values = {},
  onChange,
  errors = {},
  disabled = false,
  showAdvanced = false,
  onOAuthConnect,
  oauthConnected = false,
}) {
  const theme = useTheme()
  const [advancedOpen, setAdvancedOpen] = useState(showAdvanced)
  const [showPasswords, setShowPasswords] = useState({})

  const config = CONNECTOR_FIELDS[connectorType] || { name: connectorType, fields: [] }
  const fields = config.fields || []
  const advancedFields = config.advanced || []
  const isOAuth = config.oauth || false

  const handleChange = (fieldName, value) => {
    onChange?.({ ...values, [fieldName]: value })
  }

  const togglePassword = (fieldName) => {
    setShowPasswords((prev) => ({ ...prev, [fieldName]: !prev[fieldName] }))
  }

  const renderField = (field) => {
    const value = values[field.name] ?? field.default ?? ''
    const error = errors[field.name]
    const showPassword = showPasswords[field.name]

    switch (field.type) {
      case 'password':
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            type={showPassword ? 'text' : 'password'}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            required={field.required}
            error={Boolean(error)}
            helperText={error || field.helpText}
            disabled={disabled}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => togglePassword(field.name)}
                    edge="end"
                    size="small"
                  >
                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />
        )

      case 'textarea':
        return (
          <TextField
            key={field.name}
            fullWidth
            multiline
            rows={4}
            label={field.label}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            required={field.required}
            error={Boolean(error)}
            helperText={error || field.helpText}
            disabled={disabled}
            sx={{ mb: 2 }}
          />
        )

      case 'number':
        return (
          <TextField
            key={field.name}
            fullWidth
            type="number"
            label={field.label}
            value={value}
            onChange={(e) => handleChange(field.name, parseInt(e.target.value) || '')}
            required={field.required}
            error={Boolean(error)}
            helperText={error || field.helpText}
            disabled={disabled}
            sx={{ mb: 2 }}
          />
        )

      case 'boolean':
        return (
          <FormControlLabel
            key={field.name}
            control={
              <Switch
                checked={Boolean(value)}
                onChange={(e) => handleChange(field.name, e.target.checked)}
                disabled={disabled}
              />
            }
            label={field.label}
            sx={{ mb: 2, display: 'block' }}
          />
        )

      case 'select':
        return (
          <FormControl key={field.name} fullWidth sx={{ mb: 2 }} error={Boolean(error)}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={value}
              label={field.label}
              onChange={(e) => handleChange(field.name, e.target.value)}
              required={field.required}
              disabled={disabled}
            >
              {field.options?.map((opt) => (
                <MenuItem key={opt} value={opt}>
                  {opt}
                </MenuItem>
              ))}
            </Select>
            {(error || field.helpText) && (
              <Typography variant="caption" color={error ? 'error' : 'text.secondary'} sx={{ mt: 0.5, ml: 1.5 }}>
                {error || field.helpText}
              </Typography>
            )}
          </FormControl>
        )

      default:
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            required={field.required}
            error={Boolean(error)}
            helperText={error || field.helpText}
            disabled={disabled}
            sx={{ mb: 2 }}
          />
        )
    }
  }

  return (
    <Box>
      {/* OAuth Section */}
      {isOAuth && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
            Authentication
          </Typography>
          <OAuthButton
            provider={connectorType}
            connected={oauthConnected}
            onConnect={onOAuthConnect}
            disabled={disabled}
          />
        </Box>
      )}

      {/* Main Fields */}
      {(!isOAuth || oauthConnected) && fields.length > 0 && (
        <Box>
          {isOAuth && (
            <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
              Configuration
            </Typography>
          )}
          {fields.map(renderField)}
        </Box>
      )}

      {/* Advanced Fields */}
      {advancedFields.length > 0 && (
        <Accordion
          expanded={advancedOpen}
          onChange={() => setAdvancedOpen(!advancedOpen)}
          elevation={0}
          sx={{
            mt: 2,
            backgroundColor: alpha(theme.palette.background.default, 0.5),
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              Advanced Options
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {advancedFields.map(renderField)}
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  )
}

/**
 * Get connector field configuration
 */
export function getConnectorConfig(connectorType) {
  return CONNECTOR_FIELDS[connectorType] || null
}

/**
 * Validate connection form values
 */
export function validateConnectionForm(connectorType, values) {
  const config = CONNECTOR_FIELDS[connectorType]
  if (!config) return { valid: true, errors: {} }

  const errors = {}
  const fields = [...(config.fields || []), ...(config.advanced || [])]

  fields.forEach((field) => {
    if (field.required && !values[field.name]) {
      errors[field.name] = `${field.label} is required`
    }
  })

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  }
}

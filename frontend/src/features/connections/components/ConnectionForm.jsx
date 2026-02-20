import { useState, useCallback, useMemo, useRef } from 'react'
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Button,
  Alert,
  Collapse,
  Typography,
  Switch,
  FormControlLabel,
  Divider,
  FormHelperText,
  CircularProgress,
  Tooltip,
  InputAdornment,
  IconButton,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'

// Help text for each field
const FIELD_HELP = {
  name: 'A friendly name to identify this connection. Example: "Production Database" or "Local Dev".',
  db_type: 'The type of database you\'re connecting to. Contact your database administrator if you\'re unsure.',
  host: 'The server address where your database is hosted. This could be a domain name (db.example.com) or an IP address (192.168.1.1). Use "localhost" for local databases.',
  port: 'The port number your database listens on. Default ports: PostgreSQL (5432), MySQL (3306), SQL Server (1433). Usually you don\'t need to change this.',
  database: 'The name of the specific database you want to connect to on the server. Ask your database administrator if you\'re not sure.',
  database_sqlite: 'The file path to your SQLite database file. Example: /home/user/data/myapp.db',
  username: 'Your database username. This is the account that will be used to run queries.',
  password: 'Your database password. This will be stored securely and encrypted.',
  ssl: 'Enable SSL/TLS encryption for secure connections. Recommended for production databases, especially over the internet.',
}

function HelpIcon({ field }) {
  const helpText = FIELD_HELP[field]
  if (!helpText) return null

  return (
    <Tooltip title={helpText} arrow placement="top">
      <IconButton size="small" sx={{ p: 0.5 }} aria-label={helpText}>
        <HelpOutlineIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
      </IconButton>
    </Tooltip>
  )
}
import { testConnection } from '@/api/client'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import {
  validateRequired,
  validateMinLength,
  validateMaxLength,
  combineValidators,
} from '@/utils/validation'

const DB_TYPES = [
  { value: 'sqlite', label: 'SQLite', port: null, requiresAuth: false },
  { value: 'postgresql', label: 'PostgreSQL', port: 5432, requiresAuth: true },
  { value: 'mysql', label: 'MySQL', port: 3306, requiresAuth: true },
  { value: 'mssql', label: 'SQL Server', port: 1433, requiresAuth: true },
  { value: 'mariadb', label: 'MariaDB', port: 3306, requiresAuth: true },
]

// Field validators
const validators = {
  name: combineValidators(
    (v) => validateRequired(v, 'Connection name'),
    (v) => validateMinLength(v, 2, 'Connection name'),
    (v) => validateMaxLength(v, 100, 'Connection name')
  ),
  host: (value, allValues) => {
    if (allValues.db_type === 'sqlite') return { valid: true, error: null }
    return combineValidators(
      (v) => validateRequired(v, 'Host'),
      (v) => validateMaxLength(v, 255, 'Host')
    )(value)
  },
  database: combineValidators(
    (v) => validateRequired(v, 'Database name'),
    (v) => validateMaxLength(v, 255, 'Database name')
  ),
  port: (value) => {
    const port = parseInt(value, 10)
    if (isNaN(port) || port < 1 || port > 65535) {
      return { valid: false, error: 'Port must be between 1 and 65535' }
    }
    return { valid: true, error: null }
  },
}

export default function ConnectionForm({ connection, onSave, onCancel, loading }) {
  const initialDbType = DB_TYPES.some((type) => type.value === connection?.db_type)
    ? connection?.db_type
    : 'sqlite'
  const [formData, setFormData] = useState({
    name: connection?.name || '',
    db_type: initialDbType,
    host: connection?.host || 'localhost',
    port: connection?.port || 5432,
    database: connection?.database || '',
    username: connection?.username || '',
    password: '',
    ssl: connection?.ssl ?? true,
  })
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [error, setError] = useState(null)
  const [touched, setTouched] = useState({})
  const [fieldErrors, setFieldErrors] = useState({})
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null) // 'success' | 'error' | null
  const submitDebounceRef = useRef(false)
  const { execute } = useInteraction()

  const handleChange = useCallback((field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value
    setFormData((prev) => {
      const newData = { ...prev, [field]: value }
      // Validate on change if field was already touched
      if (touched[field] && validators[field]) {
        const result = validators[field](value, newData)
        setFieldErrors((e) => ({ ...e, [field]: result.error }))
      }
      return newData
    })
    setError(null)
  }, [touched])

  const handleBlur = useCallback((field) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }))
    if (validators[field]) {
      const result = validators[field](formData[field], formData)
      setFieldErrors((prev) => ({ ...prev, [field]: result.error }))
    }
  }, [formData])

  const handleDbTypeChange = useCallback((event) => {
    const dbType = event.target.value
    const typeConfig = DB_TYPES.find((t) => t.value === dbType)
    setFormData((prev) => ({
      ...prev,
      db_type: dbType,
      port: typeConfig?.port || prev.port,
    }))
    setTestResult(null)
  }, [])

  const buildConnectionUrl = useCallback(() => {
    if (formData.db_type === 'sqlite') {
      // For SQLite we rely on the explicit `database` path field (sent as `database`)
      // because `sqlite:///relative/path.db` parses as an absolute path on Windows.
      return null
    }
    const auth = formData.username
      ? `${formData.username}${formData.password ? `:${formData.password}` : ''}@`
      : ''
    return `${formData.db_type}://${auth}${formData.host}:${formData.port}/${formData.database}`
  }, [formData])

  const handleTestConnection = useCallback(async () => {
    // Validate required fields first
    const requiredErrors = {}
    if (!formData.database.trim()) {
      requiredErrors.database = 'Database is required to test'
    }
    if (formData.db_type !== 'sqlite' && !formData.host.trim()) {
      requiredErrors.host = 'Host is required to test'
    }

    if (Object.keys(requiredErrors).length > 0) {
      setFieldErrors((prev) => ({ ...prev, ...requiredErrors }))
      setTouched((prev) => ({ ...prev, database: true, host: true }))
      return
    }

    await execute({
      type: InteractionType.EXECUTE,
      label: 'Test connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        dbType: formData.db_type,
        action: 'test_connection',
      },
      action: async () => {
        setTesting(true)
        setTestResult(null)
        setError(null)

        try {
          const db_url = buildConnectionUrl()
          const result = await testConnection({
            db_url,
            db_type: formData.db_type,
            database: formData.database,
          })
          if (
            result?.status === 'healthy'
            || result?.healthy
            || result?.status === 'ok'
            || result?.ok
          ) {
            setTestResult('success')
          } else {
            setTestResult('error')
            setError(result?.message || result?.error || 'Connection test failed')
          }
          return result
        } catch (err) {
          setTestResult('error')
          setError(err.message || 'Connection test failed')
          throw err
        } finally {
          setTesting(false)
        }
      },
    })
  }, [buildConnectionUrl, execute, formData])

  const handleSubmit = useCallback((e) => {
    e.preventDefault()

    // Debounce protection against double-submit
    if (submitDebounceRef.current) return
    submitDebounceRef.current = true
    setTimeout(() => { submitDebounceRef.current = false }, 1000)

    // Mark all fields as touched
    const allTouched = { name: true, host: true, database: true, port: true }
    setTouched(allTouched)

    // Validate all fields
    const errors = {}
    let hasErrors = false

    for (const [field, validator] of Object.entries(validators)) {
      const result = validator(formData[field], formData)
      if (!result.valid) {
        errors[field] = result.error
        hasErrors = true
      }
    }

    setFieldErrors(errors)

    if (hasErrors) {
      const firstError = Object.values(errors).find(Boolean)
      setError(firstError || 'Please fix the errors above')
      return
    }

    const db_url = buildConnectionUrl()

    onSave({
      ...formData,
      db_url,
    })
  }, [formData, onSave, buildConnectionUrl])

  const isSqlite = formData.db_type === 'sqlite'

  // Compute whether the form has minimum required data for submission
  const isFormValid = useMemo(() => {
    const nameValid = formData.name.trim().length >= 2
    const dbValid = formData.database.trim().length > 0
    if (isSqlite) return nameValid && dbValid
    const hostValid = formData.host.trim().length > 0
    return nameValid && dbValid && hostValid
  }, [formData.name, formData.database, formData.host, isSqlite])

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack spacing={3}>
        {error && (
          <Alert
            severity="error"
            onClose={() => setError(null)}
            action={
              testResult === 'error' && (
                <Button
                  color="inherit"
                  size="small"
                  onClick={handleTestConnection}
                  disabled={testing}
                >
                  Try Again
                </Button>
              )
            }
          >
            {error}
          </Alert>
        )}

        <Alert severity="info">
          Use a read-only account when possible. Testing only checks connectivity. Saved credentials are encrypted for
          reuse. Deleting a connection never deletes data from your database.
        </Alert>

        <TextField
          label={
            <Stack direction="row" alignItems="center" spacing={0.5} component="span">
              <span>Connection Name</span>
              <HelpIcon field="name" />
            </Stack>
          }
          value={formData.name}
          onChange={handleChange('name')}
          onBlur={handleBlur('name')}
          placeholder="e.g., Production Database"
          required
          fullWidth
          inputProps={{ maxLength: 100 }}
          error={touched.name && Boolean(fieldErrors.name)}
          helperText={touched.name && fieldErrors.name}
        />

        <FormControl fullWidth>
          <InputLabel>
            <Stack direction="row" alignItems="center" spacing={0.5} component="span">
              <span>Database Type</span>
              <HelpIcon field="db_type" />
            </Stack>
          </InputLabel>
          <Select
            value={formData.db_type}
            onChange={handleDbTypeChange}
            label="Database Type      "
          >
            {DB_TYPES.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>Not sure? Ask your database administrator</FormHelperText>
        </FormControl>

        {!isSqlite && (
          <Stack direction="row" spacing={2}>
            <TextField
              label={
                <Stack direction="row" alignItems="center" spacing={0.5} component="span">
                  <span>Server Address</span>
                  <HelpIcon field="host" />
                </Stack>
              }
              value={formData.host}
              onChange={handleChange('host')}
              onBlur={handleBlur('host')}
              placeholder="e.g., db.example.com"
              required
              sx={{ flex: 2 }}
              error={touched.host && Boolean(fieldErrors.host)}
              helperText={touched.host ? fieldErrors.host : 'The URL or IP address of your database server'}
            />
            <TextField
              label={
                <Stack direction="row" alignItems="center" spacing={0.5} component="span">
                  <span>Port</span>
                  <HelpIcon field="port" />
                </Stack>
              }
              type="number"
              value={formData.port}
              onChange={handleChange('port')}
              onBlur={handleBlur('port')}
              sx={{ flex: 1 }}
              error={touched.port && Boolean(fieldErrors.port)}
              helperText={touched.port ? fieldErrors.port : 'Usually automatic'}
            />
          </Stack>
        )}

        <TextField
          label={
            <Stack direction="row" alignItems="center" spacing={0.5} component="span">
              <span>{isSqlite ? 'Database Path' : 'Database Name'}</span>
              <HelpIcon field={isSqlite ? 'database_sqlite' : 'database'} />
            </Stack>
          }
          value={formData.database}
          onChange={handleChange('database')}
          onBlur={handleBlur('database')}
          placeholder={isSqlite ? '/path/to/database.db' : 'e.g., my_database'}
          required
          fullWidth
          error={touched.database && Boolean(fieldErrors.database)}
          helperText={touched.database ? fieldErrors.database : (isSqlite ? 'Full path to your SQLite file' : 'The name of the database on the server')}
        />

        {!isSqlite && (
          <>
            <TextField
              label={
                <Stack direction="row" alignItems="center" spacing={0.5} component="span">
                  <span>Username</span>
                  <HelpIcon field="username" />
                </Stack>
              }
              value={formData.username}
              onChange={handleChange('username')}
              placeholder="e.g., postgres"
              fullWidth
              helperText="The database account to use"
            />

            <TextField
              label={
                <Stack direction="row" alignItems="center" spacing={0.5} component="span">
                  <span>Password</span>
                  <HelpIcon field="password" />
                </Stack>
              }
              type="password"
              value={formData.password}
              onChange={handleChange('password')}
              placeholder="Enter password"
              fullWidth
              helperText="Stored securely and encrypted"
            />
          </>
        )}

        {/* Advanced Settings */}
        <Box>
          <Button
            variant="text"
            size="small"
            onClick={() => setShowAdvanced((prev) => !prev)}
            endIcon={showAdvanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{ textTransform: 'none', fontWeight: 500 }}
          >
            Advanced Settings
          </Button>

          <Collapse in={showAdvanced}>
            <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
              <Stack spacing={2}>
                {!isSqlite && (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.ssl}
                        onChange={handleChange('ssl')}
                      />
                    }
                    label={
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <span>Use Secure Connection (SSL)</span>
                        <HelpIcon field="ssl" />
                      </Stack>
                    }
                  />
                )}
                {isSqlite && (
                  <Typography variant="caption" color="text.secondary">
                    SQLite databases use file-based storage and do not require additional configuration.
                  </Typography>
                )}
              </Stack>
            </Box>
          </Collapse>
        </Box>

        <Divider />

        {/* Test Connection Result */}
        {testResult && (
          <Alert
            severity={testResult === 'success' ? 'success' : 'error'}
            icon={testResult === 'success' ? <CheckCircleIcon /> : <ErrorIcon />}
            onClose={() => setTestResult(null)}
            action={
              testResult === 'error' && (
                <Button
                  color="inherit"
                  size="small"
                  onClick={handleTestConnection}
                  disabled={testing}
                >
                  Retry
                </Button>
              )
            }
          >
            {testResult === 'success'
              ? 'Connection successful! Database is reachable.'
              : error || 'Connection failed. Check your settings and try again.'}
          </Alert>
        )}

        {/* Actions */}
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button
            variant="text"
            onClick={handleTestConnection}
            disabled={loading || testing}
            startIcon={testing ? <CircularProgress size={16} /> : null}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </Button>
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !isFormValid}
          >
            {connection ? 'Update Connection' : 'Add Connection'}
          </Button>
        </Stack>
      </Stack>
    </Box>
  )
}

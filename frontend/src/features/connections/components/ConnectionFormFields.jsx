/**
 * Core form fields for ConnectionForm.
 */
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  FormHelperText,
  Tooltip,
  IconButton,
} from '@mui/material'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import { DB_TYPES } from '../hooks/useConnectionForm'

const FIELD_HELP = {
  name: 'A friendly name to identify this connection. Example: "Production Database" or "Local Dev".',
  db_type: 'The type of database you\'re connecting to. Contact your database administrator if you\'re unsure.',
  host: 'The server address where your database is hosted. This could be a domain name (db.example.com) or an IP address (192.168.1.1). Use "localhost" for local databases.',
  port: 'The port number your database listens on. Default ports: PostgreSQL (5432), MySQL (3306), SQL Server (1433). Usually you don\'t need to change this.',
  database: 'The name of the specific database you want to connect to on the server. Ask your database administrator if you\'re not sure.',
  database_sqlite: 'The file path to your SQLite database file. Example: /home/user/data/myapp.db',
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

export function ConnectionNameField({ formData, touched, fieldErrors, handleChange, handleBlur }) {
  return (
    <TextField
      label={
        <Stack direction="row" alignItems="center" spacing={0.5} component="span">
          <span>Connection Name</span><HelpIcon field="name" />
        </Stack>
      }
      value={formData.name}
      onChange={handleChange('name')}
      onBlur={handleBlur('name')}
      placeholder="e.g., Production Database"
      required fullWidth
      inputProps={{ maxLength: 100 }}
      error={touched.name && Boolean(fieldErrors.name)}
      helperText={touched.name && fieldErrors.name}
    />
  )
}

export function DbTypeField({ formData, handleDbTypeChange }) {
  return (
    <FormControl fullWidth>
      <InputLabel>
        <Stack direction="row" alignItems="center" spacing={0.5} component="span">
          <span>Database Type</span><HelpIcon field="db_type" />
        </Stack>
      </InputLabel>
      <Select value={formData.db_type} onChange={handleDbTypeChange} label="Database Type      ">
        {DB_TYPES.map((type) => (
          <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
        ))}
      </Select>
      <FormHelperText>Not sure? Ask your database administrator</FormHelperText>
    </FormControl>
  )
}

export function HostPortFields({ formData, touched, fieldErrors, handleChange, handleBlur }) {
  return (
    <Stack direction="row" spacing={2}>
      <TextField
        label={
          <Stack direction="row" alignItems="center" spacing={0.5} component="span">
            <span>Server Address</span><HelpIcon field="host" />
          </Stack>
        }
        value={formData.host}
        onChange={handleChange('host')}
        onBlur={handleBlur('host')}
        placeholder="e.g., db.example.com"
        required sx={{ flex: 2 }}
        error={touched.host && Boolean(fieldErrors.host)}
        helperText={touched.host ? fieldErrors.host : 'The URL or IP address of your database server'}
      />
      <TextField
        label={
          <Stack direction="row" alignItems="center" spacing={0.5} component="span">
            <span>Port</span><HelpIcon field="port" />
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
  )
}

export function DatabaseField({ formData, isSqlite, touched, fieldErrors, handleChange, handleBlur }) {
  return (
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
      required fullWidth
      error={touched.database && Boolean(fieldErrors.database)}
      helperText={touched.database ? fieldErrors.database : (isSqlite ? 'Full path to your SQLite file' : 'The name of the database on the server')}
    />
  )
}

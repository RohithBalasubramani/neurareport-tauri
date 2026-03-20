/**
 * Advanced settings and credential fields for ConnectionForm.
 */
import {
  TextField,
  Stack,
  Switch,
  FormControlLabel,
  Typography,
  Tooltip,
  IconButton,
  Collapse,
  Button,
  Box,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'

const FIELD_HELP = {
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

export function CredentialFields({ formData, handleChange }) {
  return (
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
  )
}

export function AdvancedSettings({ formData, isSqlite, showAdvanced, setShowAdvanced, handleChange }) {
  return (
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
                control={<Switch checked={formData.ssl} onChange={handleChange('ssl')} />}
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
  )
}

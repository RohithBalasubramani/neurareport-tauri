/**
 * Email / SMTP settings card
 */
import {
  Stack,
  Typography,
  FormControlLabel,
  Switch,
  Button,
  TextField,
  CircularProgress,
  useTheme,
} from '@mui/material'
import InputAdornment from '@mui/material/InputAdornment'
import IconButton from '@mui/material/IconButton'
import EmailIcon from '@mui/icons-material/Email'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import SendIcon from '@mui/icons-material/Send'
import SaveIcon from '@mui/icons-material/Save'
import SettingCard from './SettingCard'

export default function SmtpCard({
  smtp,
  smtpLoading,
  smtpTesting,
  showSmtpPassword,
  setShowSmtpPassword,
  onSmtpSave,
  onSmtpTest,
  onSmtpChange,
}) {
  const theme = useTheme()

  return (
    <SettingCard icon={EmailIcon} title="Email / SMTP">
      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 2 }}>
        Configure SMTP server for sending report emails. Settings are stored securely.
      </Typography>
      <Stack spacing={2}>
        <Stack direction="row" spacing={2}>
          <TextField
            fullWidth
            size="small"
            label="SMTP Host"
            placeholder="smtp.gmail.com"
            value={smtp.host}
            onChange={onSmtpChange('host')}
          />
          <TextField
            size="small"
            label="Port"
            type="number"
            value={smtp.port}
            onChange={onSmtpChange('port')}
            sx={{ width: 120, flexShrink: 0 }}
          />
        </Stack>
        <TextField
          fullWidth
          size="small"
          label="Sender Email"
          placeholder="noreply@example.com"
          value={smtp.sender}
          onChange={onSmtpChange('sender')}
        />
        <Stack direction="row" spacing={2}>
          <TextField
            fullWidth
            size="small"
            label="Username"
            placeholder="your-email@gmail.com"
            value={smtp.username}
            onChange={onSmtpChange('username')}
          />
          <TextField
            fullWidth
            size="small"
            label="Password"
            type={showSmtpPassword ? 'text' : 'password'}
            value={smtp.password}
            onChange={onSmtpChange('password')}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setShowSmtpPassword(p => !p)} edge="end">
                      {showSmtpPassword ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />
        </Stack>
        <FormControlLabel
          control={<Switch checked={smtp.use_tls} onChange={onSmtpChange('use_tls')} size="small" />}
          label={<Typography variant="body2" sx={{ color: theme.palette.text.primary }}>Use TLS encryption</Typography>}
        />
        <Stack direction="row" spacing={1.5}>
          <Button
            variant="contained"
            size="small"
            startIcon={smtpLoading ? <CircularProgress size={16} /> : <SaveIcon />}
            onClick={onSmtpSave}
            disabled={smtpLoading || !smtp.host}
            sx={{ borderRadius: 1 }}
          >
            {smtpLoading ? 'Saving...' : 'Save'}
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={smtpTesting ? <CircularProgress size={16} /> : <SendIcon />}
            onClick={onSmtpTest}
            disabled={smtpTesting || !smtp.host}
            sx={{ borderRadius: 1 }}
          >
            {smtpTesting ? 'Testing...' : 'Test Connection'}
          </Button>
        </Stack>
      </Stack>
    </SettingCard>
  )
}

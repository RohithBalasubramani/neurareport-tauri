/**
 * Security settings card: 2FA, password, sessions
 */
import {
  Stack,
  Typography,
  FormControlLabel,
  Switch,
  Divider,
  Alert,
  Button,
  TextField,
  Box,
  useTheme,
  alpha,
} from '@mui/material'
import LockIcon from '@mui/icons-material/Lock'
import { useToast } from '@/components/ToastProvider'
import SettingCard from './SettingCard'

export default function SecurityCard({
  twoFactorEnabled,
  setTwoFactorEnabled,
  showTwoFactorSetup,
  setShowTwoFactorSetup,
  onTwoFactorToggle,
}) {
  const theme = useTheme()
  const toast = useToast()

  return (
    <SettingCard icon={LockIcon} title="Security">
      <Stack spacing={2}>
        <FormControlLabel
          control={
            <Switch
              checked={twoFactorEnabled}
              onChange={onTwoFactorToggle}
              size="small"
            />
          }
          label={
            <Stack>
              <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
                Two-Factor Authentication (2FA)
              </Typography>
              <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
                {twoFactorEnabled
                  ? 'Your account is protected with 2FA'
                  : 'Add an extra layer of security to your account'}
              </Typography>
            </Stack>
          }
        />
        {twoFactorEnabled && (
          <Alert severity="success" sx={{ borderRadius: 1 }}>
            Two-factor authentication is enabled. Your account is more secure.
          </Alert>
        )}
        {showTwoFactorSetup && (
          <Alert severity="info" sx={{ borderRadius: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Set up Two-Factor Authentication
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              To enable 2FA, scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
              and enter the verification code.
            </Typography>
            <Box sx={{ textAlign: 'center', py: 2, bgcolor: 'background.paper', borderRadius: 1, mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                [QR Code would appear here]
              </Typography>
            </Box>
            <TextField
              fullWidth
              size="small"
              label="Verification Code"
              placeholder="Enter 6-digit code"
              sx={{ mb: 2 }}
            />
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                size="small"
                onClick={() => {
                  setTwoFactorEnabled(true)
                  setShowTwoFactorSetup(false)
                  toast.show('Two-factor authentication enabled!', 'success')
                }}
              >
                Verify & Enable
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => setShowTwoFactorSetup(false)}
              >
                Cancel
              </Button>
            </Stack>
          </Alert>
        )}

        <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.08) }} />

        <Box>
          <Typography variant="body2" sx={{ color: theme.palette.text.primary, mb: 0.5 }}>
            Change Password
          </Typography>
          <Typography variant="caption" sx={{ color: theme.palette.text.secondary, display: 'block', mb: 1 }}>
            Update your password to keep your account secure.
          </Typography>
          <Button variant="outlined" size="small" sx={{ borderRadius: 1 }}>
            Change Password
          </Button>
        </Box>

        <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.08) }} />

        <Box>
          <Typography variant="body2" sx={{ color: theme.palette.text.primary, mb: 0.5 }}>
            Active Sessions
          </Typography>
          <Typography variant="caption" sx={{ color: theme.palette.text.secondary, display: 'block', mb: 1 }}>
            You're currently logged in on 1 device.
          </Typography>
          <Button variant="outlined" size="small" sx={{ borderRadius: 1, color: 'text.secondary' }}>
            Sign Out Other Devices
          </Button>
        </Box>
      </Stack>
    </SettingCard>
  )
}

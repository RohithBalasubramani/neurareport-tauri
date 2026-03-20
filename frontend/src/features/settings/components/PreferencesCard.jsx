/**
 * User preferences card: demo mode, toggles
 */
import {
  Stack,
  Typography,
  FormControlLabel,
  Switch,
  Divider,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import SettingsIcon from '@mui/icons-material/Settings'
import DownloadIcon from '@mui/icons-material/Download'
import SettingCard from './SettingCard'
import { ExportButton } from '@/styles'

export function ExportCard({ exporting, onExportConfig }) {
  const theme = useTheme()

  return (
    <SettingCard icon={DownloadIcon} title="Export & Backup">
      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 2 }}>
        Export your configuration for backup or migration purposes.
      </Typography>
      <ExportButton
        variant="outlined"
        startIcon={exporting ? <CircularProgress size={16} /> : <DownloadIcon />}
        onClick={onExportConfig}
        disabled={exporting}
      >
        {exporting ? 'Exporting...' : 'Export Configuration'}
      </ExportButton>
    </SettingCard>
  )
}

export default function PreferencesCard({
  preferences,
  demoMode,
  onDemoModeChange,
  onPrefChange,
}) {
  const theme = useTheme()

  return (
    <SettingCard icon={SettingsIcon} title="Preferences">
      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 2 }}>
        These preferences are synced with the server and cached locally.
      </Typography>
      <Stack spacing={1}>
        <FormControlLabel
          control={
            <Switch
              checked={demoMode}
              onChange={onDemoModeChange}
              size="small"
            />
          }
          label={
            <Stack>
              <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
                Demo Mode
              </Typography>
              <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
                Explore with sample data (no real database required)
              </Typography>
            </Stack>
          }
        />
        <Divider sx={{ my: 1, borderColor: alpha(theme.palette.divider, 0.06) }} />
        <FormControlLabel
          control={
            <Switch
              checked={preferences.autoRefreshJobs ?? true}
              onChange={onPrefChange('autoRefreshJobs')}
              size="small"
            />
          }
          label={
            <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
              Auto-refresh jobs list
            </Typography>
          }
        />
        <FormControlLabel
          control={
            <Switch
              checked={preferences.showNotifications ?? true}
              onChange={onPrefChange('showNotifications')}
              size="small"
            />
          }
          label={
            <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
              Show desktop notifications
            </Typography>
          }
        />
        <FormControlLabel
          control={
            <Switch
              checked={preferences.confirmDelete ?? true}
              onChange={onPrefChange('confirmDelete')}
              size="small"
            />
          }
          label={
            <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
              Confirm before deleting items
            </Typography>
          }
        />
        <FormControlLabel
          control={
            <Switch
              checked={preferences.compactTables ?? false}
              onChange={onPrefChange('compactTables')}
              size="small"
            />
          }
          label={
            <Typography variant="body2" sx={{ color: theme.palette.text.primary }}>
              Use compact table view
            </Typography>
          }
        />
      </Stack>
    </SettingCard>
  )
}

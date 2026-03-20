/**
 * Personal settings card: language, timezone
 */
import { Stack, TextField, MenuItem, useTheme } from '@mui/material'
import { Typography } from '@mui/material'
import LanguageIcon from '@mui/icons-material/Language'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import PersonIcon from '@mui/icons-material/Person'
import SettingCard from './SettingCard'
import { TIMEZONE_OPTIONS, LANGUAGE_OPTIONS } from '../hooks/useSettingsState'

export default function PersonalSettingsCard({
  selectedLanguage,
  selectedTimezone,
  onLanguageChange,
  onTimezoneChange,
}) {
  const theme = useTheme()

  return (
    <SettingCard icon={PersonIcon} title="Personal Settings">
      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 2 }}>
        Customize your personal experience with NeuraReport.
      </Typography>
      <Stack spacing={2}>
        <TextField
          select
          fullWidth
          size="small"
          label="Language"
          value={selectedLanguage}
          onChange={onLanguageChange}
          InputProps={{
            startAdornment: <LanguageIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 20 }} />,
          }}
        >
          {LANGUAGE_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          fullWidth
          size="small"
          label="Timezone"
          value={selectedTimezone}
          onChange={onTimezoneChange}
          InputProps={{
            startAdornment: <AccessTimeIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 20 }} />,
          }}
        >
          {TIMEZONE_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>
      </Stack>
    </SettingCard>
  )
}

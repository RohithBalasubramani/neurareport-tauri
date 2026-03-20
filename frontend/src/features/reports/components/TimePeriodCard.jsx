import {
  Box,
  Typography,
  Stack,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  Checkbox,
  InputAdornment,
  useTheme,
  alpha,
} from '@mui/material'
import TodayIcon from '@mui/icons-material/Today'
import DateRangeIcon from '@mui/icons-material/DateRange'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import FilterListIcon from '@mui/icons-material/FilterList'
import { GlassCard, StyledFormControl } from '@/styles'
import { getDatePresets } from '../hooks/useReportDateRange'
import {
  SectionLabel,
  StyledTextField,
  PresetChip,
} from './ReportsStyledComponents'

export default function TimePeriodCard({
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  startTime,
  setStartTime,
  endTime,
  setEndTime,
  datePreset,
  setDatePreset,
  handleDatePreset,
  keyFields,
  keyValues,
  keyOptions,
  onKeyValueChange,
}) {
  const theme = useTheme()

  return (
    <GlassCard>
      <SectionLabel>
        <TodayIcon sx={{ fontSize: 14 }} />
        Time Period
      </SectionLabel>

      {/* Date preset chips */}
      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
        {Object.entries(getDatePresets()).map(([key, preset]) => (
          <PresetChip
            key={key}
            label={preset.label}
            icon={<TodayIcon sx={{ fontSize: 14 }} />}
            onClick={() => handleDatePreset(key)}
            selected={datePreset === key}
            variant={datePreset === key ? 'filled' : 'outlined'}
          />
        ))}
        <PresetChip
          label="Custom"
          icon={<DateRangeIcon sx={{ fontSize: 14 }} />}
          onClick={() => handleDatePreset('custom')}
          selected={datePreset === 'custom'}
          variant={datePreset === 'custom' ? 'filled' : 'outlined'}
        />
      </Stack>

      {/* Date & time inputs */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="flex-start">
        <StyledTextField
          label="Start Date"
          type="date"
          value={startDate}
          onChange={(e) => {
            setStartDate(e.target.value)
            setDatePreset('custom')
          }}
          InputLabelProps={{ shrink: true }}
          fullWidth
          size="small"
        />
        <StyledTextField
          label="Start Time"
          type="time"
          value={startTime}
          onChange={(e) => {
            setStartTime(e.target.value)
            setDatePreset('custom')
          }}
          InputLabelProps={{ shrink: true }}
          size="small"
          sx={{ maxWidth: { sm: 160 }, minWidth: 130 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AccessTimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
        />
        <StyledTextField
          label="End Date"
          type="date"
          value={endDate}
          onChange={(e) => {
            setEndDate(e.target.value)
            setDatePreset('custom')
          }}
          InputLabelProps={{ shrink: true }}
          fullWidth
          size="small"
        />
        <StyledTextField
          label="End Time"
          type="time"
          value={endTime}
          onChange={(e) => {
            setEndTime(e.target.value)
            setDatePreset('custom')
          }}
          InputLabelProps={{ shrink: true }}
          size="small"
          sx={{ maxWidth: { sm: 160 }, minWidth: 130 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AccessTimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
        />
      </Stack>
      <Typography variant="caption" sx={{ color: 'text.secondary', mt: -0.5 }}>
        Time is optional — leave blank to include all records for the selected dates.
      </Typography>

      {/* Key field filters (conditional) */}
      {keyFields.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Divider sx={{ mb: 2, borderColor: alpha(theme.palette.divider, 0.2) }} />
          <SectionLabel>
            <FilterListIcon sx={{ fontSize: 14 }} />
            Filter Parameters
          </SectionLabel>
          <Stack spacing={2}>
            {keyFields.map((key) => (
              <StyledFormControl key={key} fullWidth size="small">
                <InputLabel>{key}</InputLabel>
                <Select
                  multiple
                  value={keyValues[key] || []}
                  onChange={(e) => onKeyValueChange(key, e.target.value, keyOptions[key] || [])}
                  label={key}
                  renderValue={(selected) => {
                    const clean = selected.filter(v => v !== '__all__')
                    return clean.length === 0
                      ? 'All'
                      : (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {clean.map((v) => (
                            <Chip key={v} label={v} size="small" />
                          ))}
                        </Box>
                      )
                  }}
                >
                  <MenuItem value="__all__">
                    <Checkbox
                      checked={(keyValues[key] || []).length === (keyOptions[key] || []).length && (keyOptions[key] || []).length > 0}
                      indeterminate={(keyValues[key] || []).length > 0 && (keyValues[key] || []).length < (keyOptions[key] || []).length}
                      size="small"
                    />
                    <em>All</em>
                  </MenuItem>
                  <Divider />
                  {(keyOptions[key] || []).map((option) => (
                    <MenuItem key={option} value={option}>
                      <Checkbox checked={(keyValues[key] || []).includes(option)} size="small" />
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </StyledFormControl>
            ))}
          </Stack>
        </Box>
      )}
    </GlassCard>
  )
}

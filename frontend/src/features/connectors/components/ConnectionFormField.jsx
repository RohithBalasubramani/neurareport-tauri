import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Typography,
  InputAdornment,
  IconButton,
} from '@mui/material'
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material'

export default function ConnectionFormField({
  field,
  value,
  error,
  disabled,
  showPassword,
  onChange,
  onTogglePassword,
}) {
  switch (field.type) {
    case 'password':
      return (
        <TextField
          key={field.name}
          fullWidth
          label={field.label}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          required={field.required}
          error={Boolean(error)}
          helperText={error || field.helpText}
          disabled={disabled}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => onTogglePassword(field.name)}
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
          onChange={(e) => onChange(field.name, e.target.value)}
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
          onChange={(e) => onChange(field.name, parseInt(e.target.value) || '')}
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
              onChange={(e) => onChange(field.name, e.target.checked)}
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
            onChange={(e) => onChange(field.name, e.target.value)}
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
          onChange={(e) => onChange(field.name, e.target.value)}
          required={field.required}
          error={Boolean(error)}
          helperText={error || field.helpText}
          disabled={disabled}
          sx={{ mb: 2 }}
        />
      )
  }
}

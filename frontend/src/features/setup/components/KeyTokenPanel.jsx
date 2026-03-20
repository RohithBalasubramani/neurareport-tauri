import {
  Box, Typography, Stack, TextField, Chip, Alert, Autocomplete,
} from '@mui/material'
import { ALL_OPTION, formatTokenLabel } from '../utils/templatesPaneUtils'

export default function KeyTokenPanel({
  templatesWithKeys,
  keysReady,
  keyValues,
  keyOptions,
  keyOptionsLoading,
  onKeyValueChange,
}) {
  return (
    <Stack spacing={1.5} sx={{ mt: 2 }}>
      <Typography variant="subtitle2">Key Token Values</Typography>
      {!keysReady && (
        <Alert severity="warning">Fill in all key token values to enable discovery and runs.</Alert>
      )}
      {templatesWithKeys.map(({ tpl, tokens }) => (
        <Box
          key={tpl.id}
          sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.5, bgcolor: 'background.paper' }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{tpl.name || tpl.id}</Typography>
          <Stack spacing={1} sx={{ mt: 1 }}>
            {tokens.map(({ name, required, options = [] }) => {
              const rawOptions = Array.isArray(options) && options.length ? options : (keyOptions?.[tpl.id]?.[name] || [])
              const normalizedOptions = Array.from(
                new Set(
                  rawOptions
                    .map((option) => (option == null ? '' : String(option).trim()))
                    .filter(Boolean),
                ),
              )
              const dropdownOptions = [ALL_OPTION, ...normalizedOptions]
              const loading = Boolean(keyOptionsLoading?.[tpl.id])
              const storedValue = Array.isArray(keyValues?.[tpl.id]?.[name]) ? keyValues[tpl.id][name] : []
              const value = storedValue.includes(ALL_OPTION)
                ? [ALL_OPTION]
                : storedValue
              return (
                <Autocomplete
                  key={`${tpl.id}-${name}`}
                  multiple
                  disableCloseOnSelect
                  options={dropdownOptions}
                  value={value}
                  loading={loading}
                  onChange={(_event, newValue) => {
                    let next = Array.isArray(newValue) ? newValue.filter(Boolean) : []
                    if (next.includes(ALL_OPTION)) {
                      next = [ALL_OPTION, ...normalizedOptions]
                    } else {
                      next = Array.from(new Set(next))
                    }
                    onKeyValueChange(tpl.id, name, next)
                  }}
                  getOptionLabel={(option) => (option === ALL_OPTION ? 'All' : option)}
                  renderTags={(tagValue, getTagProps) =>
                    tagValue.map((option, index) => (
                      <Chip
                        {...getTagProps({ index })}
                        key={`${tpl.id}-${name}-tag-${option}-${index}`}
                        size="small"
                        label={option === ALL_OPTION ? 'All' : option}
                      />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label={`${formatTokenLabel(name)}${required ? ' *' : ''}`}
                      required={required}
                      placeholder={loading ? 'Loading...' : dropdownOptions.length ? 'Select values' : 'No options'}
                    />
                  )}
                />
              )
            })}
          </Stack>
        </Box>
      ))}
    </Stack>
  )
}

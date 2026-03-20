import {
  Alert,
  Autocomplete,
  Box,
  Chip,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'

export default function KeyTokenValuesSection({
  selected,
  keysMissing,
  templatesWithKeys,
  keyValues,
  keyOptions,
  keyOptionsLoading,
  onKeyValueChange,
}) {
  const SELECT_ALL_OPTION = '__NR_SELECT_ALL__'
  const ALL_SENTINELS = new Set(['all', 'select all', SELECT_ALL_OPTION.toLowerCase()])

  return (
    <Stack spacing={1.5}>
      <Typography variant="subtitle2">Key Token Values</Typography>
      {keysMissing && (
        <Alert severity="warning">Fill in all key token values to enable discovery and runs.</Alert>
      )}
      {templatesWithKeys.length > 0 ? (
        templatesWithKeys.map(({ tpl, tokens }) => (
          <Box
            key={tpl.id}
            sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.5, bgcolor: 'background.paper' }}
          >
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{tpl.name || tpl.id}</Typography>
            <Stack spacing={1} sx={{ mt: 1 }}>
              {tokens.map((token) => {
                const templateOptions = keyOptions?.[tpl.id] || {}
                const tokenOptions = templateOptions[token] || []
                const loading = Boolean(keyOptionsLoading?.[tpl.id])
                const stored = keyValues?.[tpl.id]?.[token]
                const rawValue = Array.isArray(stored)
                  ? stored
                  : stored
                    ? [stored]
                    : []
                const uniqueTokenOptions = tokenOptions.filter((opt, idx, arr) => arr.indexOf(opt) === idx)
                const optionsWithAll = uniqueTokenOptions.length > 1 ? [...uniqueTokenOptions, SELECT_ALL_OPTION] : uniqueTokenOptions
                const isAllStored = rawValue.some(
                  (val) => typeof val === 'string' && ALL_SENTINELS.has(val.toLowerCase()),
                )
                const displayValue = isAllStored
                  ? [SELECT_ALL_OPTION]
                  : rawValue
                      .filter((val, idx) => rawValue.indexOf(val) === idx)
                      .filter((val) => val !== SELECT_ALL_OPTION)
                return (
                  <Autocomplete
                    key={token}
                    multiple
                    freeSolo
                    options={optionsWithAll}
                    value={displayValue}
                    getOptionLabel={(option) => (option === SELECT_ALL_OPTION ? 'All values' : option)}
                    filterSelectedOptions
                    renderTags={(value, getTagProps) => {
                      const isAllSelectedExplicit =
                        uniqueTokenOptions.length > 0 &&
                        value.length === uniqueTokenOptions.length &&
                        value.every((item) => uniqueTokenOptions.includes(item))
                      const selectedIncludesAllSentinel = value.some(
                        (item) => typeof item === 'string' && ALL_SENTINELS.has(item.toLowerCase()),
                      )
                      if (isAllSelectedExplicit || selectedIncludesAllSentinel) {
                        return [
                          <Chip
                            {...getTagProps({ index: 0 })}
                            key="all-values"
                            label="All values"
                          />,
                        ]
                      }
                      return value.map((option, index) => (
                        <Chip
                          {...getTagProps({ index })}
                          key={option}
                          label={option === SELECT_ALL_OPTION ? 'All values' : option}
                        />
                      ))
                    }}
                    onChange={(_event, newValue) => {
                      const cleaned = Array.isArray(newValue) ? newValue : []
                      const normalized = cleaned
                        .map((item) => (typeof item === 'string' ? item.trim() : ''))
                        .filter((item) => item.length > 0)
                      const hasSelectAll = normalized.some((item) => {
                        const lower = item.toLowerCase()
                        return item === SELECT_ALL_OPTION || ALL_SENTINELS.has(lower)
                      })
                      const sanitized = normalized.filter(
                        (item) => !ALL_SENTINELS.has(item.toLowerCase()) && item !== SELECT_ALL_OPTION,
                      )
                      if (hasSelectAll) {
                        const allList = uniqueTokenOptions.length
                          ? [SELECT_ALL_OPTION, ...uniqueTokenOptions]
                          : [SELECT_ALL_OPTION]
                        onKeyValueChange(tpl.id, token, allList)
                      } else {
                        onKeyValueChange(tpl.id, token, sanitized)
                      }
                    }}
                    isOptionEqualToValue={(option, optionValue) => option === optionValue}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label={token}
                        required
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {loading ? <CircularProgress color="inherit" size={16} /> : null}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
                  />
                )
              })}
            </Stack>
          </Box>
        ))
      ) : (
        <Box
          sx={{
            border: '1px dashed',
            borderColor: 'divider',
            borderRadius: 1,
            p: 1.5,
            bgcolor: 'background.default',
            color: 'text.secondary',
          }}
        >
          <Typography variant="body2">
            {selected.length === 0
              ? 'Select a template to configure key token filters.'
              : 'Selected templates do not define key tokens.'}
          </Typography>
        </Box>
      )}
    </Stack>
  )
}

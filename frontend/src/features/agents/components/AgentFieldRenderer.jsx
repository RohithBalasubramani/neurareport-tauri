/**
 * Agent Form Field Renderer Component
 */
import { Box, TextField, Grid, Chip, Alert, CircularProgress, Select, MenuItem, FormControl, InputLabel, Typography, Autocomplete } from '@mui/material'
import ConnectionSelector from '@/components/common/ConnectionSelector'

export default function AgentFieldRenderer({
  field,
  selectedAgent,
  formData,
  recentRuns,
  runsLoading,
  selectedConnectionId,
  onFieldChange,
  onConnectionChange,
}) {
  // For data_analyst, hide data field if using sample data or database connection
  if (selectedAgent.type === 'data_analyst' && field.name === 'data') {
    const dataSource = formData.dataSource || 'paste_spreadsheet'
    if (dataSource === 'sample_sales' || dataSource === 'sample_inventory') {
      return (
        <Grid item xs={12} key={field.name}>
          <Alert severity="info" sx={{ mt: 1 }}>
            Using sample {dataSource === 'sample_sales' ? 'sales' : 'inventory'} data. Just enter your question above!
          </Alert>
        </Grid>
      )
    }
    if (dataSource === 'database_connection') {
      return (
        <Grid item xs={12} key={field.name}>
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={onConnectionChange}
            label="Select Database"
            showStatus
          />
        </Grid>
      )
    }
  }

  // Conditionally hide question/compareRunId fields based on analysisType
  if (selectedAgent.type === 'report_analyst') {
    const analysisType = formData.analysisType || 'summarize'
    if (field.name === 'question' && analysisType !== 'qa') return null
    if (field.name === 'compareRunId' && analysisType !== 'compare') return null
  }

  return (
    <Grid item xs={12} md={field.multiline ? 12 : 6} key={field.name}>
      {field.type === 'reportRunPicker' ? (
        <Autocomplete
          freeSolo
          options={recentRuns}
          loading={runsLoading}
          getOptionLabel={(option) => {
            if (typeof option === 'string') return option
            const name = option.templateName || option.template_name || option.templateId || option.template_id || ''
            const date = option.createdAt || option.created_at || ''
            const dateStr = date ? new Date(date).toLocaleDateString() : ''
            return `${name} — ${dateStr} (${option.id?.slice(0, 8)}...)`
          }}
          value={formData[field.name] || null}
          onChange={(_, value) => {
            const runId = typeof value === 'string' ? value : value?.id || ''
            onFieldChange(field.name, runId)
          }}
          onInputChange={(_, value, reason) => {
            if (reason === 'input') onFieldChange(field.name, value)
          }}
          renderOption={(props, option) => {
            const { key, ...rest } = props
            const name = option.templateName || option.template_name || option.templateId || option.template_id || ''
            const date = option.createdAt || option.created_at || ''
            const dateStr = date ? new Date(date).toLocaleString() : ''
            const period = [option.startDate || option.start_date, option.endDate || option.end_date].filter(Boolean).join(' – ')
            return (
              <li key={key} {...rest}>
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <Typography variant="body2" fontWeight={500}>{name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {dateStr}{period ? ` | ${period}` : ''} | {option.id?.slice(0, 12)}...
                  </Typography>
                </Box>
              </li>
            )
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              label={field.label}
              placeholder={field.placeholder}
              required={field.required}
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {runsLoading ? <CircularProgress size={18} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
      ) : field.type === 'select' ? (
        <FormControl fullWidth>
          <InputLabel>{field.label}</InputLabel>
          <Select
            value={formData[field.name] || field.default || ''}
            label={field.label}
            onChange={(e) => onFieldChange(field.name, e.target.value)}
          >
            {field.options.map((opt) => {
              let label = opt.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
              if (opt === 'paste_spreadsheet') label = 'Paste from Spreadsheet (Recommended)'
              if (opt === 'database_connection') label = 'Query Database Connection'
              if (opt === 'sample_sales') label = 'Use Sample Sales Data'
              if (opt === 'sample_inventory') label = 'Use Sample Inventory Data'
              if (opt === 'custom_json') label = 'Enter Raw JSON (Advanced)'
              return (
                <MenuItem key={opt} value={opt}>
                  {label}
                </MenuItem>
              )
            })}
          </Select>
        </FormControl>
      ) : field.type === 'multiselect' ? (
        <FormControl fullWidth>
          <InputLabel>{field.label}</InputLabel>
          <Select
            multiple
            value={formData[field.name] || []}
            label={field.label}
            onChange={(e) => onFieldChange(field.name, e.target.value)}
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value.replace(/_/g, ' ')} size="small" />
                ))}
              </Box>
            )}
          >
            {field.options.map((opt) => (
              <MenuItem key={opt} value={opt}>
                {opt.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      ) : field.type === 'number' ? (
        <TextField
          fullWidth
          type="number"
          label={field.label}
          value={formData[field.name] ?? field.default ?? ''}
          onChange={(e) => onFieldChange(field.name, parseInt(e.target.value))}
          inputProps={{ min: field.min, max: field.max }}
          required={field.required}
        />
      ) : field.type === 'spreadsheet' ? (
        <TextField
          fullWidth
          label={formData.dataSource === 'custom_json' ? 'JSON Data' : field.label}
          value={formData[field.name] || ''}
          onChange={(e) => onFieldChange(field.name, e.target.value)}
          multiline
          rows={field.rows || 4}
          required={field.required}
          placeholder={formData.dataSource === 'custom_json'
            ? '[{"name": "John", "value": 100}, {"name": "Jane", "value": 200}]'
            : field.placeholder || 'Copy from Excel/Sheets and paste here...'}
          helperText={formData.dataSource === 'custom_json'
            ? 'Enter valid JSON array of objects'
            : 'Supports tab-separated (Excel) or comma-separated (CSV) data'}
        />
      ) : (
        <TextField
          fullWidth
          label={field.label}
          value={formData[field.name] || ''}
          onChange={(e) => onFieldChange(field.name, e.target.value)}
          multiline={field.multiline}
          rows={field.rows || 4}
          required={field.required}
          placeholder={field.placeholder}
        />
      )}
    </Grid>
  )
}

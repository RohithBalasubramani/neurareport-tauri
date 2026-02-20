/**
 * Pivot Table Builder Component
 * Drag-and-drop interface for creating pivot tables from spreadsheet data.
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import {
  Close as CloseIcon,
  DragIndicator as DragIcon,
  Functions as AggregateIcon,
  FilterList as FilterIcon,
  ViewColumn as ColumnIcon,
  TableRows as RowIcon,
  DataObject as ValuesIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  SwapVert as SortIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const BuilderContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const FieldListPanel = styled(Box)(({ theme }) => ({
  width: 240,
  padding: theme.spacing(2),
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

const ConfigPanel = styled(Box)(({ theme }) => ({
  width: 280,
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

const PreviewPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(2),
  overflowY: 'auto',
}))

const DropZone = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isDragOver',
})(({ theme, isDragOver }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(2),
  minHeight: 80,
  border: `2px dashed ${isDragOver ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.3)}`,
  borderRadius: 8,
  backgroundColor: isDragOver ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : 'transparent',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const FieldChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.25),
  cursor: 'grab',
  '&:active': {
    cursor: 'grabbing',
  },
}))

const DraggableField = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  padding: theme.spacing(0.75, 1.5),
  cursor: 'grab',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
  '&:active': {
    cursor: 'grabbing',
  },
}))

const PreviewTable = styled('table')(({ theme }) => ({
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: '14px',
  '& th, & td': {
    padding: theme.spacing(0.75, 1),
    border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    textAlign: 'left',
  },
  '& th': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    fontWeight: 600,
  },
  '& tbody tr:hover': {
    backgroundColor: alpha(theme.palette.action.hover, 0.5),
  },
}))

// =============================================================================
// AGGREGATION FUNCTIONS
// =============================================================================

const AGGREGATIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'average', label: 'Average' },
  { value: 'min', label: 'Min' },
  { value: 'max', label: 'Max' },
  { value: 'countDistinct', label: 'Count Distinct' },
  { value: 'product', label: 'Product' },
  { value: 'stdev', label: 'Std Dev' },
  { value: 'variance', label: 'Variance' },
]

const SORT_OPTIONS = [
  { value: 'none', label: 'No Sort' },
  { value: 'asc', label: 'A to Z' },
  { value: 'desc', label: 'Z to A' },
  { value: 'value_asc', label: 'Value (Low to High)' },
  { value: 'value_desc', label: 'Value (High to Low)' },
]

// =============================================================================
// FIELD SETTINGS DIALOG
// =============================================================================

function FieldSettingsDialog({ open, field, zone, onClose, onSave }) {
  const [localField, setLocalField] = useState(field || {})

  const handleChange = (key, value) => {
    setLocalField((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    onSave?.(localField)
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Field Settings: {field?.name}</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2}>
          {zone === 'values' && (
            <>
              <FormControl size="small" fullWidth>
                <InputLabel>Summarize by</InputLabel>
                <Select
                  value={localField.aggregation || 'sum'}
                  label="Summarize by"
                  onChange={(e) => handleChange('aggregation', e.target.value)}
                >
                  {AGGREGATIONS.map((agg) => (
                    <MenuItem key={agg.value} value={agg.value}>
                      {agg.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Custom Name"
                size="small"
                fullWidth
                value={localField.customName || ''}
                onChange={(e) => handleChange('customName', e.target.value)}
                placeholder={`${localField.aggregation || 'Sum'} of ${localField.name}`}
              />

              <FormControl size="small" fullWidth>
                <InputLabel>Number Format</InputLabel>
                <Select
                  value={localField.format || 'general'}
                  label="Number Format"
                  onChange={(e) => handleChange('format', e.target.value)}
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="number">Number (1,234.56)</MenuItem>
                  <MenuItem value="currency">Currency ($1,234.56)</MenuItem>
                  <MenuItem value="percent">Percentage (12.34%)</MenuItem>
                  <MenuItem value="scientific">Scientific (1.23E+03)</MenuItem>
                </Select>
              </FormControl>
            </>
          )}

          {(zone === 'rows' || zone === 'columns') && (
            <>
              <FormControl size="small" fullWidth>
                <InputLabel>Sort</InputLabel>
                <Select
                  value={localField.sort || 'none'}
                  label="Sort"
                  onChange={(e) => handleChange('sort', e.target.value)}
                >
                  {SORT_OPTIONS.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Custom Name"
                size="small"
                fullWidth
                value={localField.customName || ''}
                onChange={(e) => handleChange('customName', e.target.value)}
              />
            </>
          )}

          {zone === 'filters' && (
            <>
              <Typography variant="body2" color="text.secondary">
                Select values to include:
              </Typography>
              {/* Filter value selection would go here */}
              <Alert severity="info">
                Filter configuration coming soon
              </Alert>
            </>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function PivotTableBuilder({
  availableFields = [],
  config = { rows: [], columns: [], values: [], filters: [] },
  onConfigChange,
  data = [],
  onRefresh,
  onClose,
}) {
  const theme = useTheme()
  const [draggedField, setDraggedField] = useState(null)
  const [dragOverZone, setDragOverZone] = useState(null)
  const [settingsDialog, setSettingsDialog] = useState({ open: false, field: null, zone: null })
  const [expandedZones, setExpandedZones] = useState(['rows', 'columns', 'values', 'filters'])

  // Toggle zone expansion
  const toggleZone = useCallback((zone) => {
    setExpandedZones((prev) =>
      prev.includes(zone) ? prev.filter((z) => z !== zone) : [...prev, zone]
    )
  }, [])

  // Handle drag start
  const handleDragStart = useCallback((field, sourceZone = null) => {
    setDraggedField({ ...field, sourceZone })
  }, [])

  // Handle drag over
  const handleDragOver = useCallback((e, zone) => {
    e.preventDefault()
    setDragOverZone(zone)
  }, [])

  // Handle drag leave
  const handleDragLeave = useCallback(() => {
    setDragOverZone(null)
  }, [])

  // Handle drop
  const handleDrop = useCallback((e, targetZone) => {
    e.preventDefault()
    setDragOverZone(null)

    if (!draggedField) return

    const newConfig = { ...config }

    // Remove from source zone if it was moved
    if (draggedField.sourceZone) {
      newConfig[draggedField.sourceZone] = newConfig[draggedField.sourceZone].filter(
        (f) => f.name !== draggedField.name
      )
    }

    // Add to target zone
    const fieldToAdd = {
      name: draggedField.name,
      type: draggedField.type,
      aggregation: targetZone === 'values' ? 'sum' : undefined,
    }

    // Check if field already exists in target zone
    const existsInTarget = newConfig[targetZone].some((f) => f.name === draggedField.name)
    if (!existsInTarget) {
      newConfig[targetZone] = [...newConfig[targetZone], fieldToAdd]
    }

    onConfigChange?.(newConfig)
    setDraggedField(null)
  }, [draggedField, config, onConfigChange])

  // Remove field from zone
  const handleRemoveField = useCallback((zone, fieldName) => {
    const newConfig = { ...config }
    newConfig[zone] = newConfig[zone].filter((f) => f.name !== fieldName)
    onConfigChange?.(newConfig)
  }, [config, onConfigChange])

  // Open field settings
  const handleOpenSettings = useCallback((field, zone) => {
    setSettingsDialog({ open: true, field, zone })
  }, [])

  // Save field settings
  const handleSaveSettings = useCallback((updatedField) => {
    const { zone } = settingsDialog
    const newConfig = { ...config }
    newConfig[zone] = newConfig[zone].map((f) =>
      f.name === updatedField.name ? updatedField : f
    )
    onConfigChange?.(newConfig)
    setSettingsDialog({ open: false, field: null, zone: null })
  }, [settingsDialog, config, onConfigChange])

  // Generate preview data
  const previewData = useMemo(() => {
    // This would be replaced with actual pivot table calculation
    if (config.rows.length === 0 && config.columns.length === 0) return []

    // Sample preview data
    return [
      { rowLabel: 'Category A', col1: 1234, col2: 5678, total: 6912 },
      { rowLabel: 'Category B', col1: 2345, col2: 6789, total: 9134 },
      { rowLabel: 'Category C', col1: 3456, col2: 7890, total: 11346 },
      { rowLabel: 'Grand Total', col1: 7035, col2: 20357, total: 27392 },
    ]
  }, [config])

  // Render drop zone
  const renderDropZone = (zone, icon, label) => {
    const Icon = icon
    const fields = config[zone] || []
    const isExpanded = expandedZones.includes(zone)

    return (
      <Box sx={{ mb: 2 }}>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          onClick={() => toggleZone(zone)}
          sx={{ cursor: 'pointer', mb: 0.5 }}
        >
          <Stack direction="row" alignItems="center" spacing={1}>
            <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {label}
            </Typography>
            {fields.length > 0 && (
              <Chip label={fields.length} size="small" sx={{ height: 18, fontSize: '10px' }} />
            )}
          </Stack>
          {isExpanded ? <CollapseIcon fontSize="small" /> : <ExpandIcon fontSize="small" />}
        </Stack>

        <Collapse in={isExpanded}>
          <DropZone
            elevation={0}
            isDragOver={dragOverZone === zone}
            onDragOver={(e) => handleDragOver(e, zone)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, zone)}
          >
            {fields.length === 0 ? (
              <Typography variant="caption" color="text.disabled" sx={{ textAlign: 'center', display: 'block' }}>
                Drag fields here
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                {fields.map((field) => (
                  <FieldChip
                    key={field.name}
                    label={
                      zone === 'values' && field.aggregation
                        ? `${AGGREGATIONS.find((a) => a.value === field.aggregation)?.label || 'Sum'} of ${field.customName || field.name}`
                        : field.customName || field.name
                    }
                    size="small"
                    draggable
                    onDragStart={() => handleDragStart(field, zone)}
                    onClick={() => handleOpenSettings(field, zone)}
                    onDelete={() => handleRemoveField(zone, field.name)}
                    deleteIcon={<CloseIcon sx={{ fontSize: 14 }} />}
                  />
                ))}
              </Box>
            )}
          </DropZone>
        </Collapse>
      </Box>
    )
  }

  return (
    <BuilderContainer>
      {/* Available Fields */}
      <FieldListPanel>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Fields
          </Typography>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={onRefresh}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>

        <TextField
          size="small"
          fullWidth
          placeholder="Search fields..."
          sx={{ mb: 2 }}
        />

        <List dense disablePadding>
          {availableFields.map((field) => (
            <DraggableField
              key={field.name}
              draggable
              onDragStart={() => handleDragStart(field)}
            >
              <DragIcon sx={{ color: 'text.disabled', fontSize: 16, mr: 1 }} />
              <ListItemText
                primary={field.name}
                secondary={field.type}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </DraggableField>
          ))}
        </List>

        {availableFields.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No fields available
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Select a data range first
            </Typography>
          </Box>
        )}
      </FieldListPanel>

      {/* Configuration Zones */}
      <ConfigPanel>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
          Pivot Table Areas
        </Typography>

        {renderDropZone('filters', FilterIcon, 'Filters')}
        {renderDropZone('columns', ColumnIcon, 'Columns')}
        {renderDropZone('rows', RowIcon, 'Rows')}
        {renderDropZone('values', ValuesIcon, 'Values')}

        <Divider sx={{ my: 2 }} />

        <Button
          fullWidth
          variant="contained"
          startIcon={<CalculateIcon />}
          disabled={config.values.length === 0}
        >
          Generate Pivot Table
        </Button>
      </ConfigPanel>

      {/* Preview */}
      <PreviewPanel>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Preview
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Stack>

        {config.values.length === 0 ? (
          <Paper
            elevation={0}
            sx={{
              p: 4,
              textAlign: 'center',
              border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
              borderRadius: 1,  // Figma spec: 8px
            }}
          >
            <CalculateIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Drag fields to build your pivot table
            </Typography>
            <Typography variant="body2" color="text.disabled">
              Add at least one field to Values to see results
            </Typography>
          </Paper>
        ) : (
          <Paper
            elevation={0}
            sx={{
              border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
              borderRadius: 1,  // Figma spec: 8px
              overflow: 'auto',
            }}
          >
            <PreviewTable>
              <thead>
                <tr>
                  <th>{config.rows[0]?.customName || config.rows[0]?.name || 'Row Labels'}</th>
                  {config.columns.length > 0 ? (
                    <>
                      <th>Value 1</th>
                      <th>Value 2</th>
                    </>
                  ) : (
                    config.values.map((v) => (
                      <th key={v.name}>
                        {v.customName || `${AGGREGATIONS.find((a) => a.value === v.aggregation)?.label || 'Sum'} of ${v.name}`}
                      </th>
                    ))
                  )}
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {previewData.map((row, i) => (
                  <tr key={i} style={{ fontWeight: row.rowLabel === 'Grand Total' ? 600 : 400 }}>
                    <td>{row.rowLabel}</td>
                    <td>{row.col1.toLocaleString()}</td>
                    <td>{row.col2.toLocaleString()}</td>
                    <td>{row.total.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </PreviewTable>
          </Paper>
        )}
      </PreviewPanel>

      {/* Field Settings Dialog */}
      <FieldSettingsDialog
        open={settingsDialog.open}
        field={settingsDialog.field}
        zone={settingsDialog.zone}
        onClose={() => setSettingsDialog({ open: false, field: null, zone: null })}
        onSave={handleSaveSettings}
      />
    </BuilderContainer>
  )
}

// Missing import
import { Alert } from '@mui/material'

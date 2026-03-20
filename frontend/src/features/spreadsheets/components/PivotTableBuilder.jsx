/**
 * Pivot Table Builder Component
 * Drag-and-drop interface for creating pivot tables from spreadsheet data.
 */
import {
  Box, Typography, IconButton, Tooltip, TextField,
  Button, Stack, Divider, List, ListItemText,
  ListItemButton, alpha, styled,
} from '@mui/material'
import {
  DragIndicator as DragIcon, FilterList as FilterIcon,
  ViewColumn as ColumnIcon, TableRows as RowIcon,
  DataObject as ValuesIcon, Refresh as RefreshIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { usePivotTableBuilder } from '../hooks/usePivotTableBuilder'
import FieldSettingsDialog from './FieldSettingsDialog'
import PivotDropZone from './PivotDropZone'
import PivotPreviewTable from './PivotPreviewTable'

const BuilderContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const FieldListPanel = styled(Box)(({ theme }) => ({
  width: 240, padding: theme.spacing(2),
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper, overflowY: 'auto',
}))

const ConfigPanel = styled(Box)(({ theme }) => ({
  width: 280, padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper, overflowY: 'auto',
}))

const DraggableField = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8, marginBottom: theme.spacing(0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  padding: theme.spacing(0.75, 1.5), cursor: 'grab',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
  '&:active': { cursor: 'grabbing' },
}))

const ZONE_CONFIG = [
  { zone: 'filters', icon: FilterIcon, label: 'Filters' },
  { zone: 'columns', icon: ColumnIcon, label: 'Columns' },
  { zone: 'rows', icon: RowIcon, label: 'Rows' },
  { zone: 'values', icon: ValuesIcon, label: 'Values' },
]

export default function PivotTableBuilder({
  availableFields = [],
  config = { rows: [], columns: [], values: [], filters: [] },
  onConfigChange, data = [], onRefresh, onClose,
}) {
  const {
    dragOverZone, settingsDialog, expandedZones, previewData,
    setSettingsDialog, toggleZone, handleDragStart, handleDragOver,
    handleDragLeave, handleDrop, handleRemoveField,
    handleOpenSettings, handleSaveSettings,
  } = usePivotTableBuilder({ config, onConfigChange })

  return (
    <BuilderContainer>
      <FieldListPanel>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Fields</Typography>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={onRefresh}><RefreshIcon fontSize="small" /></IconButton>
          </Tooltip>
        </Stack>
        <TextField size="small" fullWidth placeholder="Search fields..." sx={{ mb: 2 }} />
        <List dense disablePadding>
          {availableFields.map((field) => (
            <DraggableField key={field.name} draggable onDragStart={() => handleDragStart(field)}>
              <DragIcon sx={{ color: 'text.disabled', fontSize: 16, mr: 1 }} />
              <ListItemText
                primary={field.name} secondary={field.type}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </DraggableField>
          ))}
        </List>
        {availableFields.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">No fields available</Typography>
            <Typography variant="caption" color="text.disabled">Select a data range first</Typography>
          </Box>
        )}
      </FieldListPanel>
      <ConfigPanel>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>Pivot Table Areas</Typography>
        {ZONE_CONFIG.map(({ zone, icon, label }) => (
          <PivotDropZone
            key={zone} zone={zone} icon={icon} label={label}
            fields={config[zone] || []} isExpanded={expandedZones.includes(zone)}
            isDragOver={dragOverZone === zone} onToggleZone={toggleZone}
            onDragOver={handleDragOver} onDragLeave={handleDragLeave}
            onDrop={handleDrop} onDragStart={handleDragStart}
            onOpenSettings={handleOpenSettings} onRemoveField={handleRemoveField}
          />
        ))}
        <Divider sx={{ my: 2 }} />
        <Button fullWidth variant="contained" startIcon={<CalculateIcon />} disabled={config.values.length === 0}>
          Generate Pivot Table
        </Button>
      </ConfigPanel>
      <PivotPreviewTable config={config} previewData={previewData} onClose={onClose} />
      <FieldSettingsDialog
        open={settingsDialog.open} field={settingsDialog.field} zone={settingsDialog.zone}
        onClose={() => setSettingsDialog({ open: false, field: null, zone: null })}
        onSave={handleSaveSettings}
      />
    </BuilderContainer>
  )
}

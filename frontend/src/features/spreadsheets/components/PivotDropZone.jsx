/**
 * Pivot Table Drop Zone
 * A droppable area for pivot table field configuration.
 */
import {
  Box,
  Typography,
  Stack,
  Chip,
  Collapse,
  Paper,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { AGGREGATIONS } from '../hooks/usePivotTableBuilder'

const DropZoneContainer = styled(Paper, {
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

export default function PivotDropZone({
  zone,
  icon: Icon,
  label,
  fields,
  isExpanded,
  isDragOver,
  onToggleZone,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragStart,
  onOpenSettings,
  onRemoveField,
}) {
  return (
    <Box sx={{ mb: 2 }}>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        onClick={() => onToggleZone(zone)}
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
        <DropZoneContainer
          elevation={0}
          isDragOver={isDragOver}
          onDragOver={(e) => onDragOver(e, zone)}
          onDragLeave={onDragLeave}
          onDrop={(e) => onDrop(e, zone)}
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
                  onDragStart={() => onDragStart(field, zone)}
                  onClick={() => onOpenSettings(field, zone)}
                  onDelete={() => onRemoveField(zone, field.name)}
                  deleteIcon={<CloseIcon sx={{ fontSize: 14 }} />}
                />
              ))}
            </Box>
          )}
        </DropZoneContainer>
      </Collapse>
    </Box>
  )
}

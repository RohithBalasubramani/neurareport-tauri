/**
 * DrillDownDataList — renders the list of drillable data items.
 */
import {
  Box,
  Typography,
  Stack,
  List,
  ListItemText,
  ListItemIcon,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Divider,
  alpha,
  useTheme,
} from '@mui/material'
import {
  ChevronRight as ChevronIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as DocumentIcon,
} from '@mui/icons-material'
import {
  DataCard,
  DrillableRow,
  ChangeIndicator,
  ProgressBar,
  ProgressFill,
  formatValue,
  getTrendIcon,
} from './DrillDownPanelStyles'

export function DrillDownDataItems({ data, summary, selectedItem, valueFormat, onItemClick }) {
  if (data.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <FolderOpenIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          No data at this level
        </Typography>
      </Box>
    )
  }

  return (
    <List disablePadding>
      {data.map((item, index) => {
        const TrendIcon = getTrendIcon(item.change)
        const trend = item.change > 0 ? 'up' : item.change < 0 ? 'down' : 'flat'
        const isDrillable = item.children || item.drillable
        const percentage = summary ? (item.value / summary.total) * 100 : 0

        return (
          <DrillableRow
            key={item.id || index}
            onClick={() => onItemClick(item)}
            selected={selectedItem?.id === item.id}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>
              {isDrillable ? (
                <FolderIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
              ) : (
                <DocumentIcon sx={{ fontSize: 20, color: 'text.secondary' }} />
              )}
            </ListItemIcon>

            <ListItemText
              primary={
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {item.label}
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {formatValue(item.value, valueFormat)}
                  </Typography>
                </Stack>
              }
              secondary={
                <Box sx={{ mt: 0.75 }}>
                  <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
                    <ProgressBar sx={{ flex: 1 }}>
                      <ProgressFill width={percentage} />
                    </ProgressBar>
                    <Typography variant="caption" color="text.secondary" sx={{ minWidth: 40 }}>
                      {percentage.toFixed(1)}%
                    </Typography>
                  </Stack>

                  {item.change !== undefined && (
                    <ChangeIndicator trend={trend}>
                      <TrendIcon sx={{ fontSize: 14, mr: 0.25 }} />
                      {item.change > 0 ? '+' : ''}
                      {item.change}%
                    </ChangeIndicator>
                  )}

                  {item.subtitle && (
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                      {item.subtitle}
                    </Typography>
                  )}
                </Box>
              }
            />

            {isDrillable && (
              <ChevronIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
            )}
          </DrillableRow>
        )
      })}
    </List>
  )
}

export function DrillDownItemDetails({ selectedItem, valueFormat }) {
  const theme = useTheme()
  if (!selectedItem || !selectedItem.details) return null

  return (
    <>
      <Divider sx={{ my: 2 }} />
      <DataCard elevation={0}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
          {selectedItem.label} Details
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableBody>
              {Object.entries(selectedItem.details).map(([key, value]) => (
                <TableRow key={key}>
                  <TableCell sx={{ fontWeight: 500, color: 'text.secondary', border: 0, py: 0.5, pl: 0 }}>
                    {key}
                  </TableCell>
                  <TableCell sx={{ border: 0, py: 0.5 }}>
                    {typeof value === 'number' ? formatValue(value, valueFormat) : value}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </DataCard>
    </>
  )
}

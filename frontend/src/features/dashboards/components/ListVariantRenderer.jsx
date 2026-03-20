/**
 * List variant sub-renderer for WidgetRenderer (alerts, timeline, eventlog).
 */
import {
  Box,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import { Timeline as TimelineIcon } from '@mui/icons-material'
import { AlertListCard, SEVERITY_COLORS } from './WidgetRendererStyles'

export default function ListVariantRenderer({ variantKey, vConfig, data, config }) {
  const listType = vConfig.listType || 'alerts'
  const title = config?.title || vConfig.label

  if (listType === 'alerts') {
    const items = data?.alerts || data?.events || data?.items || []
    return (
      <AlertListCard>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          {title}
        </Typography>
        {items.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No alerts to display.
          </Typography>
        ) : (
          <List dense disablePadding>
            {items.slice(0, 10).map((item, i) => (
              <ListItem key={i} disableGutters sx={{ py: 0.25 }}>
                <ListItemText
                  primary={item.message || item.title || item.text || `Alert ${i + 1}`}
                  secondary={item.timestamp || item.time || ''}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
                {item.severity && (
                  <Chip
                    label={item.severity}
                    size="small"
                    color={SEVERITY_COLORS[item.severity] || 'default'}
                    sx={{ ml: 1 }}
                  />
                )}
              </ListItem>
            ))}
          </List>
        )}
      </AlertListCard>
    )
  }

  if (listType === 'timeline') {
    const items = data?.events || data?.timeline || data?.items || []
    return (
      <AlertListCard>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          {title}
        </Typography>
        {items.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No events to display.
          </Typography>
        ) : (
          <List dense disablePadding>
            {items.slice(0, 15).map((item, i) => (
              <ListItem key={i} disableGutters sx={{ py: 0.25 }}>
                <Box sx={{ mr: 1.5, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <TimelineIcon sx={{ fontSize: 16, color: 'text.disabled' }} />
                  {i < items.length - 1 && (
                    <Box sx={{ width: 1, flex: 1, bgcolor: 'divider', minHeight: 12 }} />
                  )}
                </Box>
                <ListItemText
                  primary={item.message || item.title || item.text || `Event ${i + 1}`}
                  secondary={item.timestamp || item.time || ''}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
              </ListItem>
            ))}
          </List>
        )}
      </AlertListCard>
    )
  }

  // eventlog
  const items = data?.events || data?.logs || data?.items || []
  return (
    <AlertListCard>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        {title}
      </Typography>
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No log entries to display.
        </Typography>
      ) : (
        <List dense disablePadding>
          {items.slice(0, 20).map((item, i) => (
            <ListItem key={i} disableGutters sx={{ py: 0.15 }}>
              <Typography
                variant="caption"
                sx={{ fontFamily: 'monospace', color: 'text.disabled', mr: 1, minWidth: 60 }}
              >
                {item.timestamp || item.time || ''}
              </Typography>
              <ListItemText
                primary={item.message || item.text || `Log ${i + 1}`}
                primaryTypographyProps={{ variant: 'body2', sx: { fontFamily: 'monospace', fontSize: '12px' } }}
              />
              {item.level && (
                <Chip
                  label={item.level}
                  size="small"
                  variant="outlined"
                  sx={{ ml: 1, height: 18, fontSize: '10px' }}
                />
              )}
            </ListItem>
          ))}
        </List>
      )}
    </AlertListCard>
  )
}

import { Box, Typography, CircularProgress, Chip } from '@mui/material'
import TableChartIcon from '@mui/icons-material/TableChart'
import { GlassCard } from '@/styles/components'

const statusColors = {
  migrated: 'success',
  pending: 'warning',
  error: 'error',
}

const healthColors = {
  mapped: 'success',
  partial: 'warning',
  unmapped: 'error',
}

export default function DeviceTableOverview({ deviceTables = [], loading }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (deviceTables.length === 0) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <TableChartIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">No device tables</Typography>
        <Typography variant="body2" color="text.secondary">
          This Logger database has no configured device data tables.
        </Typography>
      </GlassCard>
    )
  }

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 2 }}>
      {deviceTables.map((dt) => (
        <GlassCard key={dt.id} sx={{ '&:hover': { transform: 'none' } }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
            {dt.name}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            {dt.status && (
              <Chip
                label={dt.status}
                size="small"
                color={statusColors[dt.status] || 'default'}
                variant="outlined"
              />
            )}
            {dt.mapping_health && (
              <Chip
                label={`Mapping: ${dt.mapping_health}`}
                size="small"
                color={healthColors[dt.mapping_health] || 'default'}
                variant="outlined"
              />
            )}
          </Box>
          {dt.last_migrated_at && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              Last migrated: {new Date(dt.last_migrated_at).toLocaleString()}
            </Typography>
          )}
        </GlassCard>
      ))}
    </Box>
  )
}

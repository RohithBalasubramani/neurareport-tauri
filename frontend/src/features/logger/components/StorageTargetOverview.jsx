import { Box, Typography, CircularProgress, Chip } from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import { GlassCard } from '@/styles/components'

const providerLabels = {
  sqlite: 'SQLite',
  postgres: 'PostgreSQL',
  postgresql: 'PostgreSQL',
  mysql: 'MySQL',
  mssql: 'SQL Server',
}

const providerColors = {
  sqlite: 'default',
  postgres: 'primary',
  postgresql: 'primary',
  mysql: 'warning',
  mssql: 'secondary',
}

export default function StorageTargetOverview({ storageTargets = [], loading }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (storageTargets.length === 0) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <StorageIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">No storage targets</Typography>
        <Typography variant="body2" color="text.secondary">
          This Logger database has no configured storage targets.
        </Typography>
      </GlassCard>
    )
  }

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 2 }}>
      {storageTargets.map((target) => (
        <GlassCard key={target.id} sx={{ '&:hover': { transform: 'none' } }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight={600}>{target.name}</Typography>
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {target.is_default && <Chip label="Default" size="small" color="info" variant="outlined" />}
              <Chip
                label={providerLabels[target.provider] || target.provider}
                size="small"
                color={providerColors[target.provider] || 'default'}
                variant="outlined"
              />
            </Box>
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              mb: 1,
            }}
          >
            {target.connection_string || '—'}
          </Typography>

          {target.status && (
            <Chip
              label={target.status}
              size="small"
              color={target.status === 'connected' ? 'success' : target.status === 'error' ? 'error' : 'default'}
              variant="outlined"
            />
          )}

          {target.last_error && (
            <Typography
              variant="caption"
              sx={{ color: 'error.main', display: 'block', mt: 0.5 }}
            >
              {target.last_error}
            </Typography>
          )}
        </GlassCard>
      ))}
    </Box>
  )
}

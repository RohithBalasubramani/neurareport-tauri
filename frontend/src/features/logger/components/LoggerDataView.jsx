import { Box, Typography, Button, Chip, Alert } from '@mui/material'
import SensorsIcon from '@mui/icons-material/Sensors'
import RadarIcon from '@mui/icons-material/Radar'
import { GlassCard } from '@/styles/components'

export default function LoggerDataView({
  selectedConnectionId,
  loggerConnections,
  discovering,
  handleDiscover,
}) {
  if (!selectedConnectionId) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <SensorsIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No Logger Database Selected
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select an existing PostgreSQL connection or click "Discover Logger" to find Logger databases.
          Once connected, you can use Logger data in templates and reports.
        </Typography>
        <Button
          variant="contained"
          startIcon={<RadarIcon />}
          onClick={handleDiscover}
          disabled={discovering}
        >
          Discover Logger Databases
        </Button>
      </GlassCard>
    )
  }

  return (
    <GlassCard>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        Data Pipeline Integration
      </Typography>
      <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
        This Logger database is available as a data source throughout NeuraReport.
        You can select it in the <strong>Reports</strong> page, <strong>Template Creator</strong>,
        and any feature that uses the Data Source selector.
      </Alert>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 2 }}>
        {loggerConnections.filter(c => c.id === selectedConnectionId).map(c => (
          <GlassCard key={c.id} sx={{ '&:hover': { transform: 'none' } }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
              {c.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', fontSize: '0.75rem', mb: 1 }}>
              {c.db_type}
            </Typography>
            <Chip
              size="small"
              label={c.status || 'connected'}
              color={c.status === 'connected' || !c.status ? 'success' : 'default'}
              variant="outlined"
            />
          </GlassCard>
        ))}
      </Box>

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          onClick={() => window.location.href = '/neurareport/reports'}
          size="small"
        >
          Go to Reports
        </Button>
        <Button
          variant="outlined"
          onClick={() => window.location.href = '/neurareport/templates/create'}
          size="small"
        >
          Create Template
        </Button>
        <Button
          variant="outlined"
          onClick={() => window.location.href = '/neurareport/connections'}
          size="small"
        >
          Manage Connections
        </Button>
      </Box>
    </GlassCard>
  )
}

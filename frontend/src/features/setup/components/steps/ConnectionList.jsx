import {
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  CardActionArea,
  Radio,
  Chip,
  Alert,
  alpha,
} from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { neutral } from '@/app/theme'

export default function ConnectionList({ connections, selectedId, onSelect }) {
  if (connections.length === 0 || connections.every((c) => c.isDemo)) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        No database connections yet. Add one below or try demo mode above.
      </Alert>
    )
  }

  return (
    <Stack spacing={2} sx={{ mb: 3 }}>
      {connections.map((conn) => (
        <Card
          key={conn.id}
          variant="outlined"
          sx={{
            border: 2,
            borderColor: selectedId === conn.id ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
            transition: 'border-color 0.2s',
          }}
        >
          <CardActionArea onClick={() => onSelect(conn.id)}>
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Radio
                checked={selectedId === conn.id}
                sx={{ p: 0 }}
              />
              <StorageIcon sx={{ color: 'text.secondary' }} />
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" fontWeight={500}>
                  {conn.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {conn.db_type} • {conn.summary || conn.database}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  size="small"
                  label={conn.status === 'connected' ? 'Connected' : 'Disconnected'}
                  variant="outlined"
                  sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                />
                {selectedId === conn.id && (
                  <CheckCircleIcon sx={{ color: 'text.secondary' }} />
                )}
              </Stack>
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
    </Stack>
  )
}

/**
 * Column definitions for the Connections DataTable.
 */
import { useMemo } from 'react'
import {
  Box,
  Chip,
  Stack,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import StorageIcon from '@mui/icons-material/Storage'
import FavoriteButton from '@/features/favorites/components/FavoriteButton.jsx'
import { neutral, status as statusColors } from '@/app/theme'
import { IconContainer } from './ConnectionsStyledComponents'

export function useConnectionColumns({ favorites, handleFavoriteToggle, activeConnectionId }) {
  const theme = useTheme()

  const columns = useMemo(() => [
    {
      field: 'name',
      headerName: 'Name',
      minWidth: 200,
      flex: 1,
      renderCell: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FavoriteButton
            entityType="connections"
            entityId={row.id}
            initialFavorite={favorites.has(row.id)}
            onToggle={(isFav) => handleFavoriteToggle(row.id, isFav)}
          />
          <IconContainer
            sx={{
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            }}
          >
            <StorageIcon sx={{ color: theme.palette.text.secondary, fontSize: 16 }} />
          </IconContainer>
          <Box sx={{ minWidth: 0 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Box data-testid="connection-name" sx={{ fontWeight: 500, fontSize: '14px', color: theme.palette.text.primary }}>
                {value}
              </Box>
              {activeConnectionId === row.id && (
                <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
              )}
            </Stack>
            <Box sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
              {row.summary || row.db_type}
            </Box>
          </Box>
        </Box>
      ),
    },
    {
      field: 'db_type',
      headerName: 'Type',
      width: 120,
      renderCell: (value) => {
        const typeLabels = { sqlite: 'SQLite', postgresql: 'PostgreSQL', postgres: 'PostgreSQL', mysql: 'MySQL', mssql: 'SQL Server', oracle: 'Oracle', csv: 'CSV', excel: 'Excel', json: 'JSON' }
        return (
          <Chip
            label={typeLabels[(value || '').toLowerCase()] || value || 'Unknown'}
            size="small"
            data-testid="connection-db-type"
            sx={{
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              color: theme.palette.text.secondary,
              fontSize: '0.75rem',
              borderRadius: 1,
            }}
          />
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (value) => {
        const isConnected = value === 'connected'
        return (
          <Chip
            icon={isConnected
              ? <CheckCircleIcon sx={{ fontSize: 14 }} />
              : <ErrorIcon sx={{ fontSize: 14 }} />
            }
            label={value || 'Unknown'}
            size="small"
            data-testid="connection-status"
            sx={{
              fontSize: '0.75rem',
              textTransform: 'capitalize',
              borderRadius: 1,
              bgcolor: isConnected
                ? alpha(statusColors.success, 0.1)
                : alpha(statusColors.destructive, 0.1),
              color: isConnected
                ? statusColors.success
                : statusColors.destructive,
              '& .MuiChip-icon': {
                color: 'inherit',
              },
            }}
          />
        )
      },
    },
    {
      field: 'lastLatencyMs',
      headerName: 'Latency',
      width: 100,
      renderCell: (value) => (
        <Box data-testid="connection-latency" sx={{ color: theme.palette.text.secondary, fontSize: '14px' }}>
          {value ? `${value}ms` : '-'}
        </Box>
      ),
    },
    {
      field: 'lastConnected',
      headerName: 'Last Connected',
      width: 160,
      renderCell: (value) => {
        if (!value) return <Box sx={{ color: theme.palette.text.disabled, fontSize: '14px' }}>-</Box>
        const d = new Date(value)
        const now = new Date()
        const diffMs = now - d
        const diffMin = Math.floor(diffMs / 60000)
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        let relative
        if (diffMin < 1) relative = 'Just now'
        else if (diffMin < 60) relative = `${diffMin}m ago`
        else if (diffHr < 24) relative = `${diffHr}h ago`
        else if (diffDay < 7) relative = `${diffDay}d ago`
        else relative = d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Box data-testid="connection-last-connected" sx={{ color: theme.palette.text.secondary, fontSize: '14px', cursor: 'default' }}>
              {relative}
            </Box>
          </Tooltip>
        )
      },
    },
  ], [favorites, handleFavoriteToggle, theme, activeConnectionId])

  const filters = useMemo(() => [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'connected', label: 'Connected' },
        { value: 'disconnected', label: 'Disconnected' },
        { value: 'error', label: 'Error' },
      ],
    },
    {
      key: 'db_type',
      label: 'Type',
      options: [
        { value: 'sqlite', label: 'SQLite' },
        { value: 'postgresql', label: 'PostgreSQL' },
      ],
    },
  ], [])

  return { columns, filters }
}

/**
 * Hook: DataTable column definitions for templates
 */
import { useMemo } from 'react'
import { Box, Stack, Tooltip, Typography, useTheme } from '@mui/material'
import FavoriteButton from '@/features/favorites/components/FavoriteButton.jsx'
import { getKindConfig, getStatusConfig } from '../components/templateConfigHelpers'
import {
  KindIconContainer,
  KindChip,
  StatusChip,
  TagChip,
} from '../components/TemplateStyledComponents'

export default function useTemplateColumns({ favorites, handleFavoriteToggle }) {
  const theme = useTheme()

  return useMemo(() => [
    {
      field: 'name',
      headerName: 'Design',
      minWidth: 200,
      flex: 1,
      renderCell: (value, row) => {
        const config = getKindConfig(theme, row.kind)
        const Icon = config.icon
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FavoriteButton
              entityType="templates"
              entityId={row.id}
              initialFavorite={favorites.has(row.id)}
              onToggle={(isFav) => handleFavoriteToggle(row.id, isFav)}
            />
            <KindIconContainer>
              <Icon sx={{ color: 'text.secondary', fontSize: 18 }} />
            </KindIconContainer>
            <Box sx={{ minWidth: 0, overflow: 'hidden' }}>
              <Typography sx={{
                fontWeight: 500,
                fontSize: '14px',
                color: 'text.primary',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {value || row.id}
              </Typography>
              <Typography sx={{
                fontSize: '0.75rem',
                color: 'text.secondary',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {row.description || `${row.kind?.toUpperCase() || 'PDF'} Design`}
              </Typography>
            </Box>
          </Box>
        )
      },
    },
    {
      field: 'kind',
      headerName: 'Type',
      width: 100,
      renderCell: (value) => {
        const config = getKindConfig(theme, value)
        return (
          <KindChip
            label={value?.toUpperCase() || 'PDF'}
            size="small"
            kindColor={config.color}
            kindBg={config.bgColor}
          />
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (value) => {
        const config = getStatusConfig(theme, value)
        return (
          <StatusChip
            label={value || 'approved'}
            size="small"
            statusColor={config.color}
            statusBg={config.bgColor}
          />
        )
      },
    },
    {
      field: 'mappingKeys',
      headerName: 'Fields',
      width: 80,
      renderCell: (value, row) => {
        const count = Array.isArray(value) ? value.length : Array.isArray(row.mappingKeys) ? row.mappingKeys.length : row.tokens_count
        return (
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            {count || '-'}
          </Typography>
        )
      },
    },
    {
      field: 'tags',
      headerName: 'Tags',
      width: 180,
      renderCell: (value) => {
        const tags = Array.isArray(value) ? value : []
        if (!tags.length) {
          return <Typography sx={{ fontSize: '0.75rem', color: 'text.disabled' }}>-</Typography>
        }
        return (
          <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap' }}>
            {tags.slice(0, 2).map((tag) => (
              <TagChip key={tag} label={tag} size="small" />
            ))}
            {tags.length > 2 && (
              <Typography variant="caption" color="text.secondary">
                +{tags.length - 2}
              </Typography>
            )}
          </Stack>
        )
      },
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 120,
      renderCell: (value, row) => {
        const raw = value || row.created_at
        if (!raw) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(raw)
        const now = new Date()
        const diffDay = Math.floor((now - d) / 86400000)
        const relative = diffDay < 1 ? 'Today' : diffDay < 2 ? 'Yesterday' : diffDay < 7 ? `${diffDay}d ago` : d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
    {
      field: 'lastRunAt',
      headerName: 'Last Run',
      width: 120,
      renderCell: (value, row) => {
        const raw = value || row.last_run_at
        if (!raw) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(raw)
        const now = new Date()
        const diffMs = now - d
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        const relative = diffHr < 1 ? 'Just now' : diffHr < 24 ? `${diffHr}h ago` : diffDay < 7 ? `${diffDay}d ago` : d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
    {
      field: 'updatedAt',
      headerName: 'Updated',
      width: 140,
      renderCell: (value, row) => {
        const raw = value || row.updated_at
        return (
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            {raw ? new Date(raw).toLocaleDateString() : '-'}
          </Typography>
        )
      },
    },
  ], [theme, favorites, handleFavoriteToggle])
}

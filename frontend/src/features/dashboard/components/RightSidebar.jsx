import {
  Box,
  Typography,
  Stack,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import DescriptionIcon from '@mui/icons-material/Description'
import InsightsIcon from '@mui/icons-material/Insights'
import StarIcon from '@mui/icons-material/Star'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import { neutral } from '@/app/theme'
import { GlassCard } from '@/styles'

export default function RightSidebar({ topTemplates, favorites, handleNavigate }) {
  const theme = useTheme()

  return (
    <Stack spacing={3}>
      {/* Top Designs */}
      <GlassCard sx={{ animationDelay: '300ms' }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <InsightsIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          <Typography variant="subtitle2" fontWeight={600}>
            Top Designs
          </Typography>
        </Stack>

        {topTemplates.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No design usage data yet
          </Typography>
        ) : (
          <Stack spacing={1.5}>
            {topTemplates.slice(0, 4).map((tpl, idx) => (
              <Stack
                key={tpl.id}
                direction="row"
                alignItems="center"
                spacing={1.5}
                onClick={() =>
                  handleNavigate(`/reports?template=${tpl.id}`, 'Open reports', { templateId: tpl.id })
                }
                sx={{
                  cursor: 'pointer',
                  p: 1,
                  mx: -1,
                  borderRadius: 1.5,
                  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
                  },
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                    fontSize: '0.75rem',
                  }}
                >
                  {tpl.kind === 'excel' ? (
                    <TableChartIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  ) : (
                    <PictureAsPdfIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  )}
                </Avatar>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body2" fontWeight={600} noWrap>
                    {tpl.name}
                  </Typography>
                  <Typography variant="caption" color="text.tertiary">
                    {tpl.runCount} runs
                  </Typography>
                </Box>
              </Stack>
            ))}
          </Stack>
        )}
      </GlassCard>

      {/* Favorites */}
      <GlassCard sx={{ animationDelay: '350ms' }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <StarIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          <Typography variant="subtitle2" fontWeight={600}>
            Favorites
          </Typography>
        </Stack>

        {favorites.templates.length === 0 && favorites.connections.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No favorites yet. Star designs or connections for quick access.
          </Typography>
        ) : (
          <Stack spacing={1}>
            {favorites.templates.slice(0, 3).map((tpl) => (
              <Stack
                key={tpl.id}
                direction="row"
                alignItems="center"
                spacing={1}
                sx={{
                  cursor: 'pointer',
                  p: 0.75,
                  mx: -0.75,
                  borderRadius: 1,
                  '&:hover': { bgcolor: alpha(theme.palette.action.hover, 0.5) },
                }}
                onClick={() =>
                  handleNavigate(`/reports?template=${tpl.id}`, 'Open reports', { templateId: tpl.id })
                }
              >
                <DescriptionIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                  {tpl.name}
                </Typography>
              </Stack>
            ))}
            {favorites.connections.slice(0, 2).map((conn) => (
              <Stack
                key={conn.id}
                direction="row"
                alignItems="center"
                spacing={1}
                sx={{
                  cursor: 'pointer',
                  p: 0.75,
                  mx: -0.75,
                  borderRadius: 1,
                  '&:hover': { bgcolor: alpha(theme.palette.action.hover, 0.5) },
                }}
                onClick={() => handleNavigate('/connections', 'Open connections')}
              >
                <StorageIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                  {conn.name}
                </Typography>
              </Stack>
            ))}
          </Stack>
        )}
      </GlassCard>
    </Stack>
  )
}

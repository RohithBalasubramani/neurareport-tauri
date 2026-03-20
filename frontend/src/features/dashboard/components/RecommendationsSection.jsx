import {
  Box,
  Typography,
  Stack,
  Button,
  Chip,
  Avatar,
  Grow,
  alpha,
  useTheme,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import { neutral } from '@/app/theme'
import { shimmer, GlassCard } from '@/styles'
import { RecommendationCard } from './DashboardStyledComponents'

export default function RecommendationsSection({
  recommendations,
  recLoading,
  recFromAI,
  templates,
  handleRefreshRecommendations,
  handleNavigate,
}) {
  const theme = useTheme()

  return (
    <GlassCard
      sx={{
        mt: 4,
        background: theme.palette.mode === 'dark'
          ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.04)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`
          : undefined,
        animationDelay: '400ms',
      }}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 1,
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AutoAwesomeIcon sx={{ fontSize: 24, color: 'white' }} />
          </Box>
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>
              {recFromAI ? 'AI Recommendations' : 'Recent Designs'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {recFromAI ? 'Smart design suggestions based on your data' : 'Showing your recent designs (AI unavailable)'}
            </Typography>
          </Box>
        </Stack>
        <Button
          size="small"
          startIcon={<LightbulbIcon sx={{ fontSize: 16 }} />}
          onClick={handleRefreshRecommendations}
          disabled={recLoading}
          sx={{ fontWeight: 600 }}
        >
          {recLoading ? 'Loading...' : recFromAI ? 'Refresh' : 'Try AI Again'}
        </Button>
      </Stack>

      {recLoading ? (
        <Box
          sx={{
            height: 120,
            borderRadius: 1,
            background: `linear-gradient(90deg, ${alpha(theme.palette.action.hover, 0.5)} 25%, ${alpha(theme.palette.action.hover, 0.8)} 50%, ${alpha(theme.palette.action.hover, 0.5)} 75%)`,
            backgroundSize: '200% 100%',
            animation: `${shimmer} 1.5s ease-in-out infinite`,
          }}
        />
      ) : recommendations.length === 0 ? (
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 2,
            }}
          >
            <LightbulbIcon sx={{ fontSize: 28, color: 'text.secondary' }} />
          </Box>
          {templates.length === 0 ? (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload a report design to unlock AI recommendations
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleNavigate('/templates', 'Open templates')}
                startIcon={<AddIcon />}
                sx={{ borderRadius: 1 }}
              >
                Add Report Design
              </Button>
            </>
          ) : (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                No recommendations yet
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleRefreshRecommendations}
                sx={{ borderRadius: 1 }}
              >
                Get AI Recommendations
              </Button>
            </>
          )}
        </Box>
      ) : (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
            gap: 2,
          }}
        >
          {recommendations.map((rec, idx) => (
            <Grow key={rec.id} in timeout={400 + idx * 100}>
              <RecommendationCard
                onClick={() =>
                  handleNavigate(`/reports?template=${rec.id}`, 'Open reports', { templateId: rec.id })
                }
              >
                <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
                  <Avatar
                    sx={{
                      width: 28,
                      height: 28,
                      bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                    }}
                  >
                    {rec.kind === 'excel' ? (
                      <TableChartIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                    ) : (
                      <PictureAsPdfIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                    )}
                  </Avatar>
                  {rec.matchScore && (
                    <Chip
                      label={`${Math.round((rec.matchScore || 0) * 100)}% match`}
                      size="small"
                      sx={{
                        height: 20,
                        fontSize: '10px',
                        fontWeight: 600,
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                        color: 'text.secondary',
                      }}
                    />
                  )}
                </Stack>
                <Typography variant="body2" fontWeight={600} noWrap sx={{ mb: 0.5 }}>
                  {rec.name}
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    lineHeight: 1.4,
                  }}
                >
                  {rec.description}
                </Typography>
              </RecommendationCard>
            </Grow>
          ))}
        </Box>
      )}
    </GlassCard>
  )
}

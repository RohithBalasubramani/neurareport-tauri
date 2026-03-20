import {
  Box,
  Typography,
  Button,
  Stack,
  TextField,
  CircularProgress,
  Grid,
  Avatar,
  Zoom,
  alpha,
  useTheme,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import BarChartIcon from '@mui/icons-material/BarChart'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import ZoomableChart from '../components/ZoomableChart'

export default function ChartsTab({
  chartQuery,
  setChartQuery,
  isGeneratingCharts,
  generatedCharts,
  onGenerateCharts,
}) {
  const theme = useTheme()

  return (
    <>
      <GlassCard sx={{ mb: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
          <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
            <AutoAwesomeIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Generate Charts with Natural Language
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Describe the visualization you want and AI will create it
            </Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={2}>
          <TextField
            fullWidth
            placeholder='e.g., "Show revenue by quarter as a line chart" or "Compare categories in a pie chart"'
            value={chartQuery}
            onChange={(e) => setChartQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onGenerateCharts()}
            disabled={isGeneratingCharts}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 1,  // Figma spec: 8px
              },
            }}
          />
          <Button
            variant="contained"
            onClick={onGenerateCharts}
            disabled={!chartQuery.trim() || isGeneratingCharts}
            startIcon={isGeneratingCharts ? <CircularProgress size={16} color="inherit" /> : <BarChartIcon />}
            sx={{
              minWidth: 160,
              borderRadius: 1,  // Figma spec: 8px
              textTransform: 'none',
              fontWeight: 600,
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              '&:hover': {
                background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              },
            }}
          >
            Generate
          </Button>
        </Stack>
      </GlassCard>

      <Grid container spacing={3}>
        {generatedCharts.map((chart, idx) => (
          <Grid size={{ xs: 12, md: 6 }} key={chart.id || idx}>
            <Zoom in timeout={300 + idx * 100}>
              <Box>
                <GlassCard>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    {chart.title}
                  </Typography>
                  {chart.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {chart.description}
                    </Typography>
                  )}
                  <Box sx={{ height: 320 }}>
                    <ZoomableChart spec={chart} data={chart.data} height={300} />
                  </Box>
                  {chart.ai_insights?.length > 0 && (
                    <Box
                      sx={{
                        mt: 2,
                        p: 2,
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                        borderRadius: 1,
                        border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                      }}
                    >
                      <Typography variant="caption" fontWeight={600} color="text.secondary">
                        AI INSIGHTS
                      </Typography>
                      {chart.ai_insights.map((insight, i) => (
                        <Typography key={i} variant="body2" sx={{ mt: 0.5 }}>
                          • {insight}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </GlassCard>
              </Box>
            </Zoom>
          </Grid>
        ))}
      </Grid>
    </>
  )
}

import {
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  alpha,
} from '@mui/material'
import ScienceIcon from '@mui/icons-material/Science'
import CloudIcon from '@mui/icons-material/Cloud'
import { neutral } from '@/app/theme'

export default function QuickStartCards({ selectedId, demoId, onSelectDemo, onSkip }) {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="subtitle2" fontWeight={600} color="text.secondary" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
        Quick Start
      </Typography>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <Card
          variant="outlined"
          sx={{
            flex: 1,
            border: 2,
            borderColor: selectedId === demoId ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
            bgcolor: selectedId === demoId ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
            },
          }}
        >
          <CardActionArea onClick={onSelectDemo} sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <ScienceIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
              <Typography variant="subtitle1" fontWeight={600}>
                Try Demo Mode
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Explore with sample data — no setup needed
              </Typography>
              <Chip label="Recommended for first-time users" size="small" variant="outlined" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
            </CardContent>
          </CardActionArea>
        </Card>

        <Card
          variant="outlined"
          sx={{
            flex: 1,
            border: 2,
            borderColor: 'divider',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'secondary.main',
            },
          }}
        >
          <CardActionArea onClick={onSkip} sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', py: 3 }}>
              <CloudIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
              <Typography variant="subtitle1" fontWeight={600}>
                Skip for Now
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Set up data source later and explore templates first
              </Typography>
            </CardContent>
          </CardActionArea>
        </Card>
      </Stack>
    </Box>
  )
}

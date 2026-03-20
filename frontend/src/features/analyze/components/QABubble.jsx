import {
  Box,
  Typography,
  Paper,
  Stack,
  Avatar,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import { neutral } from '@/app/theme'

export default function QABubble({ qa, index }) {
  const theme = useTheme()
  return (
    <Fade in timeout={300 + index * 100}>
      <Box sx={{ mb: 3 }}>
        {/* Question */}
        <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1.5 }}>
          <Paper
            sx={{
              maxWidth: '80%',
              p: 2,
              px: 3,
              borderRadius: '20px 20px 4px 20px',
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              color: 'common.white',
              boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.2)}`,
            }}
          >
            <Typography variant="body1" fontWeight={500}>
              {qa.question}
            </Typography>
          </Paper>
        </Stack>

        {/* Answer */}
        <Stack direction="row" sx={{ mb: 1 }}>
          <Avatar
            sx={{
              width: 36,
              height: 36,
              mr: 1.5,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
              color: 'text.secondary',
            }}
          >
            <SmartToyIcon sx={{ fontSize: 20 }} />
          </Avatar>
          <Paper
            sx={{
              maxWidth: '80%',
              p: 2,
              px: 3,
              borderRadius: '4px 20px 20px 20px',
              bgcolor: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
              {qa.answer}
            </Typography>
            {qa.sources?.length > 0 && (
              <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  Sources:
                </Typography>
                {qa.sources.slice(0, 2).map((source, i) => (
                  <Typography key={i} variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                    "{source.content_preview?.slice(0, 100)}..."
                  </Typography>
                ))}
              </Box>
            )}
          </Paper>
        </Stack>
      </Box>
    </Fade>
  )
}

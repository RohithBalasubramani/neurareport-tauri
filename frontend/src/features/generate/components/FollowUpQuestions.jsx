import { Box, Stack, Typography, Chip } from '@mui/material'
import LightbulbIcon from '@mui/icons-material/Lightbulb'

export default function FollowUpQuestions({ questions, onQuestionClick }) {
  if (!questions || questions.length === 0) return null

  return (
    <Box sx={{ px: 2, pb: 1.5 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <LightbulbIcon fontSize="small" color="action" />
        <Typography variant="caption" color="text.secondary">
          Quick responses:
        </Typography>
      </Stack>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        {questions.map((question, idx) => (
          <Chip
            key={idx}
            label={question}
            size="small"
            variant="outlined"
            onClick={() => onQuestionClick(question)}
            sx={{
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          />
        ))}
      </Stack>
    </Box>
  )
}

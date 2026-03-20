import {
  Box,
  Stack,
  Typography,
  Paper,
  Chip,
  Avatar,
  Button,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import CheckIcon from '@mui/icons-material/Check'

const KIND_ICONS = {
  pdf: PictureAsPdfIcon,
  excel: TableChartIcon,
}

export default function RecommendationCard({ rec, onSelect }) {
  const template = rec.template || rec
  const kind = template.kind || 'pdf'
  const Icon = KIND_ICONS[kind] || PictureAsPdfIcon
  const score = typeof rec.score === 'number' ? rec.score : null

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        cursor: 'pointer',
        transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
        '&:hover': {
          borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
          bgcolor: 'action.hover',
        },
      }}
      onClick={() => onSelect(template)}
    >
      <Stack
        direction="row"
        alignItems="flex-start"
        spacing={2}
      >
        <Avatar
          variant="rounded"
          sx={{
            width: 40,
            height: 40,
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
          }}
        >
          <Icon
            sx={{
              color: 'text.secondary',
            }}
          />
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Stack
            direction="row"
            alignItems="center"
            spacing={1}
            sx={{ mb: 0.5 }}
          >
            <Typography variant="subtitle2" fontWeight={600}>
              {template.name || template.id}
            </Typography>
            <Chip
              label={kind.toUpperCase()}
              size="small"
              variant="outlined"
              sx={{ height: 20, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
            />
            {score !== null && (
              <Chip
                label={`${Math.round(score * 100)}% match`}
                size="small"
                sx={{ height: 20, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            )}
          </Stack>
          {rec.explanation && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {rec.explanation}
            </Typography>
          )}
          {!rec.explanation && template.description && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {template.description}
            </Typography>
          )}
        </Box>
        <Button
          size="small"
          variant="outlined"
          startIcon={<CheckIcon />}
          onClick={(e) => {
            e.stopPropagation()
            onSelect(template)
          }}
          sx={{ textTransform: 'none', whiteSpace: 'nowrap' }}
        >
          Select
        </Button>
      </Stack>
    </Paper>
  )
}

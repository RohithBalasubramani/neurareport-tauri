/**
 * Collapsible saved queries panel
 */
import {
  Typography,
  Stack,
  Box,
  IconButton,
  Tooltip,
  Collapse,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import { neutral } from '@/app/theme'
import { GlassCard } from '@/styles'

const SavedQueryItem = styled(Stack)(({ theme }) => ({
  padding: theme.spacing(1),
  borderRadius: 10,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    transform: 'translateX(4px)',
  },
}))

export default function SavedQueriesPanel({
  open,
  savedQueries,
  onLoadQuery,
  onDeleteClick,
}) {
  const theme = useTheme()

  return (
    <Collapse in={open}>
      <GlassCard>
        <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
          Saved Queries
        </Typography>
        {savedQueries.length === 0 ? (
          <Typography variant="body2" sx={{ color: theme.palette.text.disabled }}>
            No saved queries yet
          </Typography>
        ) : (
          <Stack spacing={1}>
            {savedQueries.slice(0, 5).map((q) => (
              <SavedQueryItem
                key={q.id}
                direction="row"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box sx={{ flex: 1 }} onClick={() => onLoadQuery(q)}>
                  <Typography variant="body2" fontWeight={500} sx={{ color: theme.palette.text.primary }}>
                    {q.name}
                  </Typography>
                  {q.description && (
                    <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
                      {q.description}
                    </Typography>
                  )}
                </Box>
                <Tooltip title="Delete saved query">
                  <IconButton
                    size="small"
                    onClick={() => onDeleteClick(q)}
                    aria-label="Delete saved query"
                  >
                    <DeleteIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
                  </IconButton>
                </Tooltip>
              </SavedQueryItem>
            ))}
          </Stack>
        )}
      </GlassCard>
    </Collapse>
  )
}

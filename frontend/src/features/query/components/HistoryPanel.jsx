/**
 * Collapsible query history panel
 */
import {
  Typography,
  Stack,
  Box,
  Chip,
  IconButton,
  Collapse,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import { neutral } from '@/app/theme'
import { GlassCard } from '@/styles'

const HistoryItem = styled(Stack)(({ theme }) => ({
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

const ConfidenceChip = styled(Chip)(({ theme }) => ({
  height: 20,
  fontSize: '12px',
  fontWeight: 600,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  color: theme.palette.text.secondary,
  borderRadius: 6,
}))

export default function HistoryPanel({
  open,
  queryHistory,
  onSelectHistory,
  onDeleteClick,
}) {
  const theme = useTheme()

  return (
    <Collapse in={open}>
      <GlassCard>
        <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
          Recent Queries
        </Typography>
        {queryHistory.length === 0 ? (
          <Typography variant="body2" sx={{ color: theme.palette.text.disabled }}>
            No query history yet
          </Typography>
        ) : (
          <Stack spacing={1}>
            {queryHistory.slice(0, 5).map((h) => (
              <HistoryItem
                key={h.id}
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                onClick={() => onSelectHistory(h)}
              >
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body2" sx={{ color: theme.palette.text.primary }} noWrap>
                    {h.question}
                  </Typography>
                  <Stack direction="row" spacing={1} mt={0.5}>
                    <ConfidenceChip
                      size="small"
                      label={`${Math.round(h.confidence * 100)}%`}
                    />
                    {h.success ? (
                      <Chip
                        size="small"
                        label="Success"
                        sx={{
                          height: 20,
                          fontSize: '12px',
                          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                          color: theme.palette.text.secondary,
                          borderRadius: 1.5,
                        }}
                      />
                    ) : (
                      <Chip
                        size="small"
                        label="Failed"
                        sx={{
                          height: 20,
                          fontSize: '12px',
                          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                          color: theme.palette.text.secondary,
                          borderRadius: 1.5,
                        }}
                      />
                    )}
                  </Stack>
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDeleteClick(h)
                  }}
                >
                  <DeleteIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
                </IconButton>
              </HistoryItem>
            ))}
          </Stack>
        )}
      </GlassCard>
    </Collapse>
  )
}

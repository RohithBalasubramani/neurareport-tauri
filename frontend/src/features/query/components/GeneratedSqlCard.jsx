/**
 * Generated SQL display card with execute controls
 */
import {
  Typography,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  FormControlLabel,
  Switch,
  useTheme,
  alpha,
  styled,
  Box,
} from '@mui/material'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import SaveIcon from '@mui/icons-material/Save'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import { neutral } from '@/app/theme'
import { GlassCard } from '@/styles'
import DisabledTooltip from '@/components/ux/DisabledTooltip'
import { ExecuteButton, StyledTextField } from './styledComponents'

const ExplanationBox = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderRadius: 12,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

const ConfidenceChip = styled(Chip)(({ theme }) => ({
  height: 20,
  fontSize: '12px',
  fontWeight: 600,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  color: theme.palette.text.secondary,
  borderRadius: 6,
}))

export default function GeneratedSqlCard({
  generatedSQL, confidence, explanation, warnings, includeTotal,
  isExecuting, writeOperation, executeDisabledReason, selectedConnectionId,
  onSqlChange, onCopySQL, onOpenSaveDialog, onExecute, onSetIncludeTotal,
}) {
  const theme = useTheme()
  if (!generatedSQL) return null

  return (
    <GlassCard>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary }}>Generated SQL</Typography>
          {confidence > 0 && <ConfidenceChip size="small" label={`${Math.round(confidence * 100)}% confidence`} />}
        </Stack>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Copy SQL">
            <IconButton size="small" onClick={onCopySQL} aria-label="Copy SQL">
              <ContentCopyIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Save Query">
            <IconButton size="small" onClick={onOpenSaveDialog} aria-label="Save Query">
              <SaveIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      <StyledTextField
        fullWidth multiline minRows={3} maxRows={10} value={generatedSQL}
        onChange={(e) => onSqlChange(e.target.value)}
        sx={{ '& .MuiOutlinedInput-root': { fontFamily: 'monospace', fontSize: '0.875rem' } }}
      />

      {warnings.length > 0 && (
        <Stack spacing={0.5} mt={1}>
          {warnings.map((w, i) => (
            <Alert key={i} severity="warning" sx={{ py: 0, borderRadius: 1 }}>{w}</Alert>
          ))}
        </Stack>
      )}

      {explanation && (
        <ExplanationBox>
          <Stack direction="row" alignItems="flex-start" spacing={1}>
            <LightbulbIcon sx={{ color: theme.palette.text.secondary, fontSize: 18, mt: 0.25 }} />
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>{explanation}</Typography>
          </Stack>
        </ExplanationBox>
      )}

      <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ xs: 'stretch', sm: 'center' }}
        justifyContent="space-between" mt={2} spacing={1.5}>
        <FormControlLabel
          control={<Switch size="small" checked={includeTotal} onChange={(event) => onSetIncludeTotal(event.target.checked)} />}
          label="Include total row count (slower)" sx={{ color: theme.palette.text.secondary }}
        />
        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
          <Chip size="small" label="Read-only recommended" variant="outlined" sx={{ fontSize: '12px' }} />
          {writeOperation && (
            <Chip size="small" label={`${writeOperation.toUpperCase()} detected`}
              sx={{ fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
          )}
        </Stack>
        <DisabledTooltip
          disabled={Boolean(executeDisabledReason) || isExecuting}
          reason={isExecuting ? 'Query is currently running...' : executeDisabledReason}
          hint={!selectedConnectionId ? 'Select a database from the dropdown above'
            : !generatedSQL.trim() ? 'Enter a question and click Generate first' : undefined}
        >
          <ExecuteButton
            startIcon={isExecuting ? <CircularProgress size={16} color="inherit" /> : <PlayArrowIcon />}
            onClick={onExecute} disabled={Boolean(executeDisabledReason) || isExecuting}
          >
            {isExecuting ? 'Executing...' : 'Execute Query'}
          </ExecuteButton>
        </DisabledTooltip>
      </Stack>
      {writeOperation && (
        <Alert severity="warning" sx={{ mt: 1.5, borderRadius: 1 }}>
          Write queries can modify data and may not be reversible. You will be asked to confirm before execution.
        </Alert>
      )}
    </GlassCard>
  )
}

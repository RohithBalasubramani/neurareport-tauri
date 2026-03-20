/**
 * Irreversible Action Confirmation Dialog
 *
 * Shows confirmation UI with severity indicators, type confirmation,
 * checkbox confirmation, and cooldown timers.
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  Checkbox,
  FormControlLabel,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Warning as WarningIcon,
  Error as DangerIcon,
  DeleteForever as DeleteIcon,
} from '@mui/icons-material'
import { ActionSeverity, shake, getSeverityConfig } from './irreversibleConstants'

const severityIcons = {
  [ActionSeverity.LOW]: WarningIcon,
  [ActionSeverity.MEDIUM]: WarningIcon,
  [ActionSeverity.HIGH]: DangerIcon,
  [ActionSeverity.CRITICAL]: DeleteIcon,
}

export default function IrreversibleConfirmDialog({
  open,
  action,
  itemName,
  typeConfirmation,
  onTypeConfirmationChange,
  checkboxConfirmed,
  onCheckboxChange,
  cooldownRemaining,
  isConfirmationValid,
  onConfirm,
  onCancel,
}) {
  const theme = useTheme()

  if (!action) return null

  const severityConfig = getSeverityConfig(action.severity, theme)
  const SeverityIcon = severityIcons[action.severity] || WarningIcon

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: alpha(theme.palette.background.paper, 0.98),
          borderRadius: 1,  // Figma spec: 8px
          border: `2px solid ${severityConfig.color}`,
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          bgcolor: alpha(severityConfig.color, 0.1),
          borderBottom: `1px solid ${alpha(severityConfig.color, 0.2)}`,
        }}
      >
        <SeverityIcon sx={{ color: severityConfig.color, fontSize: 28 }} />
        <Box>
          <Typography variant="h6" fontWeight={600}>
            {action.label}
          </Typography>
          <Typography variant="caption" sx={{ color: severityConfig.color, fontWeight: 600 }}>
            {severityConfig.label}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        {itemName && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            You are about to {action.label.toLowerCase()} <strong>"{itemName}"</strong>
          </Alert>
        )}

        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
          This action will:
        </Typography>
        <Box component="ul" sx={{ mt: 1, pl: 2 }}>
          {action.consequences.map((consequence, idx) => (
            <Typography component="li" variant="body2" key={idx} sx={{ mb: 0.5 }}>
              {consequence}
            </Typography>
          ))}
        </Box>

        {/* Type confirmation for critical actions */}
        {action.requiresTypeConfirmation && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Type <strong>{action.confirmationPhrase}</strong> to confirm:
            </Typography>
            <TextField
              fullWidth
              value={typeConfirmation}
              onChange={(e) => onTypeConfirmationChange(e.target.value)}
              placeholder={action.confirmationPhrase}
              error={typeConfirmation.length > 0 && typeConfirmation !== action.confirmationPhrase}
              sx={{
                '& .MuiOutlinedInput-root': {
                  animation: typeConfirmation.length > 0 && typeConfirmation !== action.confirmationPhrase
                    ? `${shake} 0.4s ease-in-out`
                    : 'none',
                },
              }}
            />
          </Box>
        )}

        {/* Checkbox for high/critical severity */}
        {[ActionSeverity.HIGH, ActionSeverity.CRITICAL].includes(action.severity) && (
          <FormControlLabel
            control={
              <Checkbox
                checked={checkboxConfirmed}
                onChange={(e) => onCheckboxChange(e.target.checked)}
                sx={{ color: severityConfig.color }}
              />
            }
            label={
              <Typography variant="body2">
                I understand this action is <strong>permanent</strong> and cannot be undone
              </Typography>
            }
            sx={{ mt: 2 }}
          />
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
        <Button onClick={onCancel} variant="outlined">
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          disabled={!isConfirmationValid}
          sx={{ minWidth: 120, color: 'text.secondary' }}
        >
          {cooldownRemaining > 0 ? (
            `Wait ${cooldownRemaining}s`
          ) : (
            action.label
          )}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

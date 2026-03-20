/**
 * Drawer Footer Actions
 * Confirm/Cancel buttons for drawer panels
 */
import {
  Box,
  Button,
  Stack,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'

export default function DrawerFooter({
  actions,
  loading = false,
  confirmLabel = 'Save',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  confirmDisabled = false,
}) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        px: 3,
        py: 2.5,
        borderTop: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
        bgcolor: theme.palette.background.paper,
      }}
    >
      {actions || (
        <Stack direction="row" spacing={1.5} justifyContent="flex-end">
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={loading}
            sx={{
              borderRadius: 1,  // 8px via theme spacing
              textTransform: 'none',
              fontWeight: 500,
              color: theme.palette.text.secondary,
              borderColor: alpha(theme.palette.divider, 0.2),
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: alpha(theme.palette.text.primary, 0.3),
                bgcolor: alpha(theme.palette.text.primary, 0.05),
              },
            }}
          >
            {cancelLabel}
          </Button>
          <Button
            variant="contained"
            onClick={onConfirm}
            disabled={confirmDisabled || loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
            sx={{
              borderRadius: 1,  // 8px via theme spacing
              textTransform: 'none',
              fontWeight: 600,
              bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
                transform: 'translateY(-1px)',
              },
              '&:active': {
                transform: 'translateY(0)',
              },
            }}
          >
            {confirmLabel}
          </Button>
        </Stack>
      )}
    </Box>
  )
}

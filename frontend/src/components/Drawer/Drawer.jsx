/**
 * Premium Drawer Component
 * Slide-out panel with theme-based styling
 */
import {
  Drawer as MuiDrawer,
  Box,
  Typography,
  IconButton,
  Button,
  Stack,
  CircularProgress,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// ANIMATIONS
// =============================================================================

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`

export default function Drawer({
  open,
  onClose,
  title,
  subtitle,
  children,
  anchor = 'right',
  width = 480,
  actions,
  loading = false,
  confirmLabel = 'Save',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  confirmDisabled = false,
}) {
  const theme = useTheme()

  const handleCancel = () => {
    onCancel?.()
    onClose()
  }

  return (
    <MuiDrawer
      anchor={anchor}
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100%', sm: width },
          maxWidth: '100%',
          bgcolor: alpha(theme.palette.background.paper, 0.98),
          backdropFilter: 'blur(20px)',
          borderLeft: `1px solid ${alpha(theme.palette.divider, 0.25)}`,
          boxShadow: `0 0 64px ${alpha(theme.palette.common.black, 0.25)}`,
        },
      }}
      slotProps={{
        backdrop: {
          sx: {
            bgcolor: alpha(theme.palette.common.black, 0.5),
            backdropFilter: 'blur(4px)',
          },
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          animation: `${fadeIn} 0.3s ease-out`,
        }}
      >
        {/* Header */}
        <Box
          sx={{
            px: 3,
            py: 2.5,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
          }}
        >
          <Box>
            <Typography
              sx={{
                fontSize: '1.125rem',
                fontWeight: 600,
                color: theme.palette.text.primary,
                letterSpacing: '-0.01em',
              }}
            >
              {title}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '14px',
                  color: theme.palette.text.secondary,
                  mt: 0.5,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          <IconButton
            onClick={onClose}
            size="small"
            sx={{
              color: theme.palette.text.secondary,
              borderRadius: 1,  // 8px via theme spacing
              transition: 'all 0.2s ease',
              '&:hover': {
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                color: theme.palette.text.primary,
                transform: 'rotate(90deg)',
              },
            }}
          >
            <CloseIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Box>

        {/* Content */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 3,
            bgcolor: alpha(theme.palette.background.default, 0.5),
          }}
        >
          {children}
        </Box>

        {/* Footer Actions */}
        {(actions || onConfirm) && (
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
                  onClick={handleCancel}
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
        )}
      </Box>
    </MuiDrawer>
  )
}

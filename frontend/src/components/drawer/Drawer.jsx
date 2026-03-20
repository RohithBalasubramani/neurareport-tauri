/**
 * Premium Drawer Component
 * Slide-out panel with theme-based styling
 */
import {
  Drawer as MuiDrawer,
  Box,
  Typography,
  IconButton,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { neutral } from '@/app/theme'
import DrawerFooter from './DrawerFooter'

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
          <DrawerFooter
            actions={actions}
            loading={loading}
            confirmLabel={confirmLabel}
            cancelLabel={cancelLabel}
            onConfirm={onConfirm}
            onCancel={handleCancel}
            confirmDisabled={confirmDisabled}
          />
        )}
      </Box>
    </MuiDrawer>
  )
}

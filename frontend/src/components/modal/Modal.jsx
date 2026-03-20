/**
 * Premium Modal Component
 * Sophisticated dialog with glassmorphism and smooth animations
 */
import {
  Box,
  Fade,
  useTheme,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import {
  StyledDialog,
  DialogPaper,
  StyledDialogTitle,
  TitleText,
  SubtitleText,
  CloseButton,
  StyledDialogContent,
  StyledDivider,
  StyledDialogActions,
  CancelButton,
  ConfirmButton,
  LoadingSpinner,
} from './ModalStyles'

export default function Modal({
  open,
  onClose,
  title,
  subtitle,
  children,
  actions,
  maxWidth = 'sm',
  fullWidth = true,
  loading = false,
  hideCloseButton = false,
  dividers = true,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  confirmDisabled = false,
  confirmColor = 'primary',
  confirmVariant = 'contained',
}) {
  const handleCancel = () => {
    onCancel?.()
    onClose()
  }

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      TransitionComponent={Fade}
      TransitionProps={{ timeout: 200 }}
      PaperComponent={DialogPaper}
    >
      <StyledDialogTitle>
        <Box>
          <TitleText>{title}</TitleText>
          {subtitle && <SubtitleText>{subtitle}</SubtitleText>}
        </Box>
        {!hideCloseButton && (
          <CloseButton onClick={onClose} size="small" aria-label="Close dialog">
            <CloseIcon sx={{ fontSize: 18 }} />
          </CloseButton>
        )}
      </StyledDialogTitle>

      {dividers && <StyledDivider />}

      <StyledDialogContent>{children}</StyledDialogContent>

      {(actions || onConfirm) && (
        <StyledDialogActions>
          {actions || (
            <>
              <CancelButton variant="outlined" onClick={handleCancel} disabled={loading}>
                {cancelLabel}
              </CancelButton>
              <ConfirmButton
                variant={confirmVariant}
                className={confirmColor}
                onClick={onConfirm}
                disabled={confirmDisabled || loading}
                startIcon={loading ? <LoadingSpinner size={16} /> : null}
              >
                {confirmLabel}
              </ConfirmButton>
            </>
          )}
        </StyledDialogActions>
      )}
    </StyledDialog>
  )
}

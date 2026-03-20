/**
 * Premium Confirm Modal
 * Beautiful confirmation dialog with animations and severity states
 */
import { useEffect, useRef } from 'react'
import {
  Stack,
  useTheme,
} from '@mui/material'
import Modal from './Modal'
import {
  IconContainer,
  MessageText,
  getSeverityConfig,
  getDeletePreference,
} from './ConfirmModalStyles'

export default function ConfirmModal({
  open,
  onClose,
  onConfirm,
  title = 'Confirm',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  severity = 'warning',
  loading = false,
}) {
  const theme = useTheme()
  const config = getSeverityConfig(theme, severity)
  const Icon = config.icon
  const confirmColor = severity === 'error' ? 'error' : 'primary'
  const autoConfirmRef = useRef(false)
  const isDeleteAction = `${title} ${confirmLabel}`.toLowerCase().includes('delete')

  useEffect(() => {
    if (!open) {
      autoConfirmRef.current = false
      return
    }
    if (!isDeleteAction || autoConfirmRef.current) return
    const prefs = getDeletePreference()
    if (prefs.confirmDelete === false) {
      autoConfirmRef.current = true
      onConfirm?.()
      onClose?.()
    }
  }, [open, isDeleteAction, onConfirm, onClose])

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      maxWidth="xs"
      onConfirm={onConfirm}
      confirmLabel={confirmLabel}
      cancelLabel={cancelLabel}
      confirmColor={confirmColor}
      loading={loading}
      dividers={false}
    >
      <Stack spacing={3} alignItems="center" textAlign="center" sx={{ py: 2 }}>
        <IconContainer severity={severity} bgColor={config.bgColor}>
          <Icon sx={{ fontSize: 32, color: config.color, position: 'relative', zIndex: 1 }} />
        </IconContainer>
        <MessageText>{message}</MessageText>
      </Stack>
    </Modal>
  )
}

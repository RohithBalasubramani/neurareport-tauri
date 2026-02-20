import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material'

export default function ConfirmDialog({ open, title = 'Confirm', message, confirmText = 'Confirm', cancelText = 'Cancel', onClose, onConfirm }) {
  return (
    <Dialog open={open} onClose={() => onClose?.()}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary">{message}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose?.()}>{cancelText}</Button>
        <Button variant="contained" onClick={() => { onConfirm?.(); onClose?.() }}>
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  )
}


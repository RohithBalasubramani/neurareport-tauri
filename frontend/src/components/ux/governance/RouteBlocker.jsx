/**
 * Route Blocker Component
 *
 * Uses react-router-dom's useBlocker to prevent route changes
 * when navigation is unsafe.
 */
import { useCallback, useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Box,
  Typography,
} from '@mui/material'
import { useBlocker } from 'react-router-dom'
import { useNavigationSafety } from './NavigationSafety'

export default function RouteBlocker() {
  const { isNavigationSafe, getActiveBlockers } = useNavigationSafety()
  const [dialogOpen, setDialogOpen] = useState(false)

  // Use react-router's useBlocker to prevent route changes
  const blocker = useBlocker(
    useCallback(() => !isNavigationSafe(), [isNavigationSafe])
  )

  useEffect(() => {
    if (blocker.state === 'blocked') {
      setDialogOpen(true)
    } else {
      setDialogOpen(false)
    }
  }, [blocker.state])

  const handleProceed = useCallback(() => {
    blocker.proceed?.()
  }, [blocker])

  const handleCancel = useCallback(() => {
    blocker.reset?.()
  }, [blocker])

  const activeBlockers = getActiveBlockers()

  return (
    <Dialog open={dialogOpen} onClose={handleCancel}>
      <DialogTitle>Unsaved Changes</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Leaving this page may discard unsaved changes or interrupt active operations.
        </DialogContentText>
        {activeBlockers.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Active blockers: {activeBlockers.map((b) => b.reason).join(', ')}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel} variant="contained">Stay on this page</Button>
        <Button onClick={handleProceed}>Leave anyway</Button>
      </DialogActions>
    </Dialog>
  )
}

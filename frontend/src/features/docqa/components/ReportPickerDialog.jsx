/**
 * Select Existing Report dialog.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
} from '@mui/material'
import { Article as ArticleIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { ContentSkeleton } from '@/components/feedback/LoadingState'
import { GlassDialog } from './DocQAStyledComponents'

export default function ReportPickerDialog({
  open,
  onClose,
  runsLoading,
  availableRuns,
  handleSelectReport,
}) {
  const theme = useTheme()

  return (
    <GlassDialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Select Existing Report</Typography>
        <Typography variant="body2" color="text.secondary">
          Choose a generated report to add to this session
        </Typography>
      </DialogTitle>
      <DialogContent>
        {runsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <ContentSkeleton rows={3} />
          </Box>
        ) : availableRuns.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <ArticleIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary">No generated reports found</Typography>
            <Typography variant="caption" color="text.secondary">
              Generate a report first, then come back to analyze it here.
            </Typography>
          </Box>
        ) : (
          <List sx={{ pt: 1 }}>
            {availableRuns.map((run) => (
              <ListItem
                key={run.id} button onClick={() => handleSelectReport(run)}
                sx={{
                  borderRadius: 1, mb: 0.5,
                  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark'
                      ? alpha(theme.palette.text.primary, 0.06) : neutral[50],
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <ArticleIcon sx={{ color: 'text.secondary' }} />
                </ListItemIcon>
                <ListItemText
                  primary={run.templateName || run.id}
                  secondary={`${run.startDate} – ${run.endDate} · ${run.connectionName || 'Unknown source'}`}
                  primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap', ml: 1 }}>
                  {new Date(run.createdAt).toLocaleDateString()}
                </Typography>
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} sx={{ borderRadius: 1, textTransform: 'none' }}>Cancel</Button>
      </DialogActions>
    </GlassDialog>
  )
}

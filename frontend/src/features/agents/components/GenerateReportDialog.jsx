/**
 * Generate Report from Agent Dialog
 */
import { useState, useEffect } from 'react'
import {
  Button,
  TextField,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
} from '@mui/material'
import { Description as ReportIcon } from '@mui/icons-material'

export default function GenerateReportDialog({ open, onClose, taskId, templates, connections, onGenerate }) {
  const [templateId, setTemplateId] = useState('')
  const [connectionId, setConnectionId] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (open) {
      setTemplateId(templates?.[0]?.id || '')
      setConnectionId(connections?.[0]?.id || '')
      const today = new Date().toISOString().split('T')[0]
      const monthAgo = new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]
      setStartDate(monthAgo)
      setEndDate(today)
    }
  }, [open, templates, connections])

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      await onGenerate(taskId, {
        templateId,
        connectionId,
        startDate,
        endDate,
      })
      onClose()
    } catch (err) {
      // Error handled in parent
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 600 }}>Generate Report from Agent Result</DialogTitle>
      <DialogContent>
        <Stack spacing={2.5} sx={{ mt: 1 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Template</InputLabel>
            <Select value={templateId} onChange={(e) => setTemplateId(e.target.value)} label="Template">
              {(templates || []).map((t) => (
                <MenuItem key={t.id} value={t.id}>{t.name || t.id}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth size="small">
            <InputLabel>Connection</InputLabel>
            <Select value={connectionId} onChange={(e) => setConnectionId(e.target.value)} label="Connection">
              {(connections || []).map((c) => (
                <MenuItem key={c.id} value={c.id}>{c.name || c.id}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Stack direction="row" spacing={2}>
            <TextField
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
              size="small"
            />
            <TextField
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
              size="small"
            />
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!templateId || !connectionId || submitting}
          startIcon={submitting ? <CircularProgress size={16} /> : <ReportIcon />}
        >
          {submitting ? 'Generating...' : 'Generate Report'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

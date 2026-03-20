/**
 * Schedule create/edit dialog component.
 */
import { useState, useEffect } from 'react'
import {
  Box, Typography, Stack, InputLabel, Select, MenuItem,
  FormControlLabel, useTheme,
} from '@mui/material'
import {
  Schedule as ScheduleIcon,
  CalendarMonth as CalendarIcon,
  Email as EmailIcon,
} from '@mui/icons-material'
import { StyledFormControl } from '@/styles'
import {
  StyledDialog, DialogHeader, DialogIconContainer,
  StyledDialogContent, StyledDialogActions,
  SectionLabel, StyledTextField, StyledSwitch,
  ActionButton, PrimaryButton,
  FREQUENCY_OPTIONS, FREQUENCY_INTERVALS,
  extractDateOnly, buildDateTime, parseEmailList,
  formatEmailList, isValidEmail,
} from './ScheduleStyles'

export default function ScheduleDialog({
  open, onClose, schedule, templates, connections,
  defaultTemplateId, defaultConnectionId, onSave, onError,
}) {
  const theme = useTheme()
  const [form, setForm] = useState({
    name: '', templateId: '', connectionId: '',
    startDate: '', endDate: '', frequency: 'daily',
    runTime: '', emailRecipients: '', emailSubject: '',
    emailMessage: '', active: true,
  })
  const [saving, setSaving] = useState(false)
  const editing = Boolean(schedule)

  useEffect(() => {
    if (schedule) {
      setForm({
        name: schedule.name || '',
        templateId: schedule.template_id || '',
        connectionId: schedule.connection_id || '',
        startDate: extractDateOnly(schedule.start_date),
        endDate: extractDateOnly(schedule.end_date),
        frequency: schedule.frequency || 'daily',
        runTime: schedule.run_time || '',
        emailRecipients: formatEmailList(schedule.email_recipients),
        emailSubject: schedule.email_subject || '',
        emailMessage: schedule.email_message || '',
        active: schedule.active !== false,
      })
      return
    }
    const fallbackTemplate = defaultTemplateId || templates[0]?.id || ''
    const fallbackConnection = defaultConnectionId || connections[0]?.id || ''
    setForm({
      name: '', templateId: fallbackTemplate, connectionId: fallbackConnection,
      startDate: '', endDate: '', frequency: 'daily',
      runTime: '', emailRecipients: '', emailSubject: '',
      emailMessage: '', active: true,
    })
  }, [schedule, templates, connections, open, defaultTemplateId, defaultConnectionId])

  const handleChange = (field) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    const intervalMinutes = FREQUENCY_INTERVALS[form.frequency] || FREQUENCY_INTERVALS.daily
    const emailRecipients = parseEmailList(form.emailRecipients)
    const startDate = buildDateTime(form.startDate)
    const endDate = buildDateTime(form.endDate, true)
    const templateAllowed = templates.some((tpl) => tpl.id === form.templateId)
    const connectionAvailable = connections.some((conn) => conn.id === form.connectionId)

    if (form.startDate && form.endDate && form.endDate < form.startDate) {
      onError?.('End date must be on or after start date'); return
    }
    if (!templateAllowed) {
      onError?.('Selected template is not approved for scheduling. Choose an approved template.'); return
    }
    if (!connectionAvailable) {
      onError?.('Selected connection is no longer available. Choose another connection.'); return
    }
    if (emailRecipients.length > 0) {
      const invalidEmail = emailRecipients.find((email) => !isValidEmail(email))
      if (invalidEmail) { onError?.(`Invalid email address: ${invalidEmail}`); return }
    }

    setSaving(true)
    try {
      await onSave({
        name: form.name, templateId: form.templateId,
        connectionId: form.connectionId, startDate, endDate,
        frequency: form.frequency, intervalMinutes,
        runTime: form.runTime || undefined,
        emailRecipients: emailRecipients.length ? emailRecipients : undefined,
        emailSubject: form.emailSubject || undefined,
        emailMessage: form.emailMessage || undefined,
        active: form.active,
      })
      onClose()
    } catch {
      // Keep dialog open on save failure
    } finally { setSaving(false) }
  }

  const disableSave =
    saving || !form.name || !form.templateId || !form.connectionId || !form.startDate || !form.endDate

  return (
    <StyledDialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogHeader>
        <DialogIconContainer><ScheduleIcon /></DialogIconContainer>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {editing ? 'Edit Schedule' : 'Create Schedule'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {editing ? 'Update the schedule configuration' : 'Set up automated report generation'}
          </Typography>
        </Box>
      </DialogHeader>

      <StyledDialogContent>
        <SectionLabel><ScheduleIcon sx={{ fontSize: 16 }} />Basic Information</SectionLabel>
        <Stack spacing={2.5}>
          <StyledTextField label="Schedule Name" value={form.name} onChange={handleChange('name')} fullWidth required placeholder="e.g., Weekly Sales Report" />
          <StyledFormControl fullWidth required>
            <InputLabel>Template</InputLabel>
            <Select value={form.templateId} onChange={handleChange('templateId')} label="Template" disabled={editing}>
              {templates.map((t) => (<MenuItem key={t.id} value={t.id}>{t.name || t.id}</MenuItem>))}
            </Select>
          </StyledFormControl>
          <StyledFormControl fullWidth required>
            <InputLabel>Connection</InputLabel>
            <Select value={form.connectionId} onChange={handleChange('connectionId')} label="Connection" disabled={editing}>
              {connections.map((conn) => (<MenuItem key={conn.id} value={conn.id}>{conn.name || conn.id}</MenuItem>))}
            </Select>
          </StyledFormControl>
        </Stack>

        <SectionLabel><CalendarIcon sx={{ fontSize: 16 }} />Schedule Timing</SectionLabel>
        <Stack spacing={2.5}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <StyledTextField label="Start Date" type="date" value={form.startDate} onChange={handleChange('startDate')} InputLabelProps={{ shrink: true }} fullWidth required />
            <StyledTextField label="End Date" type="date" value={form.endDate} onChange={handleChange('endDate')} InputLabelProps={{ shrink: true }} fullWidth required />
          </Stack>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <StyledFormControl fullWidth>
              <InputLabel>Frequency</InputLabel>
              <Select value={form.frequency} onChange={handleChange('frequency')} label="Frequency">
                {FREQUENCY_OPTIONS.map((opt) => (<MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>))}
              </Select>
            </StyledFormControl>
            <StyledTextField label="Run At" type="time" value={form.runTime} onChange={handleChange('runTime')} InputLabelProps={{ shrink: true }} fullWidth helperText="Time of day in your local time (leave blank for interval-based)" />
          </Stack>
        </Stack>

        <SectionLabel><EmailIcon sx={{ fontSize: 16 }} />Email Notifications (Optional)</SectionLabel>
        <Stack spacing={2.5}>
          <StyledTextField label="Email recipients" value={form.emailRecipients} onChange={handleChange('emailRecipients')} placeholder="ops@example.com, finance@example.com" helperText="Comma or semicolon separated list" fullWidth />
          <StyledTextField label="Email subject" value={form.emailSubject} onChange={handleChange('emailSubject')} fullWidth />
          <StyledTextField label="Email message" value={form.emailMessage} onChange={handleChange('emailMessage')} multiline minRows={2} fullWidth />
        </Stack>

        <Box sx={{ mt: 3 }}>
          <FormControlLabel
            control={<StyledSwitch checked={form.active} onChange={handleChange('active')} />}
            label={
              <Box>
                <Typography variant="body2" fontWeight={500}>Active</Typography>
                <Typography variant="caption" color="text.secondary">Enable this schedule to run automatically</Typography>
              </Box>
            }
          />
        </Box>
      </StyledDialogContent>

      <StyledDialogActions>
        <ActionButton onClick={onClose}>Cancel</ActionButton>
        <PrimaryButton onClick={handleSubmit} disabled={disableSave}>
          {saving ? 'Saving...' : editing ? 'Update Schedule' : 'Create Schedule'}
        </PrimaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}

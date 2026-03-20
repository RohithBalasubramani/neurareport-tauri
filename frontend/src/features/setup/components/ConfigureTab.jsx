import { useState } from 'react'
import {
  Box, Typography, Stack, Button, TextField, Chip, Collapse,
  IconButton, Tooltip, Alert, alpha,
} from '@mui/material'
import ScheduleIcon from '@mui/icons-material/Schedule'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import { neutral } from '@/app/theme'
import GenerateAndDownload from '@/features/generate/components/GenerateAndDownload.jsx'

function CollapsibleSection({ title, icon, badge, defaultExpanded = false, children }) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  return (
    <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, overflow: 'hidden' }}>
      <Box
        onClick={() => setExpanded(!expanded)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 1.5,
          cursor: 'pointer',
          bgcolor: expanded ? 'action.hover' : 'background.paper',
          '&:hover': { bgcolor: 'action.hover' },
          transition: 'background-color 150ms cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      >
        <Stack direction="row" alignItems="center" spacing={1}>
          {icon}
          <Typography variant="subtitle2" fontWeight={600}>{title}</Typography>
          {badge && (
            <Chip size="small" label={badge} variant="outlined" sx={{ borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[200], color: 'text.secondary' }} />
          )}
        </Stack>
        <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
          <IconButton
            size="small"
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}
            aria-label={expanded ? 'Collapse section' : 'Expand section'}
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Tooltip>
      </Box>
      <Collapse in={expanded}>
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          {children}
        </Box>
      </Collapse>
    </Box>
  )
}

export default function ConfigureTab({
  selected,
  selectedTemplates,
  autoType,
  start,
  end,
  setStart,
  setEnd,
  onFind,
  finding,
  results,
  onToggleBatch,
  onGenerate,
  canGenerate,
  generateLabel,
  generation,
  keyValues,
  onKeyValueChange,
  keysReady,
  keyOptions,
  keyOptionsLoading,
  onResampleFilter,
  queuedJobs,
  queuedJobIds,
  handleNavigate,
  emailTargets,
  setEmailTargets,
  emailSubject,
  setEmailSubject,
  emailMessage,
  setEmailMessage,
}) {
  return (
    <Box sx={{ px: 2, pb: 2 }}>
      <Stack spacing={2}>
        <Alert severity="info" sx={{ borderRadius: 1 }}>
          Runs start as background jobs. Track progress in Jobs, and download outputs from History.
        </Alert>
        {queuedJobs.length > 0 && (
          <Alert
            severity="info"
            action={(
              <Button
                size="small"
                onClick={() => handleNavigate('/jobs', 'Open jobs')}
                sx={{ textTransform: 'none' }}
              >
                View Jobs
              </Button>
            )}
          >
            Reports queued in background.
            {queuedJobIds.length > 0 ? ` Job IDs: ${queuedJobIds.slice(0, 3).join(', ')}` : ' Track progress in Jobs.'}
          </Alert>
        )}
        <GenerateAndDownload
          selected={selected}
          selectedTemplates={selectedTemplates}
          autoType={autoType}
          start={start}
          end={end}
          setStart={setStart}
          setEnd={setEnd}
          onFind={onFind}
          findDisabled={finding}
          finding={finding}
          results={results}
          onToggleBatch={onToggleBatch}
          onGenerate={onGenerate}
          canGenerate={canGenerate}
          generateLabel={generateLabel}
          generation={generation}
          generatorReady
          generatorIssues={{ missing: [], needsFix: [], messages: [] }}
          keyValues={keyValues}
          onKeyValueChange={onKeyValueChange}
          keysReady={keysReady}
          keyOptions={keyOptions}
          keyOptionsLoading={keyOptionsLoading}
          onResampleFilter={onResampleFilter}
        />

        <CollapsibleSection
          title="Email Delivery"
          icon={<ScheduleIcon fontSize="small" color="action" />}
          badge={emailTargets ? 'Configured' : null}
        >
          <Stack spacing={2}>
            <TextField
              label="Email recipients"
              placeholder="ops@example.com, finance@example.com"
              value={emailTargets}
              onChange={(e) => setEmailTargets(e.target.value)}
              helperText="Comma or semicolon separated list"
              size="small"
              fullWidth
            />
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
              <TextField
                label="Email subject"
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
                size="small"
                fullWidth
              />
            </Stack>
            <TextField
              label="Email message (optional)"
              value={emailMessage}
              onChange={(e) => setEmailMessage(e.target.value)}
              multiline
              minRows={2}
              size="small"
            />
          </Stack>
        </CollapsibleSection>
      </Stack>
    </Box>
  )
}

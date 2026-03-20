import {
  Box,
  Stack,
  Typography,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  IconButton,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CodeIcon from '@mui/icons-material/Code'
import ChatIcon from '@mui/icons-material/Chat'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import { AutoSaveIndicator } from './DraftRecoveryBanner.jsx'

export default function EditorHeader({
  template,
  templateId,
  editMode,
  onEditModeChange,
  onShortcutsOpen,
  onBack,
  breadcrumbLabel,
  lastEditInfo,
  diffSummary,
  lastSaved,
  dirty,
}) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1.5} flexWrap="wrap">
      <Box sx={{ minWidth: 0, flex: 1 }}>
        <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
          <Typography variant="h5" fontWeight={600}>
            {template?.name || 'Design Editor'}
          </Typography>
          <AutoSaveIndicator lastSaved={lastSaved} dirty={dirty} />
        </Stack>
        <Typography variant="body2" color="text.secondary">
          {templateId ? `ID: ${templateId}` : 'No template selected'}
        </Typography>
        {lastEditInfo && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            Last edit: {lastEditInfo.chipLabel}
          </Typography>
        )}
        {diffSummary && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            Recent change: {diffSummary}
          </Typography>
        )}
      </Box>

      <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
        <ToggleButtonGroup
          value={editMode}
          exclusive
          onChange={onEditModeChange}
          size="small"
          aria-label="Edit mode"
        >
          <ToggleButton value="manual" aria-label="Manual edit mode">
            <Tooltip title="Code Editor - Edit HTML directly with AI assistance">
              <Stack direction="row" spacing={0.5} alignItems="center">
                <CodeIcon fontSize="small" />
                <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                  Code
                </Typography>
              </Stack>
            </Tooltip>
          </ToggleButton>
          <ToggleButton value="chat" aria-label="Chat edit mode">
            <Tooltip title="Chat Editor - Conversational AI editing">
              <Stack direction="row" spacing={0.5} alignItems="center">
                <ChatIcon fontSize="small" />
                <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                  Chat
                </Typography>
              </Stack>
            </Tooltip>
          </ToggleButton>
        </ToggleButtonGroup>

        <Tooltip title="Keyboard shortcuts">
          <IconButton size="small" onClick={onShortcutsOpen} aria-label="Keyboard shortcuts">
            <KeyboardIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Button
          variant="outlined"
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
          sx={{ textTransform: 'none', fontWeight: 600 }}
        >
          Back to {breadcrumbLabel}
        </Button>
      </Stack>
    </Stack>
  )
}

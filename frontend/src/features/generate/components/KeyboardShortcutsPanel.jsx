import { Box, Stack, Typography, Chip, alpha } from '@mui/material'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import { getShortcutDisplay, EDITOR_SHORTCUTS } from '../hooks/useEditorKeyboardShortcuts'
import { neutral, palette } from '@/app/theme'

function ShortcutKey({ children }) {
  return (
    <Box
      component="kbd"
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 0.75,
        py: 0.25,
        minWidth: 24,
        height: 22,
        borderRadius: 0.5,
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        boxShadow: (theme) => `0 1px 0 ${alpha(theme.palette.common.black, 0.1)}`,
        fontFamily: 'monospace',
        fontSize: '12px',
        fontWeight: 600,
        color: 'text.secondary',
      }}
    >
      {children}
    </Box>
  )
}

function ShortcutDisplay({ shortcutKey }) {
  const display = getShortcutDisplay(shortcutKey)
  const parts = display.split('+')

  return (
    <Stack direction="row" spacing={0.5} alignItems="center">
      {parts.map((part, idx) => (
        <ShortcutKey key={idx}>{part}</ShortcutKey>
      ))}
    </Stack>
  )
}

export default function KeyboardShortcutsPanel({ compact = false }) {
  if (compact) {
    return (
      <Stack
        direction="row"
        spacing={2}
        sx={{
          py: 1,
          px: 1.5,
          borderRadius: 1,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
          border: '1px solid',
          borderColor: (theme) => alpha(theme.palette.divider, 0.1),
        }}
      >
        <Stack direction="row" spacing={0.5} alignItems="center">
          <KeyboardIcon sx={{ fontSize: 14, color: 'text.disabled' }} />
          <Typography variant="caption" color="text.disabled">
            Shortcuts:
          </Typography>
        </Stack>
        {EDITOR_SHORTCUTS.slice(0, 3).map((shortcut) => (
          <Stack key={shortcut.key} direction="row" spacing={0.5} alignItems="center">
            <ShortcutDisplay shortcutKey={shortcut.key} />
            <Typography variant="caption" color="text.secondary">
              {shortcut.label}
            </Typography>
          </Stack>
        ))}
      </Stack>
    )
  }

  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 1.5,
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <KeyboardIcon fontSize="small" color="action" />
        <Typography variant="subtitle2">Keyboard Shortcuts</Typography>
      </Stack>

      <Stack spacing={1.5}>
        {EDITOR_SHORTCUTS.map((shortcut) => (
          <Stack
            key={shortcut.key}
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography variant="body2">{shortcut.label}</Typography>
              <Typography variant="caption" color="text.secondary">
                {shortcut.description}
              </Typography>
            </Box>
            <ShortcutDisplay shortcutKey={shortcut.key} />
          </Stack>
        ))}
      </Stack>
    </Box>
  )
}

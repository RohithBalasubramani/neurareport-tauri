import { Dialog, alpha } from '@mui/material'
import { neutral } from '@/app/theme'
import { useCommandPalette } from '../hooks/useCommandPalette'
import CommandSearchInput from './command-palette/CommandSearchInput.jsx'
import CommandList from './command-palette/CommandList.jsx'
import CommandFooter from './command-palette/CommandFooter.jsx'

export default function CommandPalette({ open, onClose }) {
  const palette = useCommandPalette({ open, onClose })

  return (
    <Dialog
      open={open}
      onClose={palette.handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: (theme) => ({
          borderRadius: 1,
          overflow: 'hidden',
          maxHeight: '70vh',
          background: theme.palette.mode === 'dark'
            ? 'rgba(30, 30, 30, 0.92)'
            : 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(12px)',
          border: '2px solid',
          borderColor: theme.palette.common.black,
        }),
      }}
      slotProps={{
        backdrop: {
          sx: {
            bgcolor: (theme) => alpha(theme.palette.background.default, 0.8),
            backdropFilter: 'blur(4px)',
          },
        },
      }}
    >
      <CommandSearchInput
        inputRef={palette.inputRef}
        query={palette.query}
        setQuery={palette.setQuery}
        onKeyDown={palette.handleKeyDown}
        isSearching={palette.isSearching}
      />
      <CommandList
        listRef={palette.listRef}
        groupedCommands={palette.groupedCommands}
        flatIndexMap={palette.flatIndexMap}
        selectedIndex={palette.selectedIndex}
        setSelectedIndex={palette.setSelectedIndex}
        filteredCommands={palette.filteredCommands}
        isSearching={palette.isSearching}
        query={palette.query}
        executeCommand={palette.executeCommand}
      />
      <CommandFooter />
    </Dialog>
  )
}

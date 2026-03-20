import {
  Box,
  Typography,
  Divider,
  CircularProgress,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip,
  alpha,
} from '@mui/material'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import { neutral } from '@/app/theme'
import { Kbd } from '@/ui'
import { ICON_MAP } from './commandRegistry'

export default function CommandList({
  listRef,
  groupedCommands,
  flatIndexMap,
  selectedIndex,
  setSelectedIndex,
  filteredCommands,
  isSearching,
  query,
  executeCommand,
}) {
  return (
    <Box ref={listRef} sx={{ overflow: 'auto', maxHeight: 400 }}>
      {Object.entries(groupedCommands).map(([groupName, commands], groupIdx) => (
        <Box key={groupName}>
          {groupIdx > 0 && <Divider />}
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ px: 2, py: 1, display: 'block', fontWeight: 600 }}
          >
            {groupName}
          </Typography>
          <List dense disablePadding sx={{ pb: 1 }}>
            {commands.map((cmd) => {
              const index = flatIndexMap.get(cmd.id) ?? 0
              const Icon = cmd.icon || ICON_MAP[cmd.iconKey] || DescriptionOutlinedIcon
              const isSelected = index === selectedIndex

              return (
                <ListItem key={cmd.id} disablePadding data-index={index}>
                  <ListItemButton
                    selected={isSelected}
                    onClick={() => executeCommand(cmd)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    sx={{
                      mx: 1,
                      borderRadius: 1,
                      '&.Mui-selected': {
                        bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        color: 'primary.contrastText',
                        '&:hover': {
                          bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        },
                        '& .MuiListItemIcon-root': {
                          color: 'inherit',
                        },
                        '& .MuiTypography-root': {
                          color: 'inherit',
                        },
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Icon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={cmd.label}
                      secondary={cmd.description}
                      primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: 500 }}
                      secondaryTypographyProps={{
                        fontSize: '0.75rem',
                        sx: { opacity: isSelected ? 0.8 : 0.6 },
                      }}
                    />
                    {cmd.type && (
                      <Chip
                        label={cmd.type}
                        size="small"
                        sx={{
                          ml: 1,
                          height: 20,
                          fontSize: '10px',
                          textTransform: 'capitalize',
                          bgcolor: isSelected ? (theme) => alpha(theme.palette.common.white, 0.2) : 'action.selected',
                        }}
                      />
                    )}
                    {cmd.shortcut && (
                      <Kbd size="small" sx={{ opacity: isSelected ? 1 : 0.5 }}>
                        {cmd.shortcut}
                      </Kbd>
                    )}
                  </ListItemButton>
                </ListItem>
              )
            })}
          </List>
        </Box>
      ))}

      {filteredCommands.length === 0 && !isSearching && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            {query.trim() ? 'No results found' : 'Type to search commands, templates, and connections'}
          </Typography>
        </Box>
      )}
      {isSearching && filteredCommands.length === 0 && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <CircularProgress size={24} />
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Searching...
          </Typography>
        </Box>
      )}
    </Box>
  )
}

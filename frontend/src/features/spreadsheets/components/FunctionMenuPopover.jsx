import {
  Box,
  Popover,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Stack,
  Chip,
  styled,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { FORMULA_FUNCTIONS } from './formulaFunctions'

const FunctionChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  height: 24,
  fontSize: '0.75rem',
  fontFamily: 'monospace',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  color: 'text.secondary',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],
  },
}))

export default function FunctionMenuPopover({ anchorEl, onClose, onSelect }) {
  return (
    <Popover
      open={Boolean(anchorEl)}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      PaperProps={{
        sx: { width: 320, maxHeight: 400, borderRadius: 1 },
      }}
    >
      <Box sx={{ p: 1.5 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Insert Function
        </Typography>
        <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
          {FORMULA_FUNCTIONS.map((func) => (
            <ListItem key={func.name} disablePadding>
              <ListItemButton
                onClick={() => onSelect(func)}
                sx={{ borderRadius: 1, py: 0.5 }}
              >
                <ListItemText
                  primary={
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <FunctionChip label={func.name} size="small" />
                    </Stack>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {func.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Popover>
  )
}

export function AutocompletePopover({ anchorEl, filteredFunctions, onClose, onInsert }) {
  return (
    <Popover
      open={Boolean(anchorEl) && filteredFunctions.length > 0}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      disableAutoFocus
      disableEnforceFocus
      PaperProps={{
        sx: { width: 250, maxHeight: 200, borderRadius: 1 },
      }}
    >
      <List dense>
        {filteredFunctions.slice(0, 8).map((func) => (
          <ListItem key={func.name} disablePadding>
            <ListItemButton
              onClick={() => onInsert(func)}
              sx={{ py: 0.5 }}
            >
              <FunctionChip label={func.name} size="small" sx={{ mr: 1 }} />
              <Typography variant="caption" color="text.secondary" noWrap>
                {func.description}
              </Typography>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Popover>
  )
}

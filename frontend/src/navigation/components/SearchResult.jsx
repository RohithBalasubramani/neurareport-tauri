/**
 * Search result item component
 */
import {
  Box,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  alpha,
  useTheme,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import StorageIcon from '@mui/icons-material/Storage'
import WorkIcon from '@mui/icons-material/Work'
import { neutral } from '@/app/theme'

const getTypeConfig = (theme, type) => {
  const configs = {
    template: { icon: DescriptionIcon, color: theme.palette.text.secondary, label: 'Template' },
    connection: { icon: StorageIcon, color: theme.palette.text.secondary, label: 'Connection' },
    job: { icon: WorkIcon, color: theme.palette.text.secondary, label: 'Job' },
  }
  return configs[type] || configs.template
}

export default function SearchResult({ result, onSelect, isSelected }) {
  const theme = useTheme()
  const config = getTypeConfig(theme, result.type)
  const Icon = config.icon

  return (
    <ListItem
      onClick={() => onSelect(result)}
      data-testid={`search-result-${result.type}-${result.id}`}
      sx={{
        px: 2,
        py: 1.5,
        cursor: 'pointer',
        bgcolor: isSelected ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
        transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
        '&:hover': {
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        },
      }}
    >
      <ListItemIcon sx={{ minWidth: 36 }}>
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '8px',
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon sx={{ fontSize: 14, color: 'text.secondary' }} />
        </Box>
      </ListItemIcon>
      <ListItemText
        primary={result.name}
        secondary={result.description}
        primaryTypographyProps={{
          fontSize: '14px',
          fontWeight: 500,
          color: theme.palette.text.primary,
        }}
        secondaryTypographyProps={{
          fontSize: '0.75rem',
          color: theme.palette.text.secondary,
        }}
      />
      <Chip
        label={config.label}
        size="small"
        sx={{
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
          color: 'text.secondary',
          fontSize: '0.625rem',
          height: 20,
          borderRadius: 1.5,
        }}
      />
    </ListItem>
  )
}

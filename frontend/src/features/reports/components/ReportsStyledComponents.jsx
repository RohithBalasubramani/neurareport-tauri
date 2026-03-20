import {
  Typography,
  Paper,
  Button,
  TextField,
  Chip,
  Box,
  ListItem,
  LinearProgress,
  styled,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'

export const SectionLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.8125rem',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  color: theme.palette.text.primary,
  marginBottom: theme.spacing(1.5),
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  '&::after': {
    content: '""',
    flex: 1,
    height: 1,
    backgroundColor: alpha(theme.palette.divider, 0.3),
  },
}))

export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    '&:hover': {
      backgroundColor: alpha(theme.palette.background.paper, 0.8),
    },
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
      boxShadow: `0 0 0 3px ${alpha(theme.palette.text.primary, 0.08)}`,
    },
  },
}))

export const PresetChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'selected',
})(({ theme, selected }) => ({
  borderRadius: 10,
  fontWeight: 500,
  fontSize: '0.75rem',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  cursor: 'pointer',
  ...(selected && {
    background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    color: theme.palette.common.white,
    boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.15)}`,
    '& .MuiChip-icon': {
      color: theme.palette.common.white,
    },
  }),
  ...(!selected && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.primary,
    border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
    '& .MuiChip-icon': {
      color: theme.palette.text.secondary,
    },
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.14) : neutral[200],
      transform: 'translateY(-1px)',
    },
  }),
}))

export const DiscoveryChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  fontWeight: 600,
  fontSize: '0.75rem',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  color: theme.palette.text.secondary,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

export const BatchListContainer = styled(Box)(({ theme }) => ({
  maxHeight: 200,
  overflow: 'auto',
  borderRadius: 12,
  border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.4),
  '&::-webkit-scrollbar': {
    width: 6,
  },
  '&::-webkit-scrollbar-track': {
    background: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    background: alpha(theme.palette.text.primary, 0.2),
    borderRadius: 8,
  },
}))

export const BatchListItem = styled(ListItem, {
  shouldForwardProp: (prop) => prop !== 'selected',
})(({ theme, selected }) => ({
  padding: theme.spacing(1, 1.5),
  cursor: 'pointer',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  ...(selected && {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  }),
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
  '&:last-child': {
    borderBottom: 'none',
  },
}))

export const PrimaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '0.875rem',
  padding: theme.spacing(1.25, 3),
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-2px)',
  },
  '&:active': {
    transform: 'translateY(0)',
  },
  '&:disabled': {
    background: theme.palette.action.disabledBackground,
    color: theme.palette.action.disabled,
    boxShadow: 'none',
  },
}))

export const SecondaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: theme.spacing(1.25, 2.5),
  borderColor: alpha(theme.palette.divider, 0.3),
  color: theme.palette.text.primary,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    transform: 'translateY(-1px)',
  },
}))

export const TextButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.75rem',
  padding: theme.spacing(0.5, 1.5),
  color: theme.palette.text.secondary,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.primary,
  },
}))

export const RunHistoryCard = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'selected',
})(({ theme, selected }) => ({
  padding: theme.spacing(2),
  borderRadius: 12,
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  border: `1px solid ${selected ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.2)}`,
  backgroundColor: selected ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : 'transparent',
  '&:hover': {
    borderColor: alpha(theme.palette.divider, 0.4),
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50],
    '& .view-summary-hint': {
      opacity: 1,
      color: theme.palette.text.primary,
    },
  },
}))

export const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  borderRadius: 4,
  height: 6,
  backgroundColor: alpha(theme.palette.text.primary, 0.1),
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
  },
}))

export const DownloadButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.75rem',
  padding: theme.spacing(0.5, 1.5),
  borderColor: alpha(theme.palette.divider, 0.3),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  },
}))

export const AdvancedToggle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 0),
  cursor: 'pointer',
  color: theme.palette.text.secondary,
  transition: 'color 0.2s ease',
  '&:hover': {
    color: theme.palette.text.primary,
  },
}))

/** Download a file by URL — fetch as blob and trigger browser save dialog. */
export function downloadFile(url, filename, toast) {
  const label = filename || 'file'
  if (toast) toast.show(`Downloading ${label}...`, 'info')
  fetch(url)
    .then((res) => {
      if (!res.ok) throw new Error(`Download failed: ${res.status}`)
      return res.blob()
    })
    .then((blob) => {
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = filename || 'download'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(blobUrl)
      if (toast) toast.show(`Downloaded ${label}`, 'success')
    })
    .catch((err) => {
      console.error('[download]', err)
      if (toast) toast.show(`Download failed: ${err.message}`, 'error')
    })
}

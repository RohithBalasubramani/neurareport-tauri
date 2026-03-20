import {
  Box,
  Chip,
  TextField,
  Accordion,
  alpha,
  styled,
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Code as CodeIcon,
  Sync as SyncIcon,
  CheckCircle as ApprovalIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'

export const PanelContainer = styled(Box)(({ theme }) => ({
  width: 360,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.98),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

export const PanelFooter = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

export const NodeTypeChip = styled(Chip)(({ theme }) => ({
  borderRadius: 4,
  fontWeight: 600,
  fontSize: '12px',
}))

export const CodeEditor = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    fontFamily: 'monospace',
    fontSize: '14px',
    backgroundColor: alpha(theme.palette.common.black, 0.02),
  },
}))

export const VariableChip = styled(Chip)(({ theme }) => ({
  height: 24,
  fontSize: '12px',
  fontFamily: 'monospace',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],
  },
}))

export const ConfigAccordion = styled(Accordion)(({ theme }) => ({
  boxShadow: 'none',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  borderRadius: 8,
  '&:before': { display: 'none' },
  '&.Mui-expanded': {
    margin: 0,
  },
}))

export const NODE_TYPES = {
  trigger: {
    label: 'Trigger',
    color: 'success',
    icon: PlayIcon,
    configs: ['schedule', 'webhook', 'manual'],
  },
  action: {
    label: 'Action',
    color: 'primary',
    icon: SyncIcon,
    configs: ['http', 'email', 'database', 'transform', 'script'],
  },
  condition: {
    label: 'Condition',
    color: 'warning',
    icon: CodeIcon,
    configs: ['expression', 'switch'],
  },
  approval: {
    label: 'Approval',
    color: 'info',
    icon: ApprovalIcon,
    configs: ['manual', 'timeout', 'parallel'],
  },
  loop: {
    label: 'Loop',
    color: 'secondary',
    icon: SyncIcon,
    configs: ['foreach', 'while'],
  },
}

export const AVAILABLE_VARIABLES = [
  { name: 'input', description: 'Input data from previous node' },
  { name: 'env', description: 'Environment variables' },
  { name: 'workflow', description: 'Workflow metadata' },
  { name: 'timestamp', description: 'Current timestamp' },
  { name: 'user', description: 'Current user info' },
]

import EditIcon from '@mui/icons-material/Edit'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import UndoIcon from '@mui/icons-material/Undo'
import ChatIcon from '@mui/icons-material/Chat'
import HistoryIcon from '@mui/icons-material/History'

export const EDIT_TYPE_CONFIG = {
  manual: {
    icon: EditIcon,
    label: 'Manual',
    color: 'default',
  },
  ai: {
    icon: SmartToyIcon,
    label: 'AI',
    color: 'default',
  },
  chat: {
    icon: ChatIcon,
    label: 'Chat AI',
    color: 'default',
  },
  undo: {
    icon: UndoIcon,
    label: 'Undo',
    color: 'default',
  },
  default: {
    icon: HistoryIcon,
    label: 'Edit',
    color: 'default',
  },
}

export const MAX_HISTORY_ENTRIES = 500

export function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Unknown time'

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Node type definitions for workflow builder
 */
import {
  Schedule as ScheduleIcon,
  Webhook as WebhookIcon,
  Code as CodeIcon,
  Email as EmailIcon,
  Notifications as NotifyIcon,
  CallSplit as ConditionIcon,
  Loop as LoopIcon,
  CheckCircle as ApprovalIcon,
  Storage as DataIcon,
} from '@mui/icons-material'

export const NODE_TYPES = [
  { type: 'trigger', label: 'Trigger', icon: ScheduleIcon, color: 'warning', category: 'Triggers' },
  { type: 'webhook', label: 'Webhook', icon: WebhookIcon, color: 'info', category: 'Triggers' },
  { type: 'action', label: 'Action', icon: CodeIcon, color: 'primary', category: 'Actions' },
  { type: 'email', label: 'Send Email', icon: EmailIcon, color: 'secondary', category: 'Actions' },
  { type: 'notify', label: 'Notification', icon: NotifyIcon, color: 'success', category: 'Actions' },
  { type: 'condition', label: 'Condition', icon: ConditionIcon, color: 'info', category: 'Logic' },
  { type: 'loop', label: 'Loop', icon: LoopIcon, color: 'warning', category: 'Logic' },
  { type: 'approval', label: 'Approval', icon: ApprovalIcon, color: 'success', category: 'Logic' },
  { type: 'data', label: 'Data Transform', icon: DataIcon, color: 'primary', category: 'Data' },
]

export const getGroupedNodeTypes = () => {
  return NODE_TYPES.reduce((acc, node) => {
    if (!acc[node.category]) acc[node.category] = []
    acc[node.category].push(node)
    return acc
  }, {})
}

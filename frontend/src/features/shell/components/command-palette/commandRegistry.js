import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined'
import StorageOutlinedIcon from '@mui/icons-material/StorageOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined'
import WorkOutlineIcon from '@mui/icons-material/WorkOutline'
import ScheduleIcon from '@mui/icons-material/Schedule'
import DocumentScannerOutlinedIcon from '@mui/icons-material/DocumentScannerOutlined'
import HistoryIcon from '@mui/icons-material/History'
import TimelineIcon from '@mui/icons-material/Timeline'
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined'
import AddIcon from '@mui/icons-material/Add'
import SearchIcon from '@mui/icons-material/Search'
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined'
import AutoFixHighOutlinedIcon from '@mui/icons-material/AutoFixHighOutlined'
import JoinInnerOutlinedIcon from '@mui/icons-material/JoinInnerOutlined'
import MergeOutlinedIcon from '@mui/icons-material/MergeOutlined'
import ChatOutlinedIcon from '@mui/icons-material/ChatOutlined'
import SummarizeOutlinedIcon from '@mui/icons-material/SummarizeOutlined'
import BarChartOutlinedIcon from '@mui/icons-material/BarChartOutlined'
import AdminPanelSettingsOutlinedIcon from '@mui/icons-material/AdminPanelSettingsOutlined'
import PlayArrowOutlinedIcon from '@mui/icons-material/PlayArrowOutlined'

export const RECENT_KEY = 'neurareport_recent_commands'
export const MAX_RECENT = 6

export const ICON_MAP = {
  dashboard: DashboardOutlinedIcon,
  connections: StorageOutlinedIcon,
  templates: DescriptionOutlinedIcon,
  reports: AssessmentOutlinedIcon,
  jobs: WorkOutlineIcon,
  schedules: ScheduleIcon,
  analyze: DocumentScannerOutlinedIcon,
  history: HistoryIcon,
  activity: TimelineIcon,
  settings: SettingsOutlinedIcon,
  action: AddIcon,
  search: SearchIcon,
  recent: HistoryIcon,
  query: QuestionAnswerOutlinedIcon,
  enrichment: AutoFixHighOutlinedIcon,
  federation: JoinInnerOutlinedIcon,
  synthesis: MergeOutlinedIcon,
  docqa: ChatOutlinedIcon,
  summary: SummarizeOutlinedIcon,
  stats: BarChartOutlinedIcon,
  ops: AdminPanelSettingsOutlinedIcon,
}

export const COMMANDS = [
  { id: 'nav-dashboard', label: 'Go to Dashboard', description: 'View overview and analytics', icon: DashboardOutlinedIcon, iconKey: 'dashboard', action: 'navigate', path: '/', group: 'Navigation' },
  { id: 'nav-connections', label: 'Go to Connections', description: 'Manage database connections', icon: StorageOutlinedIcon, iconKey: 'connections', action: 'navigate', path: '/connections', group: 'Navigation' },
  { id: 'nav-templates', label: 'Go to Templates', description: 'Browse and manage templates', icon: DescriptionOutlinedIcon, iconKey: 'templates', action: 'navigate', path: '/templates', group: 'Navigation' },
  { id: 'nav-reports', label: 'Go to Reports', description: 'Generate reports', icon: AssessmentOutlinedIcon, iconKey: 'reports', action: 'navigate', path: '/reports', group: 'Navigation' },
  { id: 'nav-jobs', label: 'Go to Jobs', description: 'View job status', icon: WorkOutlineIcon, iconKey: 'jobs', action: 'navigate', path: '/jobs', group: 'Navigation' },
  { id: 'nav-schedules', label: 'Go to Schedules', description: 'Manage scheduled reports', icon: ScheduleIcon, iconKey: 'schedules', action: 'navigate', path: '/schedules', group: 'Navigation' },
  { id: 'nav-analyze', label: 'Go to Analyze', description: 'AI document analysis', icon: DocumentScannerOutlinedIcon, iconKey: 'analyze', action: 'navigate', path: '/analyze', group: 'Navigation' },
  { id: 'nav-history', label: 'Go to History', description: 'View report history', icon: HistoryIcon, iconKey: 'history', action: 'navigate', path: '/history', group: 'Navigation' },
  { id: 'nav-activity', label: 'Go to Activity', description: 'View activity log', icon: TimelineIcon, iconKey: 'activity', action: 'navigate', path: '/activity', group: 'Navigation' },
  { id: 'nav-settings', label: 'Go to Settings', description: 'Application settings', icon: SettingsOutlinedIcon, iconKey: 'settings', action: 'navigate', path: '/settings', group: 'Navigation' },
  { id: 'nav-query', label: 'Go to Query Builder', description: 'Build queries with natural language', icon: QuestionAnswerOutlinedIcon, iconKey: 'query', action: 'navigate', path: '/query', group: 'Setup' },
  { id: 'nav-enrichment', label: 'Go to Data Enrichment', description: 'Enrich data with AI-powered sources', icon: AutoFixHighOutlinedIcon, iconKey: 'enrichment', action: 'navigate', path: '/enrichment', group: 'Setup' },
  { id: 'nav-federation', label: 'Go to Combine Sources', description: 'Federate multiple data sources', icon: JoinInnerOutlinedIcon, iconKey: 'federation', action: 'navigate', path: '/federation', group: 'Setup' },
  { id: 'nav-synthesis', label: 'Go to Document Synthesis', description: 'Combine and synthesize documents', icon: MergeOutlinedIcon, iconKey: 'synthesis', action: 'navigate', path: '/synthesis', group: 'AI Tools' },
  { id: 'nav-docqa', label: 'Go to Ask Documents', description: 'Ask questions about your documents', icon: ChatOutlinedIcon, iconKey: 'docqa', action: 'navigate', path: '/docqa', group: 'AI Tools' },
  { id: 'nav-summary', label: 'Go to Summarize', description: 'Generate AI summaries of content', icon: SummarizeOutlinedIcon, iconKey: 'summary', action: 'navigate', path: '/summary', group: 'AI Tools' },
  { id: 'nav-stats', label: 'Go to Usage Stats', description: 'View usage statistics', icon: BarChartOutlinedIcon, iconKey: 'stats', action: 'navigate', path: '/stats', group: 'System' },
  { id: 'nav-ops', label: 'Go to Ops Console', description: 'Access health, auth, and job utilities', icon: AdminPanelSettingsOutlinedIcon, iconKey: 'ops', action: 'navigate', path: '/ops', group: 'System' },
  { id: 'new-report', label: 'New Report', description: 'Start a new report generation', icon: AddIcon, iconKey: 'action', action: 'navigate', path: '/setup/wizard', group: 'Actions', shortcut: '\u2318N' },
]

export const SEARCH_TYPE_CONFIG = {
  template: {
    icon: DescriptionOutlinedIcon,
    iconKey: 'templates',
    pathBuilder: (item) => `/templates/${item.id}/edit`,
    label: 'Template',
  },
  connection: {
    icon: StorageOutlinedIcon,
    iconKey: 'connections',
    pathBuilder: () => '/connections',
    label: 'Connection',
  },
  job: {
    icon: WorkOutlineIcon,
    iconKey: 'jobs',
    pathBuilder: () => '/jobs',
    label: 'Job',
  },
  schedule: {
    icon: ScheduleIcon,
    iconKey: 'schedules',
    pathBuilder: () => '/schedules',
    label: 'Schedule',
  },
}

export const loadRecentCommands = () => {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(RECENT_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export const persistRecentCommands = (items) => {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(RECENT_KEY, JSON.stringify(items))
  } catch {
    // ignore storage failures
  }
}

export const fuzzyScore = (query, text) => {
  if (!query || !text) return 0
  const q = query.toLowerCase()
  const t = text.toLowerCase()
  let score = 0
  let qi = 0
  let streak = 0
  for (let ti = 0; ti < t.length && qi < q.length; ti += 1) {
    if (t[ti] === q[qi]) {
      qi += 1
      streak += 1
      score += 5 + streak * 2
    } else {
      streak = 0
      score -= 1
    }
  }
  if (qi < q.length) return 0
  if (t.startsWith(q)) score += 8
  return score
}

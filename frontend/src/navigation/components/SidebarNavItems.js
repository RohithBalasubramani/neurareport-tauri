/**
 * Sidebar navigation structure
 */
import StorageIcon from '@mui/icons-material/Storage'
import DescriptionIcon from '@mui/icons-material/Description'
import AssessmentIcon from '@mui/icons-material/Assessment'
import WorkIcon from '@mui/icons-material/Work'
import SettingsIcon from '@mui/icons-material/Settings'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import DashboardIcon from '@mui/icons-material/Dashboard'
import ScheduleIcon from '@mui/icons-material/Schedule'
import HistoryIcon from '@mui/icons-material/History'
import TimelineIcon from '@mui/icons-material/Timeline'
import BarChartIcon from '@mui/icons-material/BarChart'
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import JoinInnerIcon from '@mui/icons-material/JoinInner'
import MergeIcon from '@mui/icons-material/Merge'
import ChatIcon from '@mui/icons-material/Chat'
import SummarizeIcon from '@mui/icons-material/Summarize'
import EditNoteIcon from '@mui/icons-material/EditNote'
import TableChartIcon from '@mui/icons-material/TableChart'
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize'
import WidgetsIcon from '@mui/icons-material/Widgets'
import CableIcon from '@mui/icons-material/Cable'
import AccountTreeIcon from '@mui/icons-material/AccountTree'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import SearchIcon from '@mui/icons-material/Search'
import BubbleChartIcon from '@mui/icons-material/BubbleChart'
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks'
import PaletteIcon from '@mui/icons-material/Palette'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import SensorsIcon from '@mui/icons-material/Sensors'

// Full navigation structure — all pages visible
const NAV_ITEMS = [
  {
    section: 'Home',
    items: [
      { key: 'dashboard', label: 'Dashboard', icon: DashboardIcon, path: '/', description: 'Overview & quick actions' },
    ],
  },
  {
    section: 'Reports',
    items: [
      { key: 'reports', label: 'My Reports', icon: AssessmentIcon, path: '/reports', description: 'View and download reports' },
      { key: 'history', label: 'History', icon: HistoryIcon, path: '/history', description: 'Past report runs' },
      { key: 'templates', label: 'Templates', icon: DescriptionIcon, path: '/templates', description: 'Report designs & layouts' },
      { key: 'design', label: 'Brand Kit', icon: PaletteIcon, path: '/design', description: 'Colors, fonts & logos' },
      { key: 'jobs', label: 'Running Jobs', icon: WorkIcon, path: '/jobs', badge: true, description: 'Report generation progress' },
      { key: 'schedules', label: 'Schedules', icon: ScheduleIcon, path: '/schedules', description: 'Automated report runs' },
    ],
  },
  {
    section: 'Data',
    collapsible: true,
    items: [
      { key: 'connections', label: 'Data Sources', icon: StorageIcon, path: '/connections', description: 'Database connections' },
      { key: 'logger', label: 'Logger', icon: SensorsIcon, path: '/logger', description: 'PLC data logger' },
      { key: 'connectors', label: 'Connectors', icon: CableIcon, path: '/connectors', description: 'Cloud & DB connectors' },
      { key: 'ingestion', label: 'Ingestion', icon: CloudUploadIcon, path: '/ingestion', description: 'Import documents & data' },
      { key: 'query', label: 'Query Builder', icon: QuestionAnswerIcon, path: '/query', description: 'Natural language to SQL' },
      { key: 'enrichment', label: 'Enrichment', icon: AutoFixHighIcon, path: '/enrichment', description: 'AI data enrichment' },
      { key: 'federation', label: 'Combine Sources', icon: JoinInnerIcon, path: '/federation', description: 'Cross-database federation' },
      { key: 'search', label: 'Search', icon: SearchIcon, path: '/search', description: 'Find anything' },
    ],
  },
  {
    section: 'AI Assistant',
    collapsible: true,
    items: [
      { key: 'analyze', label: 'Analyze', icon: AutoAwesomeIcon, path: '/analyze', highlight: true, description: 'AI document analysis & charts' },
      { key: 'docqa', label: 'Chat with Docs', icon: ChatIcon, path: '/docqa', description: 'Ask questions about documents' },
      { key: 'agents', label: 'AI Agents', icon: SmartToyIcon, path: '/agents', description: 'Research, analyze, write' },
      { key: 'knowledge', label: 'Knowledge Base', icon: LibraryBooksIcon, path: '/knowledge', description: 'Document library' },
      { key: 'summary', label: 'Summarize', icon: SummarizeIcon, path: '/summary', description: 'Executive summaries' },
      { key: 'synthesis', label: 'Synthesis', icon: MergeIcon, path: '/synthesis', description: 'Multi-document synthesis' },
    ],
  },
  {
    section: 'Create',
    collapsible: true,
    items: [
      { key: 'documents', label: 'Documents', icon: EditNoteIcon, path: '/documents', description: 'Write with AI help' },
      { key: 'spreadsheets', label: 'Spreadsheets', icon: TableChartIcon, path: '/spreadsheets', description: 'Data & formulas' },
      { key: 'dashboard-builder', label: 'Dashboards', icon: DashboardCustomizeIcon, path: '/dashboard-builder', description: 'Visual analytics' },
      { key: 'widgets', label: 'Widgets', icon: WidgetsIcon, path: '/widgets', description: 'AI-powered widget catalog' },
      { key: 'visualization', label: 'Diagrams', icon: BubbleChartIcon, path: '/visualization', description: 'Flowcharts, mindmaps & more' },
      { key: 'workflows', label: 'Workflows', icon: AccountTreeIcon, path: '/workflows', description: 'Automation builder' },
    ],
  },
  {
    section: 'Admin',
    collapsible: true,
    items: [
      { key: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings', description: 'Preferences & account' },
      { key: 'activity', label: 'Activity Log', icon: TimelineIcon, path: '/activity', description: 'User & system events' },
      { key: 'stats', label: 'Usage Stats', icon: BarChartIcon, path: '/stats', description: 'Analytics & metrics' },
      { key: 'ops', label: 'Ops Console', icon: AdminPanelSettingsIcon, path: '/ops', description: 'System administration' },
    ],
  },
]

export default NAV_ITEMS

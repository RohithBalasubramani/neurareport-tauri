/**
 * Agents Page - Styled Components & Constants
 */
import {
  Box,
  Card,
  Paper,
  Button,
  Typography,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'
import {
  Science as ResearchIcon,
  Analytics as DataIcon,
  Email as EmailIcon,
  Transform as ContentIcon,
  Spellcheck as ProofreadIcon,
  Assessment as ReportAnalystIcon,
} from '@mui/icons-material'

export const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

export const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

export const ContentArea = styled(Box)(() => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

export const MainPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

export const Sidebar = styled(Box)(({ theme }) => ({
  width: 350,
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  display: 'flex',
  flexDirection: 'column',
}))

export const AgentCard = styled(Card)(({ theme, selected }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  border: selected ? `2px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 24px ${alpha(theme.palette.text.primary, 0.15)}`,
  },
}))

export const ResultCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.spacing(2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

export const ActionButton = styled(Button)(() => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

export const AnalysisSectionTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  fontSize: '0.875rem',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  marginBottom: theme.spacing(1),
}))

export const FindingCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  borderRadius: 8,
}))

export const HighlightRow = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 1.5),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  '&:last-child': { borderBottom: 'none' },
}))

export const AGENTS = [
  {
    type: 'research',
    name: 'Research Agent',
    description: 'Deep-dive research and report compilation on any topic',
    icon: ResearchIcon,
    color: 'primary',
    fields: [
      { name: 'topic', label: 'Research Topic', type: 'text', required: true, multiline: true },
      { name: 'depth', label: 'Depth', type: 'select', options: ['quick', 'standard', 'comprehensive', 'exhaustive'], default: 'comprehensive' },
      { name: 'maxSections', label: 'Sections', type: 'number', default: 5, min: 1, max: 10 },
    ],
  },
  {
    type: 'data_analyst',
    name: 'Data Analyst',
    description: 'Analyze data and answer questions with insights',
    icon: DataIcon,
    color: 'info',
    fields: [
      { name: 'question', label: 'What do you want to know?', type: 'text', required: true, multiline: true, placeholder: 'e.g., What are the top 5 products by revenue? Which month had the highest sales?' },
      { name: 'dataSource', label: 'Data Source', type: 'select', options: ['paste_spreadsheet', 'database_connection', 'sample_sales', 'sample_inventory', 'custom_json'], default: 'paste_spreadsheet' },
      { name: 'data', label: 'Paste your data here (from Excel or Google Sheets)', type: 'spreadsheet', required: true, multiline: true, rows: 8, placeholder: 'Tip: Copy cells from Excel or Google Sheets and paste here. We\'ll convert it automatically!' },
    ],
  },
  {
    type: 'email_draft',
    name: 'Email Draft',
    description: 'Compose professional emails based on context',
    icon: EmailIcon,
    color: 'warning',
    fields: [
      { name: 'context', label: 'Context', type: 'text', required: true, multiline: true },
      { name: 'purpose', label: 'Purpose', type: 'text', required: true },
      { name: 'tone', label: 'Tone', type: 'select', options: ['professional', 'friendly', 'formal', 'casual'], default: 'professional' },
      { name: 'recipientInfo', label: 'Recipient Info', type: 'text' },
    ],
  },
  {
    type: 'content_repurpose',
    name: 'Content Repurpose',
    description: 'Transform content into multiple formats',
    icon: ContentIcon,
    color: 'secondary',
    fields: [
      { name: 'content', label: 'Original Content', type: 'text', required: true, multiline: true, rows: 6 },
      { name: 'sourceFormat', label: 'Source Format', type: 'select', options: ['blog', 'article', 'report', 'notes', 'transcript'], default: 'blog' },
      { name: 'targetFormats', label: 'Target Formats', type: 'multiselect', options: ['tweet_thread', 'linkedin_post', 'blog_summary', 'slides', 'email_newsletter', 'video_script'] },
    ],
  },
  {
    type: 'proofreading',
    name: 'Proofreading',
    description: 'Grammar, style, and clarity improvements',
    icon: ProofreadIcon,
    color: 'success',
    fields: [
      { name: 'text', label: 'Text to Proofread', type: 'text', required: true, multiline: true, rows: 8 },
      { name: 'styleGuide', label: 'Style Guide', type: 'select', options: ['AP', 'Chicago', 'MLA', 'APA', 'None'], default: 'None' },
    ],
  },
  {
    type: 'report_analyst',
    name: 'Report Analyst',
    description: 'Analyze, summarize, compare, or ask questions about generated reports',
    icon: ReportAnalystIcon,
    color: 'error',
    fields: [
      { name: 'runId', label: 'Report Run', type: 'reportRunPicker', required: true, placeholder: 'Select or enter a report run ID' },
      { name: 'analysisType', label: 'Analysis Type', type: 'select', options: ['summarize', 'insights', 'compare', 'qa'], default: 'summarize' },
      { name: 'question', label: 'Question (for Q&A mode)', type: 'text', multiline: true, placeholder: 'What would you like to know about this report?' },
      { name: 'compareRunId', label: 'Comparison Run ID (for compare mode)', type: 'reportRunPicker', placeholder: 'Select second report to compare against' },
    ],
  },
]

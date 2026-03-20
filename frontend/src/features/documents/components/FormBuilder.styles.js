import {
  Box,
  Paper,
  ListItemButton,
  alpha,
  styled,
} from '@mui/material'
import {
  TextFields as TextIcon,
  Numbers as NumberIcon,
  CalendarToday as DateIcon,
  CheckBox as CheckboxIcon,
  RadioButtonChecked as RadioIcon,
  ArrowDropDownCircle as SelectIcon,
  Upload as FileIcon,
  TextSnippet as TextAreaIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Link as UrlIcon,
  Edit as EditIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'

export const BuilderContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

export const FieldPalette = styled(Box)(({ theme }) => ({
  width: 280,
  padding: theme.spacing(2),
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

export const FormCanvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflowY: 'auto',
}))

export const PropertyPanel = styled(Box)(({ theme }) => ({
  width: 320,
  padding: theme.spacing(2),
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

export const FieldCard = styled(Paper, {
  shouldForwardProp: (prop) => !['isSelected', 'isDragging'].includes(prop),
})(({ theme, isSelected, isDragging }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${
    isSelected
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[900])
      : alpha(theme.palette.divider, 0.2)
  }`,
  backgroundColor: isDragging
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50])
    : theme.palette.background.paper,
  cursor: 'grab',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

export const PaletteItem = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

export const SectionHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 0),
  marginBottom: theme.spacing(1),
}))

export const FIELD_TYPES = [
  { type: 'text', label: 'Text Input', icon: TextIcon, category: 'basic' },
  { type: 'textarea', label: 'Text Area', icon: TextAreaIcon, category: 'basic' },
  { type: 'number', label: 'Number', icon: NumberIcon, category: 'basic' },
  { type: 'email', label: 'Email', icon: EmailIcon, category: 'basic' },
  { type: 'phone', label: 'Phone', icon: PhoneIcon, category: 'basic' },
  { type: 'url', label: 'URL', icon: UrlIcon, category: 'basic' },
  { type: 'date', label: 'Date', icon: DateIcon, category: 'datetime' },
  { type: 'time', label: 'Time', icon: DateIcon, category: 'datetime' },
  { type: 'datetime', label: 'Date & Time', icon: DateIcon, category: 'datetime' },
  { type: 'checkbox', label: 'Checkbox', icon: CheckboxIcon, category: 'choice' },
  { type: 'radio', label: 'Radio Group', icon: RadioIcon, category: 'choice' },
  { type: 'select', label: 'Dropdown', icon: SelectIcon, category: 'choice' },
  { type: 'multiselect', label: 'Multi-Select', icon: SelectIcon, category: 'choice' },
  { type: 'file', label: 'File Upload', icon: FileIcon, category: 'advanced' },
  { type: 'signature', label: 'Signature', icon: EditIcon, category: 'advanced' },
]

export const FIELD_CATEGORIES = [
  { id: 'basic', label: 'Basic Fields' },
  { id: 'datetime', label: 'Date & Time' },
  { id: 'choice', label: 'Choice Fields' },
  { id: 'advanced', label: 'Advanced' },
]

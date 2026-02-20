/**
 * Conditional Formatting Panel
 * UI for creating and managing conditional formatting rules in spreadsheets.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Switch,
  FormControlLabel,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import { neutral, palette, primary, secondary, status as statusColors } from '@/app/theme'
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  DragIndicator as DragIcon,
  FormatColorFill as FillIcon,
  FormatColorText as TextColorIcon,
  FormatBold as BoldIcon,
  FormatItalic as ItalicIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  DataObject as DataBarIcon,
  Circle as CircleIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 360,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const RuleCard = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isActive',
})(({ theme, isActive }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  backgroundColor: isActive ? 'transparent' : alpha(theme.palette.action.disabled, 0.05),
  opacity: isActive ? 1 : 0.7,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const ColorPreview = styled(Box)(({ theme, bgcolor, textcolor }) => ({
  width: 60,
  height: 28,
  borderRadius: 4,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: bgcolor || theme.palette.background.default,
  color: textcolor || theme.palette.text.primary,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  fontSize: '0.75rem',
  fontWeight: 600,
}))

const ColorInput = styled('input')(({ theme }) => ({
  width: 40,
  height: 32,
  padding: 0,
  border: 'none',
  borderRadius: 4,
  cursor: 'pointer',
  backgroundColor: 'transparent',
  '&::-webkit-color-swatch-wrapper': {
    padding: 0,
  },
  '&::-webkit-color-swatch': {
    border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
    borderRadius: 4,
  },
}))

// =============================================================================
// RULE TYPES AND CONDITIONS
// =============================================================================

const RULE_TYPES = [
  { value: 'cell_value', label: 'Cell Value' },
  { value: 'text_contains', label: 'Text Contains' },
  { value: 'date', label: 'Date' },
  { value: 'top_bottom', label: 'Top/Bottom Values' },
  { value: 'above_below_avg', label: 'Above/Below Average' },
  { value: 'duplicate', label: 'Duplicate Values' },
  { value: 'unique', label: 'Unique Values' },
  { value: 'blank', label: 'Blank/Non-Blank' },
  { value: 'formula', label: 'Custom Formula' },
  { value: 'color_scale', label: 'Color Scale' },
  { value: 'data_bar', label: 'Data Bar' },
  { value: 'icon_set', label: 'Icon Set' },
]

const CONDITIONS = {
  cell_value: [
    { value: 'greater_than', label: 'Greater than' },
    { value: 'less_than', label: 'Less than' },
    { value: 'equal_to', label: 'Equal to' },
    { value: 'not_equal', label: 'Not equal to' },
    { value: 'between', label: 'Between' },
    { value: 'not_between', label: 'Not between' },
  ],
  text_contains: [
    { value: 'contains', label: 'Contains' },
    { value: 'not_contains', label: 'Does not contain' },
    { value: 'begins_with', label: 'Begins with' },
    { value: 'ends_with', label: 'Ends with' },
  ],
  date: [
    { value: 'yesterday', label: 'Yesterday' },
    { value: 'today', label: 'Today' },
    { value: 'tomorrow', label: 'Tomorrow' },
    { value: 'last_7_days', label: 'Last 7 days' },
    { value: 'this_week', label: 'This week' },
    { value: 'this_month', label: 'This month' },
  ],
  top_bottom: [
    { value: 'top_n', label: 'Top N values' },
    { value: 'bottom_n', label: 'Bottom N values' },
    { value: 'top_percent', label: 'Top N%' },
    { value: 'bottom_percent', label: 'Bottom N%' },
  ],
  blank: [
    { value: 'is_blank', label: 'Is blank' },
    { value: 'not_blank', label: 'Is not blank' },
  ],
}

// Preset styles use secondary palette per Design System v4/v5
const PRESET_STYLES = [
  { label: 'Red Fill', fill: secondary.rose[100], text: secondary.rose[700] },
  { label: 'Green Fill', fill: secondary.emerald[100], text: secondary.emerald[700] },
  { label: 'Yellow Fill', fill: secondary.stone[100], text: secondary.stone[700] },
  { label: 'Blue Fill', fill: secondary.cyan[100], text: secondary.cyan[700] },
  { label: 'Orange Fill', fill: primary[100], text: secondary.stone[600] },
  { label: 'Purple Fill', fill: secondary.violet[100], text: secondary.violet[700] },
]

// =============================================================================
// RULE EDITOR DIALOG
// =============================================================================

function RuleEditorDialog({ open, rule, onClose, onSave }) {
  const theme = useTheme()
  const [localRule, setLocalRule] = useState(rule || {
    type: 'cell_value',
    condition: 'greater_than',
    value1: '',
    value2: '',
    format: {
      fill: secondary.rose[100],
      text: secondary.rose[700],
      bold: false,
      italic: false,
    },
    range: 'A1:Z100',
    priority: 1,
    enabled: true,
  })

  const handleChange = (key, value) => {
    setLocalRule((prev) => ({ ...prev, [key]: value }))
  }

  const handleFormatChange = (key, value) => {
    setLocalRule((prev) => ({
      ...prev,
      format: { ...prev.format, [key]: value },
    }))
  }

  const handleSave = () => {
    onSave?.(localRule)
    onClose()
  }

  const conditions = CONDITIONS[localRule.type] || []
  const needsValue = !['duplicate', 'unique', 'above_below_avg', 'color_scale', 'data_bar', 'icon_set'].includes(localRule.type) &&
    !['yesterday', 'today', 'tomorrow', 'is_blank', 'not_blank'].includes(localRule.condition)
  const needsTwoValues = ['between', 'not_between'].includes(localRule.condition)

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {rule?.id ? 'Edit Formatting Rule' : 'New Formatting Rule'}
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2.5}>
          {/* Range */}
          <TextField
            label="Apply to Range"
            size="small"
            fullWidth
            value={localRule.range}
            onChange={(e) => handleChange('range', e.target.value)}
            placeholder="e.g., A1:Z100"
          />

          {/* Rule Type */}
          <FormControl size="small" fullWidth>
            <InputLabel>Rule Type</InputLabel>
            <Select
              value={localRule.type}
              label="Rule Type"
              onChange={(e) => handleChange('type', e.target.value)}
            >
              {RULE_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Condition */}
          {conditions.length > 0 && (
            <FormControl size="small" fullWidth>
              <InputLabel>Condition</InputLabel>
              <Select
                value={localRule.condition}
                label="Condition"
                onChange={(e) => handleChange('condition', e.target.value)}
              >
                {conditions.map((cond) => (
                  <MenuItem key={cond.value} value={cond.value}>
                    {cond.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          {/* Value(s) */}
          {needsValue && (
            <Stack direction="row" spacing={1}>
              <TextField
                label={needsTwoValues ? 'From' : 'Value'}
                size="small"
                fullWidth
                value={localRule.value1}
                onChange={(e) => handleChange('value1', e.target.value)}
              />
              {needsTwoValues && (
                <TextField
                  label="To"
                  size="small"
                  fullWidth
                  value={localRule.value2}
                  onChange={(e) => handleChange('value2', e.target.value)}
                />
              )}
            </Stack>
          )}

          {/* Formula input */}
          {localRule.type === 'formula' && (
            <TextField
              label="Formula"
              size="small"
              fullWidth
              value={localRule.formula || ''}
              onChange={(e) => handleChange('formula', e.target.value)}
              placeholder="=$A1>100"
              helperText="Use cell references relative to the first cell in range"
            />
          )}

          <Divider />

          {/* Format Settings */}
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Format
          </Typography>

          {/* Preset Styles */}
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {PRESET_STYLES.map((preset, i) => (
              <Chip
                key={i}
                label={preset.label}
                size="small"
                onClick={() => {
                  handleFormatChange('fill', preset.fill)
                  handleFormatChange('text', preset.text)
                }}
                sx={{
                  backgroundColor: preset.fill,
                  color: preset.text,
                  '&:hover': { backgroundColor: preset.fill },
                }}
              />
            ))}
          </Stack>

          {/* Custom Colors */}
          <Stack direction="row" spacing={2} alignItems="center">
            <Stack direction="row" spacing={1} alignItems="center">
              <FillIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
              <Typography variant="caption">Fill:</Typography>
              <ColorInput
                type="color"
                value={localRule.format.fill || '#ffffff'}
                onChange={(e) => handleFormatChange('fill', e.target.value)}
              />
            </Stack>
            <Stack direction="row" spacing={1} alignItems="center">
              <TextColorIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
              <Typography variant="caption">Text:</Typography>
              <ColorInput
                type="color"
                value={localRule.format.text || '#000000'}
                onChange={(e) => handleFormatChange('text', e.target.value)}
              />
            </Stack>
          </Stack>

          {/* Font Style */}
          <Stack direction="row" spacing={1}>
            <Tooltip title="Bold">
              <IconButton
                size="small"
                onClick={() => handleFormatChange('bold', !localRule.format.bold)}
                sx={{ border: `1px solid ${alpha(theme.palette.divider, 0.2)}`, color: localRule.format.bold ? 'text.primary' : 'text.secondary' }}
              >
                <BoldIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Italic">
              <IconButton
                size="small"
                onClick={() => handleFormatChange('italic', !localRule.format.italic)}
                sx={{ border: `1px solid ${alpha(theme.palette.divider, 0.2)}`, color: localRule.format.italic ? 'text.primary' : 'text.secondary' }}
              >
                <ItalicIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>

          {/* Preview */}
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
              Preview:
            </Typography>
            <ColorPreview
              bgcolor={localRule.format.fill}
              textcolor={localRule.format.text}
              sx={{
                width: '100%',
                height: 40,
                fontWeight: localRule.format.bold ? 600 : 400,
                fontStyle: localRule.format.italic ? 'italic' : 'normal',
              }}
            >
              Sample Cell
            </ColorPreview>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          {rule?.id ? 'Save Changes' : 'Add Rule'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConditionalFormatPanel({
  rules = [],
  onRulesChange,
  selectedRange = '',
  onClose,
}) {
  const theme = useTheme()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState(null)
  const [expandedRules, setExpandedRules] = useState([])

  // Add new rule
  const handleAddRule = useCallback(() => {
    setEditingRule(null)
    setDialogOpen(true)
  }, [])

  // Edit rule
  const handleEditRule = useCallback((rule) => {
    setEditingRule(rule)
    setDialogOpen(true)
  }, [])

  // Save rule
  const handleSaveRule = useCallback((rule) => {
    if (rule.id) {
      // Update existing rule
      onRulesChange?.(rules.map((r) => (r.id === rule.id ? rule : r)))
    } else {
      // Add new rule
      onRulesChange?.([...rules, { ...rule, id: `rule_${Date.now()}` }])
    }
    setDialogOpen(false)
  }, [rules, onRulesChange])

  // Delete rule
  const handleDeleteRule = useCallback((ruleId) => {
    onRulesChange?.(rules.filter((r) => r.id !== ruleId))
  }, [rules, onRulesChange])

  // Toggle rule enabled
  const handleToggleRule = useCallback((ruleId) => {
    onRulesChange?.(
      rules.map((r) => (r.id === ruleId ? { ...r, enabled: !r.enabled } : r))
    )
  }, [rules, onRulesChange])

  // Toggle rule expansion
  const toggleRuleExpansion = useCallback((ruleId) => {
    setExpandedRules((prev) =>
      prev.includes(ruleId)
        ? prev.filter((id) => id !== ruleId)
        : [...prev, ruleId]
    )
  }, [])

  // Get rule description
  const getRuleDescription = (rule) => {
    const typeLabel = RULE_TYPES.find((t) => t.value === rule.type)?.label || rule.type
    const conditions = CONDITIONS[rule.type] || []
    const condLabel = conditions.find((c) => c.value === rule.condition)?.label || rule.condition

    if (['duplicate', 'unique'].includes(rule.type)) {
      return typeLabel
    }
    if (['color_scale', 'data_bar', 'icon_set'].includes(rule.type)) {
      return typeLabel
    }
    if (rule.condition === 'between') {
      return `${condLabel} ${rule.value1} and ${rule.value2}`
    }
    return `${condLabel} ${rule.value1 || ''}`
  }

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <FillIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Conditional Formatting
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </PanelHeader>

      <PanelContent>
        {/* Selected Range */}
        {selectedRange && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Selected Range:
            </Typography>
            <Chip
              label={selectedRange}
              size="small"
              sx={{ ml: 1, fontFamily: 'monospace' }}
            />
          </Box>
        )}

        {/* Add Rule Button */}
        <Button
          fullWidth
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddRule}
          sx={{ mb: 2 }}
        >
          Add New Rule
        </Button>

        {/* Rules List */}
        {rules.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <FillIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No formatting rules yet
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Add rules to highlight cells based on conditions
            </Typography>
          </Box>
        ) : (
          rules.map((rule, index) => (
            <RuleCard key={rule.id} elevation={0} isActive={rule.enabled}>
              <Stack direction="row" alignItems="flex-start" spacing={1}>
                <DragIcon sx={{ color: 'text.disabled', mt: 0.5, cursor: 'grab' }} />

                <Box sx={{ flex: 1 }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Chip
                        label={index + 1}
                        size="small"
                        sx={{
                          width: 24,
                          height: 24,
                          fontSize: '12px',
                          '& .MuiChip-label': { px: 0 },
                        }}
                      />
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {RULE_TYPES.find((t) => t.value === rule.type)?.label || rule.type}
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={0.5}>
                      <Switch
                        size="small"
                        checked={rule.enabled}
                        onChange={() => handleToggleRule(rule.id)}
                      />
                      <IconButton
                        size="small"
                        onClick={() => toggleRuleExpansion(rule.id)}
                      >
                        {expandedRules.includes(rule.id) ? <CollapseIcon /> : <ExpandIcon />}
                      </IconButton>
                    </Stack>
                  </Stack>

                  <Typography variant="caption" color="text.secondary">
                    {getRuleDescription(rule)}
                  </Typography>

                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
                    <ColorPreview
                      bgcolor={rule.format?.fill}
                      textcolor={rule.format?.text}
                      sx={{
                        fontWeight: rule.format?.bold ? 600 : 400,
                        fontStyle: rule.format?.italic ? 'italic' : 'normal',
                      }}
                    >
                      Abc
                    </ColorPreview>
                    <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                      {rule.range}
                    </Typography>
                  </Stack>

                  <Collapse in={expandedRules.includes(rule.id)}>
                    <Divider sx={{ my: 1.5 }} />
                    <Stack direction="row" spacing={1}>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleEditRule(rule)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        sx={{ color: 'text.secondary' }}
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDeleteRule(rule.id)}
                      >
                        Delete
                      </Button>
                    </Stack>
                  </Collapse>
                </Box>
              </Stack>
            </RuleCard>
          ))
        )}
      </PanelContent>

      {/* Rule Editor Dialog */}
      <RuleEditorDialog
        open={dialogOpen}
        rule={editingRule}
        onClose={() => setDialogOpen(false)}
        onSave={handleSaveRule}
      />
    </PanelContainer>
  )
}

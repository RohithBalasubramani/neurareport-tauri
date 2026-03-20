/**
 * Conditional Formatting Panel
 * UI for creating and managing conditional formatting rules in spreadsheets.
 */
import {
  Box,
  Typography,
  IconButton,
  Button,
  Stack,
  Chip,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Add as AddIcon,
  FormatColorFill as FillIcon,
} from '@mui/icons-material'
import { useConditionalFormat } from '../hooks/useConditionalFormat'
import RuleEditorDialog from './RuleEditorDialog'
import ConditionalFormatRuleCard from './ConditionalFormatRuleCard'

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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ConditionalFormatPanel({
  rules = [],
  onRulesChange,
  selectedRange = '',
  onClose,
}) {
  const {
    dialogOpen,
    editingRule,
    expandedRules,
    setDialogOpen,
    handleAddRule,
    handleEditRule,
    handleSaveRule,
    handleDeleteRule,
    handleToggleRule,
    toggleRuleExpansion,
  } = useConditionalFormat({ rules, onRulesChange })

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

        <Button
          fullWidth
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddRule}
          sx={{ mb: 2 }}
        >
          Add New Rule
        </Button>

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
            <ConditionalFormatRuleCard
              key={rule.id}
              rule={rule}
              index={index}
              isExpanded={expandedRules.includes(rule.id)}
              onToggleExpansion={toggleRuleExpansion}
              onToggleEnabled={handleToggleRule}
              onEdit={handleEditRule}
              onDelete={handleDeleteRule}
            />
          ))
        )}
      </PanelContent>

      <RuleEditorDialog
        open={dialogOpen}
        rule={editingRule}
        onClose={() => setDialogOpen(false)}
        onSave={handleSaveRule}
      />
    </PanelContainer>
  )
}

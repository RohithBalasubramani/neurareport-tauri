/**
 * Data Validation Panel
 * UI for creating and managing data validation rules in spreadsheets.
 */
import {
  Box,
  Typography,
  IconButton,
  Button,
  Stack,
  Chip,
  Alert,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Add as AddIcon,
  VerifiedUser as ValidationIcon,
} from '@mui/icons-material'
import { useDataValidation } from '../hooks/useDataValidation'
import ValidationEditorDialog from './ValidationEditorDialog'
import ValidationRuleCard from './ValidationRuleCard'

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

export default function DataValidationPanel({
  validations = [],
  onValidationsChange,
  selectedRange = '',
  onClose,
}) {
  const {
    dialogOpen,
    editingValidation,
    setDialogOpen,
    handleAddValidation,
    handleEditValidation,
    handleSaveValidation,
    handleDeleteValidation,
  } = useDataValidation({ validations, onValidationsChange })

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <ValidationIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Data Validation
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
          onClick={handleAddValidation}
          sx={{ mb: 2 }}
        >
          Add Validation Rule
        </Button>

        <Alert severity="info" sx={{ mb: 2, fontSize: '0.75rem' }}>
          Data validation restricts the type of data that can be entered in cells.
        </Alert>

        {validations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <ValidationIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No validation rules yet
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Add rules to restrict cell input
            </Typography>
          </Box>
        ) : (
          validations.map((validation) => (
            <ValidationRuleCard
              key={validation.id}
              validation={validation}
              onEdit={handleEditValidation}
              onDelete={handleDeleteValidation}
            />
          ))
        )}
      </PanelContent>

      <ValidationEditorDialog
        open={dialogOpen}
        validation={editingValidation}
        onClose={() => setDialogOpen(false)}
        onSave={handleSaveValidation}
      />
    </PanelContainer>
  )
}

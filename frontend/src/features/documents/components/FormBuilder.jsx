import {
  Box, Typography, IconButton, Tooltip, Paper, TextField,
  Stack, Divider, List, ListItemIcon, ListItemText, ListItemButton,
  Collapse, useTheme, alpha,
} from '@mui/material'
import {
  Add as AddIcon, ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon, Preview as PreviewIcon, Save as SaveIcon,
} from '@mui/icons-material'
import {
  BuilderContainer,
  FieldPalette,
  FormCanvas,
  PropertyPanel,
  PaletteItem,
  SectionHeader,
  FIELD_TYPES,
  FIELD_CATEGORIES,
} from './FormBuilder.styles'
import FieldPreview from './FieldPreview'
import FieldPropertiesPanel from './FieldPropertiesPanel'
import FormPreviewDialog from './FormPreviewDialog'
import { useFormBuilder } from '../hooks/useFormBuilder'

export default function FormBuilder({
  fields = [],
  onFieldsChange,
  onSave,
  formTitle = 'Untitled Form',
  onTitleChange,
  readOnly = false,
}) {
  const theme = useTheme()
  const {
    selectedFieldId,
    setSelectedFieldId,
    selectedField,
    expandedCategories,
    toggleCategory,
    previewOpen,
    setPreviewOpen,
    handleAddField,
    handleUpdateField,
    handleDeleteField,
    handleDuplicateField,
  } = useFormBuilder({ fields, onFieldsChange })

  return (
    <BuilderContainer>
      {/* Field Palette */}
      <FieldPalette>
        <SectionHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Form Fields
          </Typography>
        </SectionHeader>

        {FIELD_CATEGORIES.map((category) => {
          const categoryFields = FIELD_TYPES.filter((f) => f.category === category.id)
          const isExpanded = expandedCategories.includes(category.id)

          return (
            <Box key={category.id} sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => toggleCategory(category.id)}
                sx={{ borderRadius: 1, py: 0.5, px: 1 }}
              >
                <ListItemText
                  primary={category.label}
                  primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                />
                {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
              </ListItemButton>

              <Collapse in={isExpanded}>
                <List dense disablePadding sx={{ pl: 1, pr: 0.5 }}>
                  {categoryFields.map((fieldType) => {
                    const Icon = fieldType.icon
                    return (
                      <PaletteItem
                        key={fieldType.type}
                        onClick={() => !readOnly && handleAddField(fieldType)}
                        disabled={readOnly}
                      >
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={fieldType.label}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </PaletteItem>
                    )
                  })}
                </List>
              </Collapse>
            </Box>
          )
        })}
      </FieldPalette>

      {/* Form Canvas */}
      <FormCanvas>
        <Paper
          elevation={0}
          sx={{
            maxWidth: 720,
            mx: 'auto',
            p: 3,
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            borderRadius: 1,
          }}
        >
          <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
            <TextField
              value={formTitle}
              onChange={(e) => onTitleChange?.(e.target.value)}
              variant="standard"
              disabled={readOnly}
              InputProps={{
                sx: { fontSize: '1.5rem', fontWeight: 600 },
                disableUnderline: readOnly,
              }}
            />
            <Stack direction="row" spacing={1}>
              <Tooltip title="Preview">
                <IconButton onClick={() => setPreviewOpen(true)}>
                  <PreviewIcon />
                </IconButton>
              </Tooltip>
              {!readOnly && (
                <Tooltip title="Save">
                  <IconButton onClick={onSave} sx={{ color: 'text.secondary' }}>
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Stack>
          </Stack>

          <Divider sx={{ mb: 3 }} />

          {fields.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <AddIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Drag fields from the palette to build your form
              </Typography>
              <Typography variant="body2" color="text.disabled">
                or click a field type to add it
              </Typography>
            </Box>
          ) : (
            fields.map((field) => (
              <FieldPreview
                key={field.id}
                field={field}
                isSelected={selectedFieldId === field.id}
                onClick={() => setSelectedFieldId(field.id)}
                onDelete={() => handleDeleteField(field.id)}
                onDuplicate={() => handleDuplicateField(field.id)}
              />
            ))
          )}
        </Paper>
      </FormCanvas>

      {/* Properties Panel */}
      <PropertyPanel>
        <SectionHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Properties
          </Typography>
        </SectionHeader>
        <FieldPropertiesPanel
          field={selectedField}
          onChange={handleUpdateField}
        />
      </PropertyPanel>

      <FormPreviewDialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        formTitle={formTitle}
        fields={fields}
      />
    </BuilderContainer>
  )
}

import {
  Box,
  Typography,
  Stack,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateRecommender from '@/features/reports/components/TemplateRecommender.jsx'
import { GlassCard, StyledFormControl } from '@/styles'
import { SectionLabel } from './ReportsStyledComponents'

export default function DesignSourceCard({
  templates,
  selectedTemplate,
  activeConnection,
  onTemplateChange,
  onAiSelectTemplate,
  onConnectionChange,
  onNavigate,
}) {
  return (
    <GlassCard>
      <SectionLabel>
        <DescriptionIcon sx={{ fontSize: 14 }} />
        Design & Data Source
      </SectionLabel>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        {/* Report Design */}
        <Box sx={{ flex: 1 }}>
          <StyledFormControl fullWidth>
            <InputLabel>Report Design</InputLabel>
            <Select
              value={selectedTemplate}
              onChange={onTemplateChange}
              label="Report Design"
            >
              {templates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <span>{template.name || template.id}</span>
                    <Chip
                      label={template.kind?.toUpperCase() || 'PDF'}
                      size="small"
                      variant="outlined"
                      sx={{ borderRadius: 6, fontSize: '10px', height: 20 }}
                    />
                  </Stack>
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
        </Box>

        {/* Data Source */}
        <Box sx={{ flex: 1 }}>
          <ConnectionSelector
            value={activeConnection?.id || ''}
            onChange={onConnectionChange}
            label="Data Source"
            showStatus
          />
          {!activeConnection && (
            <Typography variant="caption" color="warning.main" sx={{ mt: 0.75, display: 'block' }}>
              No data source selected.{' '}
              <Typography
                component="span"
                variant="caption"
                sx={{ color: 'primary.main', cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => onNavigate('/connections', 'Open connections')}
              >
                Add one
              </Typography>
            </Typography>
          )}
        </Box>
      </Stack>

      {/* AI Template Picker */}
      <Box sx={{ mt: 2 }}>
        <TemplateRecommender onSelectTemplate={onAiSelectTemplate} />
      </Box>
    </GlassCard>
  )
}

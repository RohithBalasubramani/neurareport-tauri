import {
  Box, Typography, Stack, Button, Chip, Divider, Grid,
  Card, CardContent, CardActionArea, Radio, alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

export default function TemplateGallery({
  filteredGalleryTemplates,
  selectedGalleryTemplate,
  onSelectGalleryTemplate,
  onClearSelection,
  onUseGalleryTemplate,
  onShowUpload,
  onNavigate,
  wizardConnectionId,
}) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle2" fontWeight={600} color="text.secondary" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
        <AutoAwesomeIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
        Template Gallery
      </Typography>

      <Grid container spacing={2}>
        {filteredGalleryTemplates.map((template) => {
          const IconComponent = template.icon
          const isSelected = selectedGalleryTemplate?.id === template.id

          return (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card
                variant="outlined"
                sx={{
                  height: '100%',
                  border: 2,
                  borderColor: isSelected ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
                  bgcolor: isSelected ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                    transform: 'translateY(-2px)',
                    boxShadow: 2,
                  },
                }}
              >
                <CardActionArea
                  onClick={() => onSelectGalleryTemplate(template)}
                  sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                >
                  <CardContent sx={{ flex: 1 }}>
                    <Stack direction="row" alignItems="flex-start" spacing={1} sx={{ mb: 1 }}>
                      <Radio checked={isSelected} size="small" sx={{ p: 0, mr: 0.5 }} />
                      <IconComponent sx={{
                        fontSize: 24,
                        color: 'text.secondary'
                      }} />
                      <Box sx={{ flex: 1 }}>
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Typography variant="subtitle2" fontWeight={600}>
                            {template.name}
                          </Typography>
                          {template.popular && (
                            <Chip label="Popular" size="small" sx={{ height: 18, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                          )}
                        </Stack>
                        <Chip
                          label={template.kind.toUpperCase()}
                          size="small"
                          variant="outlined"
                          sx={{ height: 18, fontSize: '10px', mt: 0.5, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                        />
                      </Box>
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      {template.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {selectedGalleryTemplate && (
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            onClick={onUseGalleryTemplate}
            startIcon={<CheckCircleIcon />}
            sx={{ mr: 2 }}
          >
            Use "{selectedGalleryTemplate.name}"
          </Button>
          <Button variant="text" onClick={onClearSelection}>
            Clear Selection
          </Button>
        </Box>
      )}

      <Divider sx={{ my: 3 }}>
        <Chip label="Or start your own" size="small" />
      </Divider>

      <Stack direction="row" spacing={2}>
        <Button
          variant="contained"
          startIcon={<AutoAwesomeIcon />}
          onClick={() => onNavigate(`/templates/new/chat?from=wizard&connectionId=${encodeURIComponent(wizardConnectionId || '')}`, 'Create template with AI')}
          sx={{
            bgcolor: neutral[900],
            '&:hover': { bgcolor: neutral[700] },
          }}
        >
          Create with AI
        </Button>
        <Button
          variant="outlined"
          startIcon={<CloudUploadIcon />}
          onClick={onShowUpload}
          sx={{ borderStyle: 'dashed' }}
        >
          Upload Custom Template
        </Button>
      </Stack>
    </Box>
  )
}

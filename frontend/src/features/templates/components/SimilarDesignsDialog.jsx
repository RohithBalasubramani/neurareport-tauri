/**
 * Similar designs discovery dialog
 */
import {
  Box,
  Chip,
  Stack,
  Typography,
  useTheme,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { getKindConfig } from './templateConfigHelpers'
import {
  StyledDialog,
  DialogHeader,
  StyledDialogContent,
  StyledDialogActions,
  SecondaryButton,
  KindIconContainer,
  SimilarTemplateCard,
  AiIcon,
} from './TemplateStyledComponents'

export default function SimilarDesignsDialog({
  similarOpen,
  setSimilarOpen,
  similarTemplate,
  similarTemplates,
  similarLoading,
  handleSelectSimilarTemplate,
}) {
  const theme = useTheme()

  return (
    <StyledDialog open={similarOpen} onClose={() => setSimilarOpen(false)} maxWidth="sm" fullWidth>
      <DialogHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <AiIcon />
          <span>Similar Designs</span>
        </Stack>
      </DialogHeader>
      <StyledDialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Designs similar to "{similarTemplate?.name || similarTemplate?.id}"
        </Typography>
        {similarLoading ? (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">Loading similar designs...</Typography>
          </Box>
        ) : similarTemplates.length === 0 ? (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">No similar designs found.</Typography>
          </Box>
        ) : (
          <Stack spacing={1}>
            {similarTemplates.map((template) => {
              const config = getKindConfig(theme, template.kind)
              const Icon = config.icon
              return (
                <SimilarTemplateCard
                  key={template.id}
                  onClick={() => handleSelectSimilarTemplate(template)}
                >
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <KindIconContainer>
                      <Icon sx={{ color: 'text.secondary', fontSize: 18 }} />
                    </KindIconContainer>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2">{template.name || template.id}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {template.description || `${template.kind?.toUpperCase() || 'PDF'} Design`}
                      </Typography>
                    </Box>
                    {template.similarity_score && (
                      <Chip
                        label={`${Math.round(template.similarity_score * 100)}% match`}
                        size="small"
                        variant="outlined"
                        sx={{ borderRadius: 8, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                      />
                    )}
                  </Stack>
                </SimilarTemplateCard>
              )
            })}
          </Stack>
        )}
      </StyledDialogContent>
      <StyledDialogActions>
        <SecondaryButton variant="outlined" onClick={() => setSimilarOpen(false)}>Close</SecondaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}

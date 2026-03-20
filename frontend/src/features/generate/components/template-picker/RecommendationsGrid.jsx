import Grid from '@mui/material/Grid2'
import { alpha, Button, Card, CardContent, Chip, Stack, Typography } from '@mui/material'
import { neutral } from '@/app/theme'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import getSourceMeta from '../../utils/templateSourceMeta'

export default function RecommendationsGrid({ recommendations, onFindInAll }) {
  if (!recommendations.length) {
    return (
      <EmptyState
        size="medium"
        title="No recommendations yet"
        description="Describe what you need and click Get recommendations to see suggestions."
      />
    )
  }

  return (
    <Grid container spacing={2.5}>
      {recommendations.map((entry, index) => {
        const template = entry?.template || {}
        const meta = getSourceMeta(template.source)
        const isStarter = meta.isStarter
        return (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={template.id || `rec-${index}`} sx={{ minWidth: 0 }}>
            <Card variant="outlined">
              <CardContent>
                <Stack spacing={1.25}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {template.name || template.id || 'Template'}
                    </Typography>
                    <Chip size="small" label={meta.label} sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} variant={meta.variant} />
                  </Stack>
                  {template.description && (
                    <Typography variant="body2" color="text.secondary">
                      {template.description}
                    </Typography>
                  )}
                  {entry?.explanation && (
                    <Typography variant="body2">
                      {entry.explanation}
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    {isStarter ? 'Starter template - Review before use' : 'Company template - Editable'}
                  </Typography>
                  {!isStarter && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => onFindInAll(template.name || template.id)}
                    >
                      Find in "All" templates
                    </Button>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        )
      })}
    </Grid>
  )
}

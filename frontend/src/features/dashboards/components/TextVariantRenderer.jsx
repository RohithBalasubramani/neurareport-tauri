/**
 * Text variant sub-renderer for WidgetRenderer.
 */
import { Box, Typography, Chip } from '@mui/material'
import { NarrativeCard } from './WidgetRendererStyles'

export default function TextVariantRenderer({ variantKey, vConfig, data, config }) {
  return (
    <NarrativeCard>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        {data?.title || config?.title || vConfig.label}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
        {data?.text || data?.narrative || 'No narrative available.'}
      </Typography>
      {data?.highlights?.length > 0 && (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1.5 }}>
          {data.highlights.map((h, i) => (
            <Chip key={i} label={h} size="small" variant="outlined" />
          ))}
        </Box>
      )}
    </NarrativeCard>
  )
}

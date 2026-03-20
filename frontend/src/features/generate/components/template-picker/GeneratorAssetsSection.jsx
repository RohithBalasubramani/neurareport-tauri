import { alpha, Button, Chip, Stack, Tooltip, Typography } from '@mui/material'
import { neutral } from '@/app/theme'

export default function GeneratorAssetsSection({ generatorMeta, generatorArtifacts, generatorStatusLabel, needsUserFix, generatorUpdated, assetHref }) {
  return (
    <Stack spacing={0.75} sx={{ mt: 1 }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', rowGap: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          SQL & schema assets - {generatorMeta.dialect || 'unknown'}
        </Typography>
        <Chip size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} label={generatorStatusLabel} />
        {!!needsUserFix.length && (
          <Tooltip title={needsUserFix.join('\\n')}>
            <Chip
              size="small"
              sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              variant="outlined"
              label={`${needsUserFix.length} fix${needsUserFix.length === 1 ? '' : 'es'}`}
            />
          </Tooltip>
        )}
        {generatorUpdated && (
          <Typography variant="caption" color="text.secondary">
            Updated {generatorUpdated}
          </Typography>
        )}
      </Stack>
      <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
        {generatorArtifacts.sql && (
          <Button size="small" variant="outlined" component="a" href={assetHref(generatorArtifacts.sql)} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
            SQL Pack
          </Button>
        )}
        {generatorArtifacts.schemas && (
          <Button size="small" variant="outlined" component="a" href={assetHref(generatorArtifacts.schemas)} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
            Output Schemas
          </Button>
        )}
        {generatorArtifacts.meta && (
          <Button size="small" variant="outlined" component="a" href={assetHref(generatorArtifacts.meta)} target="_blank" rel="noopener" onClick={(e) => e.stopPropagation()}>
            Generator JSON
          </Button>
        )}
      </Stack>
    </Stack>
  )
}

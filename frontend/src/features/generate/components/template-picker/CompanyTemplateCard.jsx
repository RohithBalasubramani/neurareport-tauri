import {
  alpha,
  Box,
  Card,
  CardContent,
  Checkbox,
  Chip,
  Divider,
  Stack,
  Typography,
} from '@mui/material'
import { neutral, secondary } from '@/app/theme'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import { resolveTemplatePreviewUrl, resolveTemplateThumbnailUrl } from '@/utils/preview'
import { buildLastEditInfo } from '@/utils/templateMeta'
import { buildDownloadUrl, getTemplateKind } from '../../utils/generateFeatureUtils'
import { withBase } from '../../services/generateApi'
import GeneratorAssetsSection from './GeneratorAssetsSection.jsx'
import CompanyCardFooter from './CompanyCardFooter.jsx'

export default function CompanyTemplateCard({
  template: t,
  selectedState,
  outputFormats,
  setOutputFormats,
  deleting,
  exporting,
  onToggle,
  onDelete,
  onExport,
  onEditTemplate,
  toast,
}) {
  const type = getTemplateKind(t).toUpperCase()
  const fmt = outputFormats[t.id] || 'auto'
  const previewInfo = resolveTemplatePreviewUrl(t)
  const htmlPreview = previewInfo.url
  const previewKey = previewInfo.key || `${t.id}-preview`
  const thumbnailInfo = resolveTemplateThumbnailUrl(t)
  const imagePreview = !htmlPreview ? thumbnailInfo.url : null
  const generatorArtifacts = {
    sql: t.artifacts?.generator_sql_pack_url,
    schemas: t.artifacts?.generator_output_schemas_url,
    meta: t.artifacts?.generator_assets_url,
  }
  const generatorMeta = t.generator || {}
  const hasGeneratorAssets = Object.values(generatorArtifacts).some(Boolean)
  const needsUserFix = Array.isArray(generatorMeta.needsUserFix) ? generatorMeta.needsUserFix : []
  const generatorStatusLabel = generatorMeta.invalid ? 'Needs review' : 'Ready'
  let generatorUpdated = null
  if (generatorMeta.updatedAt) {
    const parsed = new Date(generatorMeta.updatedAt)
    generatorUpdated = Number.isNaN(parsed.getTime()) ? null : parsed.toLocaleString()
  }
  const assetHref = (url) => (url ? buildDownloadUrl(withBase(url)) : null)
  const generatorReady = hasGeneratorAssets && !generatorMeta.invalid && needsUserFix.length === 0
  const lastEditInfo = buildLastEditInfo(t.generator?.summary)
  const lastEditChipLabel = lastEditInfo?.chipLabel || 'Not edited yet'
  const lastEditChipColor = lastEditInfo?.color || 'default'
  const lastEditChipVariant = lastEditInfo?.variant || 'outlined'

  const handleCardToggle = () => {
    if (!selectedState) {
      if (!hasGeneratorAssets) {
        toast.show('Generate SQL & schema assets for this template before selecting it.', 'warning')
        return
      }
      if (!generatorReady) {
        const detail = needsUserFix.length ? `Resolve: ${needsUserFix.join(', ')}` : 'Generator assets need attention.'
        toast.show(detail, 'warning')
        return
      }
    }
    onToggle(t.id)
  }

  const handleCardKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleCardToggle()
    }
  }

  return (
    <Card
      variant="outlined"
      sx={[
        {
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 300,
          transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',
        },
        selectedState && {
          borderColor: 'text.secondary',
          boxShadow: `0 0 0 1px ${alpha(secondary.violet[500], 0.28)}`,
        },
      ]}
    >
      <Checkbox
        checked={selectedState}
        onChange={() => onToggle(t.id)}
        onClick={(event) => event.stopPropagation()}
        sx={{ position: 'absolute', top: 12, left: 12, zIndex: 1 }}
        aria-label={`Select ${t.name}`}
      />
      <Box role="button" tabIndex={0} onKeyDown={handleCardKeyDown} onClick={handleCardToggle} sx={{ height: '100%', cursor: 'pointer' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, height: '100%', flexGrow: 1 }}>
          <Box
            sx={{
              minHeight: 180,
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              overflow: 'hidden',
              bgcolor: 'background.default',
              p: 1,
              aspectRatio: '210 / 297',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {htmlPreview ? (
              <ScaledIframePreview
                key={previewKey}
                src={htmlPreview}
                title={`${t.name} preview`}
                sx={{ width: '100%', height: '100%' }}
                frameAspectRatio="210 / 297"
                pageShadow
                pageBorderColor={alpha(neutral[900], 0.08)}
                marginGuides={{ inset: 28, color: alpha(secondary.violet[500], 0.28) }}
              />
            ) : imagePreview ? (
              <Box component="img" src={imagePreview} alt={`${t.name} preview`} loading="lazy" sx={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', display: 'block' }} />
            ) : (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}
              >
                No preview yet
              </Typography>
            )}
          </Box>
          <Stack spacing={0.75}>
            {!!t.description && (
              <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {t.description}
              </Typography>
            )}
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {(t.tags || []).slice(0, 3).map((tag) => <Chip key={tag} label={tag} size="small" />)}
              {(t.tags || []).length > 3 && <Chip size="small" variant="outlined" label={`+${(t.tags || []).length - 3}`} />}
            </Stack>
            {hasGeneratorAssets && (
              <GeneratorAssetsSection
                generatorMeta={generatorMeta}
                generatorArtifacts={generatorArtifacts}
                generatorStatusLabel={generatorStatusLabel}
                needsUserFix={needsUserFix}
                generatorUpdated={generatorUpdated}
                assetHref={assetHref}
              />
            )}
          </Stack>
          <Divider sx={{ mt: 'auto', my: 1 }} />
          <CompanyCardFooter
            t={t}
            type={type}
            fmt={fmt}
            selectedState={selectedState}
            deleting={deleting}
            exporting={exporting}
            setOutputFormats={setOutputFormats}
            handleCardToggle={handleCardToggle}
            onDelete={onDelete}
            onExport={onExport}
            onEditTemplate={onEditTemplate}
            lastEditChipLabel={lastEditChipLabel}
            lastEditChipColor={lastEditChipColor}
            lastEditChipVariant={lastEditChipVariant}
            lastEditInfo={lastEditInfo}
          />
        </CardContent>
      </Box>
    </Card>
  )
}

import Grid from '@mui/material/Grid2'
import {
  alpha,
  Box,
  Button,
  Card,
  CardActionArea,
  CardActions,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import { neutral, secondary } from '@/app/theme'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import { previewFrameSx } from '../../utils/templatesPaneUtils'

export default function SetupTemplateCard({
  template: t,
  selectedState,
  deleting,
  cardData,
  onToggle,
  onDelete,
  onThumbClick,
}) {
  const { previewInfo, htmlPreview, imagePreview, boxClickable, mappingKeyCount, exportHref, type } = cardData

  return (
    <Grid size={{ xs: 12, sm: 6, md: 6 }} key={t.id} sx={{ minWidth: 0 }}>
      <Card
        variant="outlined"
        sx={[
          {
            position: 'relative',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            minHeight: 280,
            transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1)',
          },
          selectedState && {
            borderColor: 'text.secondary',
            boxShadow: `0 0 0 1px ${alpha(secondary.violet[500], 0.28)}`,
          },
        ]}
      >
        <CardActionArea component="div" onClick={() => onToggle(t.id)} sx={{ height: '100%' }}>
          <CardContent sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, height: '100%', flexGrow: 1 }}>
            <Box
              sx={[previewFrameSx, boxClickable && { cursor: 'pointer' }]}
              onClick={(e) => {
                if (htmlPreview) {
                  onThumbClick(e, { url: htmlPreview, key: previewInfo.key, type: 'html' })
                } else if (imagePreview) {
                  onThumbClick(e, { url: imagePreview, key: imagePreview, type: 'image' })
                }
              }}
            >
              {htmlPreview ? (
                <ScaledIframePreview
                  key={previewInfo.key}
                  src={htmlPreview}
                  title={`${t.name} preview`}
                  sx={{ width: '100%', height: '100%' }}
                  frameAspectRatio="210 / 297"
                />
              ) : imagePreview ? (
                <img
                  src={imagePreview}
                  alt={`${t.name} preview`}
                  loading="lazy"
                  style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block', cursor: 'inherit' }}
                />
              ) : (
                <Typography variant="caption" color="text.secondary" sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  No preview yet
                </Typography>
              )}
            </Box>

            {!!t.description && (
              <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {t.description}
              </Typography>
            )}
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {(t.tags || []).slice(0, 4).map((tag) => (
                <Chip key={tag} label={tag} size="small" />
              ))}
              {!!(t.tags || []).slice(4).length && <Chip size="small" label={`+${(t.tags || []).length - 4}`} variant="outlined" />}
            </Stack>
            <Divider sx={{ mt: 'auto', my: 1 }} />
            <Stack spacing={1} alignItems="flex-start">
              <Typography variant="subtitle1" sx={{ fontWeight: 600, lineHeight: 1.2 }} noWrap>
                {t.name}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', rowGap: 1 }}>
                <Chip size="small" label={type} variant="outlined" />
                {mappingKeyCount > 0 && (
                  <Chip
                    size="small"
                    sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                    variant="outlined"
                    label={`${mappingKeyCount} key ${mappingKeyCount === 1 ? 'filter' : 'filters'}`}
                  />
                )}
              </Stack>
            </Stack>
          </CardContent>
        </CardActionArea>
        <CardActions
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
            px: 2,
            pb: 2,
            gap: 1,
            flexWrap: 'wrap',
          }}
        >
          <Button
            size="small"
            variant={selectedState ? 'contained' : 'outlined'}
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              onToggle(t.id)
            }}
            startIcon={selectedState ? <CheckRoundedIcon fontSize="small" /> : undefined}
          >
            {selectedState ? 'Selected' : 'Select'}
          </Button>
          <Stack direction="row" spacing={0.5} alignItems="center">
            <Tooltip title={exportHref ? 'Export template ZIP' : 'Export unavailable in mock mode'}>
              <span>
                <IconButton
                  size="small"
                  component={exportHref ? 'a' : 'button'}
                  href={exportHref || undefined}
                  target={exportHref ? '_blank' : undefined}
                  rel={exportHref ? 'noopener' : undefined}
                  onClick={(e) => {
                    if (!exportHref) e.preventDefault()
                    e.stopPropagation()
                  }}
                >
                  <Inventory2OutlinedIcon fontSize="small" />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Delete template">
              <span>
                <IconButton
                  size="small"
                  sx={{ color: 'text.secondary' }}
                  disabled={deleting === t.id}
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    onDelete(t)
                  }}
                >
                  {deleting === t.id ? (
                    <CircularProgress size={16} color="inherit" />
                  ) : (
                    <DeleteOutlineIcon fontSize="small" />
                  )}
                </IconButton>
              </span>
            </Tooltip>
          </Stack>
        </CardActions>
      </Card>
    </Grid>
  )
}

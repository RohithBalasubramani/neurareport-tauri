/**
 * Brand Kits tab content for the Design page.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Brush as BrushIcon,
  TextFields as FontIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Star as DefaultIcon,
  FileDownload as ExportIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { BrandKitCard, ColorSwatch, ActionButton } from './DesignStyledComponents'
import BrandKitPreview from './BrandKitPreview'

export default function BrandKitsTab({
  brandKits,
  loading,
  openCreateKit,
  openEditKit,
  handleDeleteKit,
  handleSetDefault,
  handleExportKit,
  handleCopyColor,
}) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      {brandKits.map((kit) => (
        <Grid item xs={12} sm={6} md={4} key={kit.id}>
          <BrandKitCard
            isDefault={kit.is_default}
            data-testid={`brand-kit-card-${kit.id}`}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {kit.name}
                </Typography>
                {kit.is_default && (
                  <Chip
                    size="small"
                    label="Default"
                    icon={<DefaultIcon />}
                    sx={{
                      bgcolor: theme.palette.mode === 'dark'
                        ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                      color: 'text.secondary',
                    }}
                  />
                )}
              </Box>
              {kit.description && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
                >
                  {kit.description}
                </Typography>
              )}
              <Box sx={{ display: 'flex', gap: 0.5, mb: 1.5 }}>
                {[kit.primary_color, kit.secondary_color, kit.accent_color, kit.text_color, kit.background_color]
                  .filter(Boolean)
                  .map((c, i) => (
                    <Tooltip key={i} title={c} arrow>
                      <ColorSwatch color={c} size={28} onClick={(e) => { e.stopPropagation(); handleCopyColor(c) }} />
                    </Tooltip>
                  ))}
                {kit.colors?.slice(0, 3).map((c, i) => (
                  <Tooltip key={`extra-${i}`} title={`${c.name}: ${c.hex}`} arrow>
                    <ColorSwatch color={c.hex} size={28} onClick={(e) => { e.stopPropagation(); handleCopyColor(c.hex) }} />
                  </Tooltip>
                ))}
              </Box>
              <BrandKitPreview kit={kit} />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                <FontIcon fontSize="inherit" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                {kit.typography?.font_family || 'Inter'}
                {kit.typography?.heading_font && ` / ${kit.typography.heading_font}`}
              </Typography>
            </CardContent>
            <CardActions sx={{ px: 2, pb: 1.5 }}>
              {!kit.is_default && (
                <Button size="small" onClick={() => handleSetDefault(kit.id)} data-testid="set-default-brand-kit">
                  Set Default
                </Button>
              )}
              <Box sx={{ flex: 1 }} />
              <Tooltip title="Export">
                <IconButton size="small" onClick={() => handleExportKit(kit.id)}>
                  <ExportIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Edit">
                <IconButton size="small" onClick={() => openEditKit(kit)} data-testid="edit-brand-kit">
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton size="small" onClick={() => handleDeleteKit(kit.id)} data-testid="delete-brand-kit" aria-label="Delete brand kit">
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </CardActions>
          </BrandKitCard>
        </Grid>
      ))}
      {brandKits.length === 0 && !loading && (
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <BrushIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">No brand kits yet</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Create a brand kit to define your colors, fonts, and visual identity
            </Typography>
            <ActionButton variant="contained" startIcon={<AddIcon />} onClick={openCreateKit}>
              Create Brand Kit
            </ActionButton>
          </Box>
        </Grid>
      )}
    </Grid>
  )
}

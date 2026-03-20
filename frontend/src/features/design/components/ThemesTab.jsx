/**
 * Themes tab content for the Design page.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Divider,
  Tooltip,
  Stack,
  useTheme,
} from '@mui/material'
import {
  FormatColorFill as ColorIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Check as CheckIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material'
import { ThemeCard, ColorSwatch, ActionButton } from './DesignStyledComponents'

export default function ThemesTab({
  themes,
  loading,
  openCreateTheme,
  handleDeleteTheme,
  handleActivateTheme,
  handleCopyColor,
}) {
  return (
    <Grid container spacing={2}>
      {themes.map((t) => (
        <Grid item xs={12} sm={6} md={4} key={t.id}>
          <ThemeCard isActive={t.is_active} data-testid={`theme-card-${t.id}`}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t.mode === 'dark' ? (
                  <DarkModeIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                ) : (
                  <LightModeIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                )}
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {t.name}
                </Typography>
              </Box>
              <Stack direction="row" spacing={0.5} alignItems="center">
                {t.is_active && (
                  <Chip size="small" label="Active" icon={<CheckIcon />} color="default" />
                )}
              </Stack>
            </Box>

            {t.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                {t.description}
              </Typography>
            )}

            <Box sx={{ display: 'flex', gap: 0.5, mb: 1.5 }}>
              {Object.entries(t.colors || {}).map(([name, hex]) => (
                <Tooltip key={name} title={`${name}: ${hex}`} arrow>
                  <ColorSwatch
                    color={hex}
                    size={28}
                    onClick={() => handleCopyColor(hex)}
                  />
                </Tooltip>
              ))}
              {(!t.colors || Object.keys(t.colors).length === 0) && (
                <Typography variant="caption" color="text.disabled">
                  No colors defined
                </Typography>
              )}
            </Box>

            <Chip
              label={t.mode || 'light'}
              size="small"
              variant="outlined"
              sx={{ mb: 1.5 }}
            />

            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 0.5 }}>
              {!t.is_active ? (
                <Button size="small" onClick={() => handleActivateTheme(t.id)} data-testid="activate-theme">
                  Activate
                </Button>
              ) : (
                <Box />
              )}
              <IconButton
                size="small"
                onClick={() => handleDeleteTheme(t.id)}
                data-testid="delete-theme"
                aria-label="Delete theme"
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          </ThemeCard>
        </Grid>
      ))}

      {themes.length === 0 && !loading && (
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <ColorIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No themes yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Create themes to switch between visual styles for your reports
            </Typography>
            <ActionButton variant="contained" startIcon={<AddIcon />} onClick={openCreateTheme}>
              Create Theme
            </ActionButton>
          </Box>
        </Grid>
      )}
    </Grid>
  )
}

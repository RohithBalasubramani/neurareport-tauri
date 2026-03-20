/**
 * Design Page Container
 * Brand kit and theme management interface with color tools and typography explorer.
 */
import React from 'react'
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Stack,
  useTheme,
} from '@mui/material'
import {
  Palette as PaletteIcon,
  Brush as BrushIcon,
  FormatColorFill as ColorIcon,
  TextFields as FontIcon,
  Add as AddIcon,
  FileUpload as ImportIcon,
} from '@mui/icons-material'
import { useDesignPage } from '../hooks/useDesignPage'
import { PageContainer, Header, ContentArea, ActionButton } from '../components/DesignStyledComponents'
import BrandKitsTab from '../components/BrandKitsTab'
import ThemesTab from '../components/ThemesTab'
import ColorToolsTab from '../components/ColorToolsTab'
import TypographyTab from '../components/TypographyTab'
import BrandKitDialog from '../components/BrandKitDialog'
import ThemeDialog from '../components/ThemeDialog'

export default function DesignPageContainer() {
  const theme = useTheme()
  const state = useDesignPage()

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PaletteIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Brand Kit
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Colors, fonts, themes & accessibility tools
              </Typography>
            </Box>
          </Box>
          <Stack direction="row" spacing={1}>
            {state.activeTab === 0 && (
              <>
                <input
                  type="file"
                  ref={state.importRef}
                  accept=".json"
                  onChange={state.handleImportKit}
                  style={{ display: 'none' }}
                />
                <ActionButton
                  variant="outlined"
                  size="small"
                  startIcon={<ImportIcon />}
                  onClick={() => state.importRef.current?.click()}
                >
                  Import
                </ActionButton>
                <ActionButton
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={state.openCreateKit}
                  data-testid="design-create-button"
                >
                  New Brand Kit
                </ActionButton>
              </>
            )}
            {state.activeTab === 1 && (
              <ActionButton
                variant="contained"
                startIcon={<AddIcon />}
                onClick={state.openCreateTheme}
                data-testid="design-create-theme-button"
              >
                New Theme
              </ActionButton>
            )}
          </Stack>
        </Box>
      </Header>

      <ContentArea>
        <Tabs
          value={state.activeTab}
          onChange={(_, v) => state.setActiveTab(v)}
          sx={{ mb: 3 }}
          data-testid="design-tabs"
        >
          <Tab icon={<BrushIcon />} label="Brand Kits" iconPosition="start" data-testid="design-tab-brand-kits" />
          <Tab icon={<ColorIcon />} label="Themes" iconPosition="start" data-testid="design-tab-themes" />
          <Tab icon={<PaletteIcon />} label="Color Tools" iconPosition="start" data-testid="design-tab-color-tools" />
          <Tab icon={<FontIcon />} label="Typography" iconPosition="start" data-testid="design-tab-typography" />
        </Tabs>

        {state.error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => {}}>
            {state.error}
          </Alert>
        )}

        {state.activeTab === 0 && (
          <BrandKitsTab
            brandKits={state.brandKits}
            loading={state.loading}
            openCreateKit={state.openCreateKit}
            openEditKit={state.openEditKit}
            handleDeleteKit={state.handleDeleteKit}
            handleSetDefault={state.handleSetDefault}
            handleExportKit={state.handleExportKit}
            handleCopyColor={state.handleCopyColor}
          />
        )}

        {state.activeTab === 1 && (
          <ThemesTab
            themes={state.themes}
            loading={state.loading}
            openCreateTheme={state.openCreateTheme}
            handleDeleteTheme={state.handleDeleteTheme}
            handleActivateTheme={state.handleActivateTheme}
            handleCopyColor={state.handleCopyColor}
          />
        )}

        {state.activeTab === 2 && (
          <ColorToolsTab
            loading={state.loading}
            baseColor={state.baseColor}
            setBaseColor={state.setBaseColor}
            colorScheme={state.colorScheme}
            setColorScheme={state.setColorScheme}
            generatedPalette={state.generatedPalette}
            contrastFg={state.contrastFg}
            setContrastFg={state.setContrastFg}
            contrastBg={state.contrastBg}
            setContrastBg={state.setContrastBg}
            contrastResult={state.contrastResult}
            a11yBg={state.a11yBg}
            setA11yBg={state.setA11yBg}
            a11ySuggestions={state.a11ySuggestions}
            handleGeneratePalette={state.handleGeneratePalette}
            handleCheckContrast={state.handleCheckContrast}
            handleSuggestA11y={state.handleSuggestA11y}
            handleCopyColor={state.handleCopyColor}
          />
        )}

        {state.activeTab === 3 && (
          <TypographyTab
            selectedFont={state.selectedFont}
            fontPairings={state.fontPairings}
            fontFilter={state.fontFilter}
            setFontFilter={state.setFontFilter}
            filteredFonts={state.filteredFonts}
            handleGetPairings={state.handleGetPairings}
          />
        )}

        {state.loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        )}
      </ContentArea>

      <BrandKitDialog
        open={state.kitDialogOpen}
        onClose={() => state.setKitDialogOpen(false)}
        mode={state.kitDialogMode}
        kitForm={state.kitForm}
        setKitForm={state.setKitForm}
        kitFormExpanded={state.kitFormExpanded}
        setKitFormExpanded={state.setKitFormExpanded}
        onSave={state.handleSaveKit}
        fonts={state.fonts}
      />

      <ThemeDialog
        open={state.themeDialogOpen}
        onClose={() => state.setThemeDialogOpen(false)}
        themeForm={state.themeForm}
        setThemeForm={state.setThemeForm}
        onSave={state.handleSaveTheme}
      />
    </PageContainer>
  )
}

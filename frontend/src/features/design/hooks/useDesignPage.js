/**
 * Custom hook: all state, effects, and handlers for the Design page.
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { primary } from '@/app/theme'
import useDesignStore from '@/stores/designStore'
import useSharedData from '@/hooks/useSharedData'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { EMPTY_KIT_FORM, EMPTY_THEME_FORM } from '../components/DesignStyledComponents'

export function useDesignPage() {
  const toast = useToast()
  const { execute } = useInteraction()
  const { templates } = useSharedData()
  const importRef = useRef(null)
  const {
    brandKits,
    themes,
    fonts,
    loading,
    error,
    fetchBrandKits,
    fetchThemes,
    fetchFonts,
    createBrandKit,
    updateBrandKit,
    deleteBrandKit,
    setDefaultBrandKit,
    createTheme,
    deleteTheme,
    setActiveTheme,
    generateColorPalette,
    getColorContrast,
    suggestAccessibleColors,
    getFontPairings,
    exportBrandKit,
    importBrandKit,
    reset,
  } = useDesignStore()

  // --- Tab state ---
  const [activeTab, setActiveTab] = useState(0)

  // --- Brand Kit dialog state ---
  const [kitDialogOpen, setKitDialogOpen] = useState(false)
  const [kitDialogMode, setKitDialogMode] = useState('create')
  const [editingKitId, setEditingKitId] = useState(null)
  const [kitForm, setKitForm] = useState({ ...EMPTY_KIT_FORM })
  const [kitFormExpanded, setKitFormExpanded] = useState(false)

  // --- Theme dialog state ---
  const [themeDialogOpen, setThemeDialogOpen] = useState(false)
  const [themeForm, setThemeForm] = useState({ ...EMPTY_THEME_FORM })

  // --- Color tools state ---
  const [baseColor, setBaseColor] = useState(primary[500])
  const [colorScheme, setColorScheme] = useState('complementary')
  const [generatedPalette, setGeneratedPalette] = useState(null)
  const [contrastFg, setContrastFg] = useState('#000000')
  const [contrastBg, setContrastBg] = useState('#ffffff')
  const [contrastResult, setContrastResult] = useState(null)
  const [a11yBg, setA11yBg] = useState('#1976d2')
  const [a11ySuggestions, setA11ySuggestions] = useState(null)

  // --- Typography state ---
  const [selectedFont, setSelectedFont] = useState('')
  const [fontPairings, setFontPairings] = useState(null)
  const [fontFilter, setFontFilter] = useState('')

  useEffect(() => {
    fetchBrandKits()
    fetchThemes()
    fetchFonts()
    return () => reset()
  }, [fetchBrandKits, fetchFonts, fetchThemes, reset])

  // =========================================================================
  // BRAND KIT HANDLERS
  // =========================================================================

  const openCreateKit = () => {
    setKitDialogMode('create')
    setEditingKitId(null)
    setKitForm({ ...EMPTY_KIT_FORM })
    setKitFormExpanded(false)
    setKitDialogOpen(true)
  }

  const openEditKit = (kit) => {
    setKitDialogMode('edit')
    setEditingKitId(kit.id)
    setKitForm({
      name: kit.name || '',
      description: kit.description || '',
      primary_color: kit.primary_color || '#1976d2',
      secondary_color: kit.secondary_color || '#dc004e',
      accent_color: kit.accent_color || '#ff9800',
      text_color: kit.text_color || '#333333',
      background_color: kit.background_color || '#ffffff',
      font_family: kit.typography?.font_family || 'Inter',
      heading_font: kit.typography?.heading_font || '',
      body_font: kit.typography?.body_font || '',
    })
    setKitFormExpanded(true)
    setKitDialogOpen(true)
  }

  const handleSaveKit = useCallback(async () => {
    if (!kitForm.name.trim()) return

    const payload = {
      name: kitForm.name,
      description: kitForm.description || undefined,
      primary_color: kitForm.primary_color,
      secondary_color: kitForm.secondary_color,
      accent_color: kitForm.accent_color,
      text_color: kitForm.text_color,
      background_color: kitForm.background_color,
      typography: {
        font_family: kitForm.font_family || 'Inter',
        heading_font: kitForm.heading_font || undefined,
        body_font: kitForm.body_font || undefined,
      },
    }

    const isEdit = kitDialogMode === 'edit'
    return execute({
      type: isEdit ? InteractionType.UPDATE : InteractionType.CREATE,
      label: isEdit ? 'Update brand kit' : 'Create brand kit',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'design', name: kitForm.name },
      action: async () => {
        if (isEdit) {
          await updateBrandKit(editingKitId, payload)
          toast.show('Brand kit updated', 'success')
        } else {
          await createBrandKit(payload)
          toast.show('Brand kit created', 'success')
        }
        setKitDialogOpen(false)
      },
    })
  }, [kitForm, kitDialogMode, editingKitId, createBrandKit, updateBrandKit, execute, toast])

  const handleDeleteKit = useCallback(
    async (kitId) => {
      return execute({
        type: InteractionType.DELETE,
        label: 'Delete brand kit',
        reversibility: Reversibility.SYSTEM_MANAGED,
        intent: { source: 'design', brandKitId: kitId },
        action: async () => {
          await deleteBrandKit(kitId)
          toast.show('Brand kit deleted', 'success')
        },
      })
    },
    [deleteBrandKit, execute, toast],
  )

  const handleSetDefault = useCallback(
    async (kitId) => {
      return execute({
        type: InteractionType.UPDATE,
        label: 'Set default brand kit',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        intent: { source: 'design', brandKitId: kitId },
        action: async () => {
          await setDefaultBrandKit(kitId)
          toast.show('Default brand kit updated', 'success')
        },
      })
    },
    [execute, setDefaultBrandKit, toast],
  )

  const handleExportKit = useCallback(
    async (kitId) => {
      const data = await exportBrandKit(kitId)
      if (data) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `brand-kit-${kitId}.json`
        a.click()
        URL.revokeObjectURL(url)
        toast.show('Brand kit exported', 'success')
      }
    },
    [exportBrandKit, toast],
  )

  const handleImportKit = useCallback(
    async (evt) => {
      const file = evt.target.files?.[0]
      if (!file) return
      try {
        const text = await file.text()
        const data = JSON.parse(text)
        const kitData = data.brand_kit || data
        await execute({
          type: InteractionType.CREATE,
          label: 'Import brand kit',
          reversibility: Reversibility.SYSTEM_MANAGED,
          intent: { source: 'design', action: 'import' },
          action: async () => {
            await importBrandKit(kitData)
            toast.show('Brand kit imported', 'success')
          },
        })
      } catch {
        toast.show('Invalid brand kit file', 'error')
      }
      evt.target.value = ''
    },
    [execute, importBrandKit, toast],
  )

  // =========================================================================
  // THEME HANDLERS
  // =========================================================================

  const openCreateTheme = () => {
    setThemeForm({ ...EMPTY_THEME_FORM })
    setThemeDialogOpen(true)
  }

  const handleSaveTheme = useCallback(async () => {
    if (!themeForm.name.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Create theme',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'design', name: themeForm.name },
      action: async () => {
        await createTheme({
          name: themeForm.name,
          description: themeForm.description || undefined,
          mode: themeForm.mode,
          colors: {
            primary: themeForm.primary,
            secondary: themeForm.secondary,
            background: themeForm.background,
            surface: themeForm.surface,
            text: themeForm.text,
          },
        })
        toast.show('Theme created', 'success')
        setThemeDialogOpen(false)
      },
    })
  }, [createTheme, execute, themeForm, toast])

  const handleDeleteTheme = useCallback(
    async (themeId) => {
      return execute({
        type: InteractionType.DELETE,
        label: 'Delete theme',
        reversibility: Reversibility.SYSTEM_MANAGED,
        intent: { source: 'design', themeId },
        action: async () => {
          await deleteTheme(themeId)
          toast.show('Theme deleted', 'success')
        },
      })
    },
    [deleteTheme, execute, toast],
  )

  const handleActivateTheme = useCallback(
    async (themeId) => {
      return execute({
        type: InteractionType.UPDATE,
        label: 'Activate theme',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        intent: { source: 'design', themeId },
        action: async () => {
          await setActiveTheme(themeId)
          toast.show('Theme activated', 'success')
        },
      })
    },
    [execute, setActiveTheme, toast],
  )

  // =========================================================================
  // COLOR TOOL HANDLERS
  // =========================================================================

  const handleGeneratePalette = useCallback(async () => {
    return execute({
      type: InteractionType.GENERATE,
      label: 'Generate color palette',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { source: 'design', baseColor, colorScheme, action: 'generate_palette' },
      action: async () => {
        const palette = await generateColorPalette(baseColor, colorScheme)
        if (palette) {
          setGeneratedPalette(palette)
          toast.show('Palette generated', 'success')
        }
        return palette
      },
    })
  }, [baseColor, colorScheme, generateColorPalette, toast, execute])

  const handleCheckContrast = useCallback(async () => {
    const result = await getColorContrast(contrastFg, contrastBg)
    if (result) setContrastResult(result)
  }, [contrastFg, contrastBg, getColorContrast])

  const handleSuggestA11y = useCallback(async () => {
    const result = await suggestAccessibleColors(a11yBg)
    if (result) setA11ySuggestions(result)
  }, [a11yBg, suggestAccessibleColors])

  // =========================================================================
  // TYPOGRAPHY HANDLERS
  // =========================================================================

  const handleGetPairings = useCallback(
    async (fontName) => {
      setSelectedFont(fontName)
      const result = await getFontPairings(fontName)
      if (result) setFontPairings(result)
    },
    [getFontPairings],
  )

  const handleCopyColor = (color) => {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(color)
    } else {
      const ta = Object.assign(document.createElement('textarea'), { value: color, style: 'position:fixed;opacity:0' })
      document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove()
    }
    toast.show(`Copied ${color}`, 'success')
  }

  const filteredFonts = fonts.filter(
    (f) =>
      !fontFilter ||
      f.name.toLowerCase().includes(fontFilter.toLowerCase()) ||
      f.category.toLowerCase().includes(fontFilter.toLowerCase()),
  )

  return {
    // Store data
    brandKits,
    themes,
    fonts,
    loading,
    error,
    templates,
    importRef,

    // Tab
    activeTab,
    setActiveTab,

    // Brand kit dialog
    kitDialogOpen,
    setKitDialogOpen,
    kitDialogMode,
    kitForm,
    setKitForm,
    kitFormExpanded,
    setKitFormExpanded,
    openCreateKit,
    openEditKit,
    handleSaveKit,
    handleDeleteKit,
    handleSetDefault,
    handleExportKit,
    handleImportKit,

    // Theme dialog
    themeDialogOpen,
    setThemeDialogOpen,
    themeForm,
    setThemeForm,
    openCreateTheme,
    handleSaveTheme,
    handleDeleteTheme,
    handleActivateTheme,

    // Color tools
    baseColor,
    setBaseColor,
    colorScheme,
    setColorScheme,
    generatedPalette,
    contrastFg,
    setContrastFg,
    contrastBg,
    setContrastBg,
    contrastResult,
    a11yBg,
    setA11yBg,
    a11ySuggestions,
    handleGeneratePalette,
    handleCheckContrast,
    handleSuggestA11y,
    handleCopyColor,

    // Typography
    selectedFont,
    fontPairings,
    fontFilter,
    setFontFilter,
    filteredFonts,
    handleGetPairings,
  }
}

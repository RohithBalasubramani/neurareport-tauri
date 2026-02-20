/**
 * Design Store - Zustand store for brand kits, themes, and design system.
 */
import { create } from 'zustand';
import * as designApi from '../api/design';

const useDesignStore = create((set, get) => ({
  // State
  brandKits: [],
  themes: [],
  currentBrandKit: null,
  currentTheme: null,
  defaultBrandKit: null,
  activeTheme: null,
  fonts: [],
  loading: false,
  error: null,

  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Brand Kits
  createBrandKit: async (data) => {
    set({ loading: true, error: null });
    try {
      const brandKit = await designApi.createBrandKit(data);
      set((state) => ({
        brandKits: [brandKit, ...state.brandKits],
        currentBrandKit: brandKit,
        loading: false,
      }));
      return brandKit;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchBrandKits: async () => {
    set({ loading: true, error: null });
    try {
      const brandKits = await designApi.listBrandKits();
      const defaultKit = brandKits.find((k) => k.is_default);
      set({
        brandKits: brandKits || [],
        defaultBrandKit: defaultKit || null,
        loading: false
      });
      return brandKits;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getBrandKit: async (brandKitId) => {
    set({ loading: true, error: null });
    try {
      const brandKit = await designApi.getBrandKit(brandKitId);
      set({ currentBrandKit: brandKit, loading: false });
      return brandKit;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  updateBrandKit: async (brandKitId, data) => {
    set({ loading: true, error: null });
    try {
      const brandKit = await designApi.updateBrandKit(brandKitId, data);
      set((state) => ({
        brandKits: state.brandKits.map((k) => (k.id === brandKitId ? brandKit : k)),
        currentBrandKit: state.currentBrandKit?.id === brandKitId ? brandKit : state.currentBrandKit,
        loading: false,
      }));
      return brandKit;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteBrandKit: async (brandKitId) => {
    set({ loading: true, error: null });
    try {
      await designApi.deleteBrandKit(brandKitId);
      set((state) => ({
        brandKits: state.brandKits.filter((k) => k.id !== brandKitId),
        currentBrandKit: state.currentBrandKit?.id === brandKitId ? null : state.currentBrandKit,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  setDefaultBrandKit: async (brandKitId) => {
    set({ loading: true, error: null });
    try {
      await designApi.setDefaultBrandKit(brandKitId);
      set((state) => {
        const updatedBrandKits = state.brandKits.map((k) => ({
          ...k,
          is_default: k.id === brandKitId,
        }));
        return {
          brandKits: updatedBrandKits,
          defaultBrandKit: updatedBrandKits.find((k) => k.id === brandKitId) || null,
          loading: false,
        };
      });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  applyBrandKit: async (brandKitId, documentId) => {
    set({ loading: true, error: null });
    try {
      const result = await designApi.applyBrandKit(brandKitId, documentId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Themes
  createTheme: async (data) => {
    set({ loading: true, error: null });
    try {
      const theme = await designApi.createTheme(data);
      set((state) => ({
        themes: [theme, ...state.themes],
        currentTheme: theme,
        loading: false,
      }));
      return theme;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  fetchThemes: async () => {
    set({ loading: true, error: null });
    try {
      const themes = await designApi.listThemes();
      const active = themes.find((t) => t.is_active);
      set({
        themes: themes || [],
        activeTheme: active || null,
        loading: false
      });
      return themes;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  getTheme: async (themeId) => {
    set({ loading: true, error: null });
    try {
      const theme = await designApi.getTheme(themeId);
      set({ currentTheme: theme, loading: false });
      return theme;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  updateTheme: async (themeId, data) => {
    set({ loading: true, error: null });
    try {
      const theme = await designApi.updateTheme(themeId, data);
      set((state) => ({
        themes: state.themes.map((t) => (t.id === themeId ? theme : t)),
        currentTheme: state.currentTheme?.id === themeId ? theme : state.currentTheme,
        loading: false,
      }));
      return theme;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  deleteTheme: async (themeId) => {
    set({ loading: true, error: null });
    try {
      await designApi.deleteTheme(themeId);
      set((state) => ({
        themes: state.themes.filter((t) => t.id !== themeId),
        currentTheme: state.currentTheme?.id === themeId ? null : state.currentTheme,
        loading: false,
      }));
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  setActiveTheme: async (themeId) => {
    set({ loading: true, error: null });
    try {
      await designApi.setActiveTheme(themeId);
      set((state) => {
        const updatedThemes = state.themes.map((t) => ({
          ...t,
          is_active: t.id === themeId,
        }));
        return {
          themes: updatedThemes,
          activeTheme: updatedThemes.find((t) => t.id === themeId) || null,
          loading: false,
        };
      });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Color Palettes
  generateColorPalette: async (baseColor, scheme = 'complementary') => {
    set({ loading: true, error: null });
    try {
      const palette = await designApi.generateColorPalette(baseColor, scheme);
      set({ loading: false });
      return palette;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Typography
  fetchFonts: async () => {
    try {
      const fonts = await designApi.listFonts();
      set({ fonts: fonts || [] });
      return fonts;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  getFontPairings: async (primaryFont) => {
    try {
      const pairings = await designApi.getFontPairings(primaryFont);
      return pairings;
    } catch (err) {
      set({ error: err.message });
      return [];
    }
  },

  // Assets
  uploadLogo: async (file, brandKitId) => {
    set({ loading: true, error: null });
    try {
      const result = await designApi.uploadLogo(file, brandKitId);
      // Refresh brand kit to get updated logo
      await get().getBrandKit(brandKitId);
      set({ loading: false });
      return result;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Accessibility
  getColorContrast: async (foreground, background) => {
    try {
      const result = await designApi.getColorContrast(foreground, background);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  suggestAccessibleColors: async (baseColor, options = {}) => {
    try {
      const result = await designApi.suggestAccessibleColors(baseColor, options);
      return result;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  // Assets
  fetchAssets: async (brandKitId = null) => {
    set({ loading: true, error: null });
    try {
      const assets = await designApi.listAssets(brandKitId);
      set({ loading: false });
      return assets;
    } catch (err) {
      set({ error: err.message, loading: false });
      return [];
    }
  },

  deleteAsset: async (assetId) => {
    set({ loading: true, error: null });
    try {
      await designApi.deleteAsset(assetId);
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.message, loading: false });
      return false;
    }
  },

  // Export/Import
  exportBrandKit: async (brandKitId, format = 'json') => {
    try {
      const data = await designApi.exportBrandKit(brandKitId, format);
      return data;
    } catch (err) {
      set({ error: err.message });
      return null;
    }
  },

  importBrandKit: async (data) => {
    set({ loading: true, error: null });
    try {
      const brandKit = await designApi.importBrandKit(data);
      set((state) => ({
        brandKits: [brandKit, ...state.brandKits],
        loading: false,
      }));
      return brandKit;
    } catch (err) {
      set({ error: err.message, loading: false });
      return null;
    }
  },

  // Reset
  reset: () => set({
    currentBrandKit: null,
    currentTheme: null,
    error: null,
  }),
}));

export default useDesignStore;

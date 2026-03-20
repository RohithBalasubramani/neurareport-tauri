import { create } from 'zustand'

export const SUPPORTED_THEME_NAMES = ['light']
export const DEFAULT_THEME_NAME = 'light'

const STORAGE_KEY = 'neurareport-theme-name'

function isSupportedThemeName(themeName) {
  return SUPPORTED_THEME_NAMES.includes(themeName)
}

function loadThemeName() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw && isSupportedThemeName(raw)) {
      return raw
    }
  } catch {
    // localStorage may be unavailable
  }
  return DEFAULT_THEME_NAME
}

function persistThemeName(themeName) {
  try {
    localStorage.setItem(STORAGE_KEY, themeName)
  } catch {
    // Ignore storage failures
  }
}

function applyThemeName(themeName) {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', themeName)
}

export const useThemeStore = create((set) => ({
  themeName: loadThemeName(),

  setThemeName: (themeName) => {
    if (!isSupportedThemeName(themeName)) return
    applyThemeName(themeName)
    persistThemeName(themeName)
    set({ themeName })
  },

  loadPersistedTheme: () => {
    const themeName = loadThemeName()
    applyThemeName(themeName)
    set({ themeName })
    return themeName
  },
}))

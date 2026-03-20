/**
 * Theme barrel — exports the complete design system foundation.
 */
export { ThemeProvider } from './ThemeProvider.jsx'
export { createAppMuiTheme } from './muiTheme.js'
export { useThemeStore, SUPPORTED_THEME_NAMES, DEFAULT_THEME_NAME } from './useThemeStore.js'
export { REF_TOKENS, DEFAULT_SYS_TOKENS, getThemeTokens } from './tokens.js'

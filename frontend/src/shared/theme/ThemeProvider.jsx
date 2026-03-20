import { useMemo } from 'react'
import { CssBaseline, ThemeProvider as MuiThemeProvider } from '@mui/material'

import { createAppMuiTheme } from './muiTheme.js'
import { useThemeStore } from './useThemeStore.js'

export function ThemeProvider({ children }) {
  const themeName = useThemeStore((state) => state.themeName)
  const muiTheme = useMemo(() => createAppMuiTheme(themeName), [themeName])

  return (
    <MuiThemeProvider theme={muiTheme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  )
}

export const PREFERENCES_STORAGE_KEY = 'neurareport_preferences'

export const readPreferences = () => {
  if (typeof window === 'undefined') return {}
  try {
    const stored = window.localStorage.getItem(PREFERENCES_STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

export const emitPreferencesChanged = (prefs) => {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent('neura:preferences-changed', { detail: prefs }))
}

export const subscribePreferences = (callback) => {
  if (typeof window === 'undefined') return () => {}

  const handler = (event) => {
    if (event?.type === 'storage') {
      if (event.key !== PREFERENCES_STORAGE_KEY) return
      callback(readPreferences())
      return
    }
    if (event?.type === 'neura:preferences-changed') {
      callback(event.detail || readPreferences())
    }
  }

  window.addEventListener('storage', handler)
  window.addEventListener('neura:preferences-changed', handler)

  return () => {
    window.removeEventListener('storage', handler)
    window.removeEventListener('neura:preferences-changed', handler)
  }
}

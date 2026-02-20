const PREF_KEY = 'neurareport_preferences'

export function shouldConfirmDelete() {
  if (typeof window === 'undefined') return true
  try {
    const raw = window.localStorage.getItem(PREF_KEY)
    if (!raw) return true
    const parsed = JSON.parse(raw)
    return parsed?.confirmDelete ?? true
  } catch {
    return true
  }
}

export function confirmDelete(message) {
  if (!shouldConfirmDelete()) return true
  if (typeof window === 'undefined') return true
  return window.confirm(message)
}

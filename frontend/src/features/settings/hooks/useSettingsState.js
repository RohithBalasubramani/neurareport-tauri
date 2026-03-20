/**
 * Custom hook: all Settings page state, effects, and handlers.
 * Hook files are exempt from the 200-line limit.
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import * as api from '@/api/client'
import {
  PREFERENCES_STORAGE_KEY,
  readPreferences,
  emitPreferencesChanged,
} from '@/utils/preferences'

// =============================================================================
// HELPERS
// =============================================================================

function getPreferences() {
  return readPreferences()
}

function savePreferences(prefs) {
  try {
    localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(prefs))
    emitPreferencesChanged(prefs)
    return { success: true }
  } catch (err) {
    return { success: false, error: err.message || 'Storage quota exceeded or unavailable' }
  }
}

// =============================================================================
// CONSTANTS
// =============================================================================

export const TIMEZONE_OPTIONS = [
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Phoenix', label: 'Arizona (no DST)' },
  { value: 'America/Anchorage', label: 'Alaska Time' },
  { value: 'Pacific/Honolulu', label: 'Hawaii Time' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Central European Time' },
  { value: 'Europe/Berlin', label: 'Berlin' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time' },
  { value: 'Asia/Shanghai', label: 'China Standard Time' },
  { value: 'Asia/Kolkata', label: 'India Standard Time' },
  { value: 'Asia/Dubai', label: 'Gulf Standard Time' },
  { value: 'Australia/Sydney', label: 'Australian Eastern Time' },
  { value: 'UTC', label: 'UTC' },
]

export const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Español (Spanish)' },
  { value: 'fr', label: 'Français (French)' },
  { value: 'de', label: 'Deutsch (German)' },
  { value: 'pt', label: 'Português (Portuguese)' },
  { value: 'zh', label: '中文 (Chinese)' },
  { value: 'ja', label: '日本語 (Japanese)' },
  { value: 'ko', label: '한국어 (Korean)' },
]

// =============================================================================
// MAIN HOOK
// =============================================================================

export function useSettingsState() {
  const toast = useToast()
  const { execute } = useInteraction()
  const setDemoMode = useAppStore((s) => s.setDemoMode)
  const demoMode = useAppStore((s) => s.demoMode)

  // Health / system state
  const [loading, setLoading] = useState(true)
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)
  const [tokenUsage, setTokenUsage] = useState(null)
  const [exporting, setExporting] = useState(false)

  // Preferences
  const [preferences, setPreferences] = useState(getPreferences)
  const lastPrefChangeRef = useRef(0)

  // Personal settings
  const [selectedTimezone, setSelectedTimezone] = useState(
    Intl.DateTimeFormat().resolvedOptions().timeZone
  )
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [showTwoFactorSetup, setShowTwoFactorSetup] = useState(false)

  // SMTP settings
  const [smtp, setSmtp] = useState({ host: '', port: 587, username: '', password: '', sender: '', use_tls: true })
  const [smtpLoading, setSmtpLoading] = useState(false)
  const [smtpTesting, setSmtpTesting] = useState(false)
  const [showSmtpPassword, setShowSmtpPassword] = useState(false)

  // ---------------------------------------------------------------------------
  // Health fetch
  // ---------------------------------------------------------------------------
  const fetchHealth = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [healthData, usageData] = await Promise.all([
        api.getSystemHealth(),
        api.getTokenUsage().catch(() => null),
      ])
      setHealth(healthData)
      setTokenUsage(usageData?.usage || null)
    } catch (err) {
      setError(err.message || 'Failed to fetch system health')
    } finally {
      setLoading(false)
    }
  }, [])

  // ---------------------------------------------------------------------------
  // Preferences load
  // ---------------------------------------------------------------------------
  const loadPreferences = useCallback(async () => {
    const startedAt = Date.now()
    try {
      const data = await api.getUserPreferences()
      if (lastPrefChangeRef.current > startedAt) return
      const nextPrefs = data?.preferences || {}
      setPreferences(nextPrefs)
      savePreferences(nextPrefs)

      if (typeof nextPrefs.demoMode === 'boolean') setDemoMode(nextPrefs.demoMode)
      if (nextPrefs.timezone) setSelectedTimezone(nextPrefs.timezone)
      if (nextPrefs.language) setSelectedLanguage(nextPrefs.language)
      if (typeof nextPrefs.twoFactorEnabled === 'boolean') setTwoFactorEnabled(nextPrefs.twoFactorEnabled)
    } catch (err) {
      toast.show(err.message || 'Failed to load preferences', 'warning')
    }
  }, [setDemoMode, toast])

  // ---------------------------------------------------------------------------
  // Export config
  // ---------------------------------------------------------------------------
  const handleExportConfig = useCallback(async () => {
    setExporting(true)
    try {
      const data = await api.exportConfiguration()
      const blob = new Blob([JSON.stringify(data.config || data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `neurareport-config-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      toast.show('Configuration exported successfully', 'success')
    } catch (err) {
      toast.show(err.message || 'Failed to export configuration', 'error')
    } finally {
      setExporting(false)
    }
  }, [toast])

  // ---------------------------------------------------------------------------
  // Init effects
  // ---------------------------------------------------------------------------
  useEffect(() => {
    fetchHealth()
    loadPreferences()
  }, [fetchHealth, loadPreferences])

  // ---------------------------------------------------------------------------
  // Preference toggle handler
  // ---------------------------------------------------------------------------
  const handlePrefChange = useCallback((key) => async (event) => {
    const nextValue = event.target.checked
    const nextPrefs = { ...preferences, [key]: nextValue }
    lastPrefChangeRef.current = Date.now()
    setPreferences(nextPrefs)
    const cacheResult = savePreferences(nextPrefs)
    if (!cacheResult.success) {
      toast.show(`Failed to cache preferences locally: ${cacheResult.error}`, 'warning')
    }
    await execute({
      type: InteractionType.UPDATE,
      label: 'Update preference',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { preferenceKey: key, action: 'update_preference' },
      action: async () => {
        try {
          const result = await api.setUserPreference(key, nextValue)
          if (result?.preferences) {
            const merged = { ...nextPrefs, ...result.preferences }
            setPreferences(merged)
            savePreferences(merged)
          }
          toast.show('Preferences saved', 'success')
          return result
        } catch (err) {
          toast.show(err.message || 'Failed to save preferences', 'error')
          throw err
        }
      },
    })
  }, [preferences, toast, execute])

  // ---------------------------------------------------------------------------
  // Timezone handler
  // ---------------------------------------------------------------------------
  const handleTimezoneChange = useCallback(async (event) => {
    const value = event.target.value
    setSelectedTimezone(value)
    const nextPrefs = { ...preferences, timezone: value }
    lastPrefChangeRef.current = Date.now()
    setPreferences(nextPrefs)
    savePreferences(nextPrefs)
    await execute({
      type: InteractionType.UPDATE,
      label: 'Update timezone',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      intent: { preferenceKey: 'timezone', action: 'update_timezone' },
      action: async () => {
        try {
          await api.setUserPreference('timezone', value)
          toast.show('Timezone updated', 'success')
        } catch (err) {
          toast.show(err.message || 'Failed to save timezone', 'error')
        }
      },
    })
  }, [preferences, toast, execute])

  // ---------------------------------------------------------------------------
  // Language handler
  // ---------------------------------------------------------------------------
  const handleLanguageChange = useCallback(async (event) => {
    const value = event.target.value
    setSelectedLanguage(value)
    const nextPrefs = { ...preferences, language: value }
    lastPrefChangeRef.current = Date.now()
    setPreferences(nextPrefs)
    savePreferences(nextPrefs)
    await execute({
      type: InteractionType.UPDATE,
      label: 'Update language',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      intent: { preferenceKey: 'language', action: 'update_language' },
      action: async () => {
        try {
          await api.setUserPreference('language', value)
          toast.show('Language updated. Some changes may require a page refresh.', 'success')
        } catch (err) {
          toast.show(err.message || 'Failed to save language', 'error')
        }
      },
    })
  }, [preferences, toast, execute])

  // ---------------------------------------------------------------------------
  // 2FA handler
  // ---------------------------------------------------------------------------
  const handleTwoFactorToggle = useCallback(async (event) => {
    const enabled = event.target.checked
    if (enabled) {
      setShowTwoFactorSetup(true)
    } else {
      await execute({
        type: InteractionType.UPDATE,
        label: 'Disable two-factor authentication',
        reversibility: Reversibility.PARTIALLY_REVERSIBLE,
        intent: { action: 'disable_2fa' },
        action: async () => {
          try {
            await api.setUserPreference('twoFactorEnabled', false)
            setTwoFactorEnabled(false)
            toast.show('Two-factor authentication disabled', 'success')
          } catch (err) {
            toast.show(err.message || 'Failed to disable 2FA', 'error')
          }
        },
      })
    }
  }, [execute, toast])

  // ---------------------------------------------------------------------------
  // Demo mode handler
  // ---------------------------------------------------------------------------
  const handleDemoModeChange = useCallback(async (event) => {
    const enabled = event.target.checked
    setDemoMode(enabled)
    const nextPrefs = { ...preferences, demoMode: enabled }
    lastPrefChangeRef.current = Date.now()
    setPreferences(nextPrefs)
    const cacheResult = savePreferences(nextPrefs)
    if (!cacheResult.success) {
      toast.show(`Failed to cache preferences locally: ${cacheResult.error}`, 'warning')
    }
    await execute({
      type: InteractionType.UPDATE,
      label: 'Toggle demo mode',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { preferenceKey: 'demoMode', action: 'toggle_demo_mode' },
      action: async () => {
        try {
          const result = await api.setUserPreference('demoMode', enabled)
          if (result?.preferences) {
            const merged = { ...nextPrefs, ...result.preferences }
            setPreferences(merged)
            savePreferences(merged)
          }
          toast.show(enabled ? 'Demo mode enabled - sample data loaded' : 'Demo mode disabled', 'success')
          return result
        } catch (err) {
          toast.show(err.message || 'Failed to save preferences', 'error')
          throw err
        }
      },
    })
  }, [preferences, setDemoMode, toast, execute])

  // ---------------------------------------------------------------------------
  // SMTP handlers
  // ---------------------------------------------------------------------------
  const loadSmtpSettings = useCallback(async () => {
    try {
      const data = await api.getSmtpSettings()
      if (data?.smtp) {
        setSmtp({
          host: data.smtp.host || '',
          port: data.smtp.port || 587,
          username: data.smtp.username || '',
          password: data.smtp.password || '',
          sender: data.smtp.sender || '',
          use_tls: data.smtp.use_tls !== false,
        })
      }
    } catch {
      // silently fail on load
    }
  }, [])

  const handleSmtpSave = useCallback(async () => {
    setSmtpLoading(true)
    try {
      const result = await api.saveSmtpSettings(smtp)
      toast.show(result?.message || 'SMTP settings saved', 'success')
    } catch (err) {
      toast.show(err.message || 'Failed to save SMTP settings', 'error')
    } finally {
      setSmtpLoading(false)
    }
  }, [smtp, toast])

  const handleSmtpTest = useCallback(async () => {
    setSmtpTesting(true)
    try {
      const result = await api.testSmtpConnection()
      if (result?.status === 'connected') {
        toast.show(result.message || 'SMTP connection successful', 'success')
      } else {
        toast.show(result?.message || 'SMTP connection failed', 'error')
      }
    } catch (err) {
      toast.show(err.message || 'SMTP test failed', 'error')
    } finally {
      setSmtpTesting(false)
    }
  }, [toast])

  const handleSmtpChange = useCallback((field) => (event) => {
    const value = field === 'use_tls' ? event.target.checked
      : field === 'port' ? parseInt(event.target.value, 10) || 587
      : event.target.value
    setSmtp(prev => ({ ...prev, [field]: value }))
  }, [])

  useEffect(() => { loadSmtpSettings() }, [loadSmtpSettings])

  // ---------------------------------------------------------------------------
  // Derived values
  // ---------------------------------------------------------------------------
  const config = health?.checks?.configuration || {}
  const llm = health?.checks?.llm || health?.checks?.openai || {}
  const memory = health?.checks?.memory || {}
  const uploadsDir = health?.checks?.uploads_dir || {}
  const stateDir = health?.checks?.state_dir || {}

  return {
    // Health
    loading, health, error, tokenUsage, exporting,
    fetchHealth, handleExportConfig,
    config, llm, memory, uploadsDir, stateDir,
    // Preferences
    preferences, demoMode,
    handlePrefChange, handleDemoModeChange,
    // Personal
    selectedTimezone, selectedLanguage,
    twoFactorEnabled, setTwoFactorEnabled,
    showTwoFactorSetup, setShowTwoFactorSetup,
    handleTimezoneChange, handleLanguageChange, handleTwoFactorToggle,
    // SMTP
    smtp, smtpLoading, smtpTesting, showSmtpPassword, setShowSmtpPassword,
    handleSmtpSave, handleSmtpTest, handleSmtpChange,
  }
}

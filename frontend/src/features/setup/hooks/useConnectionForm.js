import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import { useMutation } from '@tanstack/react-query'
import {
  isMock,
  testConnection as apiTestConnection,
  upsertConnection as apiUpsertConnection,
} from '@/api/client'
import * as mock from '@/api/mock'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import useFormErrorFocus from '@/hooks/useFormErrorFocus.js'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import schema from '../constants/connectDBSchema'
import {
  sanitizeDbType,
  trimString,
  computeCurrentSignature,
  DEFAULT_FORM_VALUES,
  DB_CONFIG,
  FORM_FIELD_ORDER,
  normalizeConnection,
  payloadFromNormalized,
  formatSavedConnection,
  deriveSqliteUrl,
} from '../constants/connectDB'

export function useConnectionForm({
  editingId,
  setEditingId,
  setDetailId,
  setShowDetails,
  lastLatencyMs,
  setLastLatencyMs,
  setCanSave,
  canSave,
}) {
  const {
    connection,
    setConnection,
    setSetupStep,
    savedConnections,
    addSavedConnection,
    removeSavedConnection,
    activeConnectionId,
    setActiveConnectionId,
  } = useAppStore()

  const toast = useToast()
  const { execute } = useInteraction()
  const [showPw, setShowPw] = useState(false)
  const testedSignatureRef = useRef(null)
  const currentSignatureRef = useRef('')
  const duplicateNameTimerRef = useRef(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitted, submitCount },
    watch,
    reset,
    setValue,
    control,
    getValues,
    setError,
    clearErrors,
    setFocus,
  } = useForm({
    mode: 'onChange',
    resolver: yupResolver(schema),
    defaultValues: { ...DEFAULT_FORM_VALUES },
  })

  useEffect(() => {
    currentSignatureRef.current = computeCurrentSignature(getValues())
  }, [getValues])

  useEffect(() => {
    const subscription = watch((values) => {
      const nextSignature = computeCurrentSignature(values)
      currentSignatureRef.current = nextSignature
      if (testedSignatureRef.current && testedSignatureRef.current !== nextSignature) {
        testedSignatureRef.current = null
        setCanSave(false)
      }
    })
    return () => subscription.unsubscribe()
  }, [watch, setCanSave])

  const dbType = watch('db_type')
  const dbTypeKey = sanitizeDbType(dbType)
  const isSQLite = dbTypeKey === 'sqlite'
  const nameValue = watch('name')
  const portValue = watch('port')
  const dbNameValue = watch('db_name')
  const activeDbConfig = dbTypeKey ? DB_CONFIG[dbTypeKey] : null

  const sqliteResolvedUrl = useMemo(() => {
    if (!isSQLite) return null
    const raw = trimString(dbNameValue)
    if (!raw) return null
    if (raw.startsWith('sqlite:')) return raw
    const normalized = raw.replace(/\\/g, '/')
    if (/^[a-zA-Z]:\//.test(normalized)) return `sqlite:///${normalized}`
    if (normalized.startsWith('/')) return `sqlite://${normalized}`
    return `sqlite:///${normalized}`
  }, [isSQLite, dbNameValue])

  const sqliteResolvedPath = useMemo(() => {
    if (!sqliteResolvedUrl) return null
    return sqliteResolvedUrl.replace(/^sqlite:?\/+/, '')
  }, [sqliteResolvedUrl])

  const checkDuplicateName = useCallback((candidate) => {
    const trimmed = trimString(candidate)
    if (!trimmed) return false
    const normalized = trimmed.toLowerCase()
    return savedConnections.some((conn) => {
      if (!conn?.name) return false
      if (editingId && conn.id === editingId) return false
      const existing = trimString(conn.name)
      return !!existing && existing.toLowerCase() === normalized
    })
  }, [savedConnections, editingId])

  const copySqlitePath = useCallback(async () => {
    if (!sqliteResolvedPath) return
    try {
      if (typeof navigator !== 'undefined' && navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(sqliteResolvedPath)
      } else {
        throw new Error('Clipboard API unavailable')
      }
      toast.show('Path copied to clipboard', 'success')
    } catch {
      try {
        const textarea = document.createElement('textarea')
        textarea.value = sqliteResolvedPath
        textarea.setAttribute('readonly', '')
        textarea.style.position = 'absolute'
        textarea.style.left = '-9999px'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        toast.show('Path copied to clipboard', 'success')
      } catch {
        toast.show('Unable to copy path', 'error')
      }
    }
  }, [sqliteResolvedPath, toast])

  useEffect(() => {
    if (!dbTypeKey || dbTypeKey === 'sqlite') return
    const config = DB_CONFIG[dbTypeKey]
    if (!config?.defaultPort) return
    if (!portValue) {
      setValue('port', String(config.defaultPort))
    }
  }, [dbTypeKey, portValue, setValue])

  const hostHelperText = errors.host?.message || (isSQLite ? 'Host not required for SQLite file connections' : 'Enter the database host or IP address.')
  const portHelperText = errors.port?.message
    || (isSQLite
      ? 'Port not required for SQLite'
      : (activeDbConfig?.defaultPort ? `Defaults to ${activeDbConfig.defaultPort}` : 'Enter the TCP port for the database service.'))
  const usernameHelperText = errors.username?.message || (isSQLite ? 'Username not required for SQLite' : 'Provide the database user with read access.')
  const passwordHelperText = errors.password?.message || (isSQLite ? 'Password not required for SQLite' : 'Provide the password for the database user.')
  const portPlaceholder = !isSQLite && activeDbConfig?.defaultPort ? String(activeDbConfig.defaultPort) : ''

  useEffect(() => {
    if (duplicateNameTimerRef.current) {
      clearTimeout(duplicateNameTimerRef.current)
    }
    duplicateNameTimerRef.current = setTimeout(() => {
      const isDuplicate = checkDuplicateName(nameValue)
      if (isDuplicate) {
        if (errors.name?.type !== 'duplicate') {
          setError('name', { type: 'duplicate', message: 'Connection name already exists' })
        }
      } else if (errors.name?.type === 'duplicate') {
        clearErrors('name')
      }
      duplicateNameTimerRef.current = null
    }, 200)
    return () => {
      if (duplicateNameTimerRef.current) {
        clearTimeout(duplicateNameTimerRef.current)
        duplicateNameTimerRef.current = null
      }
    }
  }, [nameValue, checkDuplicateName, errors.name?.type, setError, clearErrors])

  useFormErrorFocus(
    { errors, isSubmitted, submitCount },
    setFocus,
    FORM_FIELD_ORDER,
  )

  const showErrorSummary = (isSubmitted || submitCount > 0) && Object.keys(errors || {}).length > 0

  const handleFocusErrorField = useCallback((fieldName) => {
    if (!fieldName) return
    try {
      setFocus(fieldName, { shouldSelect: true })
    } catch {
      /* field may be controlled via Controller without direct focus target */
    }
  }, [setFocus])

  /** ---- Test Connection ---- */
  const mutation = useMutation({
    mutationFn: async (formValues) => {
      const normalized = normalizeConnection(formValues)
      const payload = payloadFromNormalized(normalized)

      if (isMock) {
        const response = await mock.testConnection(payload)
        return { normalized, response }
      }

      const data = await apiTestConnection(payload)
      return {
        normalized,
        response: {
          ok: data.ok ?? true,
          details: data.details || 'Connected',
          latencyMs: typeof data.latency_ms === 'number' ? data.latency_ms : undefined,
          connection_id: data.connection_id,
          normalized: data.normalized || undefined,
        }
      }
    },
    onSuccess: ({ normalized, response }, formValues) => {
      const now = new Date().toISOString()
      const lm = response.latencyMs ?? null
      const typedName = (watch('name') || '').trim()

      setLastLatencyMs(lm)
      setConnection({
        status: 'connected',
        lastMessage: response.details,
        details: response.details,
        latencyMs: lm,
        db_url: normalized.db_url,
        name: typedName || normalized.displayName,
        lastCheckedAt: now,
        connectionId: response.connection_id,
        normalized: response.normalized,
        saved: false,
      })

      setActiveConnectionId(response.connection_id)
      setShowDetails(true)

      const signature = computeCurrentSignature(formValues || getValues())
      currentSignatureRef.current = signature
      testedSignatureRef.current = signature
      setCanSave(true)
      setSetupStep('generate')
      toast.show('Connection successful', 'success')
    },
    onError: (error) => {
      const detail = error?.message || 'Connection failed'
      const failedAt = new Date().toISOString()
      setCanSave(false)
      testedSignatureRef.current = null
      setConnection({ status: 'failed', lastMessage: detail, details: detail, lastCheckedAt: failedAt })
      setShowDetails(true)
      toast.show(detail, 'error')
    },
  })

  const onSubmit = async (values) => {
    if (checkDuplicateName(values.name)) {
      setError('name', { type: 'duplicate', message: 'Connection name already exists' })
      setCanSave(false)
      return
    }
    setCanSave(false)
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Test connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        dbType: sanitizeDbType(values.db_type),
        action: 'test_connection',
      },
      action: async () => mutation.mutateAsync(values),
    })
  }

  /** ---- Save & Continue ---- */
  const runSave = async () => {
    const values = watch()
    const friendlyName = trimString(values.name)
    if (checkDuplicateName(friendlyName)) {
      setError('name', { type: 'duplicate', message: 'Connection name already exists' })
      return
    }
    let normalized
    try {
      normalized = normalizeConnection(values)
    } catch (e) {
      toast.show(e.message, 'error'); return
    }
    const finalName = friendlyName || normalized.displayName
    const currentSignature = computeCurrentSignature(values)
    const signatureMatches = testedSignatureRef.current && testedSignatureRef.current === currentSignature
    if (!canSave || !signatureMatches || connection.status !== 'connected' || connection.db_url !== normalized.db_url) {
      toast.show('Test the connection with the current settings before saving', 'warning')
      return
    }
    const now = new Date().toISOString()
    const latency = connection.latencyMs ?? lastLatencyMs ?? null
    const baseDetails = connection.details || connection.lastMessage || 'Connected'
    const existingRecord = editingId ? savedConnections.find((c) => c.id === editingId) : null
    const preferredId =
      connection.connectionId ||
      existingRecord?.backend_connection_id ||
      existingRecord?.id ||
      editingId ||
      null
    const normalizedHostForSave =
      normalized.db_type === 'sqlite' ? normalized.database : normalized.host
    const normalizedDatabasePath = normalized.db_type === 'sqlite' ? normalized.database : null

    try {
      let persisted
      if (isMock) {
        const fallbackId = preferredId || `conn_${Date.now()}`
        persisted = formatSavedConnection({
          id: fallbackId,
          name: finalName,
          db_type: normalized.db_type,
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          db_url: normalized.db_url,
          host: normalizedHostForSave,
          port: normalized.port,
          database: normalized.database,
          databasePath: normalizedDatabasePath,
          driver: normalized.driver,
          ssl: normalized.ssl,
          details: baseDetails,
          hasCredentials: true,
        })
      } else {
        const response = await apiUpsertConnection({
          id: preferredId,
          name: finalName,
          dbType: normalized.db_type,
          dbUrl: normalized.db_url,
          database: normalized.database,
          host: normalized.host,
          port: normalized.port,
          username: normalized.username,
          password: normalized.password,
          ssl: normalized.ssl,
          driver: normalized.driver,
          status: 'connected',
          latencyMs: latency,
        })
        persisted = formatSavedConnection(response, {
          name: finalName,
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          db_url: normalized.db_url,
          host: normalizedHostForSave,
          port: normalized.port,
          database: normalized.database,
          databasePath: normalizedDatabasePath,
          driver: normalized.driver,
          ssl: normalized.ssl,
          details: baseDetails,
          hasCredentials: true,
        })
      }

      if (!persisted) throw new Error('Unable to persist connection. Please try again.')

      if (editingId && editingId !== persisted.id) {
        removeSavedConnection(editingId)
      }

      addSavedConnection(persisted)
      const stateAfterSave = useAppStore.getState()
      savePersistedCache({
        connections: stateAfterSave.savedConnections,
        templates: stateAfterSave.templates,
        lastUsed: stateAfterSave.lastUsed,
      })
      setDetailId(persisted.id)
      setActiveConnectionId(persisted.backend_connection_id || persisted.id)

      setEditingId(null)
      setConnection({
        saved: true,
        status: 'connected',
        name: persisted.name,
        db_url: persisted.db_url,
        latencyMs: persisted.lastLatencyMs,
        lastMessage: persisted.details,
        details: persisted.details,
        connectionId: persisted.backend_connection_id || persisted.id,
        db_type: persisted.db_type,
        host: persisted.host ?? null,
        port: persisted.port ?? null,
        database: persisted.database ?? persisted.databasePath ?? null,
        driver: persisted.driver ?? null,
        ssl: persisted.ssl ?? false,
        lastCheckedAt: now,
      })
      testedSignatureRef.current = null
      reset({ ...DEFAULT_FORM_VALUES })
      setCanSave(false)
      setSetupStep('generate')
      toast.show('Connection saved', 'success')
    } catch (err) {
      toast.show(err?.message || 'Failed to save connection', 'error')
      throw err
    }
  }

  const handleSave = async () => {
    await execute({
      type: InteractionType.UPDATE,
      label: 'Save connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: connection.connectionId || editingId || null,
        dbType: sanitizeDbType(watch('db_type')),
        action: 'save_connection',
      },
      action: async () => runSave(),
    })
  }

  return {
    // form methods
    register,
    handleSubmit,
    errors,
    isSubmitted,
    submitCount,
    watch,
    reset,
    setValue,
    control,
    getValues,
    setError,
    clearErrors,
    setFocus,
    // derived state
    dbTypeKey,
    isSQLite,
    activeDbConfig,
    sqliteResolvedPath,
    showPw,
    setShowPw,
    showErrorSummary,
    hostHelperText,
    portHelperText,
    usernameHelperText,
    passwordHelperText,
    portPlaceholder,
    // mutation
    mutation,
    // handlers
    onSubmit,
    handleSave,
    handleFocusErrorField,
    copySqlitePath,
    checkDuplicateName,
    // refs
    testedSignatureRef,
    currentSignatureRef,
  }
}

/**
 * Hook for ConnectionForm state management.
 * Manages form data, validation, testing, and submission.
 */
import { useState, useCallback, useMemo, useRef } from 'react'
import { testConnection } from '@/api/client'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import {
  validateRequired,
  validateMinLength,
  validateMaxLength,
  combineValidators,
} from '@/utils/validation'

const DB_TYPES = [
  { value: 'sqlite', label: 'SQLite', port: null, requiresAuth: false },
  { value: 'postgresql', label: 'PostgreSQL', port: 5432, requiresAuth: true },
  { value: 'mysql', label: 'MySQL', port: 3306, requiresAuth: true },
  { value: 'mssql', label: 'SQL Server', port: 1433, requiresAuth: true },
  { value: 'mariadb', label: 'MariaDB', port: 3306, requiresAuth: true },
]

// Field validators
const validators = {
  name: combineValidators(
    (v) => validateRequired(v, 'Connection name'),
    (v) => validateMinLength(v, 2, 'Connection name'),
    (v) => validateMaxLength(v, 100, 'Connection name')
  ),
  host: (value, allValues) => {
    if (allValues.db_type === 'sqlite') return { valid: true, error: null }
    return combineValidators(
      (v) => validateRequired(v, 'Host'),
      (v) => validateMaxLength(v, 255, 'Host')
    )(value)
  },
  database: combineValidators(
    (v) => validateRequired(v, 'Database name'),
    (v) => validateMaxLength(v, 255, 'Database name')
  ),
  port: (value) => {
    const port = parseInt(value, 10)
    if (isNaN(port) || port < 1 || port > 65535) {
      return { valid: false, error: 'Port must be between 1 and 65535' }
    }
    return { valid: true, error: null }
  },
}

export { DB_TYPES }

export function useConnectionForm(connection, onSave) {
  const initialDbType = DB_TYPES.some((type) => type.value === connection?.db_type)
    ? connection?.db_type
    : 'sqlite'
  const [formData, setFormData] = useState({
    name: connection?.name || '',
    db_type: initialDbType,
    host: connection?.host || 'localhost',
    port: connection?.port || 5432,
    database: connection?.database || '',
    username: connection?.username || '',
    password: '',
    ssl: connection?.ssl ?? true,
  })
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [error, setError] = useState(null)
  const [touched, setTouched] = useState({})
  const [fieldErrors, setFieldErrors] = useState({})
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null) // 'success' | 'error' | null
  const submitDebounceRef = useRef(false)
  const { execute } = useInteraction()

  const handleChange = useCallback((field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value
    setFormData((prev) => {
      const newData = { ...prev, [field]: value }
      if (touched[field] && validators[field]) {
        const result = validators[field](value, newData)
        setFieldErrors((e) => ({ ...e, [field]: result.error }))
      }
      return newData
    })
    setError(null)
  }, [touched])

  const handleBlur = useCallback((field) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }))
    if (validators[field]) {
      const result = validators[field](formData[field], formData)
      setFieldErrors((prev) => ({ ...prev, [field]: result.error }))
    }
  }, [formData])

  const handleDbTypeChange = useCallback((event) => {
    const dbType = event.target.value
    const typeConfig = DB_TYPES.find((t) => t.value === dbType)
    setFormData((prev) => ({
      ...prev,
      db_type: dbType,
      port: typeConfig?.port || prev.port,
    }))
    setTestResult(null)
  }, [])

  const buildConnectionUrl = useCallback(() => {
    if (formData.db_type === 'sqlite') {
      return null
    }
    const auth = formData.username
      ? `${formData.username}${formData.password ? `:${formData.password}` : ''}@`
      : ''
    return `${formData.db_type}://${auth}${formData.host}:${formData.port}/${formData.database}`
  }, [formData])

  const handleTestConnection = useCallback(async () => {
    const requiredErrors = {}
    if (!formData.database.trim()) {
      requiredErrors.database = 'Database is required to test'
    }
    if (formData.db_type !== 'sqlite' && !formData.host.trim()) {
      requiredErrors.host = 'Host is required to test'
    }

    if (Object.keys(requiredErrors).length > 0) {
      setFieldErrors((prev) => ({ ...prev, ...requiredErrors }))
      setTouched((prev) => ({ ...prev, database: true, host: true }))
      return
    }

    await execute({
      type: InteractionType.EXECUTE,
      label: 'Test connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        dbType: formData.db_type,
        action: 'test_connection',
      },
      action: async () => {
        setTesting(true)
        setTestResult(null)
        setError(null)

        try {
          const db_url = buildConnectionUrl()
          const result = await testConnection({
            db_url,
            db_type: formData.db_type,
            database: formData.database,
          })
          if (
            result?.status === 'healthy'
            || result?.healthy
            || result?.status === 'ok'
            || result?.ok
          ) {
            setTestResult('success')
          } else {
            setTestResult('error')
            setError(result?.message || result?.error || 'Connection test failed')
          }
          return result
        } catch (err) {
          setTestResult('error')
          setError(err.message || 'Connection test failed')
          throw err
        } finally {
          setTesting(false)
        }
      },
    })
  }, [buildConnectionUrl, execute, formData])

  const handleSubmit = useCallback((e) => {
    e.preventDefault()

    if (submitDebounceRef.current) return
    submitDebounceRef.current = true
    setTimeout(() => { submitDebounceRef.current = false }, 1000)

    const allTouched = { name: true, host: true, database: true, port: true }
    setTouched(allTouched)

    const errors = {}
    let hasErrors = false

    for (const [field, validator] of Object.entries(validators)) {
      const result = validator(formData[field], formData)
      if (!result.valid) {
        errors[field] = result.error
        hasErrors = true
      }
    }

    setFieldErrors(errors)

    if (hasErrors) {
      const firstError = Object.values(errors).find(Boolean)
      setError(firstError || 'Please fix the errors above')
      return
    }

    const db_url = buildConnectionUrl()

    onSave({
      ...formData,
      db_url,
    })
  }, [formData, onSave, buildConnectionUrl])

  const isSqlite = formData.db_type === 'sqlite'

  const isFormValid = useMemo(() => {
    const nameValid = formData.name.trim().length >= 2
    const dbValid = formData.database.trim().length > 0
    if (isSqlite) return nameValid && dbValid
    const hostValid = formData.host.trim().length > 0
    return nameValid && dbValid && hostValid
  }, [formData.name, formData.database, formData.host, isSqlite])

  return {
    formData,
    showAdvanced,
    setShowAdvanced,
    error,
    setError,
    touched,
    fieldErrors,
    testing,
    testResult,
    setTestResult,
    isSqlite,
    isFormValid,
    handleChange,
    handleBlur,
    handleDbTypeChange,
    handleTestConnection,
    handleSubmit,
  }
}

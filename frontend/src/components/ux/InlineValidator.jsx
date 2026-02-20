/**
 * Inline Validator Components
 * Real-time validation feedback that prevents errors before they happen
 *
 * UX Laws Addressed:
 * - Prevent errors before handling them
 * - Immediate feedback (within 100ms)
 * - Make system state always visible
 */
import { useState, useCallback, useEffect, useMemo, useRef } from 'react'
import {
  TextField,
  Box,
  Typography,
  Fade,
  useTheme,
  alpha,
  InputAdornment,
} from '@mui/material'
import {
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material'

// Validation states
export const ValidationState = {
  IDLE: 'idle',
  VALIDATING: 'validating',
  VALID: 'valid',
  INVALID: 'invalid',
  WARNING: 'warning',
}

/**
 * Common validation rules
 */
export const ValidationRules = {
  required: (message = 'This field is required') => ({
    validate: (value) => {
      const trimmed = typeof value === 'string' ? value.trim() : value
      return trimmed && trimmed.length > 0
    },
    message,
  }),

  minLength: (min, message) => ({
    validate: (value) => !value || value.length >= min,
    message: message || `Must be at least ${min} characters`,
  }),

  maxLength: (max, message) => ({
    validate: (value) => !value || value.length <= max,
    message: message || `Must be ${max} characters or less`,
  }),

  pattern: (regex, message = 'Invalid format') => ({
    validate: (value) => !value || regex.test(value),
    message,
  }),

  email: (message = 'Please enter a valid email address') => ({
    validate: (value) => {
      if (!value) return true
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value)
    },
    message,
  }),

  url: (message = 'Please enter a valid URL') => ({
    validate: (value) => {
      if (!value) return true
      try {
        new URL(value)
        return true
      } catch {
        return false
      }
    },
    message,
  }),

  noSpecialChars: (message = 'Special characters are not allowed') => ({
    validate: (value) => {
      if (!value) return true
      return /^[a-zA-Z0-9_\-\s]+$/.test(value)
    },
    message,
  }),

  custom: (validateFn, message) => ({
    validate: validateFn,
    message,
  }),
}

/**
 * Hook for field validation
 */
export function useFieldValidation(rules = [], options = {}) {
  const { debounceMs = 150, validateOnChange = true, validateOnBlur = true } = options

  const [value, setValue] = useState('')
  const [touched, setTouched] = useState(false)
  const [state, setState] = useState(ValidationState.IDLE)
  const [error, setError] = useState(null)
  const debounceTimerRef = useRef(null)
  const rulesRef = useRef(rules)
  rulesRef.current = rules

  // Run validation
  const runValidation = useCallback((val) => {
    for (const rule of rulesRef.current) {
      const isValid = rule.validate(val)
      if (!isValid) {
        setState(ValidationState.INVALID)
        setError(rule.message)
        return false
      }
    }
    setState(val ? ValidationState.VALID : ValidationState.IDLE)
    setError(null)
    return true
  }, [])

  // Handle change with debounce
  const handleChange = useCallback((newValue) => {
    setValue(newValue)

    if (!validateOnChange) return

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    // Set validating state immediately
    if (touched && newValue) {
      setState(ValidationState.VALIDATING)
    }

    // Debounce validation
    debounceTimerRef.current = setTimeout(() => {
      if (touched || newValue) {
        runValidation(newValue)
      }
    }, debounceMs)
  }, [validateOnChange, touched, debounceMs, runValidation])

  // Handle blur
  const handleBlur = useCallback(() => {
    setTouched(true)
    if (validateOnBlur) {
      runValidation(value)
    }
  }, [validateOnBlur, runValidation, value])

  // Validate on demand
  const validate = useCallback(() => {
    setTouched(true)
    return runValidation(value)
  }, [runValidation, value])

  // Reset
  const reset = useCallback(() => {
    setValue('')
    setTouched(false)
    setState(ValidationState.IDLE)
    setError(null)
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [])

  return {
    value,
    setValue: handleChange,
    touched,
    state,
    error,
    isValid: state === ValidationState.VALID,
    isInvalid: state === ValidationState.INVALID,
    validate,
    reset,
    handleBlur,
    inputProps: {
      value,
      onChange: (e) => handleChange(e.target.value),
      onBlur: handleBlur,
      error: touched && state === ValidationState.INVALID,
      helperText: touched && error,
    },
  }
}

/**
 * Validated TextField Component
 * Drop-in replacement for TextField with built-in validation
 */
export function ValidatedTextField({
  rules = [],
  value,
  onChange,
  onBlur,
  showValidIcon = true,
  showCharCount = false,
  maxLength,
  validateOnMount = false,
  hint,
  ...props
}) {
  const theme = useTheme()
  const [localValue, setLocalValue] = useState(value || '')
  const [touched, setTouched] = useState(validateOnMount)
  const [validationState, setValidationState] = useState(ValidationState.IDLE)
  const [errorMessage, setErrorMessage] = useState(null)

  // Sync with external value
  useEffect(() => {
    if (value !== undefined) {
      setLocalValue(value)
    }
  }, [value])

  // Auto-add maxLength rule if specified
  const allRules = useMemo(() => {
    const r = [...rules]
    if (maxLength && !r.some((rule) => rule.message?.includes('characters or less'))) {
      r.push(ValidationRules.maxLength(maxLength))
    }
    return r
  }, [rules, maxLength])

  // Validate
  const validate = useCallback((val) => {
    for (const rule of allRules) {
      if (!rule.validate(val)) {
        setValidationState(ValidationState.INVALID)
        setErrorMessage(rule.message)
        return false
      }
    }
    setValidationState(val ? ValidationState.VALID : ValidationState.IDLE)
    setErrorMessage(null)
    return true
  }, [allRules])

  // Handle change
  const validateTimerRef = useRef(null)

  useEffect(() => {
    return () => {
      if (validateTimerRef.current) {
        clearTimeout(validateTimerRef.current)
      }
    }
  }, [])

  const handleChange = useCallback((e) => {
    const newValue = e.target.value

    // Enforce maxLength at input level
    if (maxLength && newValue.length > maxLength) {
      return
    }

    setLocalValue(newValue)
    onChange?.(e)

    // Validate with slight delay for perceived performance
    if (touched) {
      if (validateTimerRef.current) {
        clearTimeout(validateTimerRef.current)
      }
      validateTimerRef.current = setTimeout(() => validate(newValue), 50)
    }
  }, [onChange, touched, validate, maxLength])

  // Handle blur
  const handleBlur = useCallback((e) => {
    setTouched(true)
    validate(localValue)
    onBlur?.(e)
  }, [onBlur, localValue, validate])

  // Determine helper text
  const helperText = useMemo(() => {
    if (touched && errorMessage) {
      return errorMessage
    }
    if (hint && !touched) {
      return hint
    }
    if (showCharCount && maxLength) {
      return `${localValue.length}/${maxLength}`
    }
    return props.helperText
  }, [touched, errorMessage, hint, showCharCount, maxLength, localValue.length, props.helperText])

  // Determine end adornment
  const endAdornment = useMemo(() => {
    if (!showValidIcon || !touched) {
      return props.InputProps?.endAdornment
    }

    let icon = null
    if (validationState === ValidationState.VALID) {
      icon = <ValidIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
    } else if (validationState === ValidationState.INVALID) {
      icon = <ErrorIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
    }

    if (!icon) {
      return props.InputProps?.endAdornment
    }

    return (
      <InputAdornment position="end">
        <Fade in>
          {icon}
        </Fade>
        {props.InputProps?.endAdornment}
      </InputAdornment>
    )
  }, [showValidIcon, touched, validationState, props.InputProps?.endAdornment])

  return (
    <TextField
      {...props}
      value={localValue}
      onChange={handleChange}
      onBlur={handleBlur}
      error={touched && validationState === ValidationState.INVALID}
      helperText={helperText}
      inputProps={{
        ...props.inputProps,
        maxLength: maxLength,
      }}
      InputProps={{
        ...props.InputProps,
        endAdornment,
      }}
      FormHelperTextProps={{
        ...props.FormHelperTextProps,
        sx: {
          ...props.FormHelperTextProps?.sx,
          display: 'flex',
          justifyContent: 'space-between',
        },
      }}
    />
  )
}

/**
 * Validation Feedback Component
 * Shows validation state with animation
 */
export function ValidationFeedback({ state, message, successMessage = 'Looks good!' }) {
  const theme = useTheme()

  if (state === ValidationState.IDLE || state === ValidationState.VALIDATING) {
    return null
  }

  const config = {
    [ValidationState.VALID]: {
      icon: <ValidIcon fontSize="small" />,
      color: theme.palette.text.secondary,
      text: successMessage,
    },
    [ValidationState.INVALID]: {
      icon: <ErrorIcon fontSize="small" />,
      color: theme.palette.text.secondary,
      text: message,
    },
    [ValidationState.WARNING]: {
      icon: <InfoIcon fontSize="small" />,
      color: theme.palette.text.secondary,
      text: message,
    },
  }[state]

  if (!config) return null

  return (
    <Fade in>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          mt: 0.5,
          color: config.color,
        }}
      >
        {config.icon}
        <Typography variant="caption">
          {config.text}
        </Typography>
      </Box>
    </Fade>
  )
}

/**
 * Character Counter Component
 */
export function CharacterCounter({ current, max, warningThreshold = 0.9 }) {
  const theme = useTheme()
  const ratio = current / max

  const color = useMemo(() => {
    if (current >= max) return theme.palette.text.secondary
    if (ratio >= warningThreshold) return theme.palette.text.secondary
    return theme.palette.text.secondary
  }, [current, max, ratio, warningThreshold, theme])

  return (
    <Typography
      variant="caption"
      sx={{
        color,
        fontWeight: current >= max ? 600 : 400,
      }}
    >
      {current}/{max}
    </Typography>
  )
}

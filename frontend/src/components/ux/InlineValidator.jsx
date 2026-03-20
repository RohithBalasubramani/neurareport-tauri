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
  Box,
  Typography,
  Fade,
  useTheme,
} from '@mui/material'
import {
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { ValidationState } from './validationRules'

// Re-export for backward compatibility
export { ValidationState, ValidationRules } from './validationRules'

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

  const handleChange = useCallback((newValue) => {
    setValue(newValue)
    if (!validateOnChange) return
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }
    if (touched && newValue) {
      setState(ValidationState.VALIDATING)
    }
    debounceTimerRef.current = setTimeout(() => {
      if (touched || newValue) {
        runValidation(newValue)
      }
    }, debounceMs)
  }, [validateOnChange, touched, debounceMs, runValidation])

  const handleBlur = useCallback(() => {
    setTouched(true)
    if (validateOnBlur) {
      runValidation(value)
    }
  }, [validateOnBlur, runValidation, value])

  const validate = useCallback(() => {
    setTouched(true)
    return runValidation(value)
  }, [runValidation, value])

  const reset = useCallback(() => {
    setValue('')
    setTouched(false)
    setState(ValidationState.IDLE)
    setError(null)
  }, [])

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

// Re-export ValidatedTextField for backward compatibility
export { default as ValidatedTextField } from './ValidatedTextField'

/**
 * Validation Feedback Component
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

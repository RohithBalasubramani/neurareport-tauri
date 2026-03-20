/**
 * Validated TextField Component
 * Drop-in replacement for TextField with built-in validation
 */
import { useState, useCallback, useEffect, useMemo, useRef } from 'react'
import {
  TextField,
  Fade,
  useTheme,
  InputAdornment,
} from '@mui/material'
import {
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { ValidationState, ValidationRules } from './validationRules'

export default function ValidatedTextField({
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

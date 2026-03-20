/**
 * Validation states and common validation rules
 */

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

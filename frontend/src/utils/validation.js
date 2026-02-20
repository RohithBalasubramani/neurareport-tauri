/**
 * Client-side Form Validation Utilities
 *
 * This module provides validation functions for common form fields
 * to catch errors before form submission.
 */

/**
 * Validation result object
 * @typedef {Object} ValidationResult
 * @property {boolean} valid - Whether the value passes validation
 * @property {string|null} error - Error message if invalid
 */

/**
 * Check if a value is empty (null, undefined, or whitespace-only string)
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  return false
}

/**
 * Validate a required field
 * @param {*} value - Value to validate
 * @param {string} fieldName - Name of the field for error message
 * @returns {ValidationResult}
 */
export function validateRequired(value, fieldName = 'This field') {
  if (isEmpty(value)) {
    return { valid: false, error: `${fieldName} is required` }
  }
  return { valid: true, error: null }
}

/**
 * Validate minimum string length
 * @param {string} value - Value to validate
 * @param {number} minLength - Minimum length
 * @param {string} fieldName - Name of the field
 * @returns {ValidationResult}
 */
export function validateMinLength(value, minLength, fieldName = 'This field') {
  if (typeof value !== 'string') {
    return { valid: false, error: `${fieldName} must be a string` }
  }
  if (value.trim().length < minLength) {
    return { valid: false, error: `${fieldName} must be at least ${minLength} characters` }
  }
  return { valid: true, error: null }
}

/**
 * Validate maximum string length
 * @param {string} value - Value to validate
 * @param {number} maxLength - Maximum length
 * @param {string} fieldName - Name of the field
 * @returns {ValidationResult}
 */
export function validateMaxLength(value, maxLength, fieldName = 'This field') {
  if (typeof value !== 'string') {
    return { valid: true, error: null }
  }
  if (value.length > maxLength) {
    return { valid: false, error: `${fieldName} must be at most ${maxLength} characters` }
  }
  return { valid: true, error: null }
}

/**
 * Validate email format
 * @param {string} value - Email to validate
 * @returns {ValidationResult}
 */
export function validateEmail(value) {
  if (isEmpty(value)) {
    return { valid: true, error: null } // Let required validation handle empty
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    return { valid: false, error: 'Please enter a valid email address' }
  }
  return { valid: true, error: null }
}

/**
 * Validate URL format
 * @param {string} value - URL to validate
 * @param {Object} options - Validation options
 * @param {boolean} options.requireProtocol - Whether to require http/https
 * @returns {ValidationResult}
 */
export function validateUrl(value, { requireProtocol = true } = {}) {
  if (isEmpty(value)) {
    return { valid: true, error: null }
  }
  try {
    const url = new URL(value)
    if (requireProtocol && !['http:', 'https:'].includes(url.protocol)) {
      return { valid: false, error: 'URL must start with http:// or https://' }
    }
    return { valid: true, error: null }
  } catch {
    return { valid: false, error: 'Please enter a valid URL' }
  }
}

/**
 * Validate database connection string
 * @param {string} value - Connection string to validate
 * @param {string} dbType - Database type
 * @returns {ValidationResult}
 */
export function validateDbConnectionString(value, dbType) {
  if (isEmpty(value)) {
    return { valid: true, error: null }
  }

  const dbTypeNorm = (dbType || '').toLowerCase()

  // PostgreSQL connection string patterns
  if (dbTypeNorm === 'postgresql' || dbTypeNorm === 'postgres') {
    if (!value.startsWith('postgresql://') && !value.startsWith('postgres://')) {
      return {
        valid: false,
        error: 'PostgreSQL connection must start with postgresql:// or postgres://',
      }
    }
  }

  // MySQL connection string patterns
  if (dbTypeNorm === 'mysql') {
    if (!value.startsWith('mysql://') && !value.startsWith('mysql+pymysql://')) {
      return {
        valid: false,
        error: 'MySQL connection must start with mysql:// or mysql+pymysql://',
      }
    }
  }

  // SQLite connection string patterns
  if (dbTypeNorm === 'sqlite') {
    if (!value.startsWith('sqlite:///') && !value.startsWith('sqlite://')) {
      return {
        valid: false,
        error: 'SQLite connection must start with sqlite:// or sqlite:///',
      }
    }
  }

  // SQL Server connection string patterns
  if (dbTypeNorm === 'mssql' || dbTypeNorm === 'sqlserver') {
    if (!value.startsWith('mssql://') && !value.startsWith('mssql+pyodbc://')) {
      return {
        valid: false,
        error: 'SQL Server connection must start with mssql:// or mssql+pyodbc://',
      }
    }
  }

  return { valid: true, error: null }
}

/**
 * Validate a date string
 * @param {string} value - Date string to validate
 * @param {string} fieldName - Name of the field
 * @returns {ValidationResult}
 */
export function validateDate(value, fieldName = 'Date') {
  if (isEmpty(value)) {
    return { valid: true, error: null }
  }
  const date = new Date(value)
  if (isNaN(date.getTime())) {
    return { valid: false, error: `${fieldName} is not a valid date` }
  }
  return { valid: true, error: null }
}

/**
 * Validate date range (start must be before or equal to end)
 * @param {string} startDate - Start date string
 * @param {string} endDate - End date string
 * @returns {ValidationResult}
 */
export function validateDateRange(startDate, endDate) {
  if (isEmpty(startDate) || isEmpty(endDate)) {
    return { valid: true, error: null }
  }
  const start = new Date(startDate)
  const end = new Date(endDate)
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return { valid: false, error: 'Invalid date format' }
  }
  if (start > end) {
    return { valid: false, error: 'Start date must be before or equal to end date' }
  }
  return { valid: true, error: null }
}

/**
 * Validate file type
 * @param {File} file - File to validate
 * @param {string[]} allowedTypes - Allowed MIME types or extensions
 * @returns {ValidationResult}
 */
export function validateFileType(file, allowedTypes) {
  if (!file) {
    return { valid: true, error: null }
  }

  const fileName = file.name.toLowerCase()
  const fileType = file.type.toLowerCase()

  const isAllowed = allowedTypes.some((type) => {
    // Check extension
    if (type.startsWith('.')) {
      return fileName.endsWith(type.toLowerCase())
    }
    // Check MIME type
    return fileType === type.toLowerCase() || fileType.startsWith(`${type.toLowerCase()}/`)
  })

  if (!isAllowed) {
    return {
      valid: false,
      error: `File type not allowed. Accepted: ${allowedTypes.join(', ')}`,
    }
  }

  return { valid: true, error: null }
}

/**
 * Validate file size
 * @param {File} file - File to validate
 * @param {number} maxSizeBytes - Maximum file size in bytes
 * @returns {ValidationResult}
 */
export function validateFileSize(file, maxSizeBytes) {
  if (!file) {
    return { valid: true, error: null }
  }

  if (file.size > maxSizeBytes) {
    const maxSizeMB = (maxSizeBytes / (1024 * 1024)).toFixed(1)
    return {
      valid: false,
      error: `File size exceeds maximum of ${maxSizeMB}MB`,
    }
  }

  return { valid: true, error: null }
}

/**
 * Run multiple validators and return first error
 * @param {Array<() => ValidationResult>} validators - Array of validator functions
 * @returns {ValidationResult}
 */
export function runValidators(validators) {
  for (const validator of validators) {
    const result = validator()
    if (!result.valid) {
      return result
    }
  }
  return { valid: true, error: null }
}

/**
 * Validate an entire form and return all errors
 * @param {Object} values - Form values object
 * @param {Object} schema - Validation schema mapping field names to validators
 * @returns {Object} Object with { valid: boolean, errors: { fieldName: errorMessage } }
 *
 * @example
 * const result = validateForm(
 *   { name: '', email: 'invalid' },
 *   {
 *     name: (v) => validateRequired(v, 'Name'),
 *     email: (v) => runValidators([
 *       () => validateRequired(v, 'Email'),
 *       () => validateEmail(v),
 *     ]),
 *   }
 * )
 * // result = { valid: false, errors: { name: 'Name is required', email: null } }
 */
export function validateForm(values, schema) {
  const errors = {}
  let valid = true

  for (const [fieldName, validator] of Object.entries(schema)) {
    const result = validator(values[fieldName], values)
    if (!result.valid) {
      valid = false
      errors[fieldName] = result.error
    } else {
      errors[fieldName] = null
    }
  }

  return { valid, errors }
}

/**
 * Create a field validator that combines multiple validation rules
 * @param  {...Function} rules - Validation functions
 * @returns {Function} Combined validator function
 */
export function combineValidators(...rules) {
  return (value, allValues) => {
    for (const rule of rules) {
      const result = rule(value, allValues)
      if (!result.valid) {
        return result
      }
    }
    return { valid: true, error: null }
  }
}

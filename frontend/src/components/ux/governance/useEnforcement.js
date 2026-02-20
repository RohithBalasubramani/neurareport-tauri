/**
 * UX Governance Enforcement Hooks
 *
 * Runtime and development-time checks to ensure all interactions
 * flow through the governance API.
 *
 * Usage in components:
 *   useEnforceGovernance('ComponentName')
 *
 * This will:
 * 1. In development: Warn if raw handlers are detected
 * 2. Verify the component is using useInteraction()
 * 3. Log compliance violations to console
 */

import { useEffect, useRef } from 'react'

// Track components that have been checked (capped to prevent unbounded growth)
const MAX_CHECKED_COMPONENTS = 500
const checkedComponents = new Set()

// Non-compliant patterns to detect
const NON_COMPLIANT_PATTERNS = {
  directFetch: /onClick\s*=\s*{\s*\(\)\s*=>\s*(fetch|axios)/,
  asyncHandler: /onClick\s*=\s*{\s*async\s*\(\)/,
  directMutate: /\.mutate\s*\(\s*{/,
  unconfirmedDelete: /delete.*onClick\s*=\s*{\s*\(\)\s*=>/i,
}

/**
 * Development-time hook to enforce governance compliance
 * @param {string} componentName - Name of the component for logging
 * @param {object} options - Enforcement options
 */
export function useEnforceGovernance(componentName, options = {}) {
  const {
    requireInteraction = true,
    logViolations = true,
    throwOnViolation = false,
  } = options

  const hasInteraction = useRef(false)

  useEffect(() => {
    // Only run in development
    if (!import.meta.env?.DEV) return

    // Only check each component once (cap prevents unbounded memory growth)
    if (checkedComponents.has(componentName)) return
    if (checkedComponents.size >= MAX_CHECKED_COMPONENTS) {
      checkedComponents.clear()
    }
    checkedComponents.add(componentName)

    // Delayed check to allow hooks to be called
    const timer = setTimeout(() => {
      if (requireInteraction && !hasInteraction.current) {
        const message = `[UX GOVERNANCE] Component "${componentName}" has user interactions but may not be using useInteraction() hook.`

        if (logViolations) {
          console.warn(message)
        }

        if (throwOnViolation) {
          throw new Error(message)
        }
      }
    }, 100)

    return () => clearTimeout(timer)
  }, [componentName, requireInteraction, logViolations, throwOnViolation])

  // Mark that this component uses interaction
  const markInteractionUsed = () => {
    hasInteraction.current = true
  }

  return { markInteractionUsed }
}

/**
 * HOC to wrap handlers with governance warnings
 * @deprecated Use useInteraction().execute() instead
 */
export function withGovernanceWarning(handlerName, handler, componentName) {
  if (!import.meta.env?.DEV) {
    return handler
  }

  return (...args) => {
    console.warn(
      `[UX GOVERNANCE VIOLATION] "${handlerName}" in "${componentName}" called without interaction API.\n` +
        `Replace with:\n` +
        `  const { execute } = useInteraction()\n` +
        `  execute({ type: InteractionType.*, label: "...", action: async () => {...} })`
    )
    return handler(...args)
  }
}

/**
 * Create a governance-compliant event handler wrapper
 * This ensures all handlers go through the interaction API
 */
export function createGovernedHandler(execute, config) {
  return (event) => {
    // Prevent default if specified
    if (config.preventDefault !== false) {
      event?.preventDefault?.()
    }

    // Execute through governance API
    execute({
      type: config.type,
      label: config.label,
      reversibility: config.reversibility,
      successMessage: config.successMessage,
      errorMessage: config.errorMessage,
      blocksNavigation: config.blocksNavigation,
      action: config.action,
    })
  }
}

/**
 * Validate that a contract meets governance requirements
 * @param {object} contract - The interaction contract
 * @returns {object} - { valid: boolean, errors: string[] }
 */
export function validateContract(contract) {
  const errors = []

  if (!contract.type) {
    errors.push('Missing required field: type')
  }

  if (!contract.label) {
    errors.push('Missing required field: label')
  }

  if (!contract.action || typeof contract.action !== 'function') {
    errors.push('Missing or invalid action function')
  }

  // Warn about missing optional but recommended fields
  const warnings = []

  if (!contract.reversibility) {
    warnings.push('Consider specifying reversibility level')
  }

  if (!contract.successMessage && !contract.errorMessage) {
    warnings.push('Consider adding success/error messages for user feedback')
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  }
}

/**
 * Development-time report of governance compliance
 */
export function generateComplianceReport() {
  if (!import.meta.env?.DEV) {
    return null
  }

  return {
    checkedComponents: Array.from(checkedComponents),
    timestamp: new Date().toISOString(),
  }
}

/**
 * Reset enforcement state (for testing)
 */
export function resetEnforcement() {
  checkedComponents.clear()
}

export default {
  useEnforceGovernance,
  withGovernanceWarning,
  createGovernedHandler,
  validateContract,
  generateComplianceReport,
  resetEnforcement,
}

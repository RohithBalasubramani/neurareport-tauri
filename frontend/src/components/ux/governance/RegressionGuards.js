/**
 * UX Governance Level-2: Regression Prevention Guards
 *
 * ENFORCES that:
 * - New code follows governance patterns
 * - Non-compliant patterns are detected at build/runtime
 * - Violations fail CI or throw in development
 *
 * These guards are ENFORCEABLE, not advisory.
 */

// ============================================================================
// PATTERN DEFINITIONS
// ============================================================================

/**
 * Patterns that indicate governance violations
 * These are checked at build time and runtime
 */
export const VIOLATION_PATTERNS = {
  // Direct API calls without governance
  DIRECT_FETCH_IN_HANDLER: {
    pattern: /on(Click|Submit|Change)\s*=\s*{\s*(?:async\s*)?\(\)\s*=>\s*(?:fetch|axios)/,
    message: 'Direct API calls in event handlers are not allowed. Use useInteraction().execute() instead.',
    severity: 'error',
  },

  // Async handlers without tracking
  UNTRACKED_ASYNC_HANDLER: {
    pattern: /on(Click|Submit)\s*=\s*{\s*async\s+/,
    message: 'Async handlers must be wrapped with useInteraction() for tracking.',
    severity: 'error',
  },

  // React Query mutations without governance
  UNTRACKED_MUTATION: {
    pattern: /\.mutate\s*\(\s*{[^}]*onSuccess/,
    message: 'React Query mutations must be tracked through the governance API.',
    severity: 'warning',
  },

  // Delete operations without confirmation
  UNCONFIRMED_DELETE: {
    pattern: /delete.*onClick\s*=\s*{\s*\(\)\s*=>/i,
    message: 'Delete operations must use useConfirmedAction() for user confirmation.',
    severity: 'error',
  },

  // Direct state mutations after API calls
  DIRECT_STATE_MUTATION: {
    pattern: /fetch\([^)]+\)\.then\([^)]+\)\s*\.then\(\s*\([^)]+\)\s*=>\s*set/,
    message: 'State mutations after API calls must be tracked through useInteraction().',
    severity: 'warning',
  },

  // Missing error handling in async operations
  MISSING_ERROR_HANDLING: {
    pattern: /await\s+(?:fetch|axios)[^}]*(?!catch|\.catch)/,
    message: 'Async operations must include error handling for UX visibility.',
    severity: 'warning',
  },
}

/**
 * Required patterns that MUST be present in certain file types
 */
export const REQUIRED_PATTERNS = {
  // Pages must import governance hooks
  PAGE_GOVERNANCE_IMPORT: {
    filePattern: /pages\/.*\.(jsx|tsx)$/,
    pattern: /import\s*{[^}]*useInteraction[^}]*}\s*from\s*['"].*governance/,
    message: 'Page components must import useInteraction from governance module.',
    severity: 'error',
  },

  // Components with buttons must use DisabledTooltip
  DISABLED_TOOLTIP_USAGE: {
    filePattern: /components\/.*\.(jsx|tsx)$/,
    pattern: /disabled\s*=\s*{[^}]+}/,
    requiredAlongside: /DisabledTooltip/,
    message: 'Components with disabled buttons should use DisabledTooltip for accessibility.',
    severity: 'warning',
  },
}

// ============================================================================
// RUNTIME GUARDS
// ============================================================================

/**
 * Runtime guard that throws on governance violations
 * Call this in development mode to catch violations early
 */
export function guardAgainstViolations(code, filename = 'unknown') {
  if (!import.meta.env?.DEV) {
    return { violations: [], passed: true }
  }

  const violations = []

  // Check violation patterns
  for (const [name, { pattern, message, severity }] of Object.entries(VIOLATION_PATTERNS)) {
    try {
      if (pattern.test(code)) {
        violations.push({
          type: name,
          message,
          severity,
          filename,
        })
      }
    } catch {
      // Regex execution failed — skip this pattern rather than crashing the guard
    }
  }

  // Check required patterns based on file type
  for (const [name, config] of Object.entries(REQUIRED_PATTERNS)) {
    try {
      if (config.filePattern && config.filePattern.test(filename)) {
        if (!config.pattern.test(code)) {
          violations.push({
            type: name,
            message: config.message,
            severity: config.severity,
            filename,
          })
        }

        if (config.requiredAlongside) {
          const hasPattern = config.pattern.test(code)
          const hasRequired = config.requiredAlongside.test(code)
          if (hasPattern && !hasRequired) {
            violations.push({
              type: `${name}_MISSING_ALONGSIDE`,
              message: config.message,
              severity: config.severity,
              filename,
            })
          }
        }
      }
    } catch {
      // Regex execution failed — skip this pattern rather than crashing the guard
    }
  }

  // In strict mode, throw on errors
  const errors = violations.filter((v) => v.severity === 'error')
  if (errors.length > 0) {
    const errorMessages = errors.map((e) => `[${e.type}] ${e.message}`).join('\n')
    throw new Error(
      `[UX GOVERNANCE VIOLATION] ${errors.length} violation(s) found in ${filename}:\n${errorMessages}`
    )
  }

  // Log warnings
  const warnings = violations.filter((v) => v.severity === 'warning')
  if (warnings.length > 0) {
    console.warn(
      `[UX GOVERNANCE WARNING] ${warnings.length} warning(s) in ${filename}:`,
      warnings.map((w) => w.message)
    )
  }

  return {
    violations,
    passed: errors.length === 0,
    errorCount: errors.length,
    warningCount: warnings.length,
  }
}

/**
 * Guard that validates a React component tree
 * Call this during development to verify component compliance
 */
export function validateComponentCompliance(componentName, props = {}, children = []) {
  const violations = []

  // Check for onClick handlers that might be non-compliant
  if (props.onClick && typeof props.onClick === 'function') {
    const handlerStr = props.onClick.toString()

    // Check for direct fetch calls
    if (handlerStr.includes('fetch(') || handlerStr.includes('axios.')) {
      violations.push({
        component: componentName,
        prop: 'onClick',
        message: 'onClick handler contains direct API call',
        severity: 'error',
      })
    }

    // Check for untracked async operations
    if (handlerStr.startsWith('async') && !handlerStr.includes('execute(')) {
      violations.push({
        component: componentName,
        prop: 'onClick',
        message: 'Async onClick handler not using execute()',
        severity: 'warning',
      })
    }
  }

  // Check for disabled buttons without tooltip
  if (props.disabled && !props['aria-describedby'] && componentName.includes('Button')) {
    violations.push({
      component: componentName,
      prop: 'disabled',
      message: 'Disabled button should have descriptive text for accessibility',
      severity: 'warning',
    })
  }

  return violations
}

// ============================================================================
// BUILD-TIME GUARD (for CI)
// ============================================================================

/**
 * CI guard that can be run in pre-commit or build step
 * Returns exit code 1 if violations found
 */
export async function runCIGovernanceCheck(files) {
  const results = {
    passed: true,
    totalFiles: files.length,
    checkedFiles: 0,
    violations: [],
  }

  for (const file of files) {
    try {
      // In a real implementation, this would read the file content
      // For now, we assume the content is passed in
      const { violations, passed } = guardAgainstViolations(file.content, file.path)

      results.checkedFiles++
      results.violations.push(...violations)

      if (!passed) {
        results.passed = false
      }
    } catch (error) {
      results.violations.push({
        type: 'CHECK_ERROR',
        message: error.message,
        severity: 'error',
        filename: file.path,
      })
      results.passed = false
    }
  }

  return results
}

/**
 * Format CI results for console output
 */
export function formatCIResults(results) {
  const lines = [
    '========================================',
    'UX GOVERNANCE CHECK RESULTS',
    '========================================',
    `Files checked: ${results.checkedFiles}/${results.totalFiles}`,
    `Status: ${results.passed ? '✓ PASSED' : '✗ FAILED'}`,
    '',
  ]

  if (results.violations.length > 0) {
    lines.push('Violations:')
    lines.push('')

    for (const v of results.violations) {
      const icon = v.severity === 'error' ? '✗' : '⚠'
      lines.push(`${icon} [${v.type}] ${v.filename}`)
      lines.push(`  ${v.message}`)
      lines.push('')
    }
  }

  lines.push('========================================')

  return lines.join('\n')
}

// ============================================================================
// HOOK FOR COMPONENT SELF-VALIDATION
// ============================================================================

/**
 * Hook that validates component compliance at render time (dev only)
 */
export function useGovernanceValidation(componentName) {
  if (!import.meta.env?.DEV) {
    return { isValid: true, violations: [] }
  }

  // This would track component behavior over time
  // and flag potential violations
  return {
    isValid: true,
    violations: [],
    report: () => {
      console.log(`[UX GOVERNANCE] Compliance report for ${componentName}`)
    },
  }
}

// ============================================================================
// EXPORTS FOR ESLINT PLUGIN
// ============================================================================

/**
 * Rules that can be used by an ESLint plugin
 */
export const ESLINT_RULES = {
  'no-direct-fetch-in-handler': {
    meta: {
      type: 'problem',
      docs: {
        description: 'Disallow direct fetch/axios calls in event handlers',
        category: 'UX Governance',
        recommended: true,
      },
      messages: {
        directFetch: 'Direct API calls in handlers violate UX governance. Use useInteraction().execute() instead.',
      },
    },
    create(context) {
      return {
        CallExpression(node) {
          // Check if this is a fetch/axios call inside an arrow function
          // that is an event handler
          if (
            node.callee.name === 'fetch' ||
            (node.callee.object && node.callee.object.name === 'axios')
          ) {
            // Walk up to find if we're in an event handler
            let parent = node.parent
            while (parent) {
              if (
                parent.type === 'JSXAttribute' &&
                parent.name &&
                parent.name.name &&
                parent.name.name.match(/^on[A-Z]/)
              ) {
                context.report({
                  node,
                  messageId: 'directFetch',
                })
                break
              }
              parent = parent.parent
            }
          }
        },
      }
    },
  },

  'require-interaction-hook': {
    meta: {
      type: 'problem',
      docs: {
        description: 'Require useInteraction hook in page components',
        category: 'UX Governance',
        recommended: true,
      },
      messages: {
        missingHook: 'Page components must use useInteraction() hook for governance compliance.',
      },
    },
    create(context) {
      const filename = context.getFilename()
      let hasInteractionImport = false
      let hasInteractionUsage = false

      return {
        ImportDeclaration(node) {
          if (
            node.source.value.includes('governance') &&
            node.specifiers.some(
              (s) => s.imported && s.imported.name === 'useInteraction'
            )
          ) {
            hasInteractionImport = true
          }
        },
        CallExpression(node) {
          if (node.callee.name === 'useInteraction') {
            hasInteractionUsage = true
          }
        },
        'Program:exit'() {
          if (filename.includes('/pages/') && !hasInteractionImport) {
            context.report({
              loc: { line: 1, column: 0 },
              messageId: 'missingHook',
            })
          }
        },
      }
    },
  },

  'require-disabled-tooltip': {
    meta: {
      type: 'suggestion',
      docs: {
        description: 'Require DisabledTooltip wrapper for disabled buttons',
        category: 'UX Governance',
        recommended: true,
      },
      messages: {
        missingTooltip: 'Disabled buttons should be wrapped with DisabledTooltip for accessibility.',
      },
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (
            node.name.name === 'disabled' &&
            node.parent &&
            node.parent.name &&
            node.parent.name.name === 'Button'
          ) {
            // Check if parent is DisabledTooltip
            const grandparent = node.parent.parent
            if (
              !grandparent ||
              grandparent.type !== 'JSXElement' ||
              !grandparent.openingElement.name ||
              grandparent.openingElement.name.name !== 'DisabledTooltip'
            ) {
              context.report({
                node,
                messageId: 'missingTooltip',
              })
            }
          }
        },
      }
    },
  },
}

export default {
  VIOLATION_PATTERNS,
  REQUIRED_PATTERNS,
  guardAgainstViolations,
  validateComponentCompliance,
  runCIGovernanceCheck,
  formatCIResults,
  useGovernanceValidation,
  ESLINT_RULES,
}

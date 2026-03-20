/**
 * UX Governance: Intent Tracking System
 *
 * Every user action generates an intent that flows:
 * UI -> Interaction API -> Backend -> Audit Log
 *
 * This provides:
 * - Complete audit trail
 * - Action correlation
 * - Error diagnosis
 * - User behavior analytics
 */
import { createContext, useContext } from 'react'
import { sessionId } from './intentConstants'
import { useIntentProvider } from './hooks/useIntentProvider'

// Re-export constants for backwards compatibility
export { IntentStatus, createIntent, createIntentHeaders, createIntentInterceptor } from './intentConstants'

// ============================================================================
// CONTEXT
// ============================================================================

const IntentContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function IntentProvider({ children, onIntentChange, maxHistory = 100, auditClient }) {
  const value = useIntentProvider({ onIntentChange, maxHistory, auditClient })

  const contextValue = {
    ...value,
    sessionId,
  }

  return (
    <IntentContext.Provider value={contextValue}>
      {children}
    </IntentContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useIntent() {
  const context = useContext(IntentContext)
  if (!context) {
    throw new Error('useIntent must be used within IntentProvider')
  }
  return context
}

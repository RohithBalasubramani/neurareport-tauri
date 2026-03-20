/**
 * ENFORCEMENT: Development-time checks
 * These functions help identify non-compliant patterns during development
 */
import { InteractionType } from './InteractionAPI'

export const GovernanceEnforcement = {
  /**
   * Wrap a raw event handler to emit warnings in development
   * @deprecated Use useInteraction().execute() instead
   */
  warnOnRawHandler: (handlerName, handler) => {
    if (import.meta.env?.DEV) {
      return (...args) => {
        console.warn(
          `[UX GOVERNANCE VIOLATION] Raw handler "${handlerName}" called without interaction API.\n` +
          `Replace with: const { execute } = useInteraction()\n` +
          `execute({ type: InteractionType.*, label: "...", action: async () => {...} })`
        )
        return handler(...args)
      }
    }
    return handler
  },

  /**
   * Assert that a component is using the interaction API
   * Call this in useEffect to verify compliance
   */
  assertCompliance: (componentName, hasInteractionHook) => {
    if (import.meta.env?.DEV && !hasInteractionHook) {
      console.error(
        `[UX GOVERNANCE VIOLATION] Component "${componentName}" has user interactions ` +
        `but is not using useInteraction() hook. This is a compliance violation.`
      )
    }
  },

  /**
   * List of patterns that should never appear in compliant code
   */
  NON_COMPLIANT_PATTERNS: [
    'onClick={() => fetch',      // Direct fetch in onClick
    'onClick={() => axios',      // Direct axios in onClick
    'onClick={async () =>',      // Async handlers without tracking
    'onSubmit={() => fetch',     // Direct fetch in form submit
    'onClick={() => delete',     // Unconfirmed deletes
    '.mutate({ onSuccess:',      // React Query without operation tracking
  ],
}

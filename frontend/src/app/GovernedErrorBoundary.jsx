/**
 * Error Boundary wrapped with UX Governance
 */
import { useCallback } from 'react'
import ErrorBoundary from '@/components/ErrorBoundary.jsx'
import {
  useInteraction,
  useNavigateInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'

export default function GovernedErrorBoundary({ children }) {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'error-boundary', ...intent },
      action,
    })
  }, [execute])

  const handleReload = useCallback(
    () => executeUI('Reload application', () => window.location.reload(), { action: 'reload' }),
    [executeUI],
  )

  const handleGoHome = useCallback(
    () => navigate('/', { label: 'Go to dashboard', intent: { source: 'error-boundary' } }),
    [navigate],
  )

  return (
    <ErrorBoundary onReload={handleReload} onGoHome={handleGoHome}>
      {children}
    </ErrorBoundary>
  )
}

/**
 * useCrossPageActions – Primary hook for inter-page data flow.
 *
 * Producer pages use: registerOutput(), sendTo(), getAvailableTargets()
 * Consumer pages use: consumeIncoming(), getAvailableOutputs()
 */
import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import useCrossPageStore from '@/stores/crossPageStore'
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import { useToast } from '@/components/ToastProvider'
import {
  FEATURE_ACCEPTS,
  FEATURE_ROUTES,
  FEATURE_LABELS,
  FEATURE_ACTIONS,
} from '@/utils/crossPageTypes'

export default function useCrossPageActions(currentFeatureKey) {
  const navigate = useNavigate()
  const { execute } = useInteraction()
  const toast = useToast()
  const setPendingTransfer = useCrossPageStore((s) => s.setPendingTransfer)
  const consumeTransfer = useCrossPageStore((s) => s.consumeTransfer)
  const registerOutputFn = useCrossPageStore((s) => s.registerOutput)
  const getAllOutputs = useCrossPageStore((s) => s.getAllOutputs)

  const sendTo = useCallback(
    (targetFeatureKey, action, payload, options = {}) => {
      const targetRoute = FEATURE_ROUTES[targetFeatureKey]
      if (!targetRoute) return Promise.resolve()

      const targetLabel = FEATURE_LABELS[targetFeatureKey] || targetFeatureKey

      return execute({
        type: InteractionType.EXECUTE,
        label: options.label || `Send to ${targetLabel}`,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: {
          source: currentFeatureKey,
          target: targetFeatureKey,
          action,
          crossPage: true,
        },
        action: async () => {
          setPendingTransfer({
            target: targetFeatureKey,
            action,
            payload,
            source: currentFeatureKey,
          })
          navigate(targetRoute)
          toast.show(
            options.successMessage || `Opening in ${targetLabel}...`,
            'info',
          )
        },
      })
    },
    [currentFeatureKey, execute, navigate, setPendingTransfer, toast],
  )

  const consumeIncoming = useCallback(
    () => consumeTransfer(currentFeatureKey),
    [consumeTransfer, currentFeatureKey],
  )

  const registerOutput = useCallback(
    (output) => registerOutputFn(currentFeatureKey, output),
    [currentFeatureKey, registerOutputFn],
  )

  const getAvailableTargets = useCallback(
    (outputType) =>
      Object.entries(FEATURE_ACCEPTS)
        .filter(
          ([key, accepts]) =>
            key !== currentFeatureKey && accepts.includes(outputType),
        )
        .map(([key]) => ({
          key,
          route: FEATURE_ROUTES[key],
          label: FEATURE_LABELS[key] || key,
          actionInfo: FEATURE_ACTIONS[key] || null,
        })),
    [currentFeatureKey],
  )

  const getAvailableOutputs = useCallback(() => {
    const accepts = FEATURE_ACCEPTS[currentFeatureKey] || []
    return getAllOutputs().filter(
      (o) => o.featureKey !== currentFeatureKey && accepts.includes(o.type),
    )
  }, [currentFeatureKey, getAllOutputs])

  return {
    sendTo,
    consumeIncoming,
    registerOutput,
    getAvailableTargets,
    getAvailableOutputs,
  }
}

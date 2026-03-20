import { useState, useCallback, useEffect } from 'react'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import * as api from '@/api/client'

export function useStepMapping({ wizardState, updateWizardState }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const templateId = useAppStore((s) => s.templateId) || wizardState.templateId
  const activeConnection = useAppStore((s) => s.activeConnection)
  const setLastApprovedTemplate = useAppStore((s) => s.setLastApprovedTemplate)

  const [loading, setLocalLoading] = useState(false)
  const [mapping, setMapping] = useState(wizardState.mapping || {})
  const [keys, setKeys] = useState(wizardState.keys || [])
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [approving, setApproving] = useState(false)
  const [approved, setApproved] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    const fetchMapping = async () => {
      if (!templateId) return

      setLocalLoading(true)
      try {
        const connectionId = wizardState.connectionId || activeConnection?.id
        await execute({
          type: InteractionType.ANALYZE,
          label: 'Load mapping preview',
          reversibility: Reversibility.SYSTEM_MANAGED,
          suppressSuccessToast: true,
          suppressErrorToast: true,
          blocksNavigation: false,
          intent: {
            connectionId,
            templateId,
            templateKind: wizardState.templateKind || 'pdf',
            action: 'mapping_preview',
          },
          action: async () => {
            try {
              const result = await api.mappingPreview(templateId, connectionId, {
                kind: wizardState.templateKind || 'pdf',
              })

              if (!cancelled) {
                if (result.mapping) {
                  setMapping(result.mapping)
                  updateWizardState({ mapping: result.mapping })
                }
                if (result.keys) {
                  setKeys(result.keys)
                  updateWizardState({ keys: result.keys })
                }
              }
              return result
            } catch (err) {
              if (!cancelled) {
                setError(err.message || 'Failed to load mapping')
              }
              throw err
            }
          },
        })
      } finally {
        if (!cancelled) {
          setLocalLoading(false)
        }
      }
    }

    if (!wizardState.mapping) {
      fetchMapping()
    }

    return () => { cancelled = true }
  }, [templateId, wizardState.connectionId, wizardState.templateKind, wizardState.mapping, activeConnection?.id, updateWizardState, execute])

  const handleMappingChange = useCallback((token, field, value) => {
    setMapping((prev) => ({
      ...prev,
      [token]: {
        ...prev[token],
        [field]: value,
      },
    }))
  }, [])

  const handleApprove = useCallback(async () => {
    setApproving(true)
    setError(null)

    try {
      const connectionId = wizardState.connectionId || activeConnection?.id

      await execute({
        type: InteractionType.UPDATE,
        label: 'Approve template mapping',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: true,
        intent: {
          connectionId,
          templateId,
          templateKind: wizardState.templateKind || 'pdf',
          action: 'mapping_approve',
        },
        action: async () => {
          try {
            const result = await api.mappingApprove(templateId, mapping, {
              connectionId,
              keys,
              kind: wizardState.templateKind || 'pdf',
              onProgress: () => {},
            })

            if (result.ok) {
              setApproved(true)
              setLastApprovedTemplate({
                id: templateId,
                name: wizardState.templateName,
                kind: wizardState.templateKind,
              })
              toast.show('Template approved and ready to use!', 'success')
            }
            return result
          } catch (err) {
            setError(err.message || 'Failed to approve mapping')
            toast.show(err.message || 'Failed to approve mapping', 'error')
            throw err
          }
        },
      })
    } finally {
      setApproving(false)
    }
  }, [templateId, mapping, keys, wizardState, activeConnection?.id, setLastApprovedTemplate, toast, execute])

  return {
    loading,
    mapping,
    keys,
    setKeys,
    showAdvanced,
    setShowAdvanced,
    approving,
    approved,
    error,
    setError,
    handleMappingChange,
    handleApprove,
  }
}

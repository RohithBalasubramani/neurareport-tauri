import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { composeDateTimeString } from './useReportDateRange'
import * as api from '@/api/client'

export default function useReportGeneration({
  selectedTemplate,
  activeConnection,
  templates,
  startDate,
  endDate,
  startTime,
  endTime,
  keyValues,
  discovery,
  selectedBatches,
  celebrate,
}) {
  const [generating, setGenerating] = useState(false)
  const [generatingDocx, setGeneratingDocx] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const toast = useToast()
  const { execute } = useInteraction()

  const handleGenerate = useCallback(async () => {
    if (!selectedTemplate || !activeConnection?.id) {
      toast.show('Please select a design and connect to a data source first', 'error')
      return
    }
    if (discovery && selectedBatches.length === 0) {
      toast.show('Select at least one batch to run', 'error')
      return
    }
    {
      const sf = composeDateTimeString(startDate, startTime)
      const ef = composeDateTimeString(endDate, endTime)
      if (sf && ef && new Date(sf) > new Date(ef)) {
        toast.show('Start date/time must be before or equal to end date/time', 'error')
        return
      }
    }

    await execute({
      type: InteractionType.EXECUTE,
      label: 'Generate report',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId: selectedTemplate,
        connectionId: activeConnection?.id,
        action: 'run_report',
      },
      action: async () => {
        setGenerating(true)
        setError(null)
        setResult(null)

        try {
          const template = templates.find((t) => t.id === selectedTemplate)

          const batches = discovery?.batches || []
          const allSelected = batches.length > 0 && selectedBatches.length === batches.length
          const useSelectedBatches = batches.length > 0 && selectedBatches.length > 0 && !allSelected

          const reportResult = await api.runReportAsJob({
            templateId: selectedTemplate,
            templateName: template?.name,
            connectionId: activeConnection.id,
            startDate: composeDateTimeString(startDate, startTime) || undefined,
            endDate: composeDateTimeString(endDate, endTime) || undefined,
            keyValues: (() => { const kv = Object.fromEntries(Object.entries(keyValues).filter(([, v]) => Array.isArray(v) ? v.length > 0 : !!v)); return Object.keys(kv).length > 0 ? kv : undefined })(),
            batchIds: useSelectedBatches ? selectedBatches : undefined,
            kind: template?.kind || 'pdf',
            xlsx: template?.kind === 'excel',
          })

          setResult(reportResult)
          toast.show('Report generation started!', 'success')
          celebrate()
          return reportResult
        } catch (err) {
          setError(err.message || 'Failed to generate report')
          toast.show(err.message || 'Failed to generate report', 'error')
          throw err
        } finally {
          setGenerating(false)
        }
      },
    })
  }, [selectedTemplate, activeConnection?.id, templates, startDate, endDate, startTime, endTime, keyValues, discovery, selectedBatches, toast, celebrate, execute])

  const handleGenerateDocx = useCallback(async (runId, fetchRunHistory) => {
    setGeneratingDocx(runId)
    try {
      const docxResult = await api.generateDocxJob(runId)
      if (docxResult.status === 'already_exists') {
        toast.show('DOCX already available', 'success')
        fetchRunHistory()
      } else {
        toast.show('DOCX conversion queued — track progress in Report Progress', 'success')
      }
    } catch (err) {
      console.error('DOCX generation failed:', err)
      toast.show('DOCX generation failed — check backend logs', 'error')
    } finally {
      setGeneratingDocx(null)
    }
  }, [toast])

  return {
    generating,
    generatingDocx,
    result,
    setResult,
    error,
    setError,
    handleGenerate,
    handleGenerateDocx,
  }
}

import { useState, useCallback } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { composeDateTimeString } from './useReportDateRange'
import * as api from '@/api/client'

export default function useReportDiscovery({
  selectedTemplate,
  activeConnection,
  templates,
  startDate,
  endDate,
  startTime,
  endTime,
  keyValues,
}) {
  const [discovering, setDiscovering] = useState(false)
  const [discovery, setDiscovery] = useState(null)
  const [batchDiscoveryOpen, setBatchDiscoveryOpen] = useState(false)
  const [selectedBatches, setSelectedBatches] = useState([])

  const toast = useToast()
  const { execute } = useInteraction()

  const handleDiscover = useCallback(async () => {
    if (!selectedTemplate || !activeConnection?.id) {
      toast.show('Select a design and data source first', 'error')
      return
    }
    if (!startDate || !endDate) {
      toast.show('Provide a start and end date to discover batches', 'error')
      return
    }
    {
      const sf = composeDateTimeString(startDate, startTime)
      const ef = composeDateTimeString(endDate, endTime)
      if (new Date(sf) > new Date(ef)) {
        toast.show('Start date/time must be before or equal to end date/time', 'error')
        return
      }
    }
    await execute({
      type: InteractionType.ANALYZE,
      label: 'Discover batches',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId: selectedTemplate,
        connectionId: activeConnection?.id,
        action: 'discover_batches',
      },
      action: async () => {
        setDiscovering(true)
        setDiscovery(null)
        try {
          const template = templates.find((t) => t.id === selectedTemplate)
          const data = await api.discoverReports({
            templateId: selectedTemplate,
            connectionId: activeConnection.id,
            startDate: composeDateTimeString(startDate, startTime),
            endDate: composeDateTimeString(endDate, endTime),
            keyValues: Object.keys(keyValues).length > 0 ? keyValues : undefined,
            kind: template?.kind || 'pdf',
          })
          setDiscovery(data)
          const batchIds = Array.isArray(data?.batches) ? data.batches.map((batch) => batch.id) : []
          setSelectedBatches(batchIds)
          return data
        } catch (err) {
          toast.show(err.message || 'Failed to discover batches', 'error')
          throw err
        } finally {
          setDiscovering(false)
        }
      },
    })
  }, [selectedTemplate, activeConnection?.id, startDate, endDate, startTime, endTime, keyValues, templates, toast, execute])

  const toggleBatch = useCallback((batchId) => {
    setSelectedBatches((prev) => {
      if (prev.includes(batchId)) {
        return prev.filter((id) => id !== batchId)
      }
      return [...prev, batchId]
    })
  }, [])

  const handleSelectAllBatches = useCallback(() => {
    const allIds = Array.isArray(discovery?.batches) ? discovery.batches.map((batch) => batch.id) : []
    setSelectedBatches(allIds)
  }, [discovery])

  const handleClearBatches = useCallback(() => {
    setSelectedBatches([])
  }, [])

  const resetDiscovery = useCallback(() => {
    setDiscovery(null)
    setSelectedBatches([])
  }, [])

  return {
    discovering,
    discovery,
    batchDiscoveryOpen,
    setBatchDiscoveryOpen,
    selectedBatches,
    handleDiscover,
    toggleBatch,
    handleSelectAllBatches,
    handleClearBatches,
    resetDiscovery,
  }
}

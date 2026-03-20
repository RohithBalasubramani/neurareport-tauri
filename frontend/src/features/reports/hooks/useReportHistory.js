import { useState, useCallback, useEffect, useRef } from 'react'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import * as api from '@/api/client'
import * as summaryApi from '@/api/summary'

export default function useReportHistory() {
  const [runHistory, setRunHistory] = useState([])
  const [selectedRun, setSelectedRun] = useState(null)
  const [runSummary, setRunSummary] = useState(null)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(false)

  const toast = useToast()
  const { execute } = useInteraction()
  const summaryRequestIdRef = useRef(0)

  // Additional state that lives outside the 5-useState limit but is tightly coupled
  const [queueingSummary, setQueueingSummary] = useState(false)
  const [expandedRunId, setExpandedRunId] = useState(null)

  const fetchRunHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const runs = await api.listReportRuns({ limit: 10 })
      setRunHistory(runs)
    } catch (err) {
      console.error('Failed to load run history:', err)
      toast.show('Failed to load run history', 'warning')
    } finally {
      setHistoryLoading(false)
    }
  }, [toast])

  useEffect(() => {
    fetchRunHistory()
  }, [fetchRunHistory])

  const handleSelectRun = useCallback(async (run) => {
    // Toggle: clicking the same run collapses it
    if (selectedRun?.id === run.id) {
      setSelectedRun(null)
      setExpandedRunId(null)
      setRunSummary(null)
      return
    }

    setSelectedRun(run)
    setExpandedRunId(run.id)
    setRunSummary(null)

    if (run?.id) {
      const requestId = ++summaryRequestIdRef.current

      setSummaryLoading(true)
      try {
        const summaryData = await summaryApi.getReportSummary(run.id)

        if (requestId === summaryRequestIdRef.current) {
          setRunSummary(summaryData.summary || summaryData)
        }
      } catch (err) {
        if (requestId === summaryRequestIdRef.current) {
          console.error('Failed to fetch summary:', err)
          setRunSummary(null)
        }
      } finally {
        if (requestId === summaryRequestIdRef.current) {
          setSummaryLoading(false)
        }
      }
    }
  }, [selectedRun?.id])

  const handleQueueSummary = useCallback(async () => {
    if (!selectedRun?.id) return
    await execute({
      type: InteractionType.GENERATE,
      label: 'Queue summary',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        runId: selectedRun?.id,
        action: 'queue_report_summary',
      },
      action: async () => {
        setQueueingSummary(true)
        try {
          const response = await summaryApi.queueReportSummary(selectedRun.id)
          const jobId = response?.job_id || response?.jobId || null
          if (jobId) {
            toast.show('Summary queued. Track progress in Report Progress.', 'success')
          } else {
            toast.show('Failed to queue summary.', 'error')
          }
          return response
        } catch (err) {
          toast.show(err?.message || 'Failed to queue summary.', 'error')
          throw err
        } finally {
          setQueueingSummary(false)
        }
      },
    })
  }, [selectedRun?.id, toast, execute])

  return {
    runHistory,
    selectedRun,
    runSummary,
    historyLoading,
    summaryLoading,
    queueingSummary,
    expandedRunId,
    fetchRunHistory,
    handleSelectRun,
    handleQueueSummary,
  }
}

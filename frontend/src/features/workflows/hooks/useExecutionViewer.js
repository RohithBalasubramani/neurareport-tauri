/**
 * Hook for ExecutionViewer state and derived data.
 */
import { useState, useEffect, useMemo, useRef } from 'react'

export function useExecutionViewer(execution) {
  const logsEndRef = useRef(null)
  const [autoScroll, setAutoScroll] = useState(true)

  // Auto scroll to bottom of logs
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [execution?.steps, autoScroll])

  // Calculate progress
  const progress = useMemo(() => {
    if (!execution?.steps?.length) return 0
    const completed = execution.steps.filter((s) => ['success', 'error', 'skipped'].includes(s.status)).length
    return (completed / execution.steps.length) * 100
  }, [execution?.steps])

  // Calculate totals
  const stats = useMemo(() => {
    if (!execution?.steps) return { success: 0, error: 0, pending: 0 }
    return {
      success: execution.steps.filter((s) => s.status === 'success').length,
      error: execution.steps.filter((s) => s.status === 'error').length,
      pending: execution.steps.filter((s) => s.status === 'pending').length,
      running: execution.steps.filter((s) => s.status === 'running').length,
    }
  }, [execution?.steps])

  return { logsEndRef, autoScroll, setAutoScroll, progress, stats }
}

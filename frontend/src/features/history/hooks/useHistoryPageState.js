/**
 * Custom hook: all state + effects + handlers for HistoryPage
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import * as api from '@/api/client'

export function useHistoryPageState() {
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const toast = useToast()
  const { execute } = useInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'history', ...intent } }),
    [navigate]
  )
  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'history', ...intent },
      action,
    })
  }, [execute])

  const executeDownload = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.DOWNLOAD,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'history', ...intent },
      action,
    })
  }, [execute])
  const templates = useAppStore((s) => s.templates)
  const didLoadRef = useRef(false)
  const bulkDeleteUndoRef = useRef(null)

  const initialStatus = searchParams.get('status') || ''
  const initialTemplate = searchParams.get('template') || ''

  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)
  const [statusFilter, setStatusFilter] = useState(initialStatus)
  const [templateFilter, setTemplateFilter] = useState(initialTemplate)
  const [selectedIds, setSelectedIds] = useState([])
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const [bulkDeleting, setBulkDeleting] = useState(false)

  const fetchHistory = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getReportHistory({
        limit: rowsPerPage,
        offset: page * rowsPerPage,
        status: statusFilter || undefined,
        templateId: templateFilter || undefined,
      })
      setHistory(data?.history || [])
      setTotal(data?.total || 0)
    } catch (err) {
      toast.show(err.message || 'Failed to load report history', 'error')
    } finally {
      setLoading(false)
    }
  }, [page, rowsPerPage, statusFilter, templateFilter, toast])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchHistory()
  }, [fetchHistory])

  useEffect(() => {
    const nextStatus = searchParams.get('status') || ''
    const nextTemplate = searchParams.get('template') || ''
    if (nextStatus !== statusFilter) setStatusFilter(nextStatus)
    if (nextTemplate !== templateFilter) setTemplateFilter(nextTemplate)
  }, [searchParams, statusFilter, templateFilter])

  useEffect(() => {
    if (!didLoadRef.current) return
    fetchHistory()
  }, [page, rowsPerPage, statusFilter, templateFilter, fetchHistory])

  const syncParams = useCallback((nextStatus, nextTemplate) => {
    const next = new URLSearchParams(searchParams)
    if (nextStatus) next.set('status', nextStatus)
    else next.delete('status')
    if (nextTemplate) next.set('template', nextTemplate)
    else next.delete('template')
    setSearchParams(next, { replace: true })
  }, [searchParams, setSearchParams])

  const handleDownload = useCallback((report, format) => {
    return executeDownload('Download report output', () => {
      const artifacts = report.artifacts || {}
      let url = null

      if (format === 'pdf' && artifacts.pdf_url) url = artifacts.pdf_url
      else if (format === 'html' && artifacts.html_url) url = artifacts.html_url
      else if (format === 'docx' && artifacts.docx_url) url = artifacts.docx_url
      else if (format === 'xlsx' && artifacts.xlsx_url) url = artifacts.xlsx_url

      if (url) {
        const fullUrl = api.withBase(url)
        const filename = `${report.templateName || 'report'}.${format}`
        toast.show(`Downloading ${filename}…`, 'info')
        fetch(fullUrl)
          .then((res) => {
            if (!res.ok) throw new Error(`Download failed: ${res.status}`)
            return res.blob()
          })
          .then((blob) => {
            const blobUrl = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = blobUrl
            a.download = filename
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(blobUrl)
            toast.show(`Downloaded ${filename}`, 'success')
          })
          .catch((err) => {
            console.error('[download]', err)
            toast.show(`Download failed: ${err.message}`, 'error')
          })
      } else {
        toast.show('Download not available', 'warning')
      }
    }, { reportId: report?.id, format })
  }, [executeDownload, toast])

  const handleDownloadClick = useCallback((event, report, format) => {
    event.stopPropagation()
    handleDownload(report, format)
  }, [handleDownload])

  const handleRowClick = useCallback((row) => {
    const artifacts = row.artifacts || {}
    if (artifacts.html_url || artifacts.pdf_url) {
      const url = artifacts.html_url || artifacts.pdf_url
      return executeDownload('Open report output', () => {
        window.open(api.withBase(url), '_blank')
      }, { reportId: row?.id, format: artifacts.html_url ? 'html' : 'pdf' })
    }
    return handleNavigate('/jobs', 'Open jobs', { reportId: row?.id })
  }, [executeDownload, handleNavigate])

  const handleBulkDeleteConfirm = useCallback(async () => {
    if (!selectedIds.length) return
    const idsToDelete = [...selectedIds]
    const removedRecords = history.filter((record) => idsToDelete.includes(record.id))
    const prevHistory = history
    const prevTotal = total
    if (!removedRecords.length) {
      setBulkDeleteOpen(false)
      return
    }

    setBulkDeleteOpen(false)
    setSelectedIds([])

    if (bulkDeleteUndoRef.current?.timeoutId) {
      clearTimeout(bulkDeleteUndoRef.current.timeoutId)
      bulkDeleteUndoRef.current = null
    }

    setHistory((prev) => prev.filter((record) => !idsToDelete.includes(record.id)))
    setTotal((prev) => Math.max(0, prev - removedRecords.length))

    let undone = false
    const timeoutId = setTimeout(async () => {
      if (undone) return
      await execute({
        type: InteractionType.DELETE,
        label: 'Delete history records',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          jobIds: idsToDelete,
          action: 'bulk_delete_history',
        },
        action: async () => {
          setBulkDeleting(true)
          try {
            const result = await api.bulkDeleteJobs(idsToDelete)
            const deletedCount = result?.deletedCount ?? result?.deleted?.length ?? 0
            const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
            if (failedCount > 0) {
              toast.show(
                `Removed ${deletedCount} record${deletedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
                'warning'
              )
            } else {
              toast.show(`Removed ${deletedCount} history record${deletedCount !== 1 ? 's' : ''}`, 'success')
            }
            fetchHistory()
            return result
          } catch (err) {
            setHistory(prevHistory)
            setTotal(prevTotal)
            toast.show(err.message || 'Failed to delete history records', 'error')
            throw err
          } finally {
            setBulkDeleting(false)
            bulkDeleteUndoRef.current = null
          }
        },
      })
    }, 5000)

    bulkDeleteUndoRef.current = { timeoutId, ids: idsToDelete, records: removedRecords }

    toast.showWithUndo(
      `Removed ${idsToDelete.length} history record${idsToDelete.length !== 1 ? 's' : ''}`,
      () => {
        undone = true
        clearTimeout(timeoutId)
        bulkDeleteUndoRef.current = null
        setHistory(prevHistory)
        setTotal(prevTotal)
        toast.show('History restored', 'success')
      },
      { severity: 'info' }
    )
  }, [selectedIds, history, total, toast, fetchHistory, execute])

  const handleBulkDeleteOpen = useCallback(() => {
    if (!selectedIds.length) return undefined
    return executeUI('Review delete history', () => setBulkDeleteOpen(true), { count: selectedIds.length })
  }, [executeUI, selectedIds])

  const handleBulkDeleteClose = useCallback(() => {
    return executeUI('Close delete history', () => setBulkDeleteOpen(false))
  }, [executeUI])

  const handleSelectionChange = useCallback((nextSelection) => {
    return executeUI('Select history entries', () => setSelectedIds(nextSelection), { count: nextSelection.length })
  }, [executeUI])

  const handleStatusFilterChange = useCallback((nextStatus) => {
    return executeUI('Filter history by status', () => {
      setStatusFilter(nextStatus)
      setPage(0)
      syncParams(nextStatus, templateFilter)
    }, { status: nextStatus })
  }, [executeUI, syncParams, templateFilter])

  const handleTemplateFilterChange = useCallback((nextTemplate) => {
    return executeUI('Filter history by template', () => {
      setTemplateFilter(nextTemplate)
      setPage(0)
      syncParams(statusFilter, nextTemplate)
    }, { templateId: nextTemplate })
  }, [executeUI, syncParams, statusFilter])

  const handleRefresh = useCallback(() => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Refresh history',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { from: 'history', action: 'refresh_history' },
      action: async () => {
        await fetchHistory()
      },
    })
  }, [execute, fetchHistory])

  const handlePageChange = useCallback((nextPage) => {
    return executeUI('Change history page', () => setPage(nextPage), { page: nextPage })
  }, [executeUI])

  const handleRowsPerPageChange = useCallback((nextRows) => {
    return executeUI('Change history page size', () => {
      setRowsPerPage(nextRows)
      setPage(0)
    }, { rowsPerPage: nextRows })
  }, [executeUI])

  return {
    // Data
    history,
    loading,
    total,
    page,
    rowsPerPage,
    statusFilter,
    templateFilter,
    selectedIds,
    bulkDeleteOpen,
    bulkDeleting,
    templates,

    // Handlers
    handleNavigate,
    handleDownload,
    handleDownloadClick,
    handleRowClick,
    handleBulkDeleteConfirm,
    handleBulkDeleteOpen,
    handleBulkDeleteClose,
    handleSelectionChange,
    handleStatusFilterChange,
    handleTemplateFilterChange,
    handleRefresh,
    handlePageChange,
    handleRowsPerPageChange,
  }
}

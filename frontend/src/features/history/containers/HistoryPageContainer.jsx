/**
 * Premium History Page
 * Sophisticated report history with glassmorphism and animations
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Typography,
  Stack,
  IconButton,
  Chip,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Button,
  Alert,
  Tooltip,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import HistoryIcon from '@mui/icons-material/History'
import DownloadIcon from '@mui/icons-material/Download'
import DeleteIcon from '@mui/icons-material/Delete'
import VisibilityIcon from '@mui/icons-material/Visibility'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import ArticleIcon from '@mui/icons-material/Article'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import CancelIcon from '@mui/icons-material/Cancel'
import AddIcon from '@mui/icons-material/Add'
import { DataTable } from '@/components/DataTable'
import { ConfirmModal } from '@/components/Modal'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import * as api from '@/api/client'
import { neutral, palette } from '@/app/theme'
import { fadeInUp, float, StyledFormControl, RefreshButton } from '@/styles'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1400,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

const PageHeader = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

const PageTitle = styled(Typography)(({ theme }) => ({
  fontSize: '1.75rem',
  fontWeight: 600,
  letterSpacing: '-0.02em',
  color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
}))

const FilterContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out 0.1s both`,
}))

const TableContainer = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(20px)',
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  overflow: 'hidden',
  animation: `${fadeInUp} 0.6s ease-out 0.2s both`,
}))

const EmptyStateContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(8, 4),
  textAlign: 'center',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
}))

const EmptyIcon = styled(HistoryIcon)(({ theme }) => ({
  fontSize: 64,
  color: alpha(theme.palette.text.secondary, 0.3),
  marginBottom: theme.spacing(2),
  animation: `${float} 3s ease-in-out infinite`,
}))

const PrimaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '0.875rem',
  padding: theme.spacing(1, 2.5),
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-2px)',
  },
}))

const SecondaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  borderColor: alpha(theme.palette.divider, 0.3),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  },
}))

const KindIconContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'iconColor',
})(({ theme }) => ({
  width: 36,
  height: 36,
  borderRadius: 8,  // Figma spec: 8px
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const StatusChip = styled(Chip, {
  shouldForwardProp: (prop) => !['statusColor', 'statusBg'].includes(prop),
})(({ theme, statusColor, statusBg }) => ({
  borderRadius: 8,
  fontWeight: 600,
  fontSize: '12px',
  backgroundColor: statusBg,
  color: statusColor,
  '& .MuiChip-icon': {
    marginLeft: theme.spacing(0.5),
    color: statusColor,
  },
}))

const ArtifactButton = styled(IconButton)(({ theme }) => ({
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'translateY(-2px)',
  },
}))

// =============================================================================
// STATUS AND KIND CONFIG HELPERS
// =============================================================================

const getStatusConfig = (theme, status) => {
  const configs = {
    completed: {
      icon: CheckCircleIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Completed',
    },
    failed: {
      icon: ErrorIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Failed',
    },
    running: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
      label: 'Running',
    },
    pending: {
      icon: HourglassEmptyIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
      label: 'Pending',
    },
    cancelled: {
      icon: CancelIcon,
      color: theme.palette.text.secondary,
      bgColor: alpha(theme.palette.text.secondary, 0.08),
      label: 'Cancelled',
    },
  }
  return configs[status] || configs.pending
}

const getKindConfig = (theme, kind) => {
  const configs = {
    pdf: { icon: PictureAsPdfIcon, color: theme.palette.text.secondary },
    excel: { icon: TableChartIcon, color: theme.palette.text.secondary },
  }
  return configs[kind] || configs.pdf
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function HistoryPage() {
  const theme = useTheme()
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
        window.open(api.withBase(url), '_blank')
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

  const bulkActions = [
    {
      label: 'Delete Selected',
      icon: <DeleteIcon sx={{ fontSize: 16 }} />,
      color: 'error',
      onClick: handleBulkDeleteOpen,
    },
  ]

  const columns = [
    {
      field: 'templateName',
      headerName: 'Design',
      renderCell: (value, row) => {
        const kind = row.templateKind || 'pdf'
        const cfg = getKindConfig(theme, kind)
        const Icon = cfg.icon
        return (
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <KindIconContainer>
              <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
            </KindIconContainer>
            <Box>
              <Typography sx={{ fontSize: '14px', fontWeight: 500, color: 'text.primary' }}>
                {value || 'Unknown'}
              </Typography>
              <Typography sx={{ fontSize: '12px', color: 'text.secondary' }}>
                {kind.toUpperCase()}
              </Typography>
            </Box>
          </Stack>
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (value) => {
        const cfg = getStatusConfig(theme, value)
        const Icon = cfg.icon
        return (
          <StatusChip
            icon={<Icon sx={{ fontSize: 14 }} />}
            label={cfg.label}
            size="small"
            statusColor={cfg.color}
            statusBg={cfg.bgColor}
          />
        )
      },
    },
    {
      field: 'createdAt',
      headerName: 'Started',
      width: 160,
      renderCell: (value) => (
        <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
          {value ? new Date(value).toLocaleString() : '-'}
        </Typography>
      ),
    },
    {
      field: 'completedAt',
      headerName: 'Completed',
      width: 160,
      renderCell: (value) => (
        <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
          {value ? new Date(value).toLocaleString() : '-'}
        </Typography>
      ),
    },
    {
      field: 'artifacts',
      headerName: 'Downloads',
      width: 150,
      renderCell: (value, row) => {
        const artifacts = value || {}
        const hasAny = artifacts.pdf_url || artifacts.html_url || artifacts.docx_url || artifacts.xlsx_url
        if (!hasAny) {
          return (
            <Typography sx={{ fontSize: '0.75rem', color: 'text.disabled' }}>
              {row.status === 'completed' ? 'No files' : '-'}
            </Typography>
          )
        }
        return (
          <Stack direction="row" spacing={0.5}>
            {artifacts.pdf_url && (
              <Tooltip title="Download PDF">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'pdf')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download PDF"
                >
                  <PictureAsPdfIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.html_url && (
              <Tooltip title="View HTML">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'html')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="View HTML"
                >
                  <VisibilityIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.docx_url && (
              <Tooltip title="Download DOCX">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'docx')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download DOCX"
                >
                  <ArticleIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
            {artifacts.xlsx_url && (
              <Tooltip title="Download XLSX">
                <ArtifactButton
                  size="small"
                  onClick={(e) => handleDownloadClick(e, row, 'xlsx')}
                  sx={{ color: 'text.secondary' }}
                  aria-label="Download XLSX"
                >
                  <TableChartIcon sx={{ fontSize: 18 }} />
                </ArtifactButton>
              </Tooltip>
            )}
          </Stack>
        )
      },
    },
  ]

  const filters = [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'completed', label: 'Completed' },
        { value: 'failed', label: 'Failed' },
        { value: 'running', label: 'Running' },
        { value: 'cancelled', label: 'Cancelled' },
      ],
    },
  ]

  return (
    <PageContainer>
      {/* Header */}
      <PageHeader>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <PageTitle>Report History</PageTitle>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              View and download previously generated reports
            </Typography>
          </Box>
          <Stack direction="row" spacing={1.5}>
            <Tooltip title="Refresh history">
              <span>
                <RefreshButton
                  onClick={handleRefresh}
                  disabled={loading}
                  aria-label="Refresh history"
                >
                  {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                </RefreshButton>
              </span>
            </Tooltip>
            <PrimaryButton
              onClick={() => handleNavigate('/reports', 'Open reports')}
              startIcon={<AddIcon />}
            >
              Generate New
            </PrimaryButton>
          </Stack>
        </Stack>
      </PageHeader>

      <Alert severity="info" sx={{ mb: 2, borderRadius: 1 }}>
        History lists completed report outputs. Deleting a history record only removes the entry here; downloaded files
        are not affected.
      </Alert>

      {/* Filters */}
      <FilterContainer direction="row" spacing={2}>
        <StyledFormControl size="small">
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => {
              const nextStatus = e.target.value
              handleStatusFilterChange(nextStatus)
            }}
            label="Status"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="running">Running</MenuItem>
            <MenuItem value="cancelled">Cancelled</MenuItem>
          </Select>
        </StyledFormControl>
        <StyledFormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Design</InputLabel>
          <Select
            value={templateFilter}
            onChange={(e) => {
              const nextTemplate = e.target.value
              handleTemplateFilterChange(nextTemplate)
            }}
            label="Design"
          >
            <MenuItem value="">All Designs</MenuItem>
            {templates.map((tpl) => (
              <MenuItem key={tpl.id} value={tpl.id}>
                {tpl.name || tpl.id.slice(0, 12)}
              </MenuItem>
            ))}
          </Select>
        </StyledFormControl>
      </FilterContainer>

      {/* History Table */}
      <TableContainer>
        {loading && history.length === 0 ? (
          <EmptyStateContainer>
            <CircularProgress size={40} />
            <Typography sx={{ mt: 2, fontSize: '0.875rem', color: 'text.secondary' }}>
              Loading history...
            </Typography>
          </EmptyStateContainer>
        ) : history.length === 0 ? (
          <EmptyStateContainer>
            <EmptyIcon />
            <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: 'text.secondary' }}>
              No report history found
            </Typography>
            <Typography sx={{ fontSize: '0.875rem', color: 'text.disabled', mt: 0.5 }}>
              Generate reports to see them here
            </Typography>
            <SecondaryButton
              variant="outlined"
              onClick={() => handleNavigate('/reports', 'Open reports')}
              sx={{ mt: 3 }}
              startIcon={<AddIcon />}
            >
              Generate Report
            </SecondaryButton>
          </EmptyStateContainer>
        ) : (
          <DataTable
            columns={columns}
            data={history}
            loading={loading}
            searchPlaceholder="Search reports..."
            onRowClick={handleRowClick}
            selectable
            onSelectionChange={handleSelectionChange}
            bulkActions={bulkActions}
            pagination={{
              page,
              rowsPerPage,
              total,
              onPageChange: handlePageChange,
              onRowsPerPageChange: handleRowsPerPageChange,
            }}
          />
        )}
      </TableContainer>

      <ConfirmModal
        open={bulkDeleteOpen}
        onClose={handleBulkDeleteClose}
        onConfirm={handleBulkDeleteConfirm}
        title="Delete History Records"
        message={`Remove ${selectedIds.length} history record${selectedIds.length !== 1 ? 's' : ''}? You can undo within a few seconds. Downloaded files are not affected.`}
        confirmLabel="Delete"
        severity="error"
        loading={bulkDeleting}
      />
    </PageContainer>
  )
}

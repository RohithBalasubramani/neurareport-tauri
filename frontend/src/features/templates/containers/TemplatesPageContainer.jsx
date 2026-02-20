/**
 * Premium Templates Page
 * Sophisticated template management with glassmorphism and animations
 */
import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  TextField,
  Button,
  Stack,
  Typography,
  InputLabel,
  Select,
  LinearProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import SettingsIcon from '@mui/icons-material/Settings'
import DescriptionIcon from '@mui/icons-material/Description'
import TableChartIcon from '@mui/icons-material/TableChart'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import ArchiveIcon from '@mui/icons-material/Archive'
import LabelIcon from '@mui/icons-material/Label'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CloseIcon from '@mui/icons-material/Close'
import { DataTable } from '@/components/DataTable'
import { ConfirmModal } from '@/components/Modal'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import FavoriteButton from '@/features/favorites/components/FavoriteButton.jsx'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice.jsx'
import * as api from '@/api/client'
import * as recommendationsApi from '@/api/recommendations'
// UX Governance - Enforced interaction API
import {
  useInteraction,
  InteractionType,
  Reversibility,
  useNavigateInteraction,
} from '@/components/ux/governance'
import { neutral, palette, status as statusColors } from '@/app/theme'
import { fadeInUp, pulse, StyledFormControl } from '@/styles'

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

const QuickFilterChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  backgroundColor: alpha(theme.palette.text.primary, 0.08),
  color: theme.palette.text.secondary,
  fontSize: '0.75rem',
  '& .MuiChip-deleteIcon': {
    color: theme.palette.text.secondary,
    '&:hover': {
      color: theme.palette.text.primary,
    },
  },
}))

const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: 8,  // Figma spec: 8px
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.15)}`,
    minWidth: 180,
    animation: `${fadeInUp} 0.2s ease-out`,
  },
}))

const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  borderRadius: 8,
  margin: theme.spacing(0.5, 1),
  padding: theme.spacing(1, 1.5),
  fontSize: '14px',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
  '& .MuiListItemIcon-root': {
    minWidth: 32,
  },
}))

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.6),
    backdropFilter: 'blur(8px)',
  },
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: 8,  // Figma spec: 8px
    boxShadow: `0 24px 64px ${alpha(theme.palette.common.black, 0.25)}`,
    animation: `${fadeInUp} 0.3s ease-out`,
  },
}))

const DialogHeader = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2.5, 3),
  fontSize: '1.125rem',
  fontWeight: 600,
}))

const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(0, 3, 3),
}))

const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  gap: theme.spacing(1),
}))

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,  // Figma spec: 8px
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    '&:hover': {
      backgroundColor: alpha(theme.palette.background.paper, 0.8),
    },
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
      boxShadow: `0 0 0 3px ${alpha(theme.palette.text.primary, 0.08)}`,
    },
  },
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: theme.spacing(1, 2.5),
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const PrimaryButton = styled(ActionButton)(({ theme }) => ({
  background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
  '&:hover': {
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
    transform: 'translateY(-1px)',
  },
  '&:disabled': {
    background: theme.palette.action.disabledBackground,
    color: theme.palette.action.disabled,
    boxShadow: 'none',
  },
}))

const SecondaryButton = styled(ActionButton)(({ theme }) => ({
  borderColor: alpha(theme.palette.divider, 0.3),
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
  borderRadius: 10,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const KindChip = styled(Chip, {
  shouldForwardProp: (prop) => !['kindColor', 'kindBg'].includes(prop),
})(({ theme, kindColor, kindBg }) => ({
  borderRadius: 8,
  fontWeight: 600,
  fontSize: '12px',
  backgroundColor: kindBg,
  color: kindColor,
}))

const StatusChip = styled(Chip, {
  shouldForwardProp: (prop) => !['statusColor', 'statusBg'].includes(prop),
})(({ theme, statusColor, statusBg }) => ({
  borderRadius: 8,
  fontWeight: 600,
  fontSize: '12px',
  textTransform: 'capitalize',
  backgroundColor: statusBg,
  color: statusColor,
}))

const TagChip = styled(Chip)(({ theme }) => ({
  borderRadius: 6,
  fontSize: '12px',
  backgroundColor: alpha(theme.palette.text.primary, 0.08),
  color: theme.palette.text.secondary,
}))

const MoreActionsButton = styled(IconButton)(({ theme }) => ({
  color: theme.palette.text.secondary,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  borderRadius: 4,
  height: 6,
  backgroundColor: alpha(theme.palette.text.primary, 0.1),
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    background: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
  },
}))

const SimilarTemplateCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    transform: 'translateX(4px)',
  },
}))

const AiIcon = styled(AutoAwesomeIcon)(({ theme }) => ({
  color: theme.palette.text.secondary,
  animation: `${pulse} 2s infinite ease-in-out`,
}))

// =============================================================================
// CONFIG HELPERS
// =============================================================================

const getKindConfig = (theme, kind) => {
  const configs = {
    pdf: {
      icon: PictureAsPdfIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    },
    excel: {
      icon: TableChartIcon,
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
    },
  }
  return configs[kind] || configs.pdf
}

const getStatusConfig = (theme, status) => {
  const s = (status || '').toLowerCase()
  const configs = {
    approved: {
      color: statusColors.success,
      bgColor: alpha(statusColors.success, 0.1),
    },
    failed: {
      color: statusColors.destructive,
      bgColor: alpha(statusColors.destructive, 0.1),
    },
    pending: {
      color: statusColors.warning,
      bgColor: alpha(statusColors.warning, 0.1),
    },
    draft: {
      color: theme.palette.text.secondary,
      bgColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[50],
    },
    archived: {
      color: theme.palette.text.secondary,
      bgColor: alpha(theme.palette.text.secondary, 0.08),
    },
  }
  return configs[s] || configs.approved
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function TemplatesPage() {
  const theme = useTheme()
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const toast = useToast()
  // UX Governance: Enforced interaction API - ALL user actions flow through this
  const { execute } = useInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'templates', ...intent } }),
    [navigate]
  )
  const templates = useAppStore((s) => s.templates)
  const setTemplates = useAppStore((s) => s.setTemplates)
  const removeTemplate = useAppStore((s) => s.removeTemplate)
  const updateTemplate = useAppStore((s) => s.updateTemplate)

  const [loading, setLoading] = useState(false)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [deletingTemplate, setDeletingTemplate] = useState(null)
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [menuTemplate, setMenuTemplate] = useState(null)
  const [duplicating, setDuplicating] = useState(false)
  const [metadataOpen, setMetadataOpen] = useState(false)
  const [metadataTemplate, setMetadataTemplate] = useState(null)
  const [metadataForm, setMetadataForm] = useState({ name: '', description: '', tags: '', status: 'approved' })
  const [metadataSaving, setMetadataSaving] = useState(false)
  const [importOpen, setImportOpen] = useState(false)
  const [importFile, setImportFile] = useState(null)
  const [importName, setImportName] = useState('')
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [allTags, setAllTags] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)
  const [bulkStatusOpen, setBulkStatusOpen] = useState(false)
  const [bulkStatus, setBulkStatus] = useState('approved')
  const [bulkTagsOpen, setBulkTagsOpen] = useState(false)
  const [bulkTags, setBulkTags] = useState('')
  const [bulkActionLoading, setBulkActionLoading] = useState(false)
  const bulkDeleteUndoRef = useRef(null)
  const didLoadRef = useRef(false)
  const [similarOpen, setSimilarOpen] = useState(false)
  const [similarTemplate, setSimilarTemplate] = useState(null)
  const [similarTemplates, setSimilarTemplates] = useState([])
  const [similarLoading, setSimilarLoading] = useState(false)
  const [favorites, setFavorites] = useState(new Set())

  const kindFilter = searchParams.get('kind') || ''
  const statusParam = searchParams.get('status') || ''

  const filteredTemplates = useMemo(() => {
    let data = templates
    if (kindFilter) {
      data = data.filter((tpl) => (tpl.kind || '').toLowerCase() === kindFilter.toLowerCase())
    }
    if (statusParam) {
      data = data.filter((tpl) => (tpl.status || '').toLowerCase() === statusParam.toLowerCase())
    }
    return data
  }, [templates, kindFilter, statusParam])

  const clearQuickFilter = useCallback((key) => {
    const next = new URLSearchParams(searchParams)
    next.delete(key)
    setSearchParams(next, { replace: true })
  }, [searchParams, setSearchParams])

  const fetchTemplatesData = useCallback(async () => {
    setLoading(true)
    try {
      const [templatesData, tagsData, favoritesData] = await Promise.all([
        api.listTemplates(),
        api.getAllTemplateTags(),
        api.getFavorites().catch(() => ({ templates: [] })),
      ])
      setTemplates(templatesData)
      setAllTags(tagsData.tags || [])
      const favIds = (favoritesData.templates || []).map((t) => t.id)
      setFavorites(new Set(favIds))
    } catch (err) {
      toast.show(err.message || 'Failed to load designs', 'error')
    } finally {
      setLoading(false)
    }
  }, [setTemplates, toast])

  const handleFavoriteToggle = useCallback((templateId, isFavorite) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      if (isFavorite) {
        next.add(templateId)
      } else {
        next.delete(templateId)
      }
      return next
    })
  }, [])

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchTemplatesData()
  }, [fetchTemplatesData])

  const handleOpenMenu = useCallback((event, template) => {
    event.stopPropagation()
    setMenuAnchor(event.currentTarget)
    setMenuTemplate(template)
  }, [])

  const handleCloseMenu = useCallback(() => {
    setMenuAnchor(null)
    setMenuTemplate(null)
  }, [])

  const handleAddTemplate = useCallback(() => {
    handleNavigate('/setup/wizard', 'Open setup wizard')
  }, [handleNavigate])

  const handleCreateWithAi = useCallback(() => {
    handleNavigate('/templates/new/chat', 'Create template with AI')
  }, [handleNavigate])

  const handleEditTemplate = useCallback(() => {
    if (menuTemplate) {
      handleNavigate(`/templates/${menuTemplate.id}/edit`, 'Edit template', { templateId: menuTemplate.id })
    }
    handleCloseMenu()
  }, [menuTemplate, handleNavigate, handleCloseMenu])

  const handleDeleteClick = useCallback(() => {
    setDeletingTemplate(menuTemplate)
    setDeleteConfirmOpen(true)
    handleCloseMenu()
  }, [menuTemplate, handleCloseMenu])

  const handleDeleteConfirm = useCallback(async () => {
    if (!deletingTemplate) return
    const templateToDelete = deletingTemplate
    const templateData = templates.find((t) => t.id === templateToDelete.id)

    setDeleteConfirmOpen(false)
    setDeletingTemplate(null)

    // UX Governance: Delete action with tracking
    execute({
      type: InteractionType.DELETE,
      label: `Delete design "${templateToDelete.name || templateToDelete.id}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      action: async () => {
        removeTemplate(templateToDelete.id)

        let undone = false
        const deleteTimeout = setTimeout(async () => {
          if (undone) return
          try {
            await api.deleteTemplate(templateToDelete.id)
          } catch (err) {
            if (templateData) {
              setTemplates((prev) => [...prev, templateData])
            }
            throw err
          }
        }, 5000)

        toast.showWithUndo(
          `"${templateToDelete.name || templateToDelete.id}" removed`,
          () => {
            undone = true
            clearTimeout(deleteTimeout)
            if (templateData) {
              setTemplates((prev) => [...prev, templateData])
            }
            toast.show('Design restored', 'success')
          },
          { severity: 'info' }
        )
      },
    })
  }, [deletingTemplate, templates, removeTemplate, setTemplates, toast, execute])

  const handleExport = useCallback(async () => {
    if (!menuTemplate) return
    const templateToExport = menuTemplate
    handleCloseMenu()

    // UX Governance: Download action with tracking
    execute({
      type: InteractionType.DOWNLOAD,
      label: `Export design "${templateToExport.name || templateToExport.id}"`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      successMessage: 'Design exported',
      errorMessage: 'Failed to export design',
      action: async () => {
        await api.exportTemplateZip(templateToExport.id)
      },
    })
  }, [menuTemplate, handleCloseMenu, execute])

  const handleDuplicate = useCallback(async () => {
    if (!menuTemplate) return
    const templateToDuplicate = menuTemplate
    handleCloseMenu()

    // UX Governance: Create action with tracking
    execute({
      type: InteractionType.CREATE,
      label: `Duplicate design "${templateToDuplicate.name || templateToDuplicate.id}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to copy design',
      action: async () => {
        setDuplicating(true)
        try {
          const result = await api.duplicateTemplate(templateToDuplicate.id)
          const duplicatedName = result?.name || (templateToDuplicate.name ? `${templateToDuplicate.name} (Copy)` : 'Design (Copy)')
          await fetchTemplatesData()
          toast.show(`Design copied as "${duplicatedName}"`, 'success')
        } finally {
          setDuplicating(false)
        }
      },
    })
  }, [menuTemplate, toast, handleCloseMenu, fetchTemplatesData, execute])

  const handleEditMetadata = useCallback(() => {
    if (!menuTemplate) return
    setMetadataTemplate(menuTemplate)
    setMetadataForm({
      name: menuTemplate.name || '',
      description: menuTemplate.description || '',
      tags: Array.isArray(menuTemplate.tags) ? menuTemplate.tags.join(', ') : '',
      status: menuTemplate.status || 'approved',
    })
    setMetadataOpen(true)
    handleCloseMenu()
  }, [menuTemplate, handleCloseMenu])

  const handleViewSimilar = useCallback(async () => {
    if (!menuTemplate) return
    setSimilarTemplate(menuTemplate)
    setSimilarOpen(true)
    setSimilarLoading(true)
    setSimilarTemplates([])
    handleCloseMenu()
    try {
      const response = await api.getSimilarTemplates(menuTemplate.id)
      setSimilarTemplates(response.similar || [])
    } catch (err) {
      console.error('Failed to fetch similar designs:', err)
      toast.show('Failed to load similar designs', 'error')
    } finally {
      setSimilarLoading(false)
    }
  }, [menuTemplate, handleCloseMenu, toast])

  const handleSelectSimilarTemplate = useCallback((template) => {
    setSimilarOpen(false)
    handleNavigate(`/reports?template=${template.id}`, 'Open reports', { templateId: template.id })
  }, [handleNavigate])

  const handleMetadataSave = useCallback(async () => {
    if (!metadataTemplate) return
    const trimmedName = metadataForm.name.trim()
    if (!trimmedName) {
      toast.show('Design name is required', 'error')
      return
    }
    if (trimmedName.length > 200) {
      toast.show('Design name must be 200 characters or less', 'error')
      return
    }
    const tags = metadataForm.tags
      ? metadataForm.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
      : []
    const invalidTag = tags.find((tag) => tag.length > 50)
    if (invalidTag) {
      toast.show(`Tag "${invalidTag.slice(0, 20)}..." exceeds 50 character limit`, 'error')
      return
    }

    const payload = {
      name: trimmedName,
      description: metadataForm.description.trim() || undefined,
      status: metadataForm.status,
      tags,
    }

    // UX Governance: Update action with tracking
    execute({
      type: InteractionType.UPDATE,
      label: `Update design details "${trimmedName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Design details updated',
      errorMessage: 'Failed to update design details',
      action: async () => {
        setMetadataSaving(true)
        try {
          const result = await api.updateTemplateMetadata(metadataTemplate.id, payload)
          const updated = result?.template || { ...metadataTemplate, ...payload }
          updateTemplate(metadataTemplate.id, (tpl) => ({ ...tpl, ...updated }))
          setMetadataOpen(false)
        } finally {
          setMetadataSaving(false)
        }
      },
    })
  }, [metadataTemplate, metadataForm, updateTemplate, execute])

  const handleOpenImport = useCallback(() => {
    setImportOpen(true)
  }, [])

  const handleImport = useCallback(async () => {
    if (!importFile) {
      toast.show('Select a design backup file first', 'error')
      return
    }
    const fileName = importFile.name || ''
    const ext = fileName.toLowerCase().split('.').pop()
    if (ext !== 'zip') {
      toast.show('Invalid file type. Please select a .zip file', 'error')
      return
    }
    const maxSize = 50 * 1024 * 1024
    if (importFile.size > maxSize) {
      toast.show('File too large. Maximum size is 50MB', 'error')
      return
    }

    // UX Governance: Upload action with tracking
    execute({
      type: InteractionType.UPLOAD,
      label: `Import design "${importName.trim() || fileName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      successMessage: 'Design imported',
      errorMessage: 'Failed to import design',
      action: async () => {
        setImporting(true)
        setImportProgress(0)
        try {
          await api.importTemplateZip({
            file: importFile,
            name: importName.trim() || undefined,
            onUploadProgress: (percent) => setImportProgress(percent),
          })
          await fetchTemplatesData()
          setImportOpen(false)
          setImportFile(null)
          setImportName('')
        } finally {
          setImporting(false)
          setImportProgress(0)
        }
      },
    })
  }, [importFile, importName, fetchTemplatesData, execute])

  const handleBulkDeleteOpen = useCallback(() => {
    if (!selectedIds.length) return
    setBulkDeleteOpen(true)
  }, [selectedIds])

  const handleBulkDeleteConfirm = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkDeleteOpen(false)
      return
    }

    const idsToDelete = [...selectedIds]
    const count = idsToDelete.length
    const removedTemplates = templates.filter((tpl) => idsToDelete.includes(tpl.id))
    if (!removedTemplates.length) {
      setBulkDeleteOpen(false)
      return
    }

    setBulkDeleteOpen(false)
    setSelectedIds([])

    if (bulkDeleteUndoRef.current?.timeoutId) {
      clearTimeout(bulkDeleteUndoRef.current.timeoutId)
      bulkDeleteUndoRef.current = null
    }

    // UX Governance: Bulk delete action with tracking
    execute({
      type: InteractionType.DELETE,
      label: `Delete ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      errorMessage: 'Failed to remove designs',
      action: async () => {
        setTemplates((prev) => prev.filter((tpl) => !idsToDelete.includes(tpl.id)))

        let undone = false
        const timeoutId = setTimeout(async () => {
          if (undone) return
          setBulkActionLoading(true)
          try {
            const result = await api.bulkDeleteTemplates(idsToDelete)
            const deletedCount = result?.deletedCount ?? result?.deleted?.length ?? 0
            const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
            if (failedCount > 0) {
              toast.show(
                `Removed ${deletedCount} design${deletedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
                'warning'
              )
            } else {
              toast.show(`Removed ${deletedCount} design${deletedCount !== 1 ? 's' : ''}`, 'success')
            }
            await fetchTemplatesData()
          } catch (err) {
            setTemplates((prev) => {
              const existing = new Set(prev.map((tpl) => tpl.id))
              const restored = removedTemplates.filter((tpl) => !existing.has(tpl.id))
              return restored.length ? [...prev, ...restored] : prev
            })
            throw err
          } finally {
            setBulkActionLoading(false)
          }
        }, 5000)

        bulkDeleteUndoRef.current = { timeoutId, ids: idsToDelete, templates: removedTemplates }

        toast.showWithUndo(
          `Removed ${count} design${count !== 1 ? 's' : ''}`,
          () => {
            undone = true
            clearTimeout(timeoutId)
            bulkDeleteUndoRef.current = null
            setTemplates((prev) => {
              const existing = new Set(prev.map((tpl) => tpl.id))
              const restored = removedTemplates.filter((tpl) => !existing.has(tpl.id))
              return restored.length ? [...prev, ...restored] : prev
            })
            toast.show('Designs restored', 'success')
          },
          { severity: 'info' }
        )
      },
    })
  }, [selectedIds, templates, toast, fetchTemplatesData, execute, setTemplates])

  const handleBulkStatusApply = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkStatusOpen(false)
      return
    }

    const count = selectedIds.length
    setBulkStatusOpen(false)

    // UX Governance: Bulk update action with tracking
    execute({
      type: InteractionType.UPDATE,
      label: `Update status for ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to update status',
      action: async () => {
        setBulkActionLoading(true)
        try {
          const result = await api.bulkUpdateTemplateStatus(selectedIds, bulkStatus)
          const updatedCount = result?.updatedCount ?? result?.updated?.length ?? 0
          const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
          if (failedCount > 0) {
            toast.show(
              `Updated ${updatedCount} design${updatedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
              'warning'
            )
          } else {
            toast.show(
              `Updated ${updatedCount} design${updatedCount !== 1 ? 's' : ''}`,
              'success'
            )
          }
          await fetchTemplatesData()
        } finally {
          setBulkActionLoading(false)
        }
      },
    })
  }, [selectedIds, bulkStatus, toast, fetchTemplatesData, execute])

  const handleBulkTagsApply = useCallback(async () => {
    if (!selectedIds.length) {
      setBulkTagsOpen(false)
      return
    }
    const tags = bulkTags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)
    if (!tags.length) {
      toast.show('Enter at least one tag', 'error')
      return
    }
    const invalidTag = tags.find((tag) => tag.length > 50)
    if (invalidTag) {
      toast.show(`Tag "${invalidTag.slice(0, 20)}..." exceeds 50 character limit`, 'error')
      return
    }

    const count = selectedIds.length
    setBulkTagsOpen(false)

    // UX Governance: Bulk update action with tracking
    execute({
      type: InteractionType.UPDATE,
      label: `Add tags to ${count} design${count !== 1 ? 's' : ''}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      errorMessage: 'Failed to add tags',
      action: async () => {
        setBulkActionLoading(true)
        try {
          const result = await api.bulkAddTemplateTags(selectedIds, tags)
          const updatedCount = result?.updatedCount ?? result?.updated?.length ?? 0
          const failedCount = result?.failedCount ?? result?.failed?.length ?? 0
          if (failedCount > 0) {
            toast.show(
              `Tagged ${updatedCount} design${updatedCount !== 1 ? 's' : ''}, ${failedCount} failed`,
              'warning'
            )
          } else {
            toast.show(
              `Tagged ${updatedCount} design${updatedCount !== 1 ? 's' : ''}`,
              'success'
            )
          }
          await fetchTemplatesData()
          setBulkTags('')
        } finally {
          setBulkActionLoading(false)
        }
      },
    })
  }, [selectedIds, bulkTags, toast, fetchTemplatesData, execute])

  const handleRowClick = useCallback((row) => {
    handleNavigate(`/reports?template=${row.id}`, 'Open reports', { templateId: row.id })
  }, [handleNavigate])

  const columns = useMemo(() => [
    {
      field: 'name',
      headerName: 'Design',
      minWidth: 200,
      flex: 1,
      renderCell: (value, row) => {
        const config = getKindConfig(theme, row.kind)
        const Icon = config.icon
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FavoriteButton
              entityType="templates"
              entityId={row.id}
              initialFavorite={favorites.has(row.id)}
              onToggle={(isFav) => handleFavoriteToggle(row.id, isFav)}
            />
            <KindIconContainer>
              <Icon sx={{ color: 'text.secondary', fontSize: 18 }} />
            </KindIconContainer>
            <Box sx={{ minWidth: 0, overflow: 'hidden' }}>
              <Typography sx={{
                fontWeight: 500,
                fontSize: '14px',
                color: 'text.primary',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {value || row.id}
              </Typography>
              <Typography sx={{
                fontSize: '0.75rem',
                color: 'text.secondary',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {row.description || `${row.kind?.toUpperCase() || 'PDF'} Design`}
              </Typography>
            </Box>
          </Box>
        )
      },
    },
    {
      field: 'kind',
      headerName: 'Type',
      width: 100,
      renderCell: (value) => {
        const config = getKindConfig(theme, value)
        return (
          <KindChip
            label={value?.toUpperCase() || 'PDF'}
            size="small"
            kindColor={config.color}
            kindBg={config.bgColor}
          />
        )
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (value) => {
        const config = getStatusConfig(theme, value)
        return (
          <StatusChip
            label={value || 'approved'}
            size="small"
            statusColor={config.color}
            statusBg={config.bgColor}
          />
        )
      },
    },
    {
      field: 'mappingKeys',
      headerName: 'Fields',
      width: 80,
      renderCell: (value, row) => {
        const count = Array.isArray(value) ? value.length : Array.isArray(row.mappingKeys) ? row.mappingKeys.length : row.tokens_count
        return (
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            {count || '-'}
          </Typography>
        )
      },
    },
    {
      field: 'tags',
      headerName: 'Tags',
      width: 180,
      renderCell: (value) => {
        const tags = Array.isArray(value) ? value : []
        if (!tags.length) {
          return <Typography sx={{ fontSize: '0.75rem', color: 'text.disabled' }}>-</Typography>
        }
        return (
          <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap' }}>
            {tags.slice(0, 2).map((tag) => (
              <TagChip key={tag} label={tag} size="small" />
            ))}
            {tags.length > 2 && (
              <Typography variant="caption" color="text.secondary">
                +{tags.length - 2}
              </Typography>
            )}
          </Stack>
        )
      },
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 120,
      renderCell: (value, row) => {
        const raw = value || row.created_at
        if (!raw) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(raw)
        const now = new Date()
        const diffDay = Math.floor((now - d) / 86400000)
        const relative = diffDay < 1 ? 'Today' : diffDay < 2 ? 'Yesterday' : diffDay < 7 ? `${diffDay}d ago` : d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
    {
      field: 'lastRunAt',
      headerName: 'Last Run',
      width: 120,
      renderCell: (value, row) => {
        const raw = value || row.last_run_at
        if (!raw) return <Typography sx={{ fontSize: '14px', color: 'text.disabled' }}>-</Typography>
        const d = new Date(raw)
        const now = new Date()
        const diffMs = now - d
        const diffHr = Math.floor(diffMs / 3600000)
        const diffDay = Math.floor(diffMs / 86400000)
        const relative = diffHr < 1 ? 'Just now' : diffHr < 24 ? `${diffHr}h ago` : diffDay < 7 ? `${diffDay}d ago` : d.toLocaleDateString()
        return (
          <Tooltip title={d.toLocaleString()} arrow>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary', cursor: 'default' }}>
              {relative}
            </Typography>
          </Tooltip>
        )
      },
    },
    {
      field: 'updatedAt',
      headerName: 'Updated',
      width: 140,
      renderCell: (value, row) => {
        const raw = value || row.updated_at
        return (
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            {raw ? new Date(raw).toLocaleDateString() : '-'}
          </Typography>
        )
      },
    },
  ], [theme, favorites, handleFavoriteToggle])

  const filters = useMemo(() => {
    const baseFilters = [
      {
        key: 'kind',
        label: 'Type',
        options: [
          { value: 'pdf', label: 'PDF' },
          { value: 'excel', label: 'Excel' },
        ],
      },
      {
        key: 'status',
        label: 'Status',
        options: [
          { value: 'approved', label: 'Approved' },
          { value: 'pending', label: 'Pending' },
          { value: 'draft', label: 'Draft' },
          { value: 'archived', label: 'Archived' },
        ],
      },
    ]

    if (allTags.length > 0) {
      baseFilters.push({
        key: 'tags',
        label: 'Tag',
        options: allTags.map((tag) => ({ value: tag, label: tag })),
        matchFn: (row, filterValue) => {
          const rowTags = Array.isArray(row.tags) ? row.tags : []
          return rowTags.includes(filterValue)
        },
      })
    }

    return baseFilters
  }, [allTags])

  const bulkActions = useMemo(() => ([
    {
      label: 'Update Status',
      icon: <ArchiveIcon sx={{ fontSize: 16 }} />,
      onClick: () => setBulkStatusOpen(true),
      disabled: bulkActionLoading,
    },
    {
      label: 'Add Tags',
      icon: <LabelIcon sx={{ fontSize: 16 }} />,
      onClick: () => setBulkTagsOpen(true),
      disabled: bulkActionLoading,
    },
  ]), [bulkActionLoading])

  return (
    <PageContainer>
      {(kindFilter || statusParam) && (
        <Stack direction="row" spacing={1} sx={{ mb: 1.5, flexWrap: 'wrap' }}>
          {kindFilter && (
            <QuickFilterChip
              label={`Type: ${kindFilter.toUpperCase()}`}
              onDelete={() => clearQuickFilter('kind')}
              size="small"
            />
          )}
          {statusParam && (
            <QuickFilterChip
              label={`Status: ${statusParam}`}
              onDelete={() => clearQuickFilter('status')}
              size="small"
            />
          )}
        </Stack>
      )}
      <Box sx={{ mb: 2 }}>
        <ReportGlossaryNotice />
      </Box>
      <DataTable
        title="Report Designs"
        subtitle="Upload and manage your report designs"
        columns={columns}
        data={filteredTemplates}
        loading={loading}
        searchPlaceholder="Search designs..."
        filters={filters}
        actions={[
          {
            label: 'Create with AI',
            icon: <AutoAwesomeIcon sx={{ fontSize: 18 }} />,
            variant: 'contained',
            onClick: handleCreateWithAi,
          },
          {
            label: 'Upload Design',
            icon: <AddIcon sx={{ fontSize: 18 }} />,
            variant: 'outlined',
            onClick: handleAddTemplate,
          },
          {
            label: 'Import Backup',
            icon: <UploadFileIcon sx={{ fontSize: 18 }} />,
            variant: 'outlined',
            onClick: handleOpenImport,
          },
        ]}
        selectable
        onSelectionChange={setSelectedIds}
        bulkActions={bulkActions}
        onBulkDelete={handleBulkDeleteOpen}
        onRowClick={handleRowClick}
        rowActions={(row) => (
          <Tooltip title="More actions">
            <MoreActionsButton
              size="small"
              onClick={(e) => handleOpenMenu(e, row)}
              aria-label="More actions"
            >
              <MoreVertIcon sx={{ fontSize: 18 }} />
            </MoreActionsButton>
          </Tooltip>
        )}
        emptyState={{
          icon: DescriptionIcon,
          title: 'No report designs yet',
          description: 'Create a template with AI or upload a PDF/Excel file.',
          actionLabel: 'Create with AI',
          onAction: handleCreateWithAi,
        }}
      />

      {/* Row Actions Menu */}
      <StyledMenu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleCloseMenu}
      >
        <StyledMenuItem onClick={handleEditTemplate}>
          <ListItemIcon><EditIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Edit</ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleEditMetadata}>
          <ListItemIcon><SettingsIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Edit Details</ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleExport}>
          <ListItemIcon><DownloadIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Export</ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleDuplicate} disabled={duplicating}>
          <ListItemIcon><ContentCopyIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>{duplicating ? 'Duplicating...' : 'Duplicate'}</ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleViewSimilar}>
          <ListItemIcon><AutoAwesomeIcon sx={{ fontSize: 16 }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>View Similar</ListItemText>
        </StyledMenuItem>
        <StyledMenuItem onClick={handleDeleteClick} sx={{ color: 'text.primary' }}>
          <ListItemIcon><DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} /></ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontSize: '14px' }}>Delete</ListItemText>
        </StyledMenuItem>
      </StyledMenu>

      {/* Delete Confirmation */}
      <ConfirmModal
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Remove Design"
        message={`Remove "${deletingTemplate?.name || deletingTemplate?.id}"? Past report files remain in History. You can undo this within a few seconds.`}
        confirmLabel="Remove"
        severity="error"
        loading={loading}
      />

      <ConfirmModal
        open={bulkDeleteOpen}
        onClose={() => setBulkDeleteOpen(false)}
        onConfirm={handleBulkDeleteConfirm}
        title="Remove Designs"
        message={`Remove ${selectedIds.length} design${selectedIds.length !== 1 ? 's' : ''}? Past report files remain in History. You can undo this within a few seconds.`}
        confirmLabel="Remove"
        severity="error"
        loading={bulkActionLoading}
      />

      {/* Edit Metadata Dialog */}
      <StyledDialog open={metadataOpen} onClose={() => setMetadataOpen(false)} maxWidth="sm" fullWidth>
        <DialogHeader>Edit Design Details</DialogHeader>
        <StyledDialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <StyledTextField
              label="Name"
              value={metadataForm.name}
              onChange={(e) => setMetadataForm((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
            />
            <StyledTextField
              label="Description"
              value={metadataForm.description}
              onChange={(e) => setMetadataForm((prev) => ({ ...prev, description: e.target.value }))}
              multiline
              minRows={2}
              fullWidth
            />
            <StyledTextField
              label="Tags"
              value={metadataForm.tags}
              onChange={(e) => setMetadataForm((prev) => ({ ...prev, tags: e.target.value }))}
              helperText="Comma-separated (e.g. finance, monthly, ops)"
              fullWidth
            />
            <StyledFormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={metadataForm.status}
                label="Status"
                onChange={(e) => setMetadataForm((prev) => ({ ...prev, status: e.target.value }))}
              >
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="archived">Archived</MenuItem>
              </Select>
            </StyledFormControl>
          </Stack>
        </StyledDialogContent>
        <StyledDialogActions>
          <SecondaryButton variant="outlined" onClick={() => setMetadataOpen(false)} disabled={metadataSaving}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={handleMetadataSave}
            disabled={metadataSaving || !metadataForm.name.trim()}
          >
            {metadataSaving ? 'Saving...' : 'Save'}
          </PrimaryButton>
        </StyledDialogActions>
      </StyledDialog>

      {/* Bulk Status Dialog */}
      <StyledDialog open={bulkStatusOpen} onClose={() => setBulkStatusOpen(false)} maxWidth="xs" fullWidth>
        <DialogHeader>Update Status</DialogHeader>
        <StyledDialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
              Update {selectedIds.length} design{selectedIds.length !== 1 ? 's' : ''} to:
            </Typography>
            <StyledFormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={bulkStatus}
                label="Status"
                onChange={(e) => setBulkStatus(e.target.value)}
              >
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="archived">Archived</MenuItem>
              </Select>
            </StyledFormControl>
          </Stack>
        </StyledDialogContent>
        <StyledDialogActions>
          <SecondaryButton variant="outlined" onClick={() => setBulkStatusOpen(false)} disabled={bulkActionLoading}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={handleBulkStatusApply}
            disabled={bulkActionLoading}
          >
            {bulkActionLoading ? 'Updating...' : 'Update'}
          </PrimaryButton>
        </StyledDialogActions>
      </StyledDialog>

      {/* Bulk Tags Dialog */}
      <StyledDialog open={bulkTagsOpen} onClose={() => setBulkTagsOpen(false)} maxWidth="sm" fullWidth>
        <DialogHeader>Add Tags</DialogHeader>
        <StyledDialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
              Add tags to {selectedIds.length} design{selectedIds.length !== 1 ? 's' : ''}.
            </Typography>
            <StyledTextField
              label="Tags"
              value={bulkTags}
              onChange={(e) => setBulkTags(e.target.value)}
              helperText="Comma-separated (e.g. finance, monthly, ops)"
              fullWidth
            />
          </Stack>
        </StyledDialogContent>
        <StyledDialogActions>
          <SecondaryButton variant="outlined" onClick={() => setBulkTagsOpen(false)} disabled={bulkActionLoading}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={handleBulkTagsApply}
            disabled={bulkActionLoading}
          >
            {bulkActionLoading ? 'Updating...' : 'Add Tags'}
          </PrimaryButton>
        </StyledDialogActions>
      </StyledDialog>

      {/* Import Dialog */}
      <StyledDialog open={importOpen} onClose={() => !importing && setImportOpen(false)} maxWidth="sm" fullWidth>
        <DialogHeader>Import Design Backup</DialogHeader>
        <StyledDialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <SecondaryButton variant="outlined" component="label" disabled={importing}>
              {importFile ? importFile.name : 'Choose backup file (.zip)'}
              <input
                type="file"
                hidden
                accept=".zip"
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
              />
            </SecondaryButton>
            <StyledTextField
              label="Design Name (optional)"
              value={importName}
              onChange={(e) => setImportName(e.target.value)}
              fullWidth
              disabled={importing}
            />
            {importing && (
              <Box sx={{ width: '100%' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Uploading... {importProgress}%
                </Typography>
                <StyledLinearProgress variant="determinate" value={importProgress} />
              </Box>
            )}
          </Stack>
        </StyledDialogContent>
        <StyledDialogActions>
          <SecondaryButton variant="outlined" onClick={() => setImportOpen(false)} disabled={importing}>Cancel</SecondaryButton>
          <PrimaryButton onClick={handleImport} disabled={importing || !importFile}>
            {importing ? 'Importing...' : 'Import'}
          </PrimaryButton>
        </StyledDialogActions>
      </StyledDialog>

      {/* Similar Designs Dialog */}
      <StyledDialog open={similarOpen} onClose={() => setSimilarOpen(false)} maxWidth="sm" fullWidth>
        <DialogHeader>
          <Stack direction="row" alignItems="center" spacing={1}>
            <AiIcon />
            <span>Similar Designs</span>
          </Stack>
        </DialogHeader>
        <StyledDialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Designs similar to "{similarTemplate?.name || similarTemplate?.id}"
          </Typography>
          {similarLoading ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">Loading similar designs...</Typography>
            </Box>
          ) : similarTemplates.length === 0 ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">No similar designs found.</Typography>
            </Box>
          ) : (
            <Stack spacing={1}>
              {similarTemplates.map((template) => {
                const config = getKindConfig(theme, template.kind)
                const Icon = config.icon
                return (
                  <SimilarTemplateCard
                    key={template.id}
                    onClick={() => handleSelectSimilarTemplate(template)}
                  >
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <KindIconContainer>
                        <Icon sx={{ color: 'text.secondary', fontSize: 18 }} />
                      </KindIconContainer>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2">{template.name || template.id}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {template.description || `${template.kind?.toUpperCase() || 'PDF'} Design`}
                        </Typography>
                      </Box>
                      {template.similarity_score && (
                        <Chip
                          label={`${Math.round(template.similarity_score * 100)}% match`}
                          size="small"
                          variant="outlined"
                          sx={{ borderRadius: 8, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                        />
                      )}
                    </Stack>
                  </SimilarTemplateCard>
                )
              })}
            </Stack>
          )}
        </StyledDialogContent>
        <StyledDialogActions>
          <SecondaryButton variant="outlined" onClick={() => setSimilarOpen(false)}>Close</SecondaryButton>
        </StyledDialogActions>
      </StyledDialog>
    </PageContainer>
  )
}

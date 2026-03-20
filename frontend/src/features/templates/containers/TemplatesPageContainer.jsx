/**
 * Premium Templates Page
 * Sophisticated template management with glassmorphism and animations
 */
import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Stack,
  Tooltip,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DescriptionIcon from '@mui/icons-material/Description'
import ArchiveIcon from '@mui/icons-material/Archive'
import LabelIcon from '@mui/icons-material/Label'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import { DataTable } from '@/components/data-table'
import { ConfirmModal } from '@/components/modal'
import { useNavigateInteraction } from '@/components/ux/governance'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice.jsx'

// Hooks
import useTemplateList from '../hooks/useTemplateList'
import useTemplateBulkActions from '../hooks/useTemplateBulkActions'
import useTemplateImport from '../hooks/useTemplateImport'
import useTemplateMetadata from '../hooks/useTemplateMetadata'
import useSimilarTemplates from '../hooks/useSimilarTemplates'
import useTemplateActions from '../hooks/useTemplateActions'
import useTemplateColumns from '../hooks/useTemplateColumns'

// Components
import { PageContainer, QuickFilterChip, MoreActionsButton } from '../components/TemplateStyledComponents'
import TemplateRowActionsMenu from '../components/TemplateRowActionsMenu'
import MetadataDialog from '../components/MetadataDialog'
import BulkStatusDialog from '../components/BulkStatusDialog'
import BulkTagsDialog from '../components/BulkTagsDialog'
import ImportDialog from '../components/ImportDialog'
import SimilarDesignsDialog from '../components/SimilarDesignsDialog'

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function TemplatesPage() {
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'templates', ...intent } }),
    [navigate]
  )

  // --- Hooks ---
  const list = useTemplateList()
  const { templates, setTemplates, removeTemplate, updateTemplate, loading, allTags, favorites, handleFavoriteToggle, fetchTemplatesData } = list

  const bulk = useTemplateBulkActions({ templates, setTemplates, fetchTemplatesData })
  const importHook = useTemplateImport({ fetchTemplatesData })
  const metadata = useTemplateMetadata({ updateTemplate })
  const similar = useSimilarTemplates({ handleNavigate })
  const actions = useTemplateActions({ templates, removeTemplate, setTemplates, fetchTemplatesData, handleNavigate })

  const columns = useTemplateColumns({ favorites, handleFavoriteToggle })

  // --- Filters from URL ---
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

  // --- Navigation handlers ---
  const handleAddTemplate = useCallback(() => handleNavigate('/setup/wizard', 'Open setup wizard'), [handleNavigate])
  const handleCreateWithAi = useCallback(() => handleNavigate('/templates/new/chat', 'Create template with AI'), [handleNavigate])
  const handleRowClick = useCallback((row) => handleNavigate(`/reports?template=${row.id}`, 'Open reports', { templateId: row.id }), [handleNavigate])

  // --- Bridge menu actions to metadata/similar hooks ---
  const handleEditMetadata = useCallback(() => {
    if (actions.menuTemplate) metadata.openMetadataDialog(actions.menuTemplate)
    actions.handleCloseMenu()
  }, [actions.menuTemplate, metadata.openMetadataDialog, actions.handleCloseMenu])

  const handleViewSimilar = useCallback(() => {
    if (actions.menuTemplate) similar.handleViewSimilar(actions.menuTemplate)
    actions.handleCloseMenu()
  }, [actions.menuTemplate, similar.handleViewSimilar, actions.handleCloseMenu])

  // --- DataTable config ---
  const filters = useMemo(() => {
    const baseFilters = [
      { key: 'kind', label: 'Type', options: [{ value: 'pdf', label: 'PDF' }, { value: 'excel', label: 'Excel' }] },
      { key: 'status', label: 'Status', options: [{ value: 'approved', label: 'Approved' }, { value: 'pending', label: 'Pending' }, { value: 'draft', label: 'Draft' }, { value: 'archived', label: 'Archived' }] },
    ]
    if (allTags.length > 0) {
      baseFilters.push({
        key: 'tags', label: 'Tag',
        options: allTags.map((tag) => ({ value: tag, label: tag })),
        matchFn: (row, filterValue) => (Array.isArray(row.tags) ? row.tags : []).includes(filterValue),
      })
    }
    return baseFilters
  }, [allTags])

  const bulkActions = useMemo(() => ([
    { label: 'Update Status', icon: <ArchiveIcon sx={{ fontSize: 16 }} />, onClick: () => bulk.setBulkStatusOpen(true), disabled: bulk.bulkActionLoading },
    { label: 'Add Tags', icon: <LabelIcon sx={{ fontSize: 16 }} />, onClick: () => bulk.setBulkTagsOpen(true), disabled: bulk.bulkActionLoading },
  ]), [bulk.bulkActionLoading])

  const tableActions = useMemo(() => [
    { label: 'Create with AI', icon: <AutoAwesomeIcon sx={{ fontSize: 18 }} />, variant: 'contained', onClick: handleCreateWithAi },
    { label: 'Upload Design', icon: <AddIcon sx={{ fontSize: 18 }} />, variant: 'outlined', onClick: handleAddTemplate },
    { label: 'Import Backup', icon: <UploadFileIcon sx={{ fontSize: 18 }} />, variant: 'outlined', onClick: importHook.handleOpenImport },
  ], [handleCreateWithAi, handleAddTemplate, importHook.handleOpenImport])

  return (
    <PageContainer>
      {(kindFilter || statusParam) && (
        <Stack direction="row" spacing={1} sx={{ mb: 1.5, flexWrap: 'wrap' }}>
          {kindFilter && <QuickFilterChip label={`Type: ${kindFilter.toUpperCase()}`} onDelete={() => clearQuickFilter('kind')} size="small" />}
          {statusParam && <QuickFilterChip label={`Status: ${statusParam}`} onDelete={() => clearQuickFilter('status')} size="small" />}
        </Stack>
      )}
      <Box sx={{ mb: 2 }}><ReportGlossaryNotice /></Box>

      <DataTable
        title="Report Designs"
        subtitle="Upload and manage your report designs"
        columns={columns}
        data={filteredTemplates}
        loading={loading}
        searchPlaceholder="Search designs..."
        filters={filters}
        actions={tableActions}
        selectable
        onSelectionChange={bulk.setSelectedIds}
        bulkActions={bulkActions}
        onBulkDelete={bulk.handleBulkDeleteOpen}
        onRowClick={handleRowClick}
        rowActions={(row) => (
          <Tooltip title="More actions">
            <MoreActionsButton size="small" onClick={(e) => actions.handleOpenMenu(e, row)} aria-label="More actions">
              <MoreVertIcon sx={{ fontSize: 18 }} />
            </MoreActionsButton>
          </Tooltip>
        )}
        emptyState={{ icon: DescriptionIcon, title: 'No report designs yet', description: 'Create a template with AI or upload a PDF/Excel file.', actionLabel: 'Create with AI', onAction: handleCreateWithAi }}
      />

      <TemplateRowActionsMenu
        menuAnchor={actions.menuAnchor}
        handleCloseMenu={actions.handleCloseMenu}
        handleEditTemplate={actions.handleEditTemplate}
        handleEditMetadata={handleEditMetadata}
        handleExport={actions.handleExport}
        handleDuplicate={actions.handleDuplicate}
        duplicating={actions.duplicating}
        handleViewSimilar={handleViewSimilar}
        handleDeleteClick={actions.handleDeleteClick}
      />

      <ConfirmModal open={actions.deleteConfirmOpen} onClose={() => actions.setDeleteConfirmOpen(false)} onConfirm={actions.handleDeleteConfirm} title="Remove Design" message={`Remove "${actions.deletingTemplate?.name || actions.deletingTemplate?.id}"? Past report files remain in History. You can undo this within a few seconds.`} confirmLabel="Remove" severity="error" loading={loading} />
      <ConfirmModal open={bulk.bulkDeleteOpen} onClose={() => bulk.setBulkDeleteOpen(false)} onConfirm={bulk.handleBulkDeleteConfirm} title="Remove Designs" message={`Remove ${bulk.selectedIds.length} design${bulk.selectedIds.length !== 1 ? 's' : ''}? Past report files remain in History. You can undo this within a few seconds.`} confirmLabel="Remove" severity="error" loading={bulk.bulkActionLoading} />

      <MetadataDialog metadataOpen={metadata.metadataOpen} setMetadataOpen={metadata.setMetadataOpen} metadataForm={metadata.metadataForm} setMetadataForm={metadata.setMetadataForm} metadataSaving={metadata.metadataSaving} handleMetadataSave={metadata.handleMetadataSave} />
      <BulkStatusDialog bulkStatusOpen={bulk.bulkStatusOpen} setBulkStatusOpen={bulk.setBulkStatusOpen} selectedCount={bulk.selectedIds.length} bulkStatus={bulk.bulkStatus} setBulkStatus={bulk.setBulkStatus} bulkActionLoading={bulk.bulkActionLoading} handleBulkStatusApply={bulk.handleBulkStatusApply} />
      <BulkTagsDialog bulkTagsOpen={bulk.bulkTagsOpen} setBulkTagsOpen={bulk.setBulkTagsOpen} selectedCount={bulk.selectedIds.length} bulkTags={bulk.bulkTags} setBulkTags={bulk.setBulkTags} bulkActionLoading={bulk.bulkActionLoading} handleBulkTagsApply={bulk.handleBulkTagsApply} />
      <ImportDialog importOpen={importHook.importOpen} setImportOpen={importHook.setImportOpen} importFile={importHook.importFile} setImportFile={importHook.setImportFile} importName={importHook.importName} setImportName={importHook.setImportName} importing={importHook.importing} importProgress={importHook.importProgress} handleImport={importHook.handleImport} />
      <SimilarDesignsDialog similarOpen={similar.similarOpen} setSimilarOpen={similar.setSimilarOpen} similarTemplate={similar.similarTemplate} similarTemplates={similar.similarTemplates} similarLoading={similar.similarLoading} handleSelectSimilarTemplate={similar.handleSelectSimilarTemplate} />
    </PageContainer>
  )
}

import {
  Box, Typography, ToggleButton, ToggleButtonGroup,
} from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SummarizeIcon from '@mui/icons-material/Summarize'
import DescriptionIcon from '@mui/icons-material/Description'
import { useStepTemplate } from '../../hooks/useStepTemplate'
import TemplateGallery from './TemplateGallery'
import TemplateUploadArea from './TemplateUploadArea'

const TEMPLATE_GALLERY = [
  {
    id: 'gallery-invoice',
    name: 'Invoice Report',
    description: 'Professional invoice template with line items, totals, and company branding',
    kind: 'pdf',
    icon: ReceiptLongIcon,
    popular: true,
  },
  {
    id: 'gallery-sales',
    name: 'Sales Summary',
    description: 'Weekly/monthly sales report with charts, metrics, and trends',
    kind: 'excel',
    icon: AssessmentIcon,
    popular: true,
  },
  {
    id: 'gallery-inventory',
    name: 'Inventory Report',
    description: 'Stock levels, reorder points, and inventory movement tracking',
    kind: 'excel',
    icon: TableChartIcon,
    popular: false,
  },
  {
    id: 'gallery-executive',
    name: 'Executive Summary',
    description: 'High-level business metrics and KPIs for leadership review',
    kind: 'pdf',
    icon: SummarizeIcon,
    popular: false,
  },
  {
    id: 'gallery-blank-pdf',
    name: 'Blank PDF Template',
    description: 'Start from scratch with a customizable PDF layout',
    kind: 'pdf',
    icon: DescriptionIcon,
    popular: false,
  },
  {
    id: 'gallery-blank-excel',
    name: 'Blank Excel Template',
    description: 'Start from scratch with a customizable spreadsheet',
    kind: 'excel',
    icon: TableChartIcon,
    popular: false,
  },
]

export default function StepTemplate({ wizardState, updateWizardState, onComplete, setLoading }) {
  const {
    templateKind,
    uploading,
    uploadProgress,
    uploadedFile,
    verifyResult,
    error,
    setError,
    queueInBackground,
    setQueueInBackground,
    queuedJobId,
    selectedGalleryTemplate,
    setSelectedGalleryTemplate,
    showUpload,
    setShowUpload,
    fileInputRef,
    acceptedTypes,
    handleNavigate,
    handleKindChange,
    handleDrop,
    handleDragOver,
    handleFileSelect,
    handleBrowseClick,
    handleSelectGalleryTemplate,
    handleUseGalleryTemplate,
  } = useStepTemplate({ wizardState, updateWizardState, setLoading })

  const filteredGalleryTemplates = TEMPLATE_GALLERY.filter(t =>
    templateKind === 'all' || t.kind === templateKind
  )

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        Choose a Report Template
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Create with AI, pick from our gallery, or upload your own design.
      </Typography>

      <Box sx={{ mb: 3 }}>
        <ToggleButtonGroup
          value={templateKind}
          exclusive
          onChange={handleKindChange}
          size="small"
        >
          <ToggleButton value="pdf" sx={{ px: 3 }}>
            <PictureAsPdfIcon sx={{ mr: 1, fontSize: 18 }} />
            PDF Reports
          </ToggleButton>
          <ToggleButton value="excel" sx={{ px: 3 }}>
            <TableChartIcon sx={{ mr: 1, fontSize: 18 }} />
            Excel Reports
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {!showUpload && !verifyResult && (
        <TemplateGallery
          filteredGalleryTemplates={filteredGalleryTemplates}
          selectedGalleryTemplate={selectedGalleryTemplate}
          onSelectGalleryTemplate={handleSelectGalleryTemplate}
          onClearSelection={() => setSelectedGalleryTemplate(null)}
          onUseGalleryTemplate={handleUseGalleryTemplate}
          onShowUpload={() => setShowUpload(true)}
          onNavigate={handleNavigate}
          wizardConnectionId={wizardState.connectionId}
        />
      )}

      {(showUpload || verifyResult) && (
        <TemplateUploadArea
          showUpload={showUpload}
          verifyResult={verifyResult}
          error={error}
          setError={setError}
          queuedJobId={queuedJobId}
          uploading={uploading}
          uploadProgress={uploadProgress}
          uploadedFile={uploadedFile}
          queueInBackground={queueInBackground}
          setQueueInBackground={setQueueInBackground}
          templateKind={templateKind}
          acceptedTypes={acceptedTypes}
          fileInputRef={fileInputRef}
          handleNavigate={handleNavigate}
          handleDrop={handleDrop}
          handleDragOver={handleDragOver}
          handleFileSelect={handleFileSelect}
          handleBrowseClick={handleBrowseClick}
          setShowUpload={setShowUpload}
        />
      )}
    </Box>
  )
}

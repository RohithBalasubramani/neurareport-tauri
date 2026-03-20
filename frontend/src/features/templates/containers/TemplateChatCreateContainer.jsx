import React from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  Breadcrumbs,
  Link,
} from '@mui/material'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SaveIcon from '@mui/icons-material/Save'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import { Link as RouterLink } from 'react-router-dom'

import Surface from '@/components/layout/Surface.jsx'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { neutral } from '@/app/theme'
import TemplateChatEditor from '@/features/generate/containers/TemplateChatEditor.jsx'
import { useTemplateChatCreate } from '../hooks/useTemplateChatCreate'
import SamplePdfUpload from '../components/SamplePdfUpload'
import TemplatePreviewPane from '../components/TemplatePreviewPane'
import TemplateNameDialog from '../components/TemplateNameDialog'

export default function TemplateChatCreateContainer() {
  const {
    selectedConnectionId,
    setSelectedConnectionId,
    setActiveConnectionId,
    currentHtml,
    previewUrl,
    nameDialogOpen,
    templateName,
    setTemplateName,
    creating,
    samplePdf,
    templateKind,
    setTemplateKind,
    fileInputRef,
    mappingPreviewData,
    mappingApproving,
    handleFileSelect,
    handleDrop,
    handleDragOver,
    handleRemovePdf,
    handleHtmlUpdate,
    handleApplySuccess,
    handleBack,
    handleOpenNameDialog,
    handleCloseNameDialog,
    handleCreateTemplate,
    handleMappingApprove,
    handleMappingSkip,
    handleMappingQueue,
    chatApi,
    SESSION_KEY,
  } = useTemplateChatCreate()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', flex: '1 1 0', minHeight: 0, overflow: 'hidden' }}>
      {/* Breadcrumb */}
      <Box sx={{ mb: 1, flexShrink: 0 }}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb">
          <Link
            component={RouterLink}
            to="/templates"
            underline="hover"
            color="text.secondary"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            Templates
          </Link>
          <Typography color="text.primary" fontWeight={600}>
            Create with AI
          </Typography>
        </Breadcrumbs>
      </Box>

      <Surface sx={{ gap: { xs: 1.5, md: 2 }, flex: '1 1 0', minHeight: 0, overflow: 'hidden' }}>
        {/* Header */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1.5} sx={{ flexShrink: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
            <AutoAwesomeIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
            <Typography variant="h6" fontWeight={600}>
              Create Template with AI
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1.5} alignItems="center">
            <ConnectionSelector
              value={selectedConnectionId}
              onChange={(connId) => {
                setSelectedConnectionId(connId)
                setActiveConnectionId(connId)
              }}
              label="Data Source"
              size="small"
              fullWidth={false}
              sx={{ minWidth: 200 }}
            />
            <Button
              variant="contained"
              onClick={handleOpenNameDialog}
              disabled={!currentHtml}
              startIcon={<SaveIcon />}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                bgcolor: neutral[900],
                '&:hover': { bgcolor: neutral[700] },
                '&.Mui-disabled': { bgcolor: neutral[300], color: neutral[500] },
              }}
            >
              Save Template
            </Button>
            <Button
              variant="outlined"
              onClick={handleBack}
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Back
            </Button>
          </Stack>
        </Stack>

        {/* Sample PDF Upload */}
        <SamplePdfUpload
          samplePdf={samplePdf}
          templateKind={templateKind}
          fileInputRef={fileInputRef}
          onFileSelect={handleFileSelect}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onRemovePdf={handleRemovePdf}
        />

        {/* Main content: Preview + Chat */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '7fr 5fr' },
            gap: 2,
            flex: 1,
            minHeight: 0,
          }}
        >
          <TemplatePreviewPane previewUrl={previewUrl} />

          <TemplateChatEditor
            templateId={SESSION_KEY}
            templateName="New Template"
            currentHtml={currentHtml}
            onHtmlUpdate={handleHtmlUpdate}
            onApplySuccess={handleApplySuccess}
            onRequestSave={handleOpenNameDialog}
            mappingPreviewData={mappingPreviewData}
            mappingApproving={mappingApproving}
            onMappingApprove={handleMappingApprove}
            onMappingSkip={handleMappingSkip}
            onMappingQueue={handleMappingQueue}
            mode="create"
            chatApi={chatApi}
          />
        </Box>
      </Surface>

      {/* Name Dialog */}
      <TemplateNameDialog
        open={nameDialogOpen}
        templateName={templateName}
        setTemplateName={setTemplateName}
        templateKind={templateKind}
        setTemplateKind={setTemplateKind}
        creating={creating}
        onClose={handleCloseNameDialog}
        onCreate={handleCreateTemplate}
      />
    </Box>
  )
}

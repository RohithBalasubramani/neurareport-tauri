/**
 * Visualization Page Container
 * Diagram and chart generation interface.
 */
import React from 'react'
import {
  Box,
  Paper,
  Card,
  Button,
  Alert,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { useVisualizationPage } from '../hooks/useVisualizationPage'
import VisualizationHeader from '../components/VisualizationHeader'
import VisualizationSidebar from '../components/VisualizationSidebar'
import VisualizationPreview from '../components/VisualizationPreview'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

const Sidebar = styled(Box)(({ theme }) => ({
  width: 300,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  padding: theme.spacing(2),
  overflow: 'auto',
}))

const PreviewArea = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: theme.palette.background.default,
  overflow: 'auto',
}))

const DiagramTypeCard = styled(Card)(({ theme, selected }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  marginBottom: theme.spacing(1),
  border: selected ? `2px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const PreviewCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: '100%',
  maxHeight: '70vh',
  overflow: 'auto',
  backgroundColor: theme.palette.background.paper,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function VisualizationPageContainer() {
  const v = useVisualizationPage()

  return (
    <PageContainer>
      <VisualizationHeader
        activeDiagram={v.activeDiagram}
        selectedType={v.selectedType}
        title={v.title}
        handleExport={v.handleExport}
        Header={Header}
      />

      <ContentArea>
        <VisualizationSidebar
          selectedType={v.selectedType}
          handleTypeChange={v.handleTypeChange}
          title={v.title}
          setTitle={v.setTitle}
          selectedConnectionId={v.selectedConnectionId}
          setSelectedConnectionId={v.setSelectedConnectionId}
          fileInputRef={v.fileInputRef}
          handleFileUpload={v.handleFileUpload}
          uploadingFile={v.uploadingFile}
          uploadedFileName={v.uploadedFileName}
          inputData={v.inputData}
          setInputData={v.setInputData}
          generating={v.generating}
          handleGenerate={v.handleGenerate}
          Sidebar={Sidebar}
          DiagramTypeCard={DiagramTypeCard}
          ActionButton={ActionButton}
        />

        <VisualizationPreview
          activeDiagram={v.activeDiagram}
          extractedTable={v.extractedTable}
          selectedType={v.selectedType}
          inputData={v.inputData}
          generating={v.generating}
          handleGenerate={v.handleGenerate}
          fileInputRef={v.fileInputRef}
          PreviewArea={PreviewArea}
          PreviewCard={PreviewCard}
          ActionButton={ActionButton}
        />
      </ContentArea>

      {v.error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {v.error}
        </Alert>
      )}
    </PageContainer>
  )
}

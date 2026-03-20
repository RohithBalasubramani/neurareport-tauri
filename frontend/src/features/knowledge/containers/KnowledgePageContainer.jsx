/**
 * Knowledge Library Page Container
 * Document library and knowledge management interface.
 * Slim orchestrator -- logic in useKnowledgeLibrary, render in sub-components.
 */
import React from 'react'
import { Alert } from '@mui/material'
import { useKnowledgeLibrary } from '../hooks/useKnowledgeLibrary'
import { PageContainer, ContentArea, MainPanel } from '../components/KnowledgeStyles'
import KnowledgeHeader from '../components/KnowledgeHeader'
import KnowledgeSidebar from '../components/KnowledgeSidebar'
import LoadingSkeleton from '../components/LoadingSkeleton'
import DocumentGrid from '../components/DocumentGrid'
import KnowledgeGraphView from '../components/KnowledgeGraphView'
import FaqView from '../components/FaqView'
import DocumentContextMenu from '../components/DocumentContextMenu'
import CreateCollectionDialog from '../components/CreateCollectionDialog'
import UploadDocumentDialog from '../components/UploadDocumentDialog'

export default function KnowledgePageContainer() {
  const {
    documents, collections, tags, knowledgeGraph, faq, stats,
    loading, error, connections, templates,
    searchQuery, setSearchQuery, selectedCollection,
    view, setView, createCollectionOpen, setCreateCollectionOpen,
    newCollectionName, setNewCollectionName,
    menuAnchor, selectedDoc,
    uploadDialogOpen, setUploadDialogOpen,
    uploadFile, uploadTitle, setUploadTitle, uploading,
    displayedDocs,
    handleSearch, handleSelectCollection, handleToggleFavorite,
    handleDeleteDocument, handleAutoTag, handleFindRelated,
    handleBuildGraph, handleGenerateFaq, handleCreateCollection,
    handleMenuOpen, handleMenuClose,
    handleUploadDocument, handleFileSelect, handleImport,
    fetchDocuments,
  } = useKnowledgeLibrary()

  const showSkeleton = loading && !documents.length && view !== 'graph' && view !== 'faq'

  return (
    <PageContainer>
      <KnowledgeHeader
        stats={stats}
        connections={connections}
        templates={templates}
        loading={loading}
        onUploadClick={() => setUploadDialogOpen(true)}
        onBuildGraph={handleBuildGraph}
        onGenerateFaq={handleGenerateFaq}
        onImport={handleImport}
      />

      <ContentArea>
        <KnowledgeSidebar
          searchQuery={searchQuery}
          onSearchQueryChange={setSearchQuery}
          onSearch={handleSearch}
          view={view}
          onViewChange={setView}
          selectedCollection={selectedCollection}
          onSelectCollection={handleSelectCollection}
          collections={collections}
          tags={tags}
          knowledgeGraph={knowledgeGraph}
          faq={faq}
          onCreateCollectionOpen={() => setCreateCollectionOpen(true)}
          onFetchDocuments={fetchDocuments}
        />

        <MainPanel>
          {showSkeleton ? (
            <LoadingSkeleton />
          ) : view === 'graph' ? (
            <KnowledgeGraphView
              knowledgeGraph={knowledgeGraph}
              loading={loading}
              documents={documents}
              onBuildGraph={handleBuildGraph}
            />
          ) : view === 'faq' ? (
            <FaqView
              faq={faq}
              loading={loading}
              documents={documents}
              onGenerateFaq={handleGenerateFaq}
            />
          ) : (
            <DocumentGrid
              documents={displayedDocs}
              loading={loading}
              onToggleFavorite={handleToggleFavorite}
              onMenuOpen={handleMenuOpen}
              onUploadClick={() => setUploadDialogOpen(true)}
            />
          )}
        </MainPanel>
      </ContentArea>

      <DocumentContextMenu
        anchorEl={menuAnchor}
        selectedDoc={selectedDoc}
        onClose={handleMenuClose}
        onAutoTag={handleAutoTag}
        onFindRelated={handleFindRelated}
        onDelete={handleDeleteDocument}
      />

      <CreateCollectionDialog
        open={createCollectionOpen}
        onClose={() => setCreateCollectionOpen(false)}
        name={newCollectionName}
        onNameChange={setNewCollectionName}
        onCreate={handleCreateCollection}
      />

      <UploadDocumentDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        uploading={uploading}
        uploadFile={uploadFile}
        uploadTitle={uploadTitle}
        onTitleChange={setUploadTitle}
        onFileSelect={handleFileSelect}
        onUpload={handleUploadDocument}
        selectedCollection={selectedCollection}
      />

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}

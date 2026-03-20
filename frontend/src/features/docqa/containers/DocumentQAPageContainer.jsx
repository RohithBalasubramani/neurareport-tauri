/**
 * Premium Document Q&A Chat Interface
 * Sophisticated AI-powered document analysis with elegant design
 */
import React from 'react'
import {
  Box,
  Typography,
} from '@mui/material'
import useDocQAStore from '@/stores/docqaStore'
import { useDocQAPage } from '../hooks/useDocQAPage'
import {
  PageContainer,
  ChatArea,
  MessagesContainer,
  LoadingOverlay,
  LoadingSpinner,
} from '../components/DocQAStyledComponents'
import DocQASidebar from '../components/DocQASidebar'
import DocQAChatHeader from '../components/DocQAChatHeader'
import ChatMessages from '../components/ChatMessages'
import ChatInput from '../components/ChatInput'
import { NoSessionState, NoMessagesState } from '../components/ChatEmptyState'
import {
  CreateSessionDialog,
  AddDocumentDialog,
  ReportPickerDialog,
  DocQAConfirmModals,
} from '../components/DocQADialogs'

export default function DocumentQAPage() {
  const state = useDocQAPage()
  const { deleteSession, removeDocument, clearHistory } = useDocQAStore()

  // Loading state
  if (state.initialLoading) {
    return (
      <PageContainer>
        <LoadingOverlay>
          <Box sx={{ textAlign: 'center' }}>
            <Box sx={{ position: 'relative', width: 48, height: 48, mx: 'auto', mb: 2 }}>
              <LoadingSpinner />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Loading your sessions...
            </Typography>
          </Box>
        </LoadingOverlay>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <DocQASidebar
        currentSession={state.currentSession}
        filteredSessions={state.filteredSessions}
        searchQuery={state.searchQuery}
        setSearchQuery={state.setSearchQuery}
        getSession={state.getSession}
        setCreateDialogOpen={state.setCreateDialogOpen}
        setDeleteSessionConfirm={state.setDeleteSessionConfirm}
        setAddDocDialogOpen={state.setAddDocDialogOpen}
        setRemoveDocConfirm={state.setRemoveDocConfirm}
        addDocument={state.addDocument}
        selectedConnectionId={state.selectedConnectionId}
        setSelectedConnectionId={state.setSelectedConnectionId}
      />

      <ChatArea>
        {state.currentSession ? (
          <>
            <DocQAChatHeader
              currentSession={state.currentSession}
              messages={state.messages}
              connections={state.connections}
              docCount={state.docCount}
              setClearChatConfirm={state.setClearChatConfirm}
            />

            <MessagesContainer>
              {state.messages.length === 0 ? (
                <NoMessagesState
                  currentSession={state.currentSession}
                  connections={state.connections}
                  templates={state.templates}
                  suggestedQuestions={state.suggestedQuestions}
                  setQuestion={state.setQuestion}
                  setAddDocDialogOpen={state.setAddDocDialogOpen}
                  handleOpenReportPicker={state.handleOpenReportPicker}
                />
              ) : (
                <ChatMessages
                  messages={state.messages}
                  asking={state.asking}
                  setQuestion={state.setQuestion}
                  handleCopyMessage={state.handleCopyMessage}
                  handleCitationClick={state.handleCitationClick}
                  handleFeedback={state.handleFeedback}
                  handleRegenerate={state.handleRegenerate}
                />
              )}
              <div ref={state.messagesEndRef} />
            </MessagesContainer>

            <ChatInput
              currentSession={state.currentSession}
              question={state.question}
              setQuestion={state.setQuestion}
              asking={state.asking}
              error={state.error}
              reset={state.reset}
              inputRef={state.inputRef}
              handleKeyDown={state.handleKeyDown}
              handleAskQuestion={state.handleAskQuestion}
              setAddDocDialogOpen={state.setAddDocDialogOpen}
            />
          </>
        ) : (
          <NoSessionState setCreateDialogOpen={state.setCreateDialogOpen} />
        )}
      </ChatArea>

      <CreateSessionDialog
        open={state.createDialogOpen}
        onClose={() => state.setCreateDialogOpen(false)}
        newSessionName={state.newSessionName}
        setNewSessionName={state.setNewSessionName}
        handleCreateSession={state.handleCreateSession}
      />

      <AddDocumentDialog
        open={state.addDocDialogOpen}
        onClose={() => state.setAddDocDialogOpen(false)}
        docName={state.docName}
        setDocName={state.setDocName}
        docContent={state.docContent}
        setDocContent={state.setDocContent}
        handleAddDocument={state.handleAddDocument}
        handleFileUpload={state.handleFileUpload}
      />

      <ReportPickerDialog
        open={state.reportPickerOpen}
        onClose={() => state.setReportPickerOpen(false)}
        runsLoading={state.runsLoading}
        availableRuns={state.availableRuns}
        handleSelectReport={state.handleSelectReport}
      />

      <DocQAConfirmModals
        deleteSessionConfirm={state.deleteSessionConfirm}
        setDeleteSessionConfirm={state.setDeleteSessionConfirm}
        removeDocConfirm={state.removeDocConfirm}
        setRemoveDocConfirm={state.setRemoveDocConfirm}
        clearChatConfirm={state.clearChatConfirm}
        setClearChatConfirm={state.setClearChatConfirm}
        currentSession={state.currentSession}
        deleteSession={deleteSession}
        removeDocument={removeDocument}
        clearHistory={clearHistory}
        execute={state.execute}
      />
    </PageContainer>
  )
}

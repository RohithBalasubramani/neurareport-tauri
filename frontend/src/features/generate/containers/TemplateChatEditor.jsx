import { Box } from '@mui/material'
import { useTemplateChatEditor } from '../hooks/useTemplateChatEditor'
import ChatMessage from '../components/ChatMessage'
import ProposedChangesPanel from '../components/ProposedChangesPanel'
import FollowUpQuestions from '../components/FollowUpQuestions'
import MappingReviewPanel from '../components/MappingReviewPanel'
import ChatHeader from '../components/ChatHeader'
import ChatInput from '../components/ChatInput'

export default function TemplateChatEditor({
  templateId,
  templateName,
  currentHtml,
  onHtmlUpdate,
  onApplySuccess,
  onRequestSave,
  onMappingApprove,
  onMappingSkip,
  onMappingQueue,
  mappingPreviewData,
  mappingApproving = false,
  mode = 'edit',
  chatApi = null,
}) {
  const {
    messagesEndRef,
    inputRef,
    inputValue,
    setInputValue,
    isProcessing,
    applying,
    followUpQuestions,
    messages,
    proposedChanges,
    proposedHtml,
    readyToApply,
    modeConfig,
    handleSendMessage,
    handleApplyChanges,
    handleRejectChanges,
    handleQuestionClick,
    handleKeyDown,
    handleClearChat,
  } = useTemplateChatEditor({
    templateId,
    templateName,
    currentHtml,
    onHtmlUpdate,
    onApplySuccess,
    onRequestSave,
    mode,
    chatApi,
  })

  return (
    <Box
      sx={{
        height: '100%',
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'divider',
        overflow: 'hidden',
      }}
    >
      <ChatHeader mode={mode} onClearChat={handleClearChat} />

      {/* Messages + Proposed Changes + Follow-ups — all in one scrollable area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 1,
          minHeight: 0,
        }}
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {readyToApply && proposedChanges && (
          <ProposedChangesPanel
            changes={proposedChanges}
            proposedHtml={proposedHtml}
            onApply={handleApplyChanges}
            onReject={handleRejectChanges}
            applying={applying}
          />
        )}

        {mappingPreviewData && onMappingApprove && (
          <MappingReviewPanel
            mappingData={mappingPreviewData.mapping}
            catalog={mappingPreviewData.catalog}
            schemaInfo={mappingPreviewData.schema_info}
            onApprove={onMappingApprove}
            onSkip={onMappingSkip}
            onQueue={onMappingQueue}
            approving={mappingApproving}
          />
        )}

        <FollowUpQuestions
          questions={followUpQuestions}
          onQuestionClick={handleQuestionClick}
        />

        <div ref={messagesEndRef} />
      </Box>

      <ChatInput
        inputRef={inputRef}
        inputValue={inputValue}
        onInputChange={setInputValue}
        onKeyDown={handleKeyDown}
        onSend={handleSendMessage}
        isProcessing={isProcessing}
        readyToApply={readyToApply}
        placeholder={modeConfig.placeholder}
      />
    </Box>
  )
}

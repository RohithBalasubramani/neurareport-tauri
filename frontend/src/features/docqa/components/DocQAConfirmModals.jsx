/**
 * Confirm modals for the Document Q&A page.
 */
import React from 'react'
import ConfirmModal from '@/components/modal/ConfirmModal'
import { InteractionType, Reversibility } from '@/components/ux/governance'

export default function DocQAConfirmModals({
  deleteSessionConfirm,
  setDeleteSessionConfirm,
  removeDocConfirm,
  setRemoveDocConfirm,
  clearChatConfirm,
  setClearChatConfirm,
  currentSession,
  deleteSession,
  removeDocument,
  clearHistory,
  execute,
}) {
  return (
    <>
      <ConfirmModal
        open={deleteSessionConfirm.open}
        onClose={() => setDeleteSessionConfirm({ open: false, sessionId: null, sessionName: '' })}
        onConfirm={() => {
          const sessionId = deleteSessionConfirm.sessionId
          const sessionName = deleteSessionConfirm.sessionName
          setDeleteSessionConfirm({ open: false, sessionId: null, sessionName: '' })
          execute({
            type: InteractionType.DELETE,
            label: `Delete session "${sessionName}"`,
            reversibility: Reversibility.IRREVERSIBLE,
            successMessage: `Session "${sessionName}" deleted`,
            errorMessage: 'Failed to delete session',
            action: async () => {
              const success = await deleteSession(sessionId)
              if (!success) throw new Error('Delete failed')
            },
          })
        }}
        title="Delete Session"
        message={`Are you sure you want to delete "${deleteSessionConfirm.sessionName}"? All documents and chat history will be permanently removed.`}
        confirmLabel="Delete"
        severity="error"
      />

      <ConfirmModal
        open={removeDocConfirm.open}
        onClose={() => setRemoveDocConfirm({ open: false, docId: null, docName: '' })}
        onConfirm={() => {
          const docId = removeDocConfirm.docId
          const docName = removeDocConfirm.docName
          setRemoveDocConfirm({ open: false, docId: null, docName: '' })
          execute({
            type: InteractionType.DELETE,
            label: `Remove document "${docName}"`,
            reversibility: Reversibility.PARTIALLY_REVERSIBLE,
            successMessage: `Document "${docName}" removed`,
            errorMessage: 'Failed to remove document',
            action: async () => {
              const success = await removeDocument(currentSession?.id, docId)
              if (!success) throw new Error('Remove failed')
            },
          })
        }}
        title="Remove Document"
        message={`Are you sure you want to remove "${removeDocConfirm.docName}" from this session?`}
        confirmLabel="Remove"
        severity="warning"
      />

      <ConfirmModal
        open={clearChatConfirm.open}
        onClose={() => setClearChatConfirm({ open: false, sessionId: null, sessionName: '', messageCount: 0 })}
        onConfirm={() => {
          const sessionId = clearChatConfirm.sessionId
          const sessionName = clearChatConfirm.sessionName
          setClearChatConfirm({ open: false, sessionId: null, sessionName: '', messageCount: 0 })
          execute({
            type: InteractionType.DELETE,
            label: `Clear chat history for "${sessionName}"`,
            reversibility: Reversibility.PARTIALLY_REVERSIBLE,
            successMessage: 'Chat history cleared',
            errorMessage: 'Failed to clear chat history',
            action: async () => {
              await clearHistory(sessionId)
            },
          })
        }}
        title="Clear Chat History"
        message={`Are you sure you want to clear all ${clearChatConfirm.messageCount} messages from "${clearChatConfirm.sessionName}"? This action cannot be undone.`}
        confirmLabel="Clear History"
        severity="warning"
      />
    </>
  )
}
